<?php

namespace App\Console\Commands;

use App\Services\ChromeCompletedQueueService;
use Illuminate\Console\Command;

class ConsumeChromeCompletedQueue extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'chrome:consume-completed';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Consume messages from chrome.queue.completed and save to database';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $this->info('Chrome Completed Queue Consumer başlatılıyor...');

        try {
            $service = new ChromeCompletedQueueService();
            $service->consume();
        } catch (\Exception $e) {
            $this->error('Hata: ' . $e->getMessage());
            \Log::error('Chrome Completed Queue Consumer hatası', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            return 1;
        }

        return 0;
    }
}

