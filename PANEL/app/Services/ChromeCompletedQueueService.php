<?php

namespace App\Services;

use App\Models\ProductAttributeValue;
use App\Models\ProductAttributeValueSummary;
use App\Models\Attribute;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class ChromeCompletedQueueService
{
    private $rabbitmqHost = '10.20.50.16';
    private $rabbitmqPort = 5672;
    private $rabbitmqUser = 'admin';
    private $rabbitmqPass = 'admin123';
    private $vhost = 'chrome'; // Chrome extension için vhost
    private $queueName = 'chrome.queue.completed';
    private $errorQueueName = 'chrome.db.queue.error';
    private $successQueueName = 'chrome.db.queue.success';

    /**
     * Consume messages from chrome.queue.completed
     */
    public function consume()
    {
        $maxRetries = 5;
        $retryDelay = 5; // seconds
        
        while (true) {
            try {
                $connection = new AMQPStreamConnection(
                    $this->rabbitmqHost,
                    $this->rabbitmqPort,
                    $this->rabbitmqUser,
                    $this->rabbitmqPass,
                    $this->vhost,
                    false,
                    'AMQPLAIN',
                    null,
                    'en_US',
                    3.0, // connection_timeout
                    3.0, // read_write_timeout
                    null,
                    false,
                    60   // heartbeat
                );

                $channel = $connection->channel();
                
                // Declare queue
                $channel->queue_declare($this->queueName, false, true, false, false);

                Log::info("Chrome Completed Queue Consumer başlatıldı: {$this->queueName}");

                $callback = function ($msg) {
                    try {
                        $messageData = json_decode($msg->body, true);
                        
                        if (!$messageData) {
                            Log::error("Chrome Completed Queue: Geçersiz JSON mesajı", [
                                'body' => $msg->body
                            ]);
                            $msg->ack();
                            return;
                        }

                        Log::info("Chrome Completed Queue: Mesaj alındı", [
                            'job_id' => $messageData['job_id'] ?? null,
                            'url' => $messageData['url'] ?? null
                        ]);

                        // Mesajı işle
                        $this->processMessage($messageData);

                        // Başarılı işlem sonrası success queue'suna gönder
                        try {
                            $this->sendToSuccessQueue($messageData);
                        } catch (\Exception $successQueueException) {
                            Log::error("Success queue'ya gönderme hatası", [
                                'error' => $successQueueException->getMessage()
                            ]);
                            // Success queue hatası ana işlemi etkilemesin
                        }

                        // Mesajı acknowledge et
                        $msg->ack();
                        
                        Log::info("Chrome Completed Queue: Mesaj başarıyla işlendi", [
                            'job_id' => $messageData['job_id'] ?? null
                        ]);

                    } catch (\Exception $e) {
                        Log::error("Chrome Completed Queue: Mesaj işleme hatası", [
                            'error' => $e->getMessage(),
                            'trace' => $e->getTraceAsString(),
                            'body' => $msg->body
                        ]);
                        
                        // Hata durumunda mesajı error queue'suna gönder
                        try {
                            $messageData = json_decode($msg->body, true);
                            if ($messageData) {
                                $this->sendToErrorQueue($messageData, $e->getMessage(), $e->getTraceAsString());
                            }
                        } catch (\Exception $errorQueueException) {
                            Log::error("Error queue'ya gönderme hatası", [
                                'error' => $errorQueueException->getMessage()
                            ]);
                        }
                        
                        // Hata durumunda mesajı reject et (requeue yapma)
                        try {
                            $msg->nack(false, false);
                        } catch (\Exception $nackException) {
                            Log::error("NACK hatası", ['error' => $nackException->getMessage()]);
                        }
                    }
                };

                // Consumer'ı başlat
                $channel->basic_qos(null, 1, null); // Her seferinde 1 mesaj işle
                $channel->basic_consume($this->queueName, '', false, false, false, false, $callback);

                Log::info("Chrome Completed Queue: Mesaj dinleme başladı");

                // Mesajları dinlemeye devam et
                while ($channel->is_consuming()) {
                    try {
                        $channel->wait(null, false, 5); // 5 saniye timeout
                    } catch (\PhpAmqpLib\Exception\AMQPTimeoutException $e) {
                        // Timeout normal, devam et
                        continue;
                    } catch (\Exception $e) {
                        Log::error("Channel wait hatası", [
                            'error' => $e->getMessage()
                        ]);
                        break;
                    }
                }

                // Bağlantı kapanmışsa, temizle ve yeniden bağlan
                try {
                    if ($channel && $channel->is_open()) {
                        $channel->close();
                    }
                } catch (\Exception $e) {
                    // Ignore
                }
                
                try {
                    if ($connection && $connection->isConnected()) {
                        $connection->close();
                    }
                } catch (\Exception $e) {
                    // Ignore
                }

            } catch (\PhpAmqpLib\Exception\AMQPConnectionClosedException $e) {
                Log::warning("RabbitMQ bağlantısı kapandı, yeniden bağlanılıyor...", [
                    'error' => $e->getMessage()
                ]);
                sleep($retryDelay);
                continue;
                
            } catch (\Exception $e) {
                Log::error("Chrome Completed Queue Consumer hatası: " . $e->getMessage(), [
                    'trace' => $e->getTraceAsString()
                ]);
                
                // Kritik hatalar için kısa bir bekleme sonrası yeniden dene
                sleep($retryDelay);
                continue;
            }
        }
    }

    /**
     * Process completed message from Chrome extension
     */
    private function processMessage(array $messageData)
    {
        // Eğer zaten aktif bir transaction varsa, yeni transaction başlatma
        if (DB::transactionLevel() > 0) {
            // Nested transaction durumunda, mevcut transaction'ı kullan
            $this->processMessageWithoutTransaction($messageData);
            return;
        }

        DB::transaction(function () use ($messageData) {
            $this->processMessageWithoutTransaction($messageData);
        });
    }

    /**
     * Process message without starting a new transaction
     */
    private function processMessageWithoutTransaction(array $messageData)
    {
        try {
            $jobId = $messageData['job_id'] ?? null;
            $productId = $messageData['product_id'] ?? null;
            $companyId = $messageData['company_id'] ?? null;
            $url = $messageData['url'] ?? null;
            $mpn = $messageData['npm'] ?? $messageData['mpn'] ?? null;
            
            // Scraped data (kazınan veriler)
            $scrapedData = $messageData['scraped_data'] ?? [];
            
            // Attributes (attribute bilgileri - eğer varsa)
            $attributes = $messageData['attributes'] ?? [];

            if (!$jobId || !$productId || !$companyId) {
                throw new \Exception("Eksik bilgi: job_id, product_id veya company_id bulunamadı");
            }

            Log::info("Chrome Completed Queue: Veri kaydı başlıyor", [
                'job_id' => $jobId,
                'product_id' => $productId,
                'company_id' => $companyId,
                'url' => $url
            ]);

            // Eğer attributes array'i varsa, onu kullan
            // Yoksa scraped_data'dan attribute'ları çıkar
            if (empty($attributes) && !empty($scrapedData)) {
                // scraped_data'dan attribute'ları oluştur
                foreach ($scrapedData as $attrName => $attrValue) {
                    // Attribute'ı bul veya oluştur
                    $attribute = Attribute::firstOrCreate(
                        ['name' => $attrName],
                        ['description' => null]
                    );

                    $attributes[] = [
                        'attributes_id' => $attribute->id,
                        'attributes_name' => $attrName
                    ];
                }
            }

            // Her attribute için kayıt yap
            $insertedCount = 0;
            $updatedCount = 0;
            $skippedCount = 0;
            $errorCount = 0;
            
            foreach ($attributes as $attr) {
                $attrId = $attr['attributes_id'] ?? null;
                $attrName = $attr['attributes_name'] ?? null;
                
                if (!$attrId || !$attrName) {
                    Log::warning("Attribute bilgisi eksik", [
                        'attr' => $attr
                    ]);
                    $skippedCount++;
                    continue;
                }

                // Scraped data'dan değeri al
                $attrValue = $scrapedData[$attrName] ?? null;

                // Null, boş string veya boş array kontrolü - bunlar kaydedilmesin
                if ($attrValue === null || $attrValue === '' || (is_array($attrValue) && empty($attrValue))) {
                    Log::info("Attribute atlandı (null/boş)", [
                        'attr_name' => $attrName,
                        'attr_id' => $attrId,
                        'attr_value' => $attrValue
                    ]);
                    $skippedCount++;
                    continue;
                }

                try {
                    // ProductAttributeValue'ye INSERT (veriyi olduğu gibi kaydet)
                    $productAttrValue = ProductAttributeValue::create([
                        'job_id' => $jobId,
                        'product_id' => $productId,
                        'mpn' => $mpn,
                        'company_id' => $companyId,
                        'attribute_id' => $attrId,
                        'value' => $attrValue
                    ]);

                    if ($productAttrValue && $productAttrValue->id) {
                        $insertedCount++;
                        Log::info("ProductAttributeValue kaydedildi", [
                            'id' => $productAttrValue->id,
                            'attr_name' => $attrName,
                            'attr_id' => $attrId,
                            'value' => $attrValue,
                            'job_id' => $jobId,
                            'product_id' => $productId
                        ]);
                    } else {
                        throw new \Exception("ProductAttributeValue kaydı oluşturulamadı - ID dönmedi");
                    }

                    // ProductAttributeValueSummary'ye UPSERT
                    $summaryResult = $this->upsertToSummaryTable(
                        $jobId,
                        $productId,
                        $companyId,
                        $attrId,
                        $mpn,
                        $attrValue,
                        $attrName
                    );
                    
                    if ($summaryResult === 'updated') {
                        $updatedCount++;
                    } elseif ($summaryResult === 'inserted') {
                        $insertedCount++;
                    }

                } catch (\Exception $e) {
                    $errorCount++;
                    Log::error("Attribute kayıt hatası", [
                        'attr_name' => $attrName,
                        'attr_id' => $attrId,
                        'attr_value' => $attrValue,
                        'error' => $e->getMessage(),
                        'trace' => $e->getTraceAsString()
                    ]);
                    // Bir attribute hatası diğerlerini etkilemesin, devam et
                }
            }
            
            // Eğer hiçbir kayıt yapılamadıysa hata fırlat
            if ($insertedCount == 0 && $updatedCount == 0 && $errorCount > 0) {
                throw new \Exception("Hiçbir attribute kaydedilemedi. Toplam hata: {$errorCount}, Atlanan: {$skippedCount}");
            }
            
            Log::info("Chrome Completed Queue: Kayıt özeti", [
                'job_id' => $jobId,
                'product_id' => $productId,
                'inserted' => $insertedCount,
                'updated' => $updatedCount,
                'skipped' => $skippedCount,
                'errors' => $errorCount
            ]);

            Log::info("Chrome Completed Queue: Veri kaydı başarılı", [
                'job_id' => $jobId,
                'product_id' => $productId
            ]);

        } catch (\Exception $e) {
            $errorMessage = $e->getMessage();
            $errorTrace = $e->getTraceAsString();
            
            Log::error("Chrome Completed Queue: Veri kayıt hatası", [
                'error' => $errorMessage,
                'trace' => $errorTrace,
                'message_data' => $messageData
            ]);
            
            // Hata durumunda mesajı error queue'suna gönder
            try {
                $this->sendToErrorQueue($messageData, $errorMessage, $errorTrace);
            } catch (\Exception $errorQueueException) {
                Log::error("Error queue'ya gönderme hatası", [
                    'error' => $errorQueueException->getMessage(),
                    'original_error' => $errorMessage
                ]);
            }
            
            throw $e;
        }
    }

    /**
     * UPSERT to ProductAttributeValueSummary table
     * @return string 'inserted', 'updated', or 'skipped'
     */
    private function upsertToSummaryTable($jobId, $productId, $companyId, $attributeId, $mpn, $value, $attrName)
    {
        try {
            // Null veya boş değer kontrolü - güncelleme/insert yapma
            if ($value === null || $value === '' || (is_array($value) && empty($value))) {
                Log::info("ProductAttributeValueSummary: SKIP - value null/boş", [
                    'attr_name' => $attrName,
                    'attr_id' => $attributeId
                ]);
                return 'skipped';
            }

            // Mevcut kaydı kontrol et
            $existingRecord = ProductAttributeValueSummary::where('company_id', $companyId)
                ->where('attribute_id', $attributeId)
                ->where('product_id', $productId)
                ->where('mpn', $mpn)
                ->first();

            if ($existingRecord) {
                // Eğer job_id aynı ve mevcut value yeni value'den küçükse güncelleme yapma
                if ($existingRecord->job_id == $jobId && $existingRecord->value && $value) {
                    try {
                        $existingValueNum = (float) str_replace([',', ' '], ['.', ''], $existingRecord->value);
                        $newValueNum = (float) str_replace([',', ' '], ['.', ''], $value);
                        
                        if ($existingValueNum < $newValueNum) {
                            Log::info("ProductAttributeValueSummary: SKIP - job_id aynı ve mevcut value daha küçük", [
                                'attr_name' => $attrName,
                                'existing_value' => $existingRecord->value,
                                'new_value' => $value
                            ]);
                            return 'skipped';
                        }
                    } catch (\Exception $e) {
                        // Sayıya çevrilemezse string karşılaştırması yap
                        if (strcmp($existingRecord->value, $value) < 0) {
                            Log::info("ProductAttributeValueSummary: SKIP - job_id aynı ve mevcut value daha küçük (string)", [
                                'attr_name' => $attrName,
                                'existing_value' => $existingRecord->value,
                                'new_value' => $value
                            ]);
                            return 'skipped';
                        }
                    }
                }

                // UPDATE: value ve job_id güncelle
                $updateResult = $existingRecord->update([
                    'value' => $value,
                    'job_id' => $jobId,
                    'updated_at' => now()
                ]);

                if ($updateResult) {
                    Log::info("ProductAttributeValueSummary: UPDATE", [
                        'id' => $existingRecord->id,
                        'attr_name' => $attrName,
                        'attr_id' => $attributeId,
                        'value' => $value,
                        'job_id' => $jobId,
                        'product_id' => $productId
                    ]);
                    return 'updated';
                } else {
                    throw new \Exception("ProductAttributeValueSummary güncelleme başarısız");
                }

            } else {
                // INSERT: Yeni kayıt ekle
                $newRecord = ProductAttributeValueSummary::create([
                    'job_id' => $jobId,
                    'product_id' => $productId,
                    'company_id' => $companyId,
                    'attribute_id' => $attributeId,
                    'mpn' => $mpn,
                    'value' => $value
                ]);

                if ($newRecord && $newRecord->id) {
                    Log::info("ProductAttributeValueSummary: INSERT", [
                        'id' => $newRecord->id,
                        'attr_name' => $attrName,
                        'attr_id' => $attributeId,
                        'value' => $value,
                        'job_id' => $jobId,
                        'product_id' => $productId
                    ]);
                    return 'inserted';
                } else {
                    throw new \Exception("ProductAttributeValueSummary kaydı oluşturulamadı - ID dönmedi");
                }
            }

        } catch (\Exception $e) {
            Log::error("ProductAttributeValueSummary hatası", [
                'attr_name' => $attrName,
                'attr_id' => $attributeId,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }
    
    /**
     * Purge chrome.queue.completed queue (tüm mesajları temizle)
     */
    public function purgeQueue()
    {
        try {
            $connection = new AMQPStreamConnection(
                $this->rabbitmqHost,
                $this->rabbitmqPort,
                $this->rabbitmqUser,
                $this->rabbitmqPass,
                $this->vhost
            );

            $channel = $connection->channel();
            
            // Queue'yu declare et
            $channel->queue_declare($this->queueName, false, true, false, false);
            
            // Queue'yu purge et (tüm mesajları sil - ready ve unacked dahil)
            $purgedCount = $channel->queue_purge($this->queueName);
            
            $channel->close();
            $connection->close();
            
            Log::info("Chrome Completed Queue purged", [
                'queue' => $this->queueName,
                'purged_count' => $purgedCount
            ]);
            
            return $purgedCount;
        } catch (\Exception $e) {
            Log::error("Queue purge hatası", [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }
    
    /**
     * Send error message to chrome.db.queue.error
     */
    private function sendToErrorQueue(array $messageData, string $errorMessage, string $errorTrace = null)
    {
        try {
            $connection = new AMQPStreamConnection(
                $this->rabbitmqHost,
                $this->rabbitmqPort,
                $this->rabbitmqUser,
                $this->rabbitmqPass,
                $this->vhost
            );

            $channel = $connection->channel();
            
            // Declare error queue
            $channel->queue_declare($this->errorQueueName, false, true, false, false);
            
            // Scraped data'yı null olmayan değerlerle filtrele
            $scrapedData = $this->filterNonNullData($messageData['scraped_data'] ?? []);
            
            // Error mesajını hazırla - tüm önemli verileri ekle
            $errorData = [
                'original_message' => $messageData,
                'scraped_data' => $scrapedData,
                'job_id' => $messageData['job_id'] ?? null,
                'product_id' => $messageData['product_id'] ?? null,
                'company_id' => $messageData['company_id'] ?? null,
                'url' => $messageData['url'] ?? null,
                'mpn' => $messageData['npm'] ?? $messageData['mpn'] ?? null,
                'attributes' => $messageData['attributes'] ?? [],
                'error_message' => $errorMessage,
                'error_trace' => $errorTrace,
                'error_timestamp' => now()->toISOString(),
                'queue_name' => $this->queueName
            ];
            
            // Create message
            $msg = new AMQPMessage(
                json_encode($errorData),
                ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
            );
            
            // Publish message
            $channel->basic_publish($msg, '', $this->errorQueueName);
            
            $channel->close();
            $connection->close();
            
            Log::info("Hata mesajı error queue'suna gönderildi", [
                'queue' => $this->errorQueueName,
                'job_id' => $messageData['job_id'] ?? null,
                'error' => $errorMessage
            ]);
            
            return true;
        } catch (\Exception $e) {
            Log::error("Error queue'ya gönderme hatası", [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            return false;
        }
    }
    
    /**
     * Send success message to chrome.db.queue.success
     */
    private function sendToSuccessQueue(array $messageData)
    {
        try {
            $connection = new AMQPStreamConnection(
                $this->rabbitmqHost,
                $this->rabbitmqPort,
                $this->rabbitmqUser,
                $this->rabbitmqPass,
                $this->vhost
            );

            $channel = $connection->channel();
            
            // Declare success queue
            $channel->queue_declare($this->successQueueName, false, true, false, false);
            
            // Scraped data'yı null olmayan değerlerle filtrele
            $scrapedData = $this->filterNonNullData($messageData['scraped_data'] ?? []);
            
            // Success mesajını hazırla - tüm önemli verileri ekle
            $successData = [
                'original_message' => $messageData,
                'scraped_data' => $scrapedData,
                'job_id' => $messageData['job_id'] ?? null,
                'product_id' => $messageData['product_id'] ?? null,
                'company_id' => $messageData['company_id'] ?? null,
                'url' => $messageData['url'] ?? null,
                'mpn' => $messageData['npm'] ?? $messageData['mpn'] ?? null,
                'attributes' => $messageData['attributes'] ?? [],
                'success_timestamp' => now()->toISOString(),
                'queue_name' => $this->queueName
            ];
            
            // Create message
            $msg = new AMQPMessage(
                json_encode($successData),
                ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
            );
            
            // Publish message
            $channel->basic_publish($msg, '', $this->successQueueName);
            
            $channel->close();
            $connection->close();
            
            Log::info("Başarılı mesaj success queue'suna gönderildi", [
                'queue' => $this->successQueueName,
                'job_id' => $messageData['job_id'] ?? null
            ]);
            
            return true;
        } catch (\Exception $e) {
            Log::error("Success queue'ya gönderme hatası", [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            return false;
        }
    }
    
    /**
     * Filter null values from data array (recursive)
     * Null, empty string, and empty array values are removed
     */
    private function filterNonNullData(array $data): array
    {
        $filtered = [];
        
        foreach ($data as $key => $value) {
            // Null kontrolü
            if ($value === null) {
                continue;
            }
            
            // Boş string kontrolü
            if ($value === '') {
                continue;
            }
            
            // Boş array kontrolü
            if (is_array($value) && empty($value)) {
                continue;
            }
            
            // Eğer nested array ise, recursive olarak filtrele
            if (is_array($value) && !empty($value)) {
                $filteredValue = $this->filterNonNullData($value);
                // Eğer filtreleme sonrası boş kaldıysa ekleme
                if (!empty($filteredValue)) {
                    $filtered[$key] = $filteredValue;
                }
            } else {
                // Normal değer, ekle
                $filtered[$key] = $value;
            }
        }
        
        return $filtered;
    }
}

