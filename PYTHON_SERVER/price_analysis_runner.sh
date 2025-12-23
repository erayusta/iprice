#!/bin/bash
# price_analysis_runner.sh

# Log dizini oluştur
LOG_DIR="/var/log/price_analysis"
mkdir -p $LOG_DIR

# Tarih formatını ayarla
DATE=$(date +%Y%m%d_%H%M)
LOG_FILE="$LOG_DIR/price_analysis_$DATE.log"

# Log başlangıç
echo "Script başlatıldı - $(date)" >> $LOG_FILE

# Scripti çalıştır
echo "Docker container içinde Python script başlatılıyor..." >> $LOG_FILE
docker exec price_analysis_service-app-1 python3 /app/app/main.py >> $LOG_FILE 2>&1

# Çıkış kodunu kontrol et
if [ $? -ne 0 ]; then
    echo "Script hatası - $(date)" >> $LOG_FILE
    LAST_LOGS=$(tail -n 20 $LOG_FILE)
    echo "Script failed. Son 20 satır log:"
    echo "$LAST_LOGS"
else
    echo "Script başarıyla tamamlandı - $(date)" >> $LOG_FILE
fi

# 30 günden eski logları temizle
find $LOG_DIR -name "price_analysis_*.log" -mtime +30 -exec rm {} \;
