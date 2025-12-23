<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Company;
use App\Models\UserProduct;
use App\Models\CompanyProductsUrl;
use Illuminate\Support\Facades\DB;

class ProcessProductUrls extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'process:product-urls {json_file_path}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Product URL verilerini işleyerek company_products_urls tablosuna ekler';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $jsonFilePath = $this->argument('json_file_path');
        
        if (!file_exists($jsonFilePath)) {
            $this->error("JSON dosyası bulunamadı: {$jsonFilePath}");
            return 1;
        }

        $this->info("Product URL verileri işleniyor...");
        
        // JSON dosyasını oku
        $jsonContent = file_get_contents($jsonFilePath);
        $data = json_decode($jsonContent, true);
        
        if (!$data || !isset($data['product_url'])) {
            $this->error("Geçersiz JSON formatı veya 'product_url' anahtarı bulunamadı");
            return 1;
        }

        $productUrls = $data['product_url'];
        $this->info("Toplam " . count($productUrls) . " product URL bulundu");

        // Tüm verileri önceden yükle
        $companies = $this->loadCompanies();
        $userProducts = $this->loadUserProducts();
        $existingRecords = $this->loadExistingRecords();
        
        $this->info("Toplam " . count($companies) . " company bulundu");
        $this->info("Toplam " . count($userProducts) . " user product bulundu");
        $this->info("Toplam " . count($existingRecords) . " mevcut kayıt bulundu");

        $stats = [
            'processed' => 0,
            'success' => 0,
            'failed' => 0,
            'skipped' => 0
        ];

        $batchData = [];
        $batchSize = 1000;

        $progressBar = $this->output->createProgressBar(count($productUrls));
        $progressBar->start();

        foreach ($productUrls as $productUrl) {
            $stats['processed']++;
            
            try {
                $result = $this->processProductUrlOptimized($productUrl, $companies, $userProducts, $existingRecords);
                
                if ($result['status'] === 'success') {
                    $batchData[] = $result['data'];
                    $stats['success']++;
                } elseif ($result['status'] === 'skipped') {
                    $stats['skipped']++;
                } else {
                    $stats['failed']++;
                }
                
                // Batch insert
                if (count($batchData) >= $batchSize) {
                    $this->insertBatch($batchData);
                    $batchData = [];
                }
                
            } catch (\Exception $e) {
                $stats['failed']++;
            }
            
            $progressBar->advance();
        }

        // Kalan verileri ekle
        if (!empty($batchData)) {
            $this->insertBatch($batchData);
        }

        $progressBar->finish();
        $this->newLine(2);

        // Sonuçları göster
        $this->info("İşlem tamamlandı!");
        $this->table(
            ['Durum', 'Sayı'],
            [
                ['İşlenen', $stats['processed']],
                ['Başarılı', $stats['success']],
                ['Atlanan', $stats['skipped']],
                ['Başarısız', $stats['failed']]
            ]
        );

        return 0;
    }

    /**
     * Company verilerini yükle
     */
    private function loadCompanies()
    {
        $companies = Company::whereNotNull('url')
            ->where('url', '!=', '')
            ->get()
            ->keyBy(function ($company) {
                return $this->extractDomain($company->url);
            });

        return $companies;
    }

    /**
     * User products verilerini yükle
     */
    private function loadUserProducts()
    {
        return UserProduct::whereNotNull('mpn')
            ->where('mpn', '!=', '')
            ->get()
            ->keyBy('mpn');
    }

    /**
     * Mevcut kayıtları yükle
     */
    private function loadExistingRecords()
    {
        return CompanyProductsUrl::all()
            ->map(function ($record) {
                return $record->company_id . '|' . $record->product_id . '|' . $record->url;
            })
            ->toArray();
    }

    /**
     * Batch insert
     */
    private function insertBatch($batchData)
    {
        if (empty($batchData)) {
            return;
        }

        try {
            DB::table('company_products_urls')->insert($batchData);
        } catch (\Exception $e) {
            $this->warn("Batch insert hatası: " . $e->getMessage());
        }
    }

    /**
     * URL'den domain çıkar
     */
    private function extractDomain($url)
    {
        if (empty($url)) {
            return null;
        }

        $parsedUrl = parse_url($url);
        if (!isset($parsedUrl['host'])) {
            return null;
        }

        $host = $parsedUrl['host'];
        
        // www. prefix'ini kaldır
        if (strpos($host, 'www.') === 0) {
            $host = substr($host, 4);
        }

        return $host;
    }

    /**
     * Optimize edilmiş product URL işleme
     */
    private function processProductUrlOptimized($productUrl, $companies, $userProducts, $existingRecords)
    {
        // URL'den domain çıkar
        $domain = $this->extractDomain($productUrl['url']);
        
        if (!$domain) {
            return [
                'status' => 'failed',
                'message' => "Geçersiz URL: " . $productUrl['url']
            ];
        }

        // Company'yi bul
        $company = $companies->get($domain);
        
        if (!$company) {
            return [
                'status' => 'failed',
                'message' => "Domain için company bulunamadı: " . $domain
            ];
        }

        // MPN ile user product bul
        $userProduct = $userProducts->get($productUrl['mpn']);
        
        if (!$userProduct) {
            return [
                'status' => 'failed',
                'message' => "MPN için user product bulunamadı: " . $productUrl['mpn']
            ];
        }

        // Duplicate kontrolü
        $recordKey = $company->id . '|' . $userProduct->id . '|' . $productUrl['url'];
        if (in_array($recordKey, $existingRecords)) {
            return [
                'status' => 'skipped',
                'message' => "Bu kayıt zaten mevcut"
            ];
        }

        // Batch insert için veri hazırla
        return [
            'status' => 'success',
            'data' => [
                'company_id' => $company->id,
                'product_id' => $userProduct->id,
                'url' => $productUrl['url'],
                'created_at' => now(),
                'updated_at' => now()
            ]
        ];
    }
}
