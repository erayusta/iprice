<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Company;
use App\Models\CompanyProductsUrl;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;

class ProductController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $query = CompanyProductsUrl::with(['company', 'userProduct']);
        
        // Search filter
        if ($request->has('search') && $request->search) {
            $query->where('url', 'LIKE', "%{$request->search}%");
        }
        
        // Company filter
        if ($request->has('company_id') && $request->company_id) {
            $query->where('company_id', $request->company_id);
        }
        
        // Product filter
        if ($request->has('product_id') && $request->product_id) {
            $query->where('product_id', $request->product_id);
        }
        
        $products = $query->orderBy('created_at', 'desc')->get();
        
        return response()->json([
            'success' => true,
            'data' => $products
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'url' => 'required|url',
                'company_id' => 'required|exists:companies,id',
                'product_id' => 'nullable|exists:user_products,id',
            ]);

            // Check if URL already exists for this company and product combination
            // Only check for non-marketplace companies
            if ($request->has('product_id') && $request->product_id) {
                $company = Company::find($request->company_id);
                
                // Only enforce single URL rule for non-marketplace companies
                if (!$company || !$company->is_marketplace) {
                    $existingUrl = CompanyProductsUrl::where('company_id', $request->company_id)
                        ->where('product_id', $request->product_id)
                        ->first();
                    
                    if ($existingUrl) {
                        return response()->json([
                            'success' => false,
                            'message' => 'Bu ürün için bu firmada zaten bir URL tanımlanmış',
                            'existing_url' => $existingUrl->url
                        ], 422);
                    }
                }
            }

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $product = CompanyProductsUrl::create($request->all());

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla oluşturuldu',
                'data' => $product->load('company')
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün oluşturulurken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Batch store multiple products.
     */
    public function batchStore(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'urls' => 'required|array|min:1',
                'urls.*' => 'required|url',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $urls = $request->input('urls');
            $results = [
                'success' => [],
                'failed' => [],
                'skipped' => []
            ];

            foreach ($urls as $url) {
                try {
                    // Extract domain from URL
                    $domain = $this->extractDomain($url);
                    
                    // Find company by domain
                    $company = $this->findCompanyByDomain($domain);
                    
                    if (!$company) {
                        $results['failed'][] = [
                            'url' => $url,
                            'reason' => 'Domain için firma bulunamadı: ' . $domain
                        ];
                        continue;
                    }

                    // Check if URL already exists
                    $existingProduct = CompanyProductsUrl::where('url', $url)->first();
                    if ($existingProduct) {
                        $results['skipped'][] = [
                            'url' => $url,
                            'reason' => 'Bu URL zaten mevcut'
                        ];
                        continue;
                    }

                    // Create product
                    $product = CompanyProductsUrl::create([
                        'url' => $url,
                        'company_id' => $company->id
                    ]);

                    $results['success'][] = [
                        'url' => $url,
                        'company' => $company->company_name,
                        'product_id' => $product->id
                    ];

                } catch (\Exception $e) {
                    $results['failed'][] = [
                        'url' => $url,
                        'reason' => 'Hata: ' . $e->getMessage()
                    ];
                }
            }

            $totalProcessed = count($urls);
            $successCount = count($results['success']);
            $failedCount = count($results['failed']);
            $skippedCount = count($results['skipped']);

            return response()->json([
                'success' => true,
                'message' => "İşlem tamamlandı. Başarılı: {$successCount}, Başarısız: {$failedCount}, Atlanan: {$skippedCount}",
                'data' => $results,
                'summary' => [
                    'total' => $totalProcessed,
                    'success' => $successCount,
                    'failed' => $failedCount,
                    'skipped' => $skippedCount
                ]
            ], 201);

        } catch (\Exception $e) {
            Log::error('Batch product store error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Toplu ürün ekleme sırasında bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        try {
            $product = CompanyProductsUrl::with(['company'])->findOrFail($id);
            
            return response()->json([
                'success' => true,
                'data' => $product
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün bulunamadı.'
            ], 404);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        try {
            $product = CompanyProductsUrl::findOrFail($id);
            
            $validator = Validator::make($request->all(), [
                'url' => 'sometimes|required|url',
                'company_id' => 'sometimes|required|exists:companies,id',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $product->update($request->all());

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla güncellendi',
                'data' => $product->load('company')
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün bulunamadı.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün güncellenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store multiple URLs for a marketplace company and product.
     */
    public function storeMarketplaceUrls(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'company_id' => 'required|exists:companies,id',
                'product_id' => 'required|exists:user_products,id',
                'urls' => 'required|array|min:1',
                'urls.*' => 'required|url',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $company = Company::find($request->company_id);
            if (!$company || !$company->is_marketplace) {
                return response()->json([
                    'success' => false,
                    'message' => 'Bu firma marketplace değil'
                ], 422);
            }

            // Check URL limit for marketplace (max 10 URLs per product)
            $existingUrlCount = CompanyProductsUrl::where('company_id', $request->company_id)
                ->where('product_id', $request->product_id)
                ->count();
            
            if ($existingUrlCount + count($request->urls) > 10) {
                return response()->json([
                    'success' => false,
                    'message' => 'Marketplace için maksimum 10 URL ekleyebilirsiniz. Mevcut: ' . $existingUrlCount
                ], 422);
            }

            $createdUrls = [];
            $errors = [];

            foreach ($request->urls as $url) {
                try {
                    // Check if URL already exists for this product and company
                    $existingUrl = CompanyProductsUrl::where('company_id', $request->company_id)
                        ->where('product_id', $request->product_id)
                        ->where('url', $url)
                        ->first();
                    
                    if ($existingUrl) {
                        $errors[] = "URL zaten mevcut: {$url}";
                        continue;
                    }

                    $productUrl = CompanyProductsUrl::create([
                        'company_id' => $request->company_id,
                        'product_id' => $request->product_id,
                        'url' => $url
                    ]);

                    $createdUrls[] = $productUrl->load('company');
                } catch (\Exception $e) {
                    $errors[] = "URL kaydedilemedi: {$url} - " . $e->getMessage();
                }
            }

            return response()->json([
                'success' => true,
                'message' => count($createdUrls) . ' URL başarıyla oluşturuldu',
                'data' => $createdUrls,
                'errors' => $errors
            ], 201);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'URL\'ler oluşturulurken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        try {
            $product = CompanyProductsUrl::findOrFail($id);
            $product->delete();

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla silindi'
            ]);
        } catch (\Illuminate\Database\Eloquent\ModelNotFoundException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün bulunamadı.'
            ], 404);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Ürün silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete all company product URLs.
     */
    public function deleteAll()
    {
        try {
            // Use raw SQL for better performance with large datasets
            $deletedCount = \DB::table('company_products_urls')->count();
            \DB::table('company_products_urls')->truncate();

            return response()->json([
                'success' => true,
                'message' => 'Tüm URL\'ler başarıyla silindi',
                'deleted_count' => $deletedCount
            ]);

        } catch (\Exception $e) {
            Log::error('Delete all URLs error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'URL\'ler silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Export all URLs to Excel format (JSON data for frontend to convert to Excel).
     */
    public function exportUrls()
    {
        try {
            // Get all URLs with company and user product relationships
            $urls = CompanyProductsUrl::with(['company', 'userProduct'])
                ->whereNotNull('product_id')
                ->whereNotNull('url')
                ->where('url', '!=', '')
                ->get();

            // Prepare export data
            $exportData = [];
            
            // Header row
            $exportData[] = ['MPN', 'Firma Adı', 'URL'];

            // Data rows
            foreach ($urls as $url) {
                $mpn = $url->userProduct ? ($url->userProduct->mpn ?? 'N/A') : 'N/A';
                // Get company name - try company_name field first, then name
                $companyName = 'N/A';
                if ($url->company) {
                    $companyName = $url->company->company_name ?? $url->company->name ?? 'N/A';
                }
                $urlValue = $url->url ?? '';

                $exportData[] = [
                    $mpn,
                    $companyName,
                    $urlValue
                ];
            }

            return response()->json([
                'success' => true,
                'data' => $exportData,
                'count' => count($exportData) - 1, // Exclude header
                'filename' => 'urun_urls_' . date('Y-m-d_H-i-s') . '.xlsx'
            ]);

        } catch (\Exception $e) {
            Log::error('Export URLs error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'URL\'ler dışa aktarılırken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Extract domain from URL.
     */
    private function extractDomain($url)
    {
        try {
            $parsedUrl = parse_url($url);
            $host = $parsedUrl['host'] ?? '';
            
            // Remove www. prefix if exists
            if (strpos($host, 'www.') === 0) {
                $host = substr($host, 4);
            }
            
            return $host;
        } catch (\Exception $e) {
            Log::error('Domain extraction error: ' . $e->getMessage());
            return '';
        }
    }

    /**
     * Find company by domain.
     */
    private function findCompanyByDomain($domain)
    {
        try {
            // First try exact match
            $company = Company::where('company_site', 'LIKE', "%{$domain}%")
                ->where('deleted', 0)
                ->first();

            if ($company) {
                return $company;
            }

            // Try to find by domain in company_site
            $companies = Company::where('deleted', 0)->get();
            
            foreach ($companies as $company) {
                if ($company->company_site) {
                    $companyDomain = $this->extractDomain($company->company_site);
                    if ($companyDomain === $domain) {
                        return $company;
                    }
                }
            }

            return null;
        } catch (\Exception $e) {
            Log::error('Company search by domain error: ' . $e->getMessage());
            return null;
        }
    }
}