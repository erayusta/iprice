#!/bin/bash
# iPriceNew - Production Rollback Script
# Bir önceki versiyona geri dön

set -e

SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
SERVER_PASS="jzVGsy8T243u"
APP_DIR="/home/iprice/price_analysis_service"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  Production Rollback${NC}"
echo -e "${RED}Bu işlem son yedeklenen versiyona geri döner!${NC}"
echo ""

read -p "Devam etmek istiyor musun? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}İptal edildi.${NC}"
    exit 1
fi

echo -e "${GREEN}🔄 Rollback başlıyor...${NC}"

sshpass -p "$SERVER_PASS" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/iprice

# Son backup'ı bul
LAST_BACKUP=$(ls -td price_analysis_service_backup_* 2>/dev/null | head -1)

if [ -z "$LAST_BACKUP" ]; then
    echo "❌ Backup bulunamadı!"
    exit 1
fi

echo "📦 Backup bulundu: $LAST_BACKUP"

# Mevcut versiyonu yedekle
sudo cp -r price_analysis_service price_analysis_service_current_$(date +%Y%m%d_%H%M%S)

# Backup'tan geri yükle
sudo rm -rf price_analysis_service
sudo cp -r $LAST_BACKUP price_analysis_service
sudo chown -R iprice:iprice price_analysis_service

# Restart
cd price_analysis_service
sudo systemctl restart iprice-analysis

echo "⏳ 10 saniye bekleniyor..."
sleep 10

echo ""
echo "📊 Container Durumu:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}"

ENDSSH

echo -e "${GREEN}✅ Rollback tamamlandı!${NC}"

