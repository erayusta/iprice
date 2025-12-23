<?php

namespace App\Services;

use App\Models\UserProduct;
use App\Models\Brand;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;

class XmlParserService
{
    /**
     * Parse XML from URL and import products to database.
     */
    public function parseAndImportFromUrl(string $xmlUrl): array
    {
        try {
            // Execution time limit kaldır (büyük XML dosyaları için)
            set_time_limit(0);
            ini_set('memory_limit', '2048M');
            
            // Fetch XML content (timeout artırıldı)
            $response = Http::timeout(120)->get($xmlUrl);
            
            if (!$response->successful()) {
                throw new \Exception('XML URL\'ye erişilemedi: ' . $response->status());
            }
            
            $xmlContent = $response->body();
            
            Log::info('XML içeriği indirildi', [
                'size_mb' => round(strlen($xmlContent) / 1024 / 1024, 2),
                'url' => $xmlUrl
            ]);
            
            return $this->parseAndImport($xmlContent);
            
        } catch (\Exception $e) {
            Log::error('XML parse error: ' . $e->getMessage());
            throw $e;
        }
    }

    /**
     * Parse XML content and import products to database.
     */
    public function parseAndImport(string $xmlContent): array
    {
        try {
            // Memory limit artır ve execution time'ı kaldır
            ini_set('memory_limit', '2048M');
            set_time_limit(0); // Unlimited execution time
            
            // Parse XML with namespace support
            Log::info('XML parsing başlıyor...');
            $xml = simplexml_load_string($xmlContent);
            
            if ($xml === false) {
                throw new \Exception('XML parse edilemedi');
            }
            
            // Register namespaces
            $xml->registerXPathNamespace('g', 'http://base.google.com/ns/1.0');
            
            $totalItems = count($xml->channel->item ?? []);
            Log::info('XML parse edildi', [
                'total_items' => $totalItems,
                'memory_usage_mb' => round(memory_get_usage(true) / 1024 / 1024, 2)
            ]);
            
            // Sonuç dizilerini limitlendir (performans için)
            $resultLimit = 100; // Her kategori için max 100 kayıt
            $results = [
                'success' => [],
                'failed' => [],
                'updated' => [],
                'skipped' => []
            ];
            
            $importedCount = 0;
            $failedCount = 0;
            $updatedCount = 0;
            $skippedCount = 0;
            
            // 1. Önce tüm brand isimlerini topla (DB query'lerini azaltmak için)
            Log::info('Brand isimleri toplanıyor...');
            $brandNames = [];
            foreach ($xml->channel->item as $item) {
                $item->registerXPathNamespace('g', 'http://base.google.com/ns/1.0');
                $brandNodes = $item->xpath('g:brand');
                if (!empty($brandNodes)) {
                    $brandName = trim((string) $brandNodes[0]);
                    if (!empty($brandName)) {
                        $brandNames[$brandName] = true;
                    }
                }
            }
            
            // Tüm brand'ları tek seferde yükle ve cache'le
            $brandNamesList = array_keys($brandNames);
            $existingBrands = Brand::whereIn('name', $brandNamesList)->get()->keyBy('name');
            $brandCache = [];
            
            // Yeni brand'ları bulk insert ile ekle
            $newBrandsToInsert = [];
            foreach ($brandNamesList as $brandName) {
                if (!isset($existingBrands[$brandName])) {
                    $newBrandsToInsert[] = [
                        'name' => $brandName,
                        'slug' => \Illuminate\Support\Str::slug($brandName),
                        'is_active' => true,
                        'created_at' => now(),
                        'updated_at' => now()
                    ];
                } else {
                    $brandCache[$brandName] = $existingBrands[$brandName]->id;
                }
            }
            
            // Yeni brand'ları ekle
            if (!empty($newBrandsToInsert)) {
                Brand::insert($newBrandsToInsert);
                // Yeni eklenen brand'ları çek
                $insertedBrands = Brand::whereIn('name', array_column($newBrandsToInsert, 'name'))
                    ->get()
                    ->keyBy('name');
                foreach ($insertedBrands as $brandName => $brand) {
                    $brandCache[$brandName] = $brand->id;
                }
            }
            
            Log::info('Brand cache oluşturuldu', [
                'total_brands' => count($brandNamesList),
                'new_brands' => count($newBrandsToInsert),
                'cached_brands' => count($brandCache)
            ]);
            
            // 2. XML'den tüm verileri çıkar (brand lookup olmadan, çok daha hızlı)
            $xmlProducts = [];
            $itemCount = 0;
            $maxItems = 5000000; // Maksimum ürün limiti
            $logInterval = 1000; // Her 1000 üründe bir log
            
            Log::info('XML ürünleri işleniyor...', ['max_items' => $maxItems]);
            
            foreach ($xml->channel->item as $item) {
                if ($itemCount >= $maxItems) {
                    break;
                }
                
                try {
                    $productData = $this->extractProductData($item, $brandCache);
                    if (!empty($productData['mpn'])) {
                        $xmlProducts[$productData['mpn']] = $productData;
                        $itemCount++;
                        
                        // Progress log (her 1000 üründe bir)
                        if ($itemCount % $logInterval === 0) {
                            Log::info('XML işleme devam ediyor...', [
                                'processed' => $itemCount,
                                'memory_mb' => round(memory_get_usage(true) / 1024 / 1024, 2)
                            ]);
                        }
                    }
                } catch (\Exception $e) {
                    if (count($results['failed']) < $resultLimit) {
                        $results['failed'][] = [
                            'title' => $item->title ?? 'Bilinmeyen',
                            'reason' => 'XML Parse Hatası: ' . $e->getMessage()
                        ];
                    }
                    $failedCount++;
                }
            }
            
            Log::info('XML ürünleri işlendi', [
                'total_processed' => $itemCount,
                'unique_mpn_count' => count($xmlProducts),
                'memory_mb' => round(memory_get_usage(true) / 1024 / 1024, 2)
            ]);
            
            // 2. Veritabanından sadece MPN ve gerekli alanları çek (performans için)
            Log::info('Veritabanından mevcut ürünler çekiliyor...');
            $dbProducts = UserProduct::select('id', 'mpn', 'name', 'title', 'link', 'product_url', 'image', 
                'price', 'sale_price', 'web_price', 'web_stock', 'gtin', 'availability', 'brand_id', 'product_type')
                ->get()
                ->keyBy('mpn');
            
            Log::info('Mevcut ürünler yüklendi', [
                'db_product_count' => count($dbProducts),
                'memory_mb' => round(memory_get_usage(true) / 1024 / 1024, 2)
            ]);
            
            // 3. Array karşılaştırması yap
            Log::info('Ürün karşılaştırması başlıyor...');
            $newProducts = [];
            $updateProducts = [];
            $comparisonLogCount = 0; // İlk 3 ürün için detaylı log
            
            foreach ($xmlProducts as $mpn => $xmlProduct) {
                if (isset($dbProducts[$mpn])) {
                    // Mevcut ürün - değişiklik kontrolü
                    $dbProduct = $dbProducts[$mpn];
                    $hasChanges = false;
                    $changes = [];
                    
                    // Sadece güncellenebilir alanları kontrol et
                    $updatableFields = [
                        'name', 'title', 'link', 'product_url', 'image', 
                        'price', 'sale_price', 'web_price', 'web_stock',
                        'gtin', 'availability', 'brand_id', 'product_type'
                    ];
                    
                    foreach ($xmlProduct as $key => $value) {
                        // Sadece güncellenebilir alanları kontrol et
                        if (!in_array($key, $updatableFields)) {
                            continue;
                        }
                        
                        // Veritabanındaki değeri al
                        $oldValue = $dbProduct->$key;
                        
                        // Tip uyumlu karşılaştırma yap
                        $isDifferent = false;
                        
                        // Float/decimal değerler için özel karşılaştırma
                        if (in_array($key, ['price', 'sale_price', 'web_price'])) {
                            $oldValueFloat = $oldValue !== null ? (float) $oldValue : null;
                            $newValueFloat = $value !== null ? (float) $value : null;
                            
                            // Null kontrolü
                            if ($oldValueFloat === null && $newValueFloat === null) {
                                $isDifferent = false;
                            } elseif ($oldValueFloat === null || $newValueFloat === null) {
                                $isDifferent = true;
                            } else {
                                // Float karşılaştırması - 0.01 hassasiyet
                                $isDifferent = abs($oldValueFloat - $newValueFloat) > 0.01;
                            }
                        } 
                        // String değerler için
                        else if (is_string($value)) {
                            $isDifferent = (string) $oldValue !== (string) $value;
                        }
                        // Integer değerler için
                        else if (is_int($value)) {
                            $isDifferent = (int) $oldValue !== (int) $value;
                        }
                        // Diğer durumlar
                        else {
                            $isDifferent = $oldValue != $value;
                        }
                        
                        if ($isDifferent) {
                            $hasChanges = true;
                            $changes[$key] = [
                                'old' => $oldValue,
                                'new' => $value
                            ];
                        }
                    }
                    
                    // İlk 3 ürün için detaylı log
                    if ($comparisonLogCount < 3) {
                        Log::info('Ürün Karşılaştırma Detayı', [
                            'mpn' => $mpn,
                            'title' => $xmlProduct['title'],
                            'has_changes' => $hasChanges,
                            'changes' => $changes,
                            'xml_price' => $xmlProduct['price'] ?? null,
                            'db_price' => $dbProduct->price,
                            'xml_stock' => $xmlProduct['web_stock'] ?? null,
                            'db_stock' => $dbProduct->web_stock,
                            'xml_availability' => $xmlProduct['availability'] ?? null,
                            'db_availability' => $dbProduct->availability
                        ]);
                        $comparisonLogCount++;
                    }
                    
                    if ($hasChanges) {
                        $updateProducts[] = [
                            'id' => $dbProduct->id,
                            'data' => $xmlProduct
                        ];
                        
                        // Sonuç dizisine ekle (limit varsa)
                        if (count($results['updated']) < $resultLimit) {
                            $results['updated'][] = [
                                'title' => $xmlProduct['title'],
                                'id' => $dbProduct->id,
                                'price' => $xmlProduct['price'],
                                'mpn' => $mpn,
                                'changes' => $changes
                            ];
                        }
                        $updatedCount++;
                    } else {
                        // Sonuç dizisine ekle (limit varsa)
                        if (count($results['skipped']) < $resultLimit) {
                            $results['skipped'][] = [
                                'title' => $xmlProduct['title'],
                                'id' => $dbProduct->id,
                                'reason' => 'Veri değişikliği yok'
                            ];
                        }
                        $skippedCount++;
                    }
                } else {
                    // Yeni ürün
                    $newProducts[] = $xmlProduct;
                }
            }
            
            // 4. Bulk operations
            $now = now();
            
            // Bulk insert yeni ürünler (batch'ler halinde)
            if (!empty($newProducts)) {
                try {
                    foreach ($newProducts as &$product) {
                        $product['created_at'] = $now;
                        $product['updated_at'] = $now;
                        // Yeni eklenen ürünler aktif olmalı
                        $product['is_active'] = 1;
                    }
                    
                    Log::info('Bulk insert başlıyor', [
                        'product_count' => count($newProducts),
                        'sample_product' => $newProducts[0] ?? null
                    ]);
                    
                    // Batch'ler halinde insert et (500'er 500'er)
                    $batchSize = 500;
                    $batches = array_chunk($newProducts, $batchSize);
                    $importedCount = 0;
                    
                    foreach ($batches as $batchIndex => $batch) {
                        Log::info('Batch insert', [
                            'batch_index' => $batchIndex + 1,
                            'batch_size' => count($batch)
                        ]);
                        
                        UserProduct::insert($batch);
                        $importedCount += count($batch);
                    }
                    
                    Log::info('Bulk insert başarılı', ['imported_count' => $importedCount]);
                    
                    // Yeni eklenen ürünleri al (sadece örnek için, limit ile)
                    $sampleProducts = UserProduct::whereIn('mpn', array_column($newProducts, 'mpn'))
                        ->select('id', 'title', 'price', 'mpn')
                        ->orderBy('id', 'desc')
                        ->limit(min($resultLimit, count($newProducts)))
                        ->get();
                    
                    foreach ($sampleProducts as $product) {
                        $results['success'][] = [
                            'title' => $product->title,
                            'id' => $product->id,
                            'price' => $product->price,
                            'mpn' => $product->mpn
                        ];
                    }
                    
                } catch (\Illuminate\Database\QueryException $e) {
                    Log::error('SQL Insert Hatası', [
                        'error_code' => $e->getCode(),
                        'error_message' => $e->getMessage(),
                        'sql_state' => $e->errorInfo[0] ?? null,
                        'driver_code' => $e->errorInfo[1] ?? null,
                        'driver_message' => $e->errorInfo[2] ?? null,
                        'sql_query' => $e->getSql() ?? null,
                        'bindings' => $e->getBindings() ?? null,
                        'product_count' => count($newProducts)
                    ]);
                    
                    // Başarısız olan ürünleri failed listesine ekle (limit ile)
                    foreach ($newProducts as $product) {
                        if (count($results['failed']) >= $resultLimit) {
                            break;
                        }
                        $results['failed'][] = [
                            'title' => $product['title'] ?? 'Bilinmeyen',
                            'reason' => 'SQL Insert Hatası: ' . $e->getMessage(),
                            'mpn' => $product['mpn'] ?? null
                        ];
                        $failedCount++;
                    }
                    $importedCount = 0;
                    
                } catch (\Exception $e) {
                    Log::error('Genel Insert Hatası', [
                        'error_message' => $e->getMessage(),
                        'error_trace' => $e->getTraceAsString(),
                        'product_count' => count($newProducts)
                    ]);
                    
                    foreach ($newProducts as $product) {
                        if (count($results['failed']) >= $resultLimit) {
                            break;
                        }
                        $results['failed'][] = [
                            'title' => $product['title'] ?? 'Bilinmeyen',
                            'reason' => 'Insert Hatası: ' . $e->getMessage(),
                            'mpn' => $product['mpn'] ?? null
                        ];
                        $failedCount++;
                    }
                    $importedCount = 0;
                }
            }
            
            // Bulk update mevcut ürünler (batch'ler halinde)
            if (!empty($updateProducts)) {
                try {
                    Log::info('Bulk update başlıyor', [
                        'update_count' => count($updateProducts)
                    ]);
                    
                    // Batch'ler halinde güncelle (500'er 500'er)
                    $updateBatchSize = 500;
                    $updateBatches = array_chunk($updateProducts, $updateBatchSize);
                    
                    foreach ($updateBatches as $batchIndex => $updateBatch) {
                        foreach ($updateBatch as $item) {
                            $productId = $item['id'];
                            $productData = $item['data'];
                            
                            // Sadece güncellenebilir alanları ayıkla
                            $updateData = array_filter($productData, function($key) {
                                return in_array($key, [
                                    'name', 'title', 'link', 'product_url', 'image', 
                                    'price', 'sale_price', 'web_price', 'web_stock',
                                    'gtin', 'availability', 'brand_id', 'product_type'
                                ]);
                            }, ARRAY_FILTER_USE_KEY);
                            
                            $updateData['updated_at'] = $now;
                            // XML'den gelen ürünler aktif olmalı
                            $updateData['is_active'] = 1;
                            
                            try {
                                UserProduct::where('id', $productId)->update($updateData);
                            } catch (\Exception $e) {
                                // Hata durumunda logla ama devam et
                                if (count($results['failed']) < $resultLimit) {
                                    $results['failed'][] = [
                                        'title' => $productData['title'] ?? 'Bilinmeyen',
                                        'reason' => 'Update Hatası: ' . $e->getMessage(),
                                        'mpn' => $productData['mpn'] ?? null,
                                        'id' => $productId
                                    ];
                                }
                                $failedCount++;
                                $updatedCount--;
                            }
                        }
                        
                        Log::info('Update batch tamamlandı', [
                            'batch_index' => $batchIndex + 1,
                            'batch_size' => count($updateBatch)
                        ]);
                    }
                    
                    Log::info('Bulk update tamamlandı', ['updated_count' => $updatedCount]);
                    
                } catch (\Exception $e) {
                    Log::error('Bulk Update Genel Hatası', [
                        'error_message' => $e->getMessage(),
                        'error_trace' => $e->getTraceAsString(),
                        'update_count' => count($updateProducts)
                    ]);
                    
                    // Tüm update işlemlerini failed olarak işaretle (limit ile)
                    foreach ($updateProducts as $item) {
                        if (count($results['failed']) >= $resultLimit) {
                            break;
                        }
                        $productData = $item['data'];
                        $results['failed'][] = [
                            'title' => $productData['title'] ?? 'Bilinmeyen',
                            'reason' => 'Bulk Update Hatası: ' . $e->getMessage(),
                            'mpn' => $productData['mpn'] ?? null,
                            'id' => $item['id'] ?? null
                        ];
                        $failedCount++;
                    }
                    $updatedCount = 0;
                }
            }
            
            // 5. XML'de olmayan ürünleri is_active = 0 yap
            $xmlMpns = array_keys($xmlProducts);
            $deactivatedCount = 0;
            
            if (!empty($dbProducts) && !empty($xmlMpns)) {
                try {
                    Log::info('XML\'de olmayan ürünler deaktif ediliyor...');
                    
                    // XML'de olmayan MPN'leri bul (MPN null olanlar da dahil)
                    $mpnsToDeactivate = [];
                    foreach ($dbProducts as $mpn => $dbProduct) {
                        // MPN null ise veya XML'de yoksa deaktif et
                        if (empty($mpn) || !in_array($mpn, $xmlMpns)) {
                            $mpnsToDeactivate[] = $dbProduct->id;
                        }
                    }
                    
                    if (!empty($mpnsToDeactivate)) {
                        // Bulk update ile is_active = 0 yap
                        $deactivateBatchSize = 500;
                        $deactivateBatches = array_chunk($mpnsToDeactivate, $deactivateBatchSize);
                        
                        foreach ($deactivateBatches as $batchIndex => $batchIds) {
                            $batchDeactivated = UserProduct::whereIn('id', $batchIds)
                                ->where('is_active', 1) // Sadece aktif olanları güncelle
                                ->update([
                                    'is_active' => 0,
                                    'updated_at' => $now
                                ]);
                            $deactivatedCount += $batchDeactivated;
                            
                            Log::info('Deaktif edilen ürün batch', [
                                'batch_index' => $batchIndex + 1,
                                'batch_size' => count($batchIds),
                                'deactivated' => $deactivatedCount
                            ]);
                        }
                        
                        Log::info('XML\'de olmayan ürünler deaktif edildi', [
                            'total_deactivated' => $deactivatedCount,
                            'total_found' => count($mpnsToDeactivate)
                        ]);
                    } else {
                        Log::info('Deaktif edilecek ürün bulunamadı');
                    }
                    
                } catch (\Exception $e) {
                    Log::error('Ürün deaktif etme hatası', [
                        'error_message' => $e->getMessage(),
                        'error_trace' => $e->getTraceAsString()
                    ]);
                }
            }
            
            return [
                'success' => true,
                'message' => "İşlem tamamlandı. Yeni: {$importedCount}, Güncellenen: {$updatedCount}, Atlanan: {$skippedCount}, Başarısız: {$failedCount}, Deaktif Edilen: {$deactivatedCount}",
                'data' => $results,
                'summary' => [
                    'total' => $importedCount + $failedCount + $updatedCount + $skippedCount,
                    'success' => $importedCount,
                    'updated' => $updatedCount,
                    'skipped' => $skippedCount,
                    'failed' => $failedCount,
                    'deactivated' => $deactivatedCount
                ],
                'note' => 'Sonuç dizilerinde her kategori için maksimum ' . $resultLimit . ' örnek gösterilmektedir.'
            ];
            
        } catch (\Illuminate\Database\QueryException $e) {
            Log::error('SQL Hatası - XML Import', [
                'error_code' => $e->getCode(),
                'error_message' => $e->getMessage(),
                'sql_state' => $e->errorInfo[0] ?? null,
                'driver_code' => $e->errorInfo[1] ?? null,
                'driver_message' => $e->errorInfo[2] ?? null,
                'sql_query' => $e->getSql() ?? null,
                'bindings' => $e->getBindings() ?? null,
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'trace' => $e->getTraceAsString()
            ]);
            
            return [
                'success' => false,
                'message' => 'SQL Hatası: ' . $e->getMessage(),
                'error_type' => 'SQL_ERROR',
                'error_details' => [
                    'code' => $e->getCode(),
                    'sql_state' => $e->errorInfo[0] ?? null,
                    'driver_code' => $e->errorInfo[1] ?? null,
                    'driver_message' => $e->errorInfo[2] ?? null
                ],
                'data' => [
                    'success' => [],
                    'failed' => [],
                    'updated' => [],
                    'skipped' => []
                ],
                'summary' => [
                    'total' => 0,
                    'success' => 0,
                    'updated' => 0,
                    'skipped' => 0,
                    'failed' => 0
                ]
            ];
            
        } catch (\Exception $e) {
            Log::error('Genel Hata - XML Import', [
                'error_message' => $e->getMessage(),
                'error_code' => $e->getCode(),
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'trace' => $e->getTraceAsString(),
                'xml_content_length' => strlen($xmlContent ?? ''),
                'xml_content_preview' => substr($xmlContent ?? '', 0, 500)
            ]);
            
            return [
                'success' => false,
                'message' => 'Genel Hata: ' . $e->getMessage(),
                'error_type' => 'GENERAL_ERROR',
                'error_details' => [
                    'code' => $e->getCode(),
                    'file' => $e->getFile(),
                    'line' => $e->getLine()
                ],
                'data' => [
                    'success' => [],
                    'failed' => [],
                    'updated' => [],
                    'skipped' => []
                ],
                'summary' => [
                    'total' => 0,
                    'success' => 0,
                    'updated' => 0,
                    'skipped' => 0,
                    'failed' => 0
                ]
            ];
        }
    }

    /**
     * Extract product data from XML item.
     */
    private function extractProductData($item, array $brandCache = []): array
    {
        try {
            // Register namespace for this item
            $item->registerXPathNamespace('g', 'http://base.google.com/ns/1.0');
            
            // Safe brand extraction (cache'den al)
            $brandNodes = $item->xpath('g:brand');
            $brandName = !empty($brandNodes) ? trim((string) $brandNodes[0]) : null;
            $brandId = null;
            
            // Brand ID'yi cache'den al (çok daha hızlı!)
            if (!empty($brandName) && isset($brandCache[$brandName])) {
                $brandId = $brandCache[$brandName];
            }
            
            // Safe xpath extraction
            $titleNodes = $item->xpath('g:title');
            $linkNodes = $item->xpath('g:link');
            $imageNodes = $item->xpath('g:image_link');
            $mpnNodes = $item->xpath('g:mpn');
            $gtinNodes = $item->xpath('g:gtin');
            $availabilityNodes = $item->xpath('g:availability');
            $productTypeNodes = $item->xpath('g:product_type');
            
            $data = [
                'user_id' => 1, // Test için ilk user'ı kullan
                'name' => !empty($titleNodes) ? (string) $titleNodes[0] : '', // name kolonu için title kullan
                'title' => !empty($titleNodes) ? (string) $titleNodes[0] : '',
                'link' => !empty($linkNodes) ? (string) $linkNodes[0] : '',
                'product_url' => !empty($linkNodes) ? (string) $linkNodes[0] : '', // product_url için link kullan
                'image' => !empty($imageNodes) ? (string) $imageNodes[0] : null,
                'mpn' => !empty($mpnNodes) ? (string) $mpnNodes[0] : null,
                'gtin' => !empty($gtinNodes) ? (string) $gtinNodes[0] : null,
                'availability' => !empty($availabilityNodes) ? (string) $availabilityNodes[0] : null,
                'brand_id' => $brandId,
                'product_type' => !empty($productTypeNodes) ? (string) $productTypeNodes[0] : null,
                'web_price' => null, // XML'de yok, null olarak bırak
                'price' => null, // Varsayılan değer
                'sale_price' => null, // Varsayılan değer
                'web_stock' => 0, // Varsayılan değer
            ];

            // Price parsing
            $priceNodes = $item->xpath('g:price');
            if (!empty($priceNodes)) {
                $data['price'] = $this->parsePrice((string) $priceNodes[0]);
            }

            // Sale price parsing
            $salePriceNodes = $item->xpath('g:sale_price');
            if (!empty($salePriceNodes)) {
                $data['sale_price'] = $this->parsePrice((string) $salePriceNodes[0]);
            }

            return $data;
            
        } catch (\Exception $e) {
            Log::error('XML Product Data Extract Hatası', [
                'error_message' => $e->getMessage(),
                'error_trace' => $e->getTraceAsString(),
                'item_title' => (string) ($item->title ?? 'Bilinmeyen'),
                'item_content' => $item->asXML() ?? 'XML parse edilemedi'
            ]);
            
            // Hata durumunda minimum veri döndür
            return [
                'title' => (string) ($item->title ?? 'Bilinmeyen Ürün'),
                'link' => '',
                'image' => null,
                'mpn' => null,
                'gtin' => null,
                'availability' => null,
                'brand_id' => null,
                'product_type' => null,
                'web_price' => null,
                'price' => null,
                'sale_price' => null,
                'extract_error' => $e->getMessage()
            ];
        }
    }

    /**
     * Parse price string to decimal.
     */
    private function parsePrice(string $priceString): ?float
    {
        try {
            if (empty($priceString)) {
                return null;
            }

            // Remove currency symbols and spaces
            $price = preg_replace('/[^\d.,]/', '', $priceString);
            
            if (empty($price)) {
                Log::warning('Price string boş kaldı', ['original_price' => $priceString]);
                return null;
            }
            
            // Handle Turkish decimal format (comma as decimal separator)
            if (strpos($price, ',') !== false && strpos($price, '.') !== false) {
                // Both comma and dot present - assume comma is decimal separator
                $price = str_replace('.', '', $price);
                $price = str_replace(',', '.', $price);
            } elseif (strpos($price, ',') !== false) {
                // Only comma - could be decimal separator
                $price = str_replace(',', '.', $price);
            }

            $parsedPrice = (float) $price;
            
            if ($parsedPrice <= 0) {
                Log::warning('Geçersiz fiyat değeri', [
                    'original_price' => $priceString,
                    'parsed_price' => $parsedPrice
                ]);
                return null;
            }
            
            return $parsedPrice;
            
        } catch (\Exception $e) {
            Log::error('Price Parse Hatası', [
                'error_message' => $e->getMessage(),
                'price_string' => $priceString,
                'error_trace' => $e->getTraceAsString()
            ]);
            return null;
        }
    }

    /**
     * Get XML structure info for debugging.
     */
    public function getXmlStructure(string $xmlUrl): array
    {
        try {
            $response = Http::timeout(30)->get($xmlUrl);
            $xmlContent = $response->body();
            $xml = simplexml_load_string($xmlContent);
            
            if ($xml === false) {
                return ['error' => 'XML parse edilemedi'];
            }
            
            $structure = [
                'channel_title' => (string) $xml->channel->title,
                'total_items' => count($xml->channel->item),
                'sample_item' => []
            ];
            
            // Get first item as sample
            if (isset($xml->channel->item[0])) {
                $firstItem = $xml->channel->item[0];
                $firstItem->registerXPathNamespace('g', 'http://base.google.com/ns/1.0');
                
                $structure['sample_item'] = [
                    'title' => (string) ($firstItem->xpath('g:title')[0] ?? 'N/A'),
                    'link' => (string) ($firstItem->xpath('g:link')[0] ?? 'N/A'),
                    'price' => (string) ($firstItem->xpath('g:price')[0] ?? 'N/A'),
                    'sale_price' => (string) ($firstItem->xpath('g:sale_price')[0] ?? 'N/A'),
                    'availability' => (string) ($firstItem->xpath('g:availability')[0] ?? 'N/A'),
                    'brand' => (string) ($firstItem->xpath('g:brand')[0] ?? 'N/A'),
                ];
            }
            
            return $structure;
            
        } catch (\Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }
}