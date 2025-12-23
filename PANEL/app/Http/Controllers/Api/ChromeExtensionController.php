<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Attribute;
use App\Models\Company;
use App\Models\CompanyAttribute;
use App\Services\ScanningService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class ChromeExtensionController extends Controller
{
    /**
     * Validate iPrice token and get user information.
     */
    public function validateToken(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();

        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        return response()->json([
            'success' => true,
            'user' => [
                'id' => $user->id,
                'name' => $user->name,
                'email' => $user->email
            ]
        ]);
    }

    /**
     * Add attribute from Chrome extension.
     */
    public function addAttribute(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
            'company_name' => 'required|string|max:255',
            'company_url' => 'required|url',
            'attribute_name' => 'required|string|max:255',
            'selector_type' => 'required|in:class,xpath',
            'selector_value' => 'required|string',
            'page_url' => 'required|url'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            DB::beginTransaction();

            // Validate token and get user
            $user = User::where('iprice_token', $request->token)->first();
            if (!$user) {
                return response()->json([
                    'success' => false,
                    'message' => 'Geçersiz token'
                ], 401);
            }

            // Extract domain from URL
            $domain = $this->extractDomain($request->company_url);
            
            // Find company by domain (check both company_site and extract domain from existing sites)
            $company = $this->findCompanyByDomain($domain);
            
            if (!$company) {
                $company = Company::create([
                    'name' => $request->company_name,
                    'url' => $request->company_url,
                    'crawler_id' => 1, // Default crawler
                    'server_id' => 1,  // Default server
                    'screenshot' => null,
                    'marketplace' => null,
                    'deleted' => false
                ]);
            }

            // Find or create attribute
            $attribute = Attribute::where('name', $request->attribute_name)->first();
            if (!$attribute) {
                $attribute = Attribute::create([
                    'name' => $request->attribute_name
                ]);
            }

            // Check if company-attribute combination already exists
            $existingCompanyAttribute = CompanyAttribute::where('company_id', $company->id)
                ->where('attribute_id', $attribute->id)
                ->first();

            if ($existingCompanyAttribute) {
                // Update existing record
                $existingCompanyAttribute->update([
                    'type' => $request->selector_type,
                    'value' => $request->selector_value
                ]);

                $companyAttribute = $existingCompanyAttribute;
            } else {
                // Create new company-attribute relationship
                $companyAttribute = CompanyAttribute::create([
                    'company_id' => $company->id,
                    'attribute_id' => $attribute->id,
                    'type' => $request->selector_type,
                    'value' => $request->selector_value
                ]);
            }

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Attribute başarıyla eklendi',
                'data' => [
                    'company' => $company,
                    'attribute' => $attribute,
                    'company_attribute' => $companyAttribute
                ]
            ]);

        } catch (\Exception $e) {
            DB::rollBack();
            
            return response()->json([
                'success' => false,
                'message' => 'Attribute eklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get available attributes for Chrome extension.
     */
    public function getAttributes(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        $attributes = Attribute::orderBy('name')->get();

        return response()->json([
            'success' => true,
            'data' => $attributes
        ]);
    }

    /**
     * Get user's companies for Chrome extension.
     */
    public function getUserCompanies(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        $companies = Company::where('deleted', false)
            ->with(['companyAttributes.attribute'])
            ->orderBy('name')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $companies
        ]);
    }

    /**
     * Test connection from Chrome extension.
     */
    public function testConnection(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        return response()->json([
            'success' => true,
            'message' => 'Bağlantı başarılı',
            'user' => [
                'name' => $user->name,
                'email' => $user->email
            ]
        ]);
    }

    /**
     * Extract domain from URL
     */
    private function extractDomain($url)
    {
        $parsedUrl = parse_url($url);
        $host = $parsedUrl['host'] ?? '';
        
        // Remove www. prefix if exists
        if (strpos($host, 'www.') === 0) {
            $host = substr($host, 4);
        }
        
        return $host;
    }

    /**
     * Find company by domain
     */
    private function findCompanyByDomain($domain)
    {
        // First try exact match - only active (non-deleted) companies
        $company = Company::where('deleted', false)
            ->where('url', 'like', '%' . $domain . '%')
            ->first();
        
        if ($company) {
            return $company;
        }
        
        // Try to find by extracting domain from existing url - only active companies
        $companies = Company::where('deleted', false)->get();
        foreach ($companies as $comp) {
            if ($comp->url) {
                $existingDomain = $this->extractDomain($comp->url);
                if ($existingDomain === $domain) {
                    return $comp;
                }
            }
        }
        
        return null;
    }

    /**
     * Sync labels (attributes) from Chrome extension
     */
    public function syncLabels(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
            'labels' => 'required|array',
            'labels.*.name' => 'required|string|max:255',
            'labels.*.description' => 'nullable|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası',
                'errors' => $validator->errors()
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        try {
            DB::beginTransaction();

            $syncedLabels = [];
            foreach ($request->labels as $labelData) {
                // Find or create attribute
                $attribute = Attribute::firstOrCreate(
                    ['name' => $labelData['name']],
                    ['description' => $labelData['description'] ?? null]
                );

                // Update description if provided
                if (isset($labelData['description']) && $attribute->description !== $labelData['description']) {
                    $attribute->update(['description' => $labelData['description']]);
                }

                $syncedLabels[] = [
                    'id' => $attribute->id,
                    'name' => $attribute->name,
                    'description' => $attribute->description
                ];
            }

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Etiketler başarıyla senkronize edildi',
                'data' => $syncedLabels
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            
            return response()->json([
                'success' => false,
                'message' => 'Etiketler senkronize edilirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get all labels (attributes) for Chrome extension
     */
    public function getLabels(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        $attributes = Attribute::orderBy('name')->get()->map(function ($attr) {
            return [
                'id' => $attr->id,
                'name' => $attr->name,
                'description' => $attr->description
            ];
        });

        return response()->json([
            'success' => true,
            'data' => $attributes
        ]);
    }

    /**
     * Sync selectors (company attributes) from Chrome extension
     */
    public function syncSelectors(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
            'selectors' => 'required|array',
            'selectors.*.domain' => 'required|string',
            'selectors.*.company_name' => 'nullable|string|max:255',
            'selectors.*.company_url' => 'nullable|url',
            'selectors.*.items' => 'required|array',
            'selectors.*.items.*.label' => 'required|string|max:255',
            'selectors.*.items.*.label_id' => 'nullable|integer|exists:attributes,id',
            'selectors.*.items.*.attribute_id' => 'nullable|integer|exists:attributes,id', // Alias for label_id
            'selectors.*.items.*.selector' => 'required|string',
            'selectors.*.items.*.selector_type' => 'required|in:class,xpath',
            'selectors.*.items.*.note' => 'nullable|string',
            'selectors.*.items.*.modules' => 'nullable|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası',
                'errors' => $validator->errors()
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        try {
            DB::beginTransaction();

            $syncedData = [];

            foreach ($request->selectors as $domainData) {
                $domain = $domainData['domain'];
                
                // Find or create company
                $company = $this->findCompanyByDomain($domain);
                
                if (!$company) {
                    // Create new company if not exists
                    $companyUrl = $domainData['company_url'] ?? 'https://' . $domain;
                    $companyName = $domainData['company_name'] ?? $domain;
                    
                    $company = Company::create([
                        'name' => $companyName,
                        'url' => $companyUrl,
                        'crawler_id' => 1,
                        'server_id' => 1,
                        'screenshot' => null,
                        'marketplace' => null,
                        'deleted' => false
                    ]);
                }

                $domainSelectors = [];

                foreach ($domainData['items'] as $item) {
                    // Find or create attribute (label)
                    // Eğer label_id veya attribute_id gönderilmişse, onu kullan
                    $attribute = null;
                    if (!empty($item['label_id']) || !empty($item['attribute_id'])) {
                        $attributeId = $item['label_id'] ?? $item['attribute_id'];
                        $attribute = Attribute::find($attributeId);
                        if (!$attribute) {
                            // Eğer ID ile bulunamazsa, name ile oluştur
                            $attribute = Attribute::firstOrCreate(
                                ['name' => $item['label']],
                                ['description' => null]
                            );
                        }
                    } else {
                        // ID gönderilmemişse, name ile bul veya oluştur
                        $attribute = Attribute::firstOrCreate(
                            ['name' => $item['label']],
                            ['description' => null]
                        );
                    }

                    // Prepare value - include note and modules in JSON format
                    $valueData = [
                        'selector' => $item['selector'],
                        'note' => $item['note'] ?? null,
                        'modules' => $item['modules'] ?? []
                    ];
                    $value = json_encode($valueData, JSON_UNESCAPED_UNICODE);

                    // Check if company attribute already exists for this company and attribute
                    $existingCompanyAttribute = CompanyAttribute::where('company_id', $company->id)
                        ->where('attribute_id', $attribute->id)
                        ->first();

                    // Update or create company attribute
                    // Eğer aynı company_id ve attribute_id için kayıt varsa, güncelle
                    // Yoksa yeni kayıt oluştur
                    $companyAttribute = CompanyAttribute::updateOrCreate(
                        [
                            'company_id' => $company->id,
                            'attribute_id' => $attribute->id
                        ],
                        [
                            'type' => $item['selector_type'],
                            'value' => $value
                        ]
                    );

                    // Log for debugging (optional - can be removed in production)
                    if ($existingCompanyAttribute) {
                        \Log::info("Company attribute updated", [
                            'company_id' => $company->id,
                            'attribute_id' => $attribute->id,
                            'old_value' => $existingCompanyAttribute->value,
                            'new_value' => $value
                        ]);
                    } else {
                        \Log::info("Company attribute created", [
                            'company_id' => $company->id,
                            'attribute_id' => $attribute->id,
                            'value' => $value
                        ]);
                    }

                    $domainSelectors[] = [
                        'label' => $item['label'],
                        'label_id' => $attribute->id,
                        'attribute_id' => $attribute->id, // Alias for compatibility
                        'selector' => $item['selector'],
                        'selector_type' => $item['selector_type'],
                        'note' => $item['note'] ?? null,
                        'modules' => $item['modules'] ?? []
                    ];
                }

                $syncedData[] = [
                    'domain' => $domain,
                    'company_id' => $company->id,
                    'company_name' => $company->name,
                    'selectors' => $domainSelectors
                ];
            }

            DB::commit();

            return response()->json([
                'success' => true,
                'message' => 'Seçiciler başarıyla senkronize edildi',
                'data' => $syncedData
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            
            return response()->json([
                'success' => false,
                'message' => 'Seçiciler senkronize edilirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get selectors (company attributes) for Chrome extension
     */
    public function getSelectors(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
            'domain' => 'nullable|string' // Optional: get selectors for specific domain
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Token gerekli'
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        try {
            $query = Company::where('deleted', false)
                ->with(['companyAttributes.attribute']);

            // Filter by domain if provided
            if ($request->has('domain') && $request->domain) {
                $domain = $this->extractDomain($request->domain);
                $query->where('url', 'like', '%' . $domain . '%');
            }

            $companies = $query->get();

            $selectorsByDomain = [];

            foreach ($companies as $company) {
                $domain = $this->extractDomain($company->url);
                
                $items = [];
                foreach ($company->companyAttributes as $companyAttribute) {
                    // Parse value (JSON format)
                    $valueData = json_decode($companyAttribute->value, true);
                    
                    $items[] = [
                        'label' => $companyAttribute->attribute->name,
                        'label_id' => $companyAttribute->attribute_id,
                        'attribute_id' => $companyAttribute->attribute_id, // Alias for compatibility
                        'selector' => $valueData['selector'] ?? $companyAttribute->value,
                        'selector_type' => $companyAttribute->type,
                        'note' => $valueData['note'] ?? null,
                        'modules' => $valueData['modules'] ?? []
                    ];
                }

                if (!empty($items)) {
                    $selectorsByDomain[] = [
                        'domain' => $domain,
                        'company_id' => $company->id,
                        'company_name' => $company->name,
                        'items' => $items
                    ];
                }
            }

            return response()->json([
                'success' => true,
                'data' => $selectorsByDomain
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Seçiciler yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Send message to RabbitMQ queue via backend (for VPN compatibility)
     * Chrome extension'dan gelen mesajları RabbitMQ'ya gönderir
     */
    public function sendToQueue(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'token' => 'required|string',
            'queue_name' => 'required|string',
            'message_data' => 'required|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Doğrulama hatası',
                'errors' => $validator->errors()
            ], 422);
        }

        $user = User::where('iprice_token', $request->token)->first();
        if (!$user) {
            return response()->json([
                'success' => false,
                'message' => 'Geçersiz token'
            ], 401);
        }

        try {
            $scanningService = new ScanningService();
            
            // Queue name'e göre server_id belirle
            // chrome.queue için server_id = 3 (chrome)
            $serverId = 3; // Default: chrome server
            
            // Queue name'e göre server belirleme
            if (strpos($request->queue_name, 'chrome.queue') === 0) {
                $serverId = 3; // chrome
            } elseif (strpos($request->queue_name, 'scrapy.queue') === 0) {
                $serverId = 1; // local
            } elseif (strpos($request->queue_name, 'selenium.queue') === 0) {
                $serverId = 1; // local
            } elseif (strpos($request->queue_name, 'playwright.queue') === 0) {
                $serverId = 1; // local
            }
            
            // Reflection kullanarak private sendToQueue metodunu çağır
            $reflection = new \ReflectionClass($scanningService);
            $method = $reflection->getMethod('sendToQueue');
            $method->setAccessible(true);
            
            $result = $method->invoke($scanningService, $request->queue_name, $request->message_data, $serverId);
            
            if ($result) {
                return response()->json([
                    'success' => true,
                    'message' => 'Mesaj başarıyla RabbitMQ\'ya gönderildi',
                    'queue_name' => $request->queue_name
                ]);
            } else {
                return response()->json([
                    'success' => false,
                    'message' => 'Mesaj RabbitMQ\'ya gönderilemedi'
                ], 500);
            }
        } catch (\Exception $e) {
            \Log::error('Chrome Extension sendToQueue error: ' . $e->getMessage(), [
                'queue_name' => $request->queue_name,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            return response()->json([
                'success' => false,
                'message' => 'Mesaj gönderilirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}