#!/bin/bash

echo "🔍 Chrome Completed Queue Monitor Başlatıldı..."
echo "================================================"
echo ""

# Başlangıç durumu
echo "📊 Başlangıç Durumu:"
docker exec laravel_app php artisan tinker --execute="
echo 'Toplam ProductAttributeValue: ' . \App\Models\ProductAttributeValue::count();
echo PHP_EOL;
echo 'Toplam ProductAttributeValueSummary: ' . \App\Models\ProductAttributeValueSummary::count();
echo PHP_EOL;
echo 'En son job_id: ' . (\App\Models\ProductAttributeValue::max('job_id') ?? 'yok');
echo PHP_EOL;
"

echo ""
echo "📝 Son 5 log satırı:"
docker exec laravel_app tail -5 storage/logs/laravel.log | grep -E "Chrome Completed Queue|ProductAttributeValue" || echo "Henüz log yok"

echo ""
echo "⏳ Test verisi bekleniyor... (Ctrl+C ile çıkış)"
echo ""

# Canlı log takibi
docker exec laravel_app tail -f storage/logs/laravel.log 2>&1 | while IFS= read -r line; do
    if echo "$line" | grep -qE "Chrome Completed Queue|ProductAttributeValue|ProductAttributeValueSummary|error|ERROR|Exception|commit|rollback"; then
        echo "[$(date +'%H:%M:%S')] $line"
        
        # Eğer "Veri kaydı başarılı" mesajı görürsek, veritabanını kontrol et
        if echo "$line" | grep -q "Veri kaydı başarılı"; then
            job_id=$(echo "$line" | grep -oP 'job_id":\K\d+')
            if [ ! -z "$job_id" ]; then
                echo ""
                echo "✅ Kayıt başarılı mesajı alındı - Job ID: $job_id"
                echo "🔍 Veritabanı kontrol ediliyor..."
                docker exec laravel_app php artisan tinker --execute="
                \$count = \App\Models\ProductAttributeValue::where('job_id', $job_id)->count();
                echo 'Job $job_id için ProductAttributeValue kayıt sayısı: ' . \$count;
                echo PHP_EOL;
                \$summaryCount = \App\Models\ProductAttributeValueSummary::where('job_id', $job_id)->count();
                echo 'Job $job_id için ProductAttributeValueSummary kayıt sayısı: ' . \$summaryCount;
                echo PHP_EOL;
                if (\$count == 0) {
                    echo '⚠️ UYARI: Job $job_id için hiç kayıt yok!';
                }
                "
                echo ""
            fi
        fi
        
        # Hata mesajı görürsek detaylı bilgi ver
        if echo "$line" | grep -qE "error|ERROR|Exception"; then
            echo ""
            echo "❌ HATA TESPİT EDİLDİ!"
            echo "Detaylı loglar:"
            docker exec laravel_app tail -20 storage/logs/laravel.log | grep -A 10 -B 5 "error\|ERROR\|Exception" | tail -15
            echo ""
        fi
    fi
done

