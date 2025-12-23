<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\CompanyAttribute;
use App\Models\Attribute;
use Illuminate\Support\Facades\DB;

class ClearAttributes extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'attributes:clear {--confirm : Onay istemeden direkt temizle}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Tüm company_attributes ve attributes kayıtlarını veritabanından temizler';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        // İstatistikleri göster
        $companyAttributesCount = CompanyAttribute::count();
        $attributesCount = Attribute::count();

        $this->info('📊 Mevcut Veri İstatistikleri:');
        $this->line("   - Company Attributes: {$companyAttributesCount}");
        $this->line("   - Attributes: {$attributesCount}");
        $this->newLine();

        // Onay iste (eğer --confirm flag'i yoksa)
        if (!$this->option('confirm')) {
            if (!$this->confirm('⚠️  Tüm company_attributes ve attributes kayıtları silinecek. Devam etmek istediğinize emin misiniz?')) {
                $this->warn('İşlem iptal edildi.');
                return 0;
            }
        }

        try {
            DB::beginTransaction();

            $this->info('🗑️  Temizleme işlemi başlatılıyor...');

            // Önce company_attributes'ı temizle (foreign key constraint nedeniyle)
            $deletedCompanyAttributes = CompanyAttribute::count();
            CompanyAttribute::truncate();
            $this->info("   ✓ {$deletedCompanyAttributes} company_attribute kaydı silindi.");

            // Sonra attributes'ı temizle
            $deletedAttributes = Attribute::count();
            Attribute::truncate();
            $this->info("   ✓ {$deletedAttributes} attribute kaydı silindi.");

            DB::commit();

            $this->newLine();
            $this->info('✅ Temizleme işlemi başarıyla tamamlandı!');
            $this->line("   Toplam silinen kayıt: " . ($deletedCompanyAttributes + $deletedAttributes));

            return 0;
        } catch (\Exception $e) {
            DB::rollBack();
            $this->error('❌ Hata oluştu: ' . $e->getMessage());
            return 1;
        }
    }
}

