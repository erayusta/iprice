<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Services\XmlParserService;
use Illuminate\Support\Facades\Log;

class ImportXmlProducts extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'xml:import {--url= : XML feed URL (opsiyonel, env\'den alınır)}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'XML feed\'den ürünleri otomatik olarak içe aktarır';

    protected $xmlParserService;

    public function __construct(XmlParserService $xmlParserService)
    {
        parent::__construct();
        $this->xmlParserService = $xmlParserService;
    }

    /**
     * Execute the console command.
     */
    public function handle()
    {
        // XML URL'ini al (önce option, sonra env, sonra default)
        $xmlUrl = $this->option('url') 
            ?: env('XML_IMPORT_URL') 
            ?: 'https://www.pt.com.tr/wp-content/uploads/wpwoof-feed/xml/iprice.xml';

        if (empty($xmlUrl)) {
            $this->error('XML URL belirtilmedi ve env değişkeni bulunamadı.');
            $this->info('Kullanım: php artisan xml:import --url=https://example.com/feed.xml');
            $this->info('Veya .env dosyasına XML_IMPORT_URL ekleyin.');
            return Command::FAILURE;
        }

        $this->info("XML Import başlatılıyor...");
        $this->info("URL: {$xmlUrl}");
        
        try {
            Log::info('XML Import cron job başlatıldı', ['url' => $xmlUrl]);
            
            $result = $this->xmlParserService->parseAndImportFromUrl($xmlUrl);
            
            if ($result['success'] ?? false) {
                $summary = $result['summary'] ?? [];
                $this->info('✓ XML Import başarıyla tamamlandı!');
                $this->info("  - Toplam: {$summary['total']} ürün");
                $this->info("  - Yeni: {$summary['inserted']} ürün");
                $this->info("  - Güncellendi: {$summary['updated']} ürün");
                $this->info("  - Atlandı: {$summary['skipped']} ürün");
                $this->info("  - Deaktif edildi: {$summary['deactivatedCount']} ürün");
                
                Log::info('XML Import cron job tamamlandı', [
                    'success' => true,
                    'summary' => $summary
                ]);
                
                return Command::SUCCESS;
            } else {
                $message = $result['message'] ?? 'Bilinmeyen hata';
                $this->error("✗ XML Import başarısız: {$message}");
                
                Log::error('XML Import cron job başarısız', [
                    'message' => $message,
                    'result' => $result
                ]);
                
                return Command::FAILURE;
            }
        } catch (\Exception $e) {
            $this->error("✗ XML Import sırasında hata oluştu: " . $e->getMessage());
            
            Log::error('XML Import cron job hatası', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            return Command::FAILURE;
        }
    }
}













