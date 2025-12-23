# Cron Job Sistemi Kurulum ve Kullanım Kılavuzu

## 🚀 Kurulum

### 1. Development Ortamı (Önerilen)

Scheduler'ı çalıştırmak için terminal'de şu komutu çalıştırın:

```bash
cd /Users/onurerdogan/Desktop/PROJE_IPRICE/PANEL
php artisan schedule:work
```

Bu komut arka planda çalışır ve her dakika planlı taramaları kontrol eder.

### 2. Production Ortamı (Sistem Cron'u)

Production ortamında sistem cron'u kullanmanız önerilir.

#### macOS/Linux için:

1. Crontab dosyasını açın:
```bash
crontab -e
```

2. Şu satırı ekleyin:
```bash
* * * * * cd /Users/onurerdogan/Desktop/PROJE_IPRICE/PANEL && php artisan schedule:run >> /dev/null 2>&1
```

3. Kaydedin ve çıkın (`:wq` vi/vim editöründe)

#### Cron'un çalışıp çalışmadığını kontrol etmek için:
```bash
crontab -l
```

## 📋 Kullanım

### Cron Job Oluşturma

1. Frontend'te `/dashboard/scanning` sayfasına gidin
2. "Planlı Taramalar (Cron Jobs)" bölümünde "Cron Job Ekle" butonuna tıklayın
3. Formu doldurun:
   - **Saat**: Taramanın çalışacağı saat (HH:MM formatında, örn: 14:30)
   - **Tarama Türü**: 
     - **Genel Tarama**: Tüm firmaları tarar
     - **Firma Bazlı Tarama**: Seçilen firmayı tarar
   - **Firma**: (Firma Bazlı seçilirse) Taranacak firmayı seçin
   - **Aktif**: Cron job'ın aktif olup olmayacağı

### Cron Job Yönetimi

- **Düzenleme**: Cron job kartındaki ✏️ düzenleme ikonuna tıklayın
- **Aktif/Pasif**: ⏸️ veya ▶️ ikonuna tıklayarak geçici olarak durdurun/başlatın
- **Silme**: 🗑️ silme ikonuna tıklayarak kalıcı olarak silin

## 🔧 Manuel Test

Scheduler'ı manuel olarak test etmek için:

```bash
# Planlı taramaları hemen çalıştır
php artisan scan:run-scheduled

# Scheduler listesini görüntüle
php artisan schedule:list

# Tek seferlik test run (scheduler'ı çalıştır)
php artisan schedule:run
```

## 📊 Nasıl Çalışır?

1. Her dakika Laravel Scheduler çalışır (`schedule:work` veya sistem cron'u ile)
2. Scheduler `scan:run-scheduled` komutunu çağırır
3. Komut, veritabanından **aktif** ve **şu anki saate eşit** cron job'ları çeker
4. Her cron job için `startQuickScan()` fonksiyonu çalıştırılır
5. Tarama başlatılır ve sonuçlar "İşlem Geçmişi" bölümünde görüntülenir

## ⚠️ Önemli Notlar

- Cron job'lar **dakika hassasiyetinde** çalışır (örn: 14:30)
- Saniye bilgisi dikkate alınmaz
- Scheduler her dakika çalıştığı için, cron job'unuz belirttiğiniz dakikada çalışır
- Pasif cron job'lar çalıştırılmaz
- Aynı saatte birden fazla cron job olabilir, hepsi sırayla çalıştırılır

## 🐛 Sorun Giderme

### Cron job çalışmıyor:

1. **Scheduler çalışıyor mu kontrol edin:**
   ```bash
   php artisan schedule:work
   ```

2. **Cron job aktif mi kontrol edin:**
   - Frontend'te cron job'un "Aktif" badge'i yeşil olmalı

3. **Saat doğru mu kontrol edin:**
   - Sistem saati ile cron job saati eşleşmeli
   - `php artisan scan:run-scheduled` komutu ile şu anki saati görebilirsiniz

4. **Log'ları kontrol edin:**
   ```bash
   tail -f storage/logs/laravel.log
   ```

5. **Manuel test:**
   ```bash
   php artisan scan:run-scheduled
   ```

### Scheduler durdurmak için:

Development'ta `schedule:work` çalışıyorsa, terminal'de `Ctrl + C` ile durdurun.

Production'da sistem cron'u çalışıyorsa:
```bash
crontab -e
# İlgili satırı silin veya başına # koyun
```

## 📁 İlgili Dosyalar

- **Command**: `app/Console/Commands/RunScheduledScans.php`
- **Model**: `app/Models/ScanCronjob.php`
- **Controller**: `app/Http/Controllers/Api/CronJobController.php`
- **Routes**: `routes/api.php` (cron-jobs endpoints)
- **Scheduler**: `routes/console.php` (scheduler tanımı)
- **Frontend**: `FRONT/pages/dashboard/scanning.vue`

---

## 📦 XML Import Cron Job

XML import işlemi otomatik olarak **her gün saat 03:00'da** çalışır.

### Kurulum

1. `.env` dosyasına XML feed URL'ini ekleyin:
```bash
XML_IMPORT_URL=https://www.pt.com.tr/wp-content/uploads/wpwoof-feed/xml/iprice.xml
```

2. Scheduler'ın çalıştığından emin olun (yukarıdaki kurulum adımlarına bakın)

### Manuel Çalıştırma

XML import'u manuel olarak çalıştırmak için:

```bash
# Default URL ile (env'den alır)
php artisan xml:import

# Özel URL ile
php artisan xml:import --url=https://example.com/feed.xml
```

### Ayarlar

- **Zaman**: Her gün saat 03:00 (Türkiye saati)
- **Timezone**: Europe/Istanbul
- **Overlap Önleme**: Aktif (aynı anda iki import çalışmaz)
- **Background Mode**: Aktif (arka planda çalışır)

### Loglar

XML import logları şu dosyada tutulur:
```bash
tail -f storage/logs/laravel.log | grep "XML Import"
```

### İlgili Dosyalar

- **Command**: `app/Console/Commands/ImportXmlProducts.php`
- **Service**: `app/Services/XmlParserService.php`
- **Scheduler**: `app/Providers/AppServiceProvider.php`

## 🎯 Örnek Kullanım

### Senaryo 1: Her gün saat 10:00'da genel tarama

1. Cron Job Ekle
2. Saat: `10:00`
3. Tarama Türü: `Genel Tarama`
4. Aktif: ✓

### Senaryo 2: Her gün saat 14:30'da Trendyol taraması

1. Cron Job Ekle
2. Saat: `14:30`
3. Tarama Türü: `Firma Bazlı Tarama`
4. Firma: `Trendyol`
5. Aktif: ✓

### Senaryo 3: Birden fazla tarama

```
09:00 - Genel Tarama (Aktif)
12:00 - Hepsiburada Taraması (Aktif)
15:00 - Trendyol Taraması (Aktif)
18:00 - N11 Taraması (Pasif - çalışmaz)
21:00 - Genel Tarama (Aktif)
```

## 🔄 Güncelleme

Scheduler'ı güncellemek için:

```bash
# Değişiklikleri yaptıktan sonra
cd /Users/onurerdogan/Desktop/PROJE_IPRICE/PANEL

# Cache'i temizle
php artisan cache:clear
php artisan config:clear

# Scheduler'ı yeniden başlat
# (Ctrl+C ile durdurup tekrar başlatın veya cron'u reload edin)
```

