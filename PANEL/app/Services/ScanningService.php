<?php

namespace App\Services;

use App\Models\JobPlan;
use App\Models\Company;
use App\Models\CompanyProductsUrl;
use App\Models\CrawlerList;
use App\Models\CompanyAttribute;
use App\Models\Attribute;
use App\Models\Server;
use App\Models\UserProduct;
use App\Models\CustomProfile;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class ScanningService
{
    private $rabbitmqHost = '10.20.50.16';
    private $rabbitmqPort = 5672;
    private $rabbitmqUser = 'admin';
    private $rabbitmqPass = 'admin123';

    /**
     * Get queue name based on application_id (crawler_id)
     */
    private function getQueueName($applicationId)
    {
        $queueMap = [

            1 => 'scrapy.queue',
            2 => 'selenium.queue',
            3 => 'playwright.queue',
            4 => 'chrome.queue',
        ];
        
        return $queueMap[$applicationId] ?? 'default.queue';
    }

    /**
     * Get server name based on server_id
     */
    private function getServerName($serverId)
    {
        $serverMap = [
            1 => 'local',
            2 => 'azure',
            3 => 'chrome',
        ];
        
        return $serverMap[$serverId] ?? 'unknown';
    }

    /**
     * Get proxy name based on proxy_id
     */
    private function getProxyName($proxyId)
    {
        static $proxyMap = null;
        
        if ($proxyMap === null) {
            $proxyMap = DB::table('proxy_settings')
                ->where('is_active', true)
                ->pluck('name', 'id')
                ->toArray();
        }
        
        return $proxyMap[$proxyId] ?? null;
    }

    /**
     * Send message to RabbitMQ queue
     */
    private function sendToQueue($queueName, $message, $serverId = 1)
    {
        try {
            $vhost = $this->getServerName($serverId);
            
            $connection = new AMQPStreamConnection(
                $this->rabbitmqHost,
                $this->rabbitmqPort,
                $this->rabbitmqUser,
                $this->rabbitmqPass,
                $vhost
            );

            $channel = $connection->channel();
            
            // Declare queue
            $channel->queue_declare($queueName, false, true, false, false);
            
            // Create message
            $msg = new AMQPMessage(
                json_encode($message),
                ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
            );
            
            // Publish message
            $channel->basic_publish($msg, '', $queueName);
            
            $channel->close();
            $connection->close();
            
            return true;
        } catch (\Exception $e) {
            \Log::error('RabbitMQ Error: ' . $e->getMessage());
            return false;
        }
    }
    /**
     * Create job data for companies (Optimized version)
     *
     * @param string|int $company_id Company ID or 'all' for all companies
     * @return array
     */
    public function create_job($company_id)
    {
        try {
            // Use raw query for better performance with large datasets
            $query = "
                SELECT 
                    c.id as company_id,
                    c.crawler_id,
                    c.server_id,
                    c.screenshot,
                    c.marketplace,
                    c.use_proxy,
                    c.proxy_id,
                    cpu.product_id,
                    cpu.url,
                    up.mpn,
                    cl.name as crawler_name,
                    sl.name as server_name
                FROM companies c
                LEFT JOIN crawler_list cl ON c.crawler_id = cl.id
                LEFT JOIN server_list sl ON c.server_id = sl.id
                INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
                INNER JOIN user_products up ON cpu.product_id::bigint = up.id
                WHERE c.deleted = false
                AND up.is_active = 1
            ";

            if ($company_id !== 'all') {
                $query .= " AND c.id = " . (int)$company_id;
            }

            $urls = DB::select($query);

            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'No companies found for the given criteria'
                ];
            }

            // Get attributes in a single query
            $companyIds = array_unique(array_column($urls, 'company_id'));
            $attributes = DB::table('company_attributes as ca')
                ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                ->whereIn('ca.company_id', $companyIds)
                ->where('ca.value', '!=', '-1') // value "-1" olan verileri alma
                ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                ->get()
                ->groupBy('company_id');

            // Prepare job data
            $jobData = [];
            $totalUrlCount = count($urls);
            $companiesCount = count($companyIds);

            // Generate unique job_id first
            $jobRecord = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Quick Scan - ' . date('Y-m-d H:i:s'),
                'data' => '{}', // Will be updated after file creation
                'status' => 'pending',
                'created_at' => now(),
                'count' => $totalUrlCount,
                'json_path' => '', // Will be updated after file creation
                'updated_at' => now()
            ]);

            // Process URLs efficiently - no need for chunks for 2k data
            $serverNames = []; // Cache server names
            $proxyNames = []; // Cache proxy names
            foreach ($urls as $url) {
                $companyAttributes = $attributes->get($url->company_id, collect())->toArray();
                
                // Cache server name to avoid repeated DB calls
                if (!isset($serverNames[$url->server_id])) {
                    $serverNames[$url->server_id] = $this->getServerName($url->server_id);
                }
                
                // Cache proxy name to avoid repeated DB calls
                $proxyType = null;
                if ($url->use_proxy && $url->proxy_id) {
                    if (!isset($proxyNames[$url->proxy_id])) {
                        $proxyNames[$url->proxy_id] = $this->getProxyName($url->proxy_id);
                    }
                    $proxyType = $proxyNames[$url->proxy_id];
                }
                
                $jobItem = [
                    'job_id' => $jobRecord,
                    'company_id' => $url->company_id,
                    'product_id' => (int)$url->product_id, // Convert to integer like old format
                    'application_id' => $url->crawler_id,
                    'server_id' => $url->server_id,
                    'server_name' => $serverNames[$url->server_id],
                    'screenshot' => (bool)($url->screenshot && $url->screenshot !== '0' && $url->screenshot !== 'false'),
                    'marketplace' => (bool)($url->marketplace && $url->marketplace !== '0' && $url->marketplace !== 'false'),
                    'use_proxy' => (bool)($url->use_proxy && $url->use_proxy !== '0' && $url->use_proxy !== 'false'),
                    'proxy_type' => $proxyType,
                    'url' => $url->url,
                    'npm' => $url->mpn, // Keep npm field name like old format
                    'attributes' => $companyAttributes
                ];
                
                $jobData[] = $jobItem;
            }

            // Shuffle job data to prevent sequential requests to same sites
            shuffle($jobData);
            
            // Create JSON file with streaming for large datasets
            $fileName = 'job_data_' . date('Y_m_d_H_i_s') . '.json';
            $filePath = 'jobs/' . $fileName;
            
            // Create JSON file efficiently - no pretty print for better performance
            $jsonData = json_encode($jobData, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($filePath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobRecord)->update([
                'json_path' => $filePath
            ]);

            // Send messages to RabbitMQ queues individually but fast
            $queueStats = $this->sendFastToQueues($jobData);

            return [
                'success' => true,
                'message' => 'Job created successfully',
                'job_id' => $jobRecord,
                'total_urls' => $totalUrlCount,
                'companies_count' => $companiesCount,
                'json_path' => $filePath,
                'queue_stats' => $queueStats
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Error creating job: ' . $e->getMessage()
            ];
        }
    }

        /**
     * Create job data for profile (custom profile scan)
     *
     * @param int $profile_id Profile ID
     * @return array
     */
    public function create_profile_job($profile_id)
    {
        try {
            // Check if profile exists
            $profile = CustomProfile::find($profile_id);
            if (!$profile) {
                return [
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ];
            }

            // Get profile product IDs
            $profileProductIds = DB::table('custom_profile_products')
                ->where('custom_profile_id', $profile_id)
                ->pluck('user_product_id')
                ->toArray();

            if (empty($profileProductIds)) {
                return [
                    'success' => false,
                    'message' => 'Bu profilde ürün bulunamadı'
                ];
            }

            // Use raw query to get URLs for profile products
            $query = "
                SELECT 
                    c.id as company_id,
                    c.crawler_id,
                    c.server_id,
                    c.screenshot,
                    c.marketplace,
                    c.use_proxy,
                    c.proxy_id,
                    cpu.product_id,
                    cpu.url,
                    up.mpn,
                    cl.name as crawler_name,
                    sl.name as server_name
                FROM companies c
                LEFT JOIN crawler_list cl ON c.crawler_id = cl.id
                LEFT JOIN server_list sl ON c.server_id = sl.id
                INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
                INNER JOIN user_products up ON cpu.product_id::bigint = up.id
                WHERE c.deleted = false
                AND up.is_active = 1
                AND up.id IN (" . implode(',', array_map('intval', $profileProductIds)) . ")
            ";

            $urls = DB::select($query);

            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'Profil için tarama yapılacak URL bulunamadı'
                ];
            }

            // Get attributes in a single query
            $companyIds = array_unique(array_column($urls, 'company_id'));
            $attributes = DB::table('company_attributes as ca')
                ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                ->whereIn('ca.company_id', $companyIds)
                ->where('ca.value', '!=', '-1')
                ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                ->get()
                ->groupBy('company_id');

            // Prepare job data
            $jobData = [];
            $totalUrlCount = count($urls);
            $companiesCount = count($companyIds);

            // Generate unique job_id first
            $jobRecord = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Profil Tarama - ' . $profile->name . ' - ' . date('Y-m-d H:i:s'),
                'data' => '{}',
                'status' => 'pending',
                'created_at' => now(),
                'count' => $totalUrlCount,
                'json_path' => '',
                'updated_at' => now()
            ]);

            // Process URLs efficiently
            $serverNames = [];
            $proxyNames = [];
            foreach ($urls as $url) {
                $companyAttributes = $attributes->get($url->company_id, collect())->toArray();
                
                // Cache server name to avoid repeated DB calls
                if (!isset($serverNames[$url->server_id])) {
                    $serverNames[$url->server_id] = $this->getServerName($url->server_id);
                }
                
                // Cache proxy name to avoid repeated DB calls
                $proxyType = null;
                if ($url->use_proxy && $url->proxy_id) {
                    if (!isset($proxyNames[$url->proxy_id])) {
                        $proxyNames[$url->proxy_id] = $this->getProxyName($url->proxy_id);
                    }
                    $proxyType = $proxyNames[$url->proxy_id];
                }
                
                $jobItem = [
                    'job_id' => $jobRecord,
                    'company_id' => $url->company_id,
                    'product_id' => (int)$url->product_id,
                    'application_id' => $url->crawler_id,
                    'server_id' => $url->server_id,
                    'server_name' => $serverNames[$url->server_id],
                    'screenshot' => (bool)($url->screenshot && $url->screenshot !== '0' && $url->screenshot !== 'false'),
                    'marketplace' => (bool)($url->marketplace && $url->marketplace !== '0' && $url->marketplace !== 'false'),
                    'use_proxy' => (bool)($url->use_proxy && $url->use_proxy !== '0' && $url->use_proxy !== 'false'),
                    'proxy_type' => $proxyType,
                    'url' => $url->url,
                    'npm' => $url->mpn,
                    'attributes' => $companyAttributes
                ];
                
                $jobData[] = $jobItem;
            }

            // Shuffle job data to prevent sequential requests to same sites
            shuffle($jobData);
            
            // Create JSON file
            $fileName = 'job_data_profile_' . $profile_id . '_' . date('Y_m_d_H_i_s') . '.json';
            $filePath = 'jobs/' . $fileName;
            
            // Create JSON file efficiently
            $jsonData = json_encode($jobData, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($filePath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobRecord)->update([
                'json_path' => $filePath
            ]);

            // Send messages to RabbitMQ queues
            $queueStats = $this->sendFastToQueues($jobData);

            return [
                'success' => true,
                'message' => 'Profil taraması başarıyla oluşturuldu',
                'job_id' => $jobRecord,
                'total_urls' => $totalUrlCount,
                'companies_count' => $companiesCount,
                'json_path' => $filePath,
                'queue_stats' => $queueStats
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Profil taraması oluşturulurken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

        /**
     * Create job data for companies (Optimized version)
     *
     * @param string|int $company_id Company ID or 'all' for all companies
     * @return array
     */
    public function create_job_chrome_extension($company_id)
    {
        try {
            // Use raw query for better performance with large datasets
            $query = "
                SELECT 
                    c.id as company_id,
                    c.crawler_id,
                    c.server_id,
                    c.screenshot,
                    c.marketplace,
                    c.use_proxy,
                    c.proxy_id,
                    cpu.product_id,
                    cpu.url,
                    up.mpn,
                    cl.name as crawler_name,
                    sl.name as server_name
                FROM companies c
                LEFT JOIN crawler_list cl ON c.crawler_id = cl.id
                LEFT JOIN server_list sl ON c.server_id = sl.id
                INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
                INNER JOIN user_products up ON cpu.product_id::bigint = up.id
                WHERE c.deleted = false
                AND up.is_active = 1
            ";

            if ($company_id !== 'all') {
                $query .= " AND c.id = " . (int)$company_id;
            }

            $urls = DB::select($query);

            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'No companies found for the given criteria'
                ];
            }

            // Get attributes in a single query
            $companyIds = array_unique(array_column($urls, 'company_id'));
            $attributes = DB::table('company_attributes as ca')
                ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                ->whereIn('ca.company_id', $companyIds)
                ->where('ca.value', '!=', '-1') // value "-1" olan verileri alma
                ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                ->get()
                ->groupBy('company_id');

            // Prepare job data
            $jobData = [];
            $totalUrlCount = count($urls);
            $companiesCount = count($companyIds);

            // Generate unique job_id first
            $jobRecord = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Quick Scan - ' . date('Y-m-d H:i:s'),
                'data' => '{}', // Will be updated after file creation
                'status' => 'pending',
                'created_at' => now(),
                'count' => $totalUrlCount,
                'json_path' => '', // Will be updated after file creation
                'updated_at' => now()
            ]);

            // Process URLs efficiently - no need for chunks for 2k data
            $proxyNames = []; // Cache proxy names
            foreach ($urls as $url) {
                $companyAttributes = $attributes->get($url->company_id, collect())->toArray();
                
                // Eğer attributes boşsa, bu item'ı ekleme
                if (empty($companyAttributes)) {
                    continue;
                }
                
                // Cache proxy name to avoid repeated DB calls
                $proxyType = null;
                if ($url->use_proxy && $url->proxy_id) {
                    if (!isset($proxyNames[$url->proxy_id])) {
                        $proxyNames[$url->proxy_id] = $this->getProxyName($url->proxy_id);
                    }
                    $proxyType = $proxyNames[$url->proxy_id];
                }
                
                // Benzersiz data_id oluştur
                $uniqueDataId = uniqid('', true);
                
                $jobItem = [
                    'job_id' => $jobRecord,
                    'data_id' => $uniqueDataId,
                    'company_id' => $url->company_id,
                    'product_id' => (int)$url->product_id, // Convert to integer like old format
                    'screenshot' => (bool)($url->screenshot && $url->screenshot !== '0' && $url->screenshot !== 'false'),
                    'use_proxy' => (bool)($url->use_proxy && $url->use_proxy !== '0' && $url->use_proxy !== 'false'),
                    'proxy_type' => $proxyType,
                    'url' => $url->url,
                    'npm' => $url->mpn, // Keep npm field name like old format
                    'attributes' => $companyAttributes
                ];
                
                $jobData[] = $jobItem;
            }

            // Shuffle job data to prevent sequential requests to same sites
            shuffle($jobData);
            
            // Create JSON file with streaming for large datasets
            $fileName = 'job_data_' . date('Y_m_d_H_i_s') . '.json';
            $filePath = 'jobs/' . $fileName;
            
            // Create JSON file efficiently - no pretty print for better performance
            $jsonData = json_encode($jobData, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($filePath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobRecord)->update([
                'json_path' => $filePath
            ]);

            // Send messages to RabbitMQ queues individually but fast
            // Chrome extension için queue'ya mesaj göndermiyoruz, sadece JSON dosyası oluşturuyoruz
            $queueStats = [];

            return [
                'success' => true,
                'message' => 'Job created successfully',
                'job_id' => $jobRecord,
                'total_urls' => $totalUrlCount,
                'companies_count' => $companiesCount,
                'json_path' => $filePath,
                'queue_stats' => $queueStats
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Error creating job: ' . $e->getMessage()
            ];
        }
    }


        /**
     * Create job data for profile (custom profile scan)
     *
     * @param int $profile_id Profile ID
     * @return array
     */
    public function create_profile_job_chrome_extension($profile_id)
    {
        try {
            // Check if profile exists
            $profile = CustomProfile::find($profile_id);
            if (!$profile) {
                return [
                    'success' => false,
                    'message' => 'Profil bulunamadı'
                ];
            }

            // Get profile product IDs
            $profileProductIds = DB::table('custom_profile_products')
                ->where('custom_profile_id', $profile_id)
                ->pluck('user_product_id')
                ->toArray();

            if (empty($profileProductIds)) {
                return [
                    'success' => false,
                    'message' => 'Bu profilde ürün bulunamadı'
                ];
            }

            // Use raw query to get URLs for profile products
            $query = "
                SELECT 
                    c.id as company_id,
                    c.crawler_id,
                    c.server_id,
                    c.screenshot,
                    c.marketplace,
                    c.use_proxy,
                    c.proxy_id,
                    cpu.product_id,
                    cpu.url,
                    up.mpn,
                    cl.name as crawler_name,
                    sl.name as server_name
                FROM companies c
                LEFT JOIN crawler_list cl ON c.crawler_id = cl.id
                LEFT JOIN server_list sl ON c.server_id = sl.id
                INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
                INNER JOIN user_products up ON cpu.product_id::bigint = up.id
                WHERE c.deleted = false
                AND up.is_active = 1
                AND up.id IN (" . implode(',', array_map('intval', $profileProductIds)) . ")
            ";

            $urls = DB::select($query);

            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'Profil için tarama yapılacak URL bulunamadı'
                ];
            }

            // Get attributes in a single query
            $companyIds = array_unique(array_column($urls, 'company_id'));
            $attributes = DB::table('company_attributes as ca')
                ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                ->whereIn('ca.company_id', $companyIds)
                ->where('ca.value', '!=', '-1')
                ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                ->get()
                ->groupBy('company_id');

            // Prepare job data
            $jobData = [];
            $totalUrlCount = count($urls);
            $companiesCount = count($companyIds);

            // Generate unique job_id first
            $jobRecord = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Profil Tarama - ' . $profile->name . ' - ' . date('Y-m-d H:i:s'),
                'data' => '{}',
                'status' => 'pending',
                'created_at' => now(),
                'count' => $totalUrlCount,
                'json_path' => '',
                'updated_at' => now()
            ]);

            // Process URLs efficiently
            $proxyNames = [];
            foreach ($urls as $url) {
                $companyAttributes = $attributes->get($url->company_id, collect())->toArray();
                
                // Eğer attributes boşsa, bu item'ı ekleme
                if (empty($companyAttributes)) {
                    continue;
                }
                
                // Cache proxy name to avoid repeated DB calls
                $proxyType = null;
                if ($url->use_proxy && $url->proxy_id) {
                    if (!isset($proxyNames[$url->proxy_id])) {
                        $proxyNames[$url->proxy_id] = $this->getProxyName($url->proxy_id);
                    }
                    $proxyType = $proxyNames[$url->proxy_id];
                }
                
                // Benzersiz data_id oluştur
                $uniqueDataId = uniqid('', true);
                
                $jobItem = [
                    'job_id' => $jobRecord,
                    'data_id' => $uniqueDataId,
                    'company_id' => $url->company_id,
                    'product_id' => (int)$url->product_id,
                    'screenshot' => (bool)($url->screenshot && $url->screenshot !== '0' && $url->screenshot !== 'false'),
                    'use_proxy' => (bool)($url->use_proxy && $url->use_proxy !== '0' && $url->use_proxy !== 'false'),
                    'proxy_type' => $proxyType,
                    'url' => $url->url,
                    'npm' => $url->mpn,
                    'attributes' => $companyAttributes
                ];
                
                $jobData[] = $jobItem;
            }

            // Shuffle job data to prevent sequential requests to same sites
            shuffle($jobData);
            
            // Create JSON file
            $fileName = 'job_data_profile_' . $profile_id . '_' . date('Y_m_d_H_i_s') . '.json';
            $filePath = 'jobs/' . $fileName;
            
            // Create JSON file efficiently
            $jsonData = json_encode($jobData, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($filePath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobRecord)->update([
                'json_path' => $filePath
            ]);

            // Send messages to RabbitMQ queues
            // Chrome extension için queue'ya mesaj göndermiyoruz, sadece JSON dosyası oluşturuyoruz
            $queueStats = [];

            return [
                'success' => true,
                'message' => 'Profil taraması başarıyla oluşturuldu',
                'job_id' => $jobRecord,
                'total_urls' => $totalUrlCount,
                'companies_count' => $companiesCount,
                'json_path' => $filePath,
                'queue_stats' => $queueStats
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Profil taraması oluşturulurken hata oluştu: ' . $e->getMessage()
            ];
        }
    }



    /**
     * Create JSON file using streaming for large datasets
     *
     * @param string $filePath
     * @param array $jobData
     * @return void
     */
    private function createJsonFileStreaming($filePath, $jobData)
    {
        $fullPath = Storage::disk('public')->path($filePath);
        $directory = dirname($fullPath);
        
        if (!is_dir($directory)) {
            mkdir($directory, 0755, true);
        }

        $file = fopen($fullPath, 'w');
        fwrite($file, "[\n");
        
        $count = count($jobData);
        for ($i = 0; $i < $count; $i++) {
            $json = json_encode($jobData[$i], JSON_UNESCAPED_UNICODE);
            fwrite($file, "    " . $json);
            
            if ($i < $count - 1) {
                fwrite($file, ",");
            }
            fwrite($file, "\n");
        }
        
        fwrite($file, "]");
        fclose($file);
    }

    /**
     * Start a quick scan using create_job
     */
    public function startQuickScan($companyId = null)
    {
        try {
            $companyId = $companyId ?: 'all';
            $result = $this->create_job($companyId);
            
            if ($result['success']) {
                return [
                    'success' => true,
                    'message' => 'Hızlı tarama başarıyla başlatıldı',
                    'scan_type' => $companyId === 'all' ? 'Genel' : 'Firma Özel',
                    'company_id' => $companyId,
                    'started_at' => now()->toISOString(),
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ];
            }
            
            return $result;
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Hızlı tarama başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Start a demo scan with custom URLs
     */
    public function startDemoScan($urls = [], $companyId = null)
    {
        try {
            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'Lütfen en az bir URL girin'
                ];
            }
            
            $result = $this->create_demo_job($urls, $companyId);
            
            if ($result['success']) {
                return [
                    'success' => true,
                    'message' => 'Demo tarama başarıyla başlatıldı (' . count($urls) . ' URL)',
                    'scan_type' => 'Demo Custom URLs',
                    'company_id' => $companyId,
                    'started_at' => now()->toISOString(),
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ];
            }
            
            return $result;
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Demo tarama başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Start a profile scan using create_profile_job
     */
    public function startProfileScan($profileId)
    {
        try {
            if (!$profileId) {
                return [
                    'success' => false,
                    'message' => 'Profil ID belirtilmedi'
                ];
            }

            $result = $this->create_profile_job($profileId);
            
            if ($result['success']) {
                return [
                    'success' => true,
                    'message' => $result['message'],
                    'scan_type' => 'Profil Tarama',
                    'profile_id' => $profileId,
                    'started_at' => now()->toISOString(),
                    'queue_stats' => $result['queue_stats'] ?? [],
                    'total_urls' => $result['total_urls'] ?? 0,
                    'companies_count' => $result['companies_count'] ?? 0,
                    'job_id' => $result['job_id'] ?? null
                ];
            }
            
            return $result;
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Profil taraması başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Create a demo job with custom URLs provided by user
     */
    private function create_demo_job($customUrls = [], $companyId = null)
    {
        try {
            if (empty($customUrls)) {
                return [
                    'success' => false,
                    'message' => 'No URLs provided'
                ];
            }

            // Default company settings if company_id is provided
            $defaultCompany = null;
            if ($companyId) {
                $defaultCompany = DB::table('companies')
                    ->leftJoin('crawler_list as cl', 'companies.crawler_id', '=', 'cl.id')
                    ->leftJoin('server_list as sl', 'companies.server_id', '=', 'sl.id')
                    ->where('companies.id', $companyId)
                    ->where('companies.deleted', false)
                    ->select(
                        'companies.id as company_id',
                        'companies.crawler_id',
                        'companies.server_id',
                        'companies.screenshot',
                        'companies.marketplace',
                        'companies.use_proxy',
                        'companies.proxy_id',
                        'cl.name as crawler_name',
                        'sl.name as server_name'
                    )
                    ->first();

                if (!$defaultCompany) {
                    return [
                        'success' => false,
                        'message' => 'Belirtilen firma bulunamadı'
                    ];
                }
            }

            // Prepare job data
            $jobData = [];
            $totalUrlCount = count($customUrls);

            // Generate unique job_id first
            $jobRecord = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Demo Scan (Custom URLs) - ' . date('Y-m-d H:i:s'),
                'data' => '{}',
                'status' => 'pending',
                'created_at' => now(),
                'count' => $totalUrlCount,
                'json_path' => '',
                'updated_at' => now()
            ]);

            // Get company attributes if company specified
            $companyAttributes = [];
            if ($companyId) {
                $attributes = DB::table('company_attributes as ca')
                    ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                    ->where('ca.company_id', $companyId)
                    ->where('ca.value', '!=', '-1')
                    ->select('a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                    ->get()
                    ->toArray();
                
                $companyAttributes = $attributes;
            }

            // Cache server and proxy names
            $serverNames = [];
            $proxyNames = [];

            // Process each custom URL
            foreach ($customUrls as $url) {
                $url = trim($url);
                if (empty($url)) continue;

                // Use default company settings or generic settings
                if ($defaultCompany) {
                    $companyIdValue = $defaultCompany->company_id;
                    $crawlerId = $defaultCompany->crawler_id;
                    $serverId = $defaultCompany->server_id;
                    $screenshot = $defaultCompany->screenshot;
                    $marketplace = $defaultCompany->marketplace;
                    $useProxy = $defaultCompany->use_proxy;
                    $proxyId = $defaultCompany->proxy_id;
                } else {
                    // Generic settings when no company specified
                    $companyIdValue = 0; // Unknown company
                    $crawlerId = 2; // Default to Selenium
                    $serverId = 1; // Default to local
                    $screenshot = false;
                    $marketplace = false;
                    $useProxy = false;
                    $proxyId = null;
                }

                // Cache server name
                if (!isset($serverNames[$serverId])) {
                    $serverNames[$serverId] = $this->getServerName($serverId);
                }

                // Cache proxy name
                $proxyType = null;
                if ($useProxy && $proxyId) {
                    if (!isset($proxyNames[$proxyId])) {
                        $proxyNames[$proxyId] = $this->getProxyName($proxyId);
                    }
                    $proxyType = $proxyNames[$proxyId];
                }

                // 🔍 URL için product_id ve mpn'i DB'den çek (varsa)
                // Önce tam eşleşme dene - sadece aktif ürünleri al
                $productData = DB::table('company_products_urls as cpu')
                    ->leftJoin('user_products as up', DB::raw('cpu.product_id::bigint'), '=', 'up.id')
                    ->where('cpu.url', $url)
                    ->where('cpu.company_id', $companyIdValue)
                    ->where(function($query) {
                        $query->whereNull('up.id')  // Product_id yoksa (esnek)
                              ->orWhere('up.is_active', 1);  // Veya aktif ürün
                    })
                    ->select('cpu.product_id', 'up.mpn')
                    ->first();
                
                // Bulamazsa, URL'i normalize et ve esnek ara
                if (!$productData) {
                    // URL'den query string ve trailing slash'i temizle
                    $normalizedUrl = rtrim(parse_url($url, PHP_URL_SCHEME) . '://' . 
                                          parse_url($url, PHP_URL_HOST) . 
                                          parse_url($url, PHP_URL_PATH), '/');
                    
                    $productData = DB::table('company_products_urls as cpu')
                        ->leftJoin('user_products as up', DB::raw('cpu.product_id::bigint'), '=', 'up.id')
                        ->where('cpu.company_id', $companyIdValue)
                        ->where(function($query) use ($url, $normalizedUrl) {
                            $query->where('cpu.url', $url)
                                  ->orWhere('cpu.url', $normalizedUrl)
                                  ->orWhere('cpu.url', $normalizedUrl . '/')
                                  ->orWhereRaw("TRIM(TRAILING '/' FROM cpu.url) = ?", [$normalizedUrl]);
                        })
                        ->where(function($query) {
                            $query->whereNull('up.id')  // Product_id yoksa (esnek)
                                  ->orWhere('up.is_active', 1);  // Veya aktif ürün
                        })
                        ->select('cpu.product_id', 'up.mpn')
                        ->first();
                }
                
                // Hala bulamazsa, URL'den product code çıkar ve MPN ile ara
                if (!$productData) {
                    // URL'den product code pattern'i çıkar (örn: MC7X4TU/A, MLPF3TU-A)
                    // Pattern: büyük harfler + rakamlar + TU + opsiyonel /A veya -A
                    if (preg_match('/([A-Z0-9]{5,}TU[\/\-]?A)/i', $url, $matches)) {
                        $productCode = strtoupper(str_replace('-', '/', $matches[1]));
                        
                        $productData = DB::table('user_products as up')
                            ->where('up.mpn', $productCode)
                            ->where('up.is_active', 1)  // Sadece aktif ürünler
                            ->select('up.id as product_id', 'up.mpn')
                            ->first();
                        
                        if ($productData) {
                            // MPN'den product_id bulundu ama VARCHAR'a çevir (cpu.product_id VARCHAR)
                            $productData->product_id = (string)$productData->product_id;
                        }
                    }
                }
                
                $productId = $productData ? (int)$productData->product_id : 0;
                $mpn = $productData ? $productData->mpn : null;

                $jobItem = [
                    'job_id' => $jobRecord,
                    'company_id' => $companyIdValue,
                    'product_id' => $productId, // ✅ DB'den çekilen product_id
                    'application_id' => $crawlerId,
                    'server_id' => $serverId,
                    'server_name' => $serverNames[$serverId],
                    'screenshot' => (bool)($screenshot && $screenshot !== '0' && $screenshot !== 'false'),
                    'marketplace' => (bool)($marketplace && $marketplace !== '0' && $marketplace !== 'false'),
                    'use_proxy' => (bool)($useProxy && $useProxy !== '0' && $useProxy !== 'false'),
                    'proxy_type' => $proxyType,
                    'url' => $url,
                    'npm' => $mpn, // ✅ DB'den çekilen mpn
                    'attributes' => $companyAttributes
                ];

                $jobData[] = $jobItem;
            }

            if (empty($jobData)) {
                return [
                    'success' => false,
                    'message' => 'Geçerli URL bulunamadı'
                ];
            }

            // Shuffle job data to prevent sequential requests to same sites
            shuffle($jobData);

            // Create JSON file
            $fileName = 'demo_custom_urls_' . date('Y_m_d_H_i_s') . '.json';
            $filePath = 'jobs/' . $fileName;

            $this->createJsonFileStreaming($filePath, $jobData);

            // Update job record with file path
            DB::table('jobs_data')
                ->where('id', $jobRecord)
                ->update([
                    'json_path' => $filePath,
                    'data' => json_encode([
                        'file_path' => $filePath,
                        'total_urls' => count($jobData),
                        'custom_urls' => true,
                        'company_id' => $companyId,
                        'created_at' => now()->toISOString()
                    ])
                ]);

            // Send messages to RabbitMQ queues
            $queueStats = $this->sendFastToQueues($jobData);

            return [
                'success' => true,
                'message' => 'Demo job created successfully with custom URLs',
                'job_id' => $jobRecord,
                'total_urls' => count($jobData),
                'companies_count' => $companyId ? 1 : 0,
                'file_path' => $filePath,
                'queue_stats' => $queueStats
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Demo job creation failed: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Get all companies for selection
     */
    public function getCompanies()
    {
        try {
            $companies = Company::where('deleted', false)
                ->select('id', 'name as company_name')
                ->orderBy('name')
                ->get();
            
            return [
                'success' => true,
                'companies' => $companies
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Firmalar yüklenirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Get scan operations history from jobs_data with pagination
     */
    public function getScanOperations($page = 1, $perPage = 10)
    {
        try {
            $offset = ($page - 1) * $perPage;
            
            // Get total count
            $totalCount = DB::table('jobs_data')->count();
            
            // Get paginated data
            $operations = DB::table('jobs_data')
                ->select('id', 'created_at', 'count as total_urls', 'json_path', 'status')
                ->orderBy('created_at', 'desc')
                ->offset($offset)
                ->limit($perPage)
                ->get();
            
            // Her job için scraper_data tablosundan bulunan veri sayısını al
            $jobIds = $operations->pluck('id')->toArray();
            $scraperDataCounts = [];
            
            if (!empty($jobIds)) {
                $scraperDataCounts = DB::table('scraper_data')
                    ->whereIn('job_id', $jobIds)
                    ->select('job_id', DB::raw('COUNT(*) as found_count'))
                    ->groupBy('job_id')
                    ->pluck('found_count', 'job_id')
                    ->toArray();
            }
            
            // Operations'a found_count ekle
            $operations = $operations->map(function ($operation) use ($scraperDataCounts) {
                $operation->found_count = $scraperDataCounts[$operation->id] ?? 0;
                return $operation;
            });
            
            $totalPages = ceil($totalCount / $perPage);
            
            return [
                'success' => true,
                'operations' => $operations,
                'pagination' => [
                    'current_page' => $page,
                    'per_page' => $perPage,
                    'total' => $totalCount,
                    'total_pages' => $totalPages,
                    'has_next' => $page < $totalPages,
                    'has_prev' => $page > 1
                ]
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'İşlem geçmişi yüklenirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Get job details from jobs_detail table
     */
    public function getJobDetails($jobId)
    {
        try {
            // First get job info from jobs_data
            $jobData = DB::table('jobs_data')
                ->where('id', $jobId)
                ->first();
            
            if (!$jobData) {
                return [
                    'success' => false,
                    'message' => 'Job bulunamadı'
                ];
            }
            
            // jobs_detail tablosu olmadığı için detayları DB'den çekmeyip boş dizi dönüyoruz.
            // Detaylı içerik için JSON görüntüleme endpoint'i kullanılabilir.
            $jobDetails = collect([]);
            
            return [
                'success' => true,
                'job_data' => $jobData,
                'job_details' => $jobDetails
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Job detayları yüklenirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Read job JSON file content using jobs_data.json_path
     */
    public function getJobJson($jobId)
    {
        try {
            $jobData = DB::table('jobs_data')
                ->where('id', $jobId)
                ->first();

            if (!$jobData) {
                return [
                    'success' => false,
                    'message' => 'Job bulunamadı'
                ];
            }

            if (empty($jobData->json_path)) {
                return [
                    'success' => false,
                    'message' => 'Bu job için json_path bulunamadı'
                ];
            }

            $pathCandidates = [];
            $jsonPath = trim((string) $jobData->json_path);

            // Normalize path: remove leading slashes
            $normalized = ltrim($jsonPath, '/');

            // If path seems to be under jobs/, assume storage/app/public/jobs
            $underJobs = str_starts_with($normalized, 'jobs/');

            // Absolute as-is
            $pathCandidates[] = $jsonPath;

            // storage/app
            $pathCandidates[] = storage_path('app/' . $normalized);

            // storage/app/public
            $pathCandidates[] = storage_path('app/public/' . $normalized);

            // if not already under public/, try prefixing public/
            if (!str_starts_with($normalized, 'public/')) {
                $pathCandidates[] = storage_path('app/public/' . 'public/' . $normalized);
            }

            // If looks like jobs/, also try explicit public/jobs
            if ($underJobs) {
                $pathCandidates[] = storage_path('app/public/jobs/' . basename($normalized));
                $pathCandidates[] = public_path('storage/jobs/' . basename($normalized));
            }

            // public/storage mirror
            $pathCandidates[] = public_path('storage/' . $normalized);

            // direct public path (if published into public directly)
            $pathCandidates[] = public_path($normalized);

            // base path fallback
            $pathCandidates[] = base_path($normalized);

            // Also try demo_ prefix variant if original not found
            $dirname = dirname($normalized);
            $basename = basename($normalized);
            $demoBasename = str_starts_with($basename, 'demo_') ? $basename : ('demo_' . $basename);
            $demoPath = trim($dirname, './') ? ($dirname . '/' . $demoBasename) : $demoBasename;

            $pathCandidates[] = storage_path('app/' . $demoPath);
            $pathCandidates[] = storage_path('app/public/' . $demoPath);
            $pathCandidates[] = public_path('storage/' . $demoPath);
            $pathCandidates[] = public_path($demoPath);

            $resolvedPath = null;
            foreach ($pathCandidates as $candidate) {
                if (is_string($candidate) && file_exists($candidate) && is_readable($candidate)) {
                    $resolvedPath = $candidate;
                    break;
                }
            }

            if (!$resolvedPath) {
                return [
                    'success' => false,
                    'message' => 'JSON dosyası bulunamadı veya okunamıyor: ' . $jobData->json_path
                ];
            }

            $content = file_get_contents($resolvedPath);
            $decoded = json_decode($content, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return [
                    'success' => false,
                    'message' => 'JSON parse hatası: ' . json_last_error_msg()
                ];
            }

            return [
                'success' => true,
                'job_data' => $jobData,
                'json' => $decoded
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'JSON okunurken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Get scheduled scans (existing method)
     */
    public function getScheduledScans()
    {
        try {
            $jobPlans = JobPlan::with('companyRelation')
                ->orderBy('time')
                ->get()
                ->map(function ($jobPlan) {
                    return [
                        'id' => $jobPlan->id,
                        'time' => $jobPlan->time,
                        'company' => $jobPlan->company,
                        'company_name' => $jobPlan->company_name,
                        'active' => $jobPlan->active
                    ];
                });
            
            return [
                'success' => true,
                'job_plans' => $jobPlans
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Planlı taramalar yüklenirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Create scheduled scan (existing method)
     */
    public function createScheduledScan($time, $company)
    {
        try {
            $jobPlan = JobPlan::create([
                'time' => $time,
                'company' => $company,
                'active' => true
            ]);
            
            return [
                'success' => true,
                'message' => 'Planlı tarama başarıyla eklendi',
                'job_plan' => $jobPlan
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Planlı tarama eklenirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Delete scheduled scan (existing method)
     */
    public function deleteScheduledScan($id)
    {
        try {
            $jobPlan = JobPlan::find($id);
            
            if (!$jobPlan) {
                return [
                    'success' => false,
                    'message' => 'Planlı tarama bulunamadı'
                ];
            }
            
            $jobPlan->delete();
            
            return [
                'success' => true,
                'message' => 'Planlı tarama başarıyla silindi'
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Planlı tarama silinirken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Send messages to RabbitMQ queues individually but fast
     */
    private function sendFastToQueues($jobData)
    {
        $queueStats = [];
        $connections = []; // Cache connections by server
        
        try {
            // Group messages by server to reuse connections
            $serverGroups = [];
            foreach ($jobData as $jobItem) {
                // Chrome extension için varsayılan değerler (eğer yoksa)
                $serverId = $jobItem['server_id'] ?? 3; // Default: chrome
                $applicationId = $jobItem['application_id'] ?? 4; // Default: Chrome Extension
                $queueName = $this->getQueueName($applicationId);
                
                if (!isset($serverGroups[$serverId])) {
                    $serverGroups[$serverId] = [];
                }
                if (!isset($serverGroups[$serverId][$queueName])) {
                    $serverGroups[$serverId][$queueName] = [];
                }
                
                $serverGroups[$serverId][$queueName][] = $jobItem;
                $queueStats[$queueName] = 0;
            }
            
            // Send messages for each server
            foreach ($serverGroups as $serverId => $queues) {
                $vhost = $this->getServerName($serverId);
                
                // Create connection once per server
                $connection = new AMQPStreamConnection(
                    $this->rabbitmqHost,
                    $this->rabbitmqPort,
                    $this->rabbitmqUser,
                    $this->rabbitmqPass,
                    $vhost
                );
                
                $channel = $connection->channel();
                
                // Send messages for each queue
                foreach ($queues as $queueName => $messages) {
                    // Declare queue once
                    $channel->queue_declare($queueName, false, true, false, false);
                    
                    // Send all messages for this queue
                    foreach ($messages as $message) {
                        $msg = new AMQPMessage(
                            json_encode($message),
                            ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
                        );
                        
                        $channel->basic_publish($msg, '', $queueName);
                        $queueStats[$queueName]++;
                    }
                }
                
                $channel->close();
                $connection->close();
            }
            
        } catch (\Exception $e) {
            \Log::error('Fast queue send error: ' . $e->getMessage());
        }
        
        return $queueStats;
    }

    /**
     * Purge all RabbitMQ queues
     * Tüm RabbitMQ queue'lerini temizler (error ve completed dahil)
     * 
     * @param string|null $environment 'local' veya 'azure', null ise tüm server'lar için çalışır
     * @return array
     */
    public function purgeQueues($environment = null)
    {
        try {
            $queues = [
                // Scrapy queues
                'scrapy.queue',
                'scrapy.queue.completed',
                'scrapy.queue.error',
                
                // Selenium queues
                'selenium.queue',
                'selenium.queue.completed',
                'selenium.queue.error',
                
                // Playwright queues
                'playwright.queue',
                'playwright.queue.completed',
                'playwright.queue.error',
                
                // Save queues
                'save.queue',
                'save.queue.completed',
                'save.queue.error',
                
                // Test queues (optional)
                'test.queue',
                'test.queue.completed',
                'test.queue.error',
            ];

            $stats = [
                'success' => 0,
                'skip' => 0,
                'error' => 0,
                'total_messages' => 0,
                'details' => []
            ];

            // Server'ları belirle
            $servers = [];
            if ($environment === null) {
                // Tüm server'lar için
                $servers = [
                    ['id' => 1, 'name' => 'local', 'vhost' => 'local'],
                    ['id' => 2, 'name' => 'azure', 'vhost' => 'azure']
                ];
            } else {
                // Sadece belirtilen server için
                $serverId = $environment === 'local' ? 1 : 2;
                $servers = [
                    ['id' => $serverId, 'name' => $environment, 'vhost' => $environment]
                ];
            }

            // Her server için queue'ları temizle
            foreach ($servers as $server) {
                $vhost = $server['vhost'];
                $vhostEncoded = str_replace('/', '%2F', $vhost);
                
                // RabbitMQ Management API port
                $apiPort = '15672';
                $apiBaseUrl = "http://{$this->rabbitmqHost}:{$apiPort}/api";
                
                foreach ($queues as $queueName) {
                    try {
                        // Queue bilgisini al
                        $queueInfoUrl = "{$apiBaseUrl}/queues/{$vhostEncoded}/{$queueName}";
                        
                        $ch = curl_init($queueInfoUrl);
                        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                        curl_setopt($ch, CURLOPT_USERPWD, "{$this->rabbitmqUser}:{$this->rabbitmqPass}");
                        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
                        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
                        
                        $response = curl_exec($ch);
                        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                        curl_close($ch);
                        
                        if ($httpCode == 404) {
                            // Queue bulunamadı, atla
                            $stats['skip']++;
                            $stats['details'][] = [
                                'queue' => $queueName,
                                'server' => $server['name'],
                                'status' => 'skip',
                                'message' => 'Queue bulunamadı',
                                'count' => 0
                            ];
                            continue;
                        }
                        
                        if ($httpCode != 200) {
                            // Hata
                            $stats['error']++;
                            $stats['details'][] = [
                                'queue' => $queueName,
                                'server' => $server['name'],
                                'status' => 'error',
                                'message' => "HTTP {$httpCode}",
                                'count' => 0
                            ];
                            continue;
                        }
                        
                        // Mesaj sayısını al
                        $queueInfo = json_decode($response, true);
                        $messageCount = $queueInfo['messages'] ?? 0;
                        
                        // Queue'yu purge et
                        $purgeUrl = "{$apiBaseUrl}/queues/{$vhostEncoded}/{$queueName}/contents";
                        
                        $ch = curl_init($purgeUrl);
                        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'DELETE');
                        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                        curl_setopt($ch, CURLOPT_USERPWD, "{$this->rabbitmqUser}:{$this->rabbitmqPass}");
                        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
                        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
                        
                        $purgeResponse = curl_exec($ch);
                        $purgeHttpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                        curl_close($ch);
                        
                        if ($purgeHttpCode == 200 || $purgeHttpCode == 204) {
                            // Başarılı
                            $stats['success']++;
                            $stats['total_messages'] += $messageCount;
                            $stats['details'][] = [
                                'queue' => $queueName,
                                'server' => $server['name'],
                                'status' => 'success',
                                'message' => 'Temizlendi',
                                'count' => $messageCount
                            ];
                        } else {
                            // Purge hatası
                            $stats['error']++;
                            $stats['details'][] = [
                                'queue' => $queueName,
                                'server' => $server['name'],
                                'status' => 'error',
                                'message' => "Purge HTTP {$purgeHttpCode}",
                                'count' => $messageCount
                            ];
                        }
                        
                    } catch (\Exception $e) {
                        $stats['error']++;
                        $stats['details'][] = [
                            'queue' => $queueName,
                            'server' => $server['name'],
                            'status' => 'error',
                            'message' => $e->getMessage(),
                            'count' => 0
                        ];
                        \Log::error("Queue purge error for {$queueName} on {$server['name']}: " . $e->getMessage());
                    }
                }
            }

            return [
                'success' => true,
                'message' => "Purge işlemi tamamlandı. Başarılı: {$stats['success']}, Atlandı: {$stats['skip']}, Hata: {$stats['error']}, Silinen Mesaj: {$stats['total_messages']}",
                'stats' => $stats
            ];

        } catch (\Exception $e) {
            \Log::error('Purge queues error: ' . $e->getMessage());
            return [
                'success' => false,
                'message' => 'Queue temizleme işlemi sırasında hata oluştu: ' . $e->getMessage(),
                'stats' => null
            ];
        }
    }

    /**
     * Get job queue status by job_id
     * Job ID'ye göre queue'lardaki mesaj sayılarını döner
     * RabbitMQ Management API'den mesajları peek ederek job_id'ye göre filtreler
     * 
     * @param int $jobId
     * @return array
     */
    public function getJobQueueStatus($jobId)
    {
        try {
            $queues = [
                // Processing queues
                'scrapy.queue',
                'selenium.queue',
                'playwright.queue',
                'save.queue',
                
                // Completed queues
                'scrapy.queue.completed',
                'selenium.queue.completed',
                'playwright.queue.completed',
                'save.queue.completed',
                
                // Error queues
                'scrapy.queue.error',
                'selenium.queue.error',
                'playwright.queue.error',
                'save.queue.error',
            ];

            $stats = [
                'pending' => 0,      // Processing queue'larda bekleyen (ready)
                'processing' => 0,  // Consumer tarafından işlenen (unacked)
                'completed' => 0,   // Completed queue'larda
                'error' => 0,        // Error queue'larda
                'queues' => []       // Detaylı queue bilgileri
            ];

            $servers = [
                ['id' => 1, 'name' => 'local', 'vhost' => 'local'],
                ['id' => 2, 'name' => 'azure', 'vhost' => 'azure']
            ];

            foreach ($servers as $server) {
                $vhost = $server['vhost'];
                $vhostEncoded = str_replace('/', '%2F', $vhost);
                $apiPort = '15672';
                $apiBaseUrl = "http://{$this->rabbitmqHost}:{$apiPort}/api";

                foreach ($queues as $queueName) {
                    try {
                        // Queue bilgisini al (mesaj sayısı, consumer sayısı)
                        $queueInfoUrl = "{$apiBaseUrl}/queues/{$vhostEncoded}/{$queueName}";
                        
                        $ch = curl_init($queueInfoUrl);
                        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                        curl_setopt($ch, CURLOPT_USERPWD, "{$this->rabbitmqUser}:{$this->rabbitmqPass}");
                        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
                        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
                        
                        $response = curl_exec($ch);
                        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                        curl_close($ch);

                        if ($httpCode != 200) {
                            continue; // Queue yoksa veya hata varsa atla
                        }

                        $queueInfo = json_decode($response, true);
                        $totalMessages = $queueInfo['messages'] ?? 0;
                        $unackedMessages = $queueInfo['messages_unacknowledged'] ?? 0;
                        $readyMessages = $totalMessages - $unackedMessages;

                        if ($totalMessages == 0) {
                            continue; // Mesaj yoksa atla
                        }

                        // Mesajları peek et (consume etmeden) - max 1000 mesaj
                        $getMessagesUrl = "{$apiBaseUrl}/queues/{$vhostEncoded}/{$queueName}/get";
                        
                        $postData = json_encode([
                            'count' => min($totalMessages, 1000), // Max 1000 mesaj peek et
                            'ackmode' => 'ack_requeue_true',      // Mesajları requeue et (consume etme)
                            'encoding' => 'auto'
                        ]);

                        $ch = curl_init($getMessagesUrl);
                        curl_setopt($ch, CURLOPT_POST, true);
                        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
                        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
                        curl_setopt($ch, CURLOPT_USERPWD, "{$this->rabbitmqUser}:{$this->rabbitmqPass}");
                        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
                        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
                        
                        $messagesResponse = curl_exec($ch);
                        $messagesHttpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                        curl_close($ch);

                        if ($messagesHttpCode != 200) {
                            continue;
                        }

                        $messages = json_decode($messagesResponse, true);
                        if (!is_array($messages)) {
                            continue;
                        }

                        // Job ID'ye göre filtrele
                        $jobMessageCount = 0;
                        foreach ($messages as $message) {
                            try {
                                // Mesaj içeriğini parse et
                                $payload = $message['payload'] ?? '';
                                
                                // Base64 decode gerekebilir
                                if (isset($message['payload_encoding']) && $message['payload_encoding'] === 'base64') {
                                    $payload = base64_decode($payload);
                                }
                                
                                $messageData = json_decode($payload, true);
                                
                                if (isset($messageData['job_id']) && $messageData['job_id'] == $jobId) {
                                    $jobMessageCount++;
                                }
                            } catch (\Exception $e) {
                                // Mesaj parse edilemezse atla
                                continue;
                            }
                        }

                        if ($jobMessageCount > 0) {
                            // Queue tipine göre kategorize et
                            $queueType = 'processing';
                            if (strpos($queueName, '.completed') !== false) {
                                $queueType = 'completed';
                                $stats['completed'] += $jobMessageCount;
                            } elseif (strpos($queueName, '.error') !== false) {
                                $queueType = 'error';
                                $stats['error'] += $jobMessageCount;
                            } else {
                                // Processing queue - ready mesajlar pending, unacked mesajlar processing
                                // Ancak job_id'ye göre filtreleme yaptığımız için, bu mesajların hepsi job'a ait
                                // Bu durumda ready mesajlar pending, unacked mesajlar processing olarak sayılır
                                // Ama biz toplam job mesaj sayısını biliyoruz, o yüzden orantılı olarak dağıtabiliriz
                                if ($readyMessages > 0 && $totalMessages > 0) {
                                    $stats['pending'] += round(($jobMessageCount * $readyMessages) / $totalMessages);
                                }
                                if ($unackedMessages > 0 && $totalMessages > 0) {
                                    $stats['processing'] += round(($jobMessageCount * $unackedMessages) / $totalMessages);
                                }
                            }

                            $stats['queues'][] = [
                                'queue' => $queueName,
                                'server' => $server['name'],
                                'type' => $queueType,
                                'count' => $jobMessageCount,
                                'total_messages' => $totalMessages,
                                'ready' => $readyMessages,
                                'unacked' => $unackedMessages
                            ];
                        }

                    } catch (\Exception $e) {
                        \Log::error("Queue status check error for {$queueName} on {$server['name']}: " . $e->getMessage());
                        continue;
                    }
                }
            }

            // Job bilgisini al
            $jobData = DB::table('jobs_data')
                ->where('id', $jobId)
                ->first();

            if (!$jobData) {
                return [
                    'success' => false,
                    'message' => 'Job bulunamadı'
                ];
            }

            $totalUrls = $jobData->count ?? 0;
            
            // Progress hesaplaması: Sadece final queue'lara bak (save.queue.completed ve error queue'ları)
            // Çünkü aynı mesaj birden fazla queue'da olabilir (selenium.queue.completed -> save.queue.completed)
            $finalCompleted = 0;
            $finalError = 0;
            
            foreach ($stats['queues'] as $queue) {
                // Sadece save.queue.completed ve error queue'larını say
                if (strpos($queue['queue'], 'save.queue.completed') !== false) {
                    $finalCompleted += $queue['count'];
                } elseif (strpos($queue['queue'], '.error') !== false) {
                    $finalError += $queue['count'];
                }
            }
            
            $processed = $finalCompleted + $finalError;
            $remaining = $totalUrls - $processed;

            return [
                'success' => true,
                'job_id' => $jobId,
                'total_urls' => $totalUrls,
                'stats' => $stats,
                'progress' => [
                    'processed' => $processed,
                    'remaining' => max(0, $remaining),
                    'completed' => $finalCompleted,  // Sadece save.queue.completed
                    'error' => $finalError,          // Tüm error queue'ları
                    'pending' => $stats['pending'],
                    'processing' => $stats['processing'],
                    'percentage' => $totalUrls > 0 ? min(100, round(($processed / $totalUrls) * 100, 2)) : 0
                ]
            ];

        } catch (\Exception $e) {
            \Log::error('Get job queue status error: ' . $e->getMessage());
            return [
                'success' => false,
                'message' => 'Job durumu alınırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Retry scan with prepared data (for Chrome Extension)
     * Hazır data ile tekrar tarama başlatır
     * 
     * @param array $data Prepared job item data
     * @return array
     */
    public function retryScanWithData($data)
    {
        try {
            // Validate required fields
            if (empty($data['url']) || empty($data['company_id']) || empty($data['product_id'])) {
                return [
                    'success' => false,
                    'message' => 'Eksik bilgi: url, company_id veya product_id bulunamadı'
                ];
            }

            // Generate unique data_id if not provided
            if (empty($data['data_id'])) {
                $data['data_id'] = uniqid('', true);
            }

            // 🔥 HER ZAMAN YENİ JOB OLUŞTUR - Mevcut job_id'yi kullanma
            // Eski job_id'yi data'dan kaldır (eğer varsa)
            $originalJobId = $data['job_id'] ?? null;
            unset($data['job_id']);
            
            // Yeni job oluştur
            $jobId = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Tekrar Tarama - ' . ($originalJobId ? 'Job #' . $originalJobId . ' - ' : '') . date('Y-m-d H:i:s'),
                'data' => '{}',
                'status' => 'pending',
                'created_at' => now(),
                'count' => 1,
                'json_path' => '',
                'updated_at' => now()
            ]);

            // Update data with new job_id
            $data['job_id'] = $jobId;

            // Her zaman yeni JSON dosyası oluştur (sadece bu data ile)
            $jobData = [$data];
            $fileName = 'job_data_retry_' . $jobId . '_' . date('Y_m_d_H_i_s') . '.json';
            $jsonPath = 'jobs/' . $fileName;

            // Save JSON file
            $jsonData = json_encode($jobData, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($jsonPath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobId)->update([
                'json_path' => $jsonPath,
                'status' => 'pending',
                'updated_at' => now()
            ]);

            return [
                'success' => true,
                'message' => 'Tekrar tarama başarıyla başlatıldı',
                'job_id' => $jobId,
                'data_id' => $data['data_id'],
                'json_path' => $jsonPath
            ];

        } catch (\Exception $e) {
            \Log::error('Retry scan with data error: ' . $e->getMessage(), [
                'data' => $data,
                'trace' => $e->getTraceAsString()
            ]);
            return [
                'success' => false,
                'message' => 'Tekrar tarama başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Retry bulk scan with prepared data array (for Chrome Extension)
     * Toplu hazır data ile tekrar tarama başlatır
     * 
     * @param array $dataArray Array of prepared job item data
     * @return array
     */
    public function retryBulkScanWithData($dataArray)
    {
        try {
            if (empty($dataArray) || !is_array($dataArray)) {
                return [
                    'success' => false,
                    'message' => 'Geçersiz data array'
                ];
            }

            // Validate all data items and clean job_id
            foreach ($dataArray as $index => $data) {
                if (empty($data['url']) || empty($data['company_id']) || empty($data['product_id'])) {
                    return [
                        'success' => false,
                        'message' => "Eksik bilgi: index {$index} - url, company_id veya product_id bulunamadı"
                    ];
                }

                // Generate unique data_id if not provided
                if (empty($data['data_id'])) {
                    $dataArray[$index]['data_id'] = uniqid('', true);
                }
                
                // 🔥 Eski job_id'yi kaldır (yeni job oluşturulacak)
                unset($dataArray[$index]['job_id']);
            }

            // Create new job
            $jobId = DB::table('jobs_data')->insertGetId([
                'job_name' => 'Toplu Tekrar Tarama - ' . count($dataArray) . ' URL - ' . date('Y-m-d H:i:s'),
                'data' => '{}',
                'status' => 'pending',
                'created_at' => now(),
                'count' => count($dataArray),
                'json_path' => '',
                'updated_at' => now()
            ]);

            // Update all data items with new job_id
            foreach ($dataArray as $index => $data) {
                $dataArray[$index]['job_id'] = $jobId;
            }

            // Create JSON file
            $fileName = 'job_data_retry_bulk_' . $jobId . '_' . date('Y_m_d_H_i_s') . '.json';
            $jsonPath = 'jobs/' . $fileName;

            // Shuffle data to prevent sequential requests
            shuffle($dataArray);

            // Save JSON file
            $jsonData = json_encode($dataArray, JSON_UNESCAPED_UNICODE);
            Storage::disk('public')->put($jsonPath, $jsonData);

            // Update jobs_data table with file path
            DB::table('jobs_data')->where('id', $jobId)->update([
                'json_path' => $jsonPath,
                'updated_at' => now()
            ]);

            return [
                'success' => true,
                'message' => count($dataArray) . ' veri için toplu tekrar tarama başarıyla başlatıldı',
                'job_id' => $jobId,
                'total_items' => count($dataArray),
                'json_path' => $jsonPath
            ];

        } catch (\Exception $e) {
            \Log::error('Retry bulk scan with data error: ' . $e->getMessage(), [
                'data_count' => count($dataArray),
                'trace' => $e->getTraceAsString()
            ]);
            return [
                'success' => false,
                'message' => 'Toplu tekrar tarama başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Quick scan for a single product
     * Belirli bir ürün için hızlı tarama başlatır
     * 
     * @param int $productId
     * @return array
     */
    public function quickScanProduct($productId)
    {
        try {
            // Get all URLs for this product
            $query = "
                SELECT 
                    c.id as company_id,
                    c.screenshot,
                    c.use_proxy,
                    c.proxy_id,
                    cpu.product_id,
                    cpu.url,
                    up.mpn
                FROM companies c
                INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
                INNER JOIN user_products up ON cpu.product_id::bigint = up.id
                WHERE c.deleted = false
                AND up.is_active = 1
                AND up.id = " . (int)$productId . "
            ";

            $urls = DB::select($query);

            if (empty($urls)) {
                return [
                    'success' => false,
                    'message' => 'Bu ürün için URL bulunamadı'
                ];
            }

            // Get attributes for all companies
            $companyIds = array_unique(array_column($urls, 'company_id'));
            $attributes = DB::table('company_attributes as ca')
                ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
                ->whereIn('ca.company_id', $companyIds)
                ->where('ca.value', '!=', '-1')
                ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
                ->get()
                ->groupBy('company_id');

            // Prepare job data
            $jobData = [];
            foreach ($urls as $url) {
                $companyId = $url->company_id;
                $productId = $url->product_id;
                
                // Get attributes for this company
                $companyAttributes = $attributes->get($companyId, collect())->map(function ($attr) use ($companyId) {
                    return [
                        'company_id' => $companyId,
                        'attributes_id' => $attr->attributes_id,
                        'attributes_name' => $attr->attributes_name,
                        'attributes_type' => $attr->attributes_type,
                        'attributes_value' => $attr->attributes_value
                    ];
                })->toArray();

                if (empty($companyAttributes)) {
                    continue; // Skip if no attributes
                }

                $jobData[] = [
                    'data_id' => uniqid('', true),
                    'company_id' => (int)$companyId,
                    'product_id' => (int)$productId,
                    'screenshot' => (bool)$url->screenshot,
                    'use_proxy' => (bool)$url->use_proxy,
                    'proxy_type' => null,
                    'url' => $url->url,
                    'npm' => $url->mpn ?? '',
                    'attributes' => $companyAttributes
                ];
            }

            if (empty($jobData)) {
                return [
                    'success' => false,
                    'message' => 'Bu ürün için tarama yapılacak veri bulunamadı (attributes eksik)'
                ];
            }

            // Use retryBulkScanWithData to create job
            return $this->retryBulkScanWithData($jobData);

        } catch (\Exception $e) {
            \Log::error('Quick scan product error: ' . $e->getMessage(), [
                'product_id' => $productId,
                'trace' => $e->getTraceAsString()
            ]);
            return [
                'success' => false,
                'message' => 'Hızlı tarama başlatılırken hata oluştu: ' . $e->getMessage()
            ];
        }
    }
}
