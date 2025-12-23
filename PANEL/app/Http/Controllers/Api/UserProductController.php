<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\UserProduct;
use App\Models\Brand;
use App\Models\CompanyProductsUrl;
use App\Services\XmlParserService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;

class UserProductController extends Controller
{
    protected $xmlParserService;

    public function __construct(XmlParserService $xmlParserService)
    {
        $this->xmlParserService = $xmlParserService;
    }

    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        try {
            // Query builder oluştur
            $query = UserProduct::query();
            
            // is_active filtresi (query parameter ile)
            if ($request->has('is_active')) {
                $isActive = $request->input('is_active');
                // String olarak "1" veya boolean true kabul et
                if ($isActive === '1' || $isActive === 1 || $isActive === true || $isActive === 'true') {
                    $query->where('is_active', 1);
                } elseif ($isActive === '0' || $isActive === 0 || $isActive === false || $isActive === 'false') {
                    $query->where('is_active', 0);
                }
            }
            
            // Tüm ürünleri getir (veya filtrelenmiş)
            $products = $query->orderBy('created_at', 'desc')->get();
            
            // Brand bilgilerini ayrı çek
            $brandIds = $products->pluck('brand_id')->filter()->unique();
            $brands = Brand::whereIn('id', $brandIds)->get()->keyBy('id');
            
            // URL sayılarını ayrı çek
            $urlCounts = $this->getProductUrlCounts($products->pluck('id')->toArray());
            
            // Brand bilgilerini ve URL sayılarını ürünlere ekle
            $products->each(function ($product) use ($brands, $urlCounts) {
                if ($product->brand_id && isset($brands[$product->brand_id])) {
                    $product->brand = $brands[$product->brand_id];
                } else {
                    $product->brand = null;
                }
                
                // URL sayısını ekle
                $product->company_product_urls_count = $urlCounts[$product->id] ?? 0;
            });

            return response()->json([
                'success' => true,
                'data' => $products,
                'total' => $products->count()
            ]);
        } catch (\Exception $e) {
            Log::error('User products index error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürünler yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Import products from XML URL.
     */
    public function importFromXml(Request $request)
    {
        try {
            // Timeout ve memory ayarları
            set_time_limit(0);
            ini_set('memory_limit', '2048M');
            
            $validator = Validator::make($request->all(), [
                'xml_url' => 'required|url',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $xmlUrl = $request->input('xml_url');
            
            Log::info('XML import başlıyor', ['url' => $xmlUrl]);
            
            $result = $this->xmlParserService->parseAndImportFromUrl($xmlUrl);
            
            Log::info('XML import tamamlandı', [
                'success' => $result['success'] ?? false,
                'summary' => $result['summary'] ?? []
            ]);
            
            try {
                $response = response()->json($result, 201);
                return $response;
            } catch (\Exception $e) {
                Log::error('Response oluşturma hatası', [
                    'error' => $e->getMessage(),
                    'trace' => $e->getTraceAsString()
                ]);
                throw $e;
            }

        } catch (\Exception $e) {
            Log::error('XML import error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'XML import sırasında bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get XML structure info.
     */
    public function getXmlInfo(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'xml_url' => 'required|url',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            $xmlUrl = $request->input('xml_url');
            $structure = $this->xmlParserService->getXmlStructure($xmlUrl);

            return response()->json([
                'success' => true,
                'data' => $structure
            ]);

        } catch (\Exception $e) {
            Log::error('XML info error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'XML bilgisi alınırken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'title' => 'required|string|max:255',
                'image' => 'nullable|url',
                'brand_name' => 'nullable|string|max:255',
                'mpn' => 'nullable|string|max:255',
                'gtin' => 'nullable|string|max:255',
                'product_type' => 'nullable|string|max:255',
                'price' => 'nullable|numeric|min:0',
                'sale_price' => 'nullable|numeric|min:0',
                'availability' => 'nullable|string|max:255',
                'link' => 'nullable|url',
                'is_active' => 'nullable|boolean|in:0,1',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            // Find or create brand
            $brandId = null;
            if ($request->brand_name) {
                $brand = Brand::firstOrCreate(
                    ['name' => $request->brand_name],
                    [
                        'slug' => \Illuminate\Support\Str::slug($request->brand_name),
                        'is_active' => true
                    ]
                );
                $brandId = $brand->id;
            }

            $productData = [
                'title' => $request->title,
                'image' => $request->image,
                'brand_id' => $brandId,
                'mpn' => $request->mpn,
                'gtin' => $request->gtin,
                'product_type' => $request->product_type,
                'price' => $request->price,
                'sale_price' => $request->sale_price,
                'availability' => $request->availability,
                'link' => $request->link,
            ];
            
            // is_active alanını ekle (varsa, yoksa varsayılan olarak 1)
            $productData['is_active'] = $request->has('is_active') ? ($request->is_active ? 1 : 0) : 1;
            
            $product = UserProduct::create($productData);

            $product->load('brand');

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla eklendi',
                'data' => $product
            ], 201);

        } catch (\Exception $e) {
            Log::error('Product store error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürün eklenirken bir hata oluştu',
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
            $product = UserProduct::with('brand')->findOrFail($id);

            return response()->json([
                'success' => true,
                'data' => $product
            ]);

        } catch (\Exception $e) {
            Log::error('Product show error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürün bulunamadı',
                'error' => $e->getMessage()
            ], 404);
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        try {
            $product = UserProduct::findOrFail($id);

            $validator = Validator::make($request->all(), [
                'title' => 'required|string|max:255',
                'image' => 'nullable|url',
                'brand_name' => 'nullable|string|max:255',
                'mpn' => 'nullable|string|max:255',
                'gtin' => 'nullable|string|max:255',
                'product_type' => 'nullable|string|max:255',
                'price' => 'nullable|numeric|min:0',
                'sale_price' => 'nullable|numeric|min:0',
                'availability' => 'nullable|string|max:255',
                'link' => 'nullable|url',
                'is_active' => 'nullable|boolean|in:0,1',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Doğrulama hatası',
                    'errors' => $validator->errors()
                ], 422);
            }

            // Find or create brand
            $brandId = $product->brand_id;
            if ($request->brand_name) {
                $brand = Brand::firstOrCreate(
                    ['name' => $request->brand_name],
                    [
                        'slug' => \Illuminate\Support\Str::slug($request->brand_name),
                        'is_active' => true
                    ]
                );
                $brandId = $brand->id;
            }

            $updateData = [
                'title' => $request->title,
                'image' => $request->image,
                'brand_id' => $brandId,
                'mpn' => $request->mpn,
                'gtin' => $request->gtin,
                'product_type' => $request->product_type,
                'price' => $request->price,
                'sale_price' => $request->sale_price,
                'availability' => $request->availability,
                'link' => $request->link,
            ];
            
            // is_active alanını ekle (varsa)
            if ($request->has('is_active')) {
                $updateData['is_active'] = $request->is_active ? 1 : 0;
            }
            
            $product->update($updateData);

            $product->load('brand');

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla güncellendi',
                'data' => $product
            ]);

        } catch (\Exception $e) {
            Log::error('Product update error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürün güncellenirken bir hata oluştu',
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
            $product = UserProduct::findOrFail($id);
            $product->delete();

            return response()->json([
                'success' => true,
                'message' => 'Ürün başarıyla silindi'
            ]);

        } catch (\Exception $e) {
            Log::error('Product delete error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürün silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete all user products.
     */
    public function deleteAll()
    {
        try {
            $deletedCount = UserProduct::count();
            UserProduct::truncate();

            return response()->json([
                'success' => true,
                'message' => 'Tüm ürünler başarıyla silindi',
                'deleted_count' => $deletedCount
            ]);

        } catch (\Exception $e) {
            Log::error('Delete all products error: ' . $e->getMessage());
            return response()->json([
                'success' => false,
                'message' => 'Ürünler silinirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get URL counts for products in a single query.
     */
    private function getProductUrlCounts(array $productIds): array
    {
        if (empty($productIds)) {
            return [];
        }

        $urlCounts = CompanyProductsUrl::whereIn('product_id', $productIds)
            ->selectRaw('product_id, COUNT(*) as url_count')
            ->groupBy('product_id')
            ->pluck('url_count', 'product_id')
            ->toArray();

        return $urlCounts;
    }
}
