<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\ScanCronjob;
use App\Services\ScanningService;
use Illuminate\Support\Facades\Log;

class RunScheduledScans extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'scan:run-scheduled';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Çalışma saatindeki planlı taramaları (Chrome Extension) başlatır';

    protected $scanningService;

    public function __construct(ScanningService $scanningService)
    {
        parent::__construct();
        $this->scanningService = $scanningService;
    }

    /**
     * Execute the console command.
     */
    public function handle()
    {
        // Log ekle: Komutun çalıştığını ve o anki saati kaydet
        // Saati açıkça Europe/Istanbul timezone'una göre al (Panelden girilen saat TR saati olduğu için)
        $currentTime = now()->setTimezone('Europe/Istanbul')->format('H:i');
        $serverTime = date('H:i'); // Sunucu sistem saati (muhtemelen UTC)
        
        Log::info("Scheduler Çalıştı. App Time (TR): {$currentTime}, Server Time (UTC): {$serverTime}");

        $this->info('Planlı taramalar kontrol ediliyor...');
        $this->info("Şu anki saat: {$currentTime}");
        
        $cronJobs = ScanCronjob::active()
            ->atTime($currentTime)
            ->with('company')
            ->get();

        if ($cronJobs->isEmpty()) {
            $this->info('Bu saatte çalışacak planlı tarama bulunamadı.');
            return;
        }

        Log::info("{$cronJobs->count()} adet planlı tarama bulundu ve başlatılıyor.");

        $this->info("{$cronJobs->count()} adet planlı tarama bulundu.");

        foreach ($cronJobs as $cronJob) {
            try {
                $this->info("Cron job #{$cronJob->id} çalıştırılıyor...");
                
                if ($cronJob->scan_type === 'all') {
                    $this->info("Genel tarama (Chrome Extension) başlatılıyor...");
                    $result = $this->scanningService->create_job_chrome_extension('all');
                } else {
                    $companyName = $cronJob->company ? $cronJob->company->company_name : 'Bilinmeyen';
                    $this->info("{$companyName} firması için tarama (Chrome Extension) başlatılıyor...");
                    $result = $this->scanningService->create_job_chrome_extension($cronJob->company_id);
                }

                if ($result && isset($result['success']) && $result['success']) {
                    $msg = "✓ Cron job #{$cronJob->id} başarıyla çalıştırıldı.";
                    $this->info($msg);
                    Log::info($msg);
                } else {
                    $msg = "✗ Cron job #{$cronJob->id} çalıştırılırken hata oluştu.";
                    $this->error($msg);
                    Log::error($msg . " Result: " . json_encode($result));
                }
            } catch (\Exception $e) {
                $msg = "✗ Cron job #{$cronJob->id} hatası: " . $e->getMessage();
                $this->error($msg);
                Log::error($msg);
            }
        }

        $this->info('Planlı tarama işlemi tamamlandı.');
    }
}
