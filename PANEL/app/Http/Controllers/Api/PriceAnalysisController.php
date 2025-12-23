<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Company;
use App\Models\CompanyProductsUrl;
use App\Models\ProductAttributeValue;
use App\Models\ProductAttributeValueSummary;
use Illuminate\Http\Request;

class PriceAnalysisController extends Controller
{
    /**
     * Get company list for price analysis
     */
    public function companyList()
    {
        try {
            $companies = Company::where('deleted', false)
                ->select('id', 'name', 'marketplace', 'url', 'company_logo')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $companies
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Şirket listesi yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get price summary
     */
    public function priceSummary()
    {
        try {
            // Fiyat attribute_id'leri: 1, 15, 16, 28, 29, 30, 31, 32, 33, 34, 35, 36
            $allPrices = ProductAttributeValueSummary::whereIn('attribute_id', [1, 15, 16, 28, 29, 30, 31, 32, 33, 34, 35, 36])
                ->select('id', 'company_id', 'value', 'updated_at', 'job_id', 'product_id', 'attribute_id')
                ->get();

            // Stok verilerini al (attribute_id = 23)
            $allStockData = ProductAttributeValueSummary::where('attribute_id', 23)
                ->select('id', 'company_id', 'value', 'updated_at', 'job_id', 'product_id', 'attribute_id')
                ->get();

            // Stok verilerini product_id ve company_id'ye göre grupla
            $groupedStock = $allStockData->groupBy(function ($item) {
                return $item->product_id . '_' . $item->company_id;
            });

            // Stok verilerini işle ve boolean'a çevir
            $stockMap = [];
            foreach ($groupedStock as $groupKey => $stockItems) {
                if ($stockItems->isEmpty()) {
                    continue;
                }

                // En büyük job_id'yi bul
                $maxJobId = $stockItems->max('job_id');
                
                // En büyük job_id'ye ait stok verisini al
                $latestStock = $stockItems->where('job_id', $maxJobId)->sortByDesc('updated_at')->first();
                
                if ($latestStock) {
                    // Value'yu boolean'a çevir: true, 1 -> TRUE, false, 0 -> FALSE
                    $stockValue = $latestStock->value;
                    $stockBoolean = false;
                    
                    if (is_bool($stockValue)) {
                        $stockBoolean = $stockValue;
                    } elseif (is_numeric($stockValue)) {
                        $stockBoolean = (bool) $stockValue;
                    } elseif (is_string($stockValue)) {
                        $stockValueLower = strtolower(trim($stockValue));
                        $stockBoolean = in_array($stockValueLower, ['true', '1', 'yes', 'on']);
                    }
                    
                    $stockMap[$groupKey] = [
                        'availability' => $stockBoolean,
                        'updated_at' => $latestStock->updated_at,
                        'job_id' => $latestStock->job_id
                    ];
                }
            }

            // product_id ve company_id'ye göre grupla
            $groupedPrices = $allPrices->groupBy(function ($item) {
                return $item->product_id . '_' . $item->company_id;
            });

            $finalPrices = [];

            foreach ($groupedPrices as $groupKey => $prices) {
                if ($prices->isEmpty()) {
                    continue;
                }

                // En büyük job_id'yi bul
                $maxJobId = $prices->max('job_id');
                
                // En büyük job_id'ye ait tüm fiyatları al
                $pricesFromLatestJob = $prices->where('job_id', $maxJobId);
                
                if ($pricesFromLatestJob->isEmpty()) {
                    continue;
                }
                
                // En büyük job_id'deki fiyatlar arasından en küçük value'yu bul (en ucuz)
                $selectedPrice = $pricesFromLatestJob->sortBy('value')->first();
                
                // Tüm fiyatlar arasından en ucuz fiyatı bul (cheapest_price için)
                $cheapestPrice = $prices->sortBy('value')->first();
                
                // Aynı value ve job_id kombinasyonuna sahip kayıtları tekilleştir (unique)
                // value ve job_id kombinasyonuna göre grupla, her gruptan en yeni olanı al
                $uniquePrices = $prices->groupBy(function ($item) {
                    return $item->value . '_' . $item->job_id;
                })->map(function ($group) {
                    // Her grup için en yeni olanı al (updated_at'e göre)
                    return $group->sortByDesc('updated_at')->first();
                })->values();
                
                // Tüm fiyatları hazırla (updated_at'e göre sıralı)
                $allPricesData = $uniquePrices->sortByDesc('updated_at')->map(function ($price) use ($selectedPrice, $cheapestPrice) {
                    return [
                        'id' => $price->id,
                        'attribute_id' => $price->attribute_id,
                        'value' => $price->value,
                        'updated_at' => $price->updated_at,
                        'job_id' => $price->job_id,
                        'is_latest' => $price->id === $selectedPrice->id,
                        'is_cheapest' => $price->id === $cheapestPrice->id
                    ];
                })->values()->toArray();

                // Stok bilgisini al
                $stockInfo = $stockMap[$groupKey] ?? null;

                // Ana fiyat olarak en büyük job_id'deki en ucuz fiyatı kullan
                $finalPrices[] = [
                    'id' => $selectedPrice->id,
                    'company_id' => $selectedPrice->company_id,
                    'product_id' => $selectedPrice->product_id,
                    'value' => $selectedPrice->value,
                    'updated_at' => $selectedPrice->updated_at,
                    'job_id' => $selectedPrice->job_id,
                    'attribute_id' => $selectedPrice->attribute_id,
                    'is_latest' => true,
                    'is_cheapest' => $selectedPrice->id === $cheapestPrice->id,
                    'cheapest_price' => $cheapestPrice->value,
                    'has_cheaper_price' => $selectedPrice->id !== $cheapestPrice->id,
                    'all_prices' => $allPricesData,
                    'total_price_count' => $prices->count(),
                    'availability' => $stockInfo ? $stockInfo['availability'] : null,
                    'availability_updated_at' => $stockInfo ? $stockInfo['updated_at'] : null,
                    'availability_job_id' => $stockInfo ? $stockInfo['job_id'] : null
                ];
            }

            // company_product_urls tablosundan tüm product_id ve company_id verilerini al
            $companyProductUrls = CompanyProductsUrl::select('product_id', 'company_id')
                ->get();

            // Hızlı lookup için bir set oluştur (product_id_company_id kombinasyonu)
            $validProductCompanyPairs = $companyProductUrls->map(function ($item) {
                return $item->product_id . '_' . $item->company_id;
            })->toArray();

            // finalPrices'dan sadece company_product_urls tablosunda olan ürünleri filtrele
            $finalPrices = array_filter($finalPrices, function ($price) use ($validProductCompanyPairs) {
                $key = $price['product_id'] . '_' . $price['company_id'];
                return in_array($key, $validProductCompanyPairs);
            });

            // array_filter sonrası index'leri yeniden düzenle
            $finalPrices = array_values($finalPrices);

            return response()->json([
                'success' => true,
                'data' => $finalPrices
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Fiyat özeti yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get company URL list
     */
    public function companyUrlList()
    {
        try {
            $companyUrls = CompanyProductsUrl::select('company_id', 'product_id', 'url')
                ->get();

            return response()->json([
                'success' => true,
                'data' => $companyUrls
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Şirket URL listesi yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get price history for a specific product and company
     */
    public function priceHistory(Request $request)
    {
        try {
            $companyId = $request->query('company_id');
            $productId = $request->query('product_id');

            if (!$companyId || !$productId) {
                return response()->json([
                    'success' => false,
                    'message' => 'company_id ve product_id parametreleri gereklidir'
                ], 400);
            }

            $priceHistory = ProductAttributeValue::where('company_id', $companyId)
                ->where('product_id', $productId)
                ->whereIn('attribute_id', [15, 16, 28, 29, 30])
                ->select('company_id', 'attribute_id', 'value', 'created_at', 'job_id', 'product_id')
                ->orderBy('created_at', 'desc')
                ->limit(3)
                ->get();

            return response()->json([
                'success' => true,
                'data' => $priceHistory
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Fiyat geçmişi yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get all prices for a specific product and company
     */
    public function productPrices(Request $request)
    {
        try {
            $companyId = $request->query('company_id');
            $productId = $request->query('product_id');

            if (!$companyId || !$productId) {
                return response()->json([
                    'success' => false,
                    'message' => 'company_id ve product_id parametreleri gereklidir'
                ], 400);
            }

            // Summary tablosundan tüm fiyatları al
            $allPrices = ProductAttributeValueSummary::where('company_id', $companyId)
                ->where('product_id', $productId)
                ->whereIn('attribute_id', [15, 16, 28, 29, 30])
                ->select('id', 'company_id', 'value', 'updated_at', 'job_id', 'product_id', 'attribute_id')
                ->orderBy('updated_at', 'desc')
                ->get();

            // En yeni ve en ucuz fiyatı belirle
            $latestPrice = $allPrices->sortByDesc('updated_at')->first();
            $cheapestPrice = $allPrices->sortBy('value')->first();

            // Fiyatları formatla
            $formattedPrices = $allPrices->map(function ($price) use ($latestPrice, $cheapestPrice) {
                return [
                    'id' => $price->id,
                    'attribute_id' => $price->attribute_id,
                    'value' => $price->value,
                    'updated_at' => $price->updated_at,
                    'job_id' => $price->job_id,
                    'is_latest' => $price->id === $latestPrice->id,
                    'is_cheapest' => $price->id === $cheapestPrice->id
                ];
            })->values();

            return response()->json([
                'success' => true,
                'data' => [
                    'prices' => $formattedPrices,
                    'latest_price' => $latestPrice ? [
                        'id' => $latestPrice->id,
                        'value' => $latestPrice->value,
                        'updated_at' => $latestPrice->updated_at
                    ] : null,
                    'cheapest_price' => $cheapestPrice ? [
                        'id' => $cheapestPrice->id,
                        'value' => $cheapestPrice->value,
                        'updated_at' => $cheapestPrice->updated_at
                    ] : null,
                    'total_count' => $allPrices->count()
                ]
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Fiyatlar yüklenirken bir hata oluştu',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}

