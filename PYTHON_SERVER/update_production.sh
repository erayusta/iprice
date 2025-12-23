#!/bin/bash
# iPriceNew - Production Update Script
# Sadece değişiklikleri sunucuya gönderir ve uygulamayı restart eder

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

# Sunucu bilgileri
SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
SERVER_PASS="jzVGsy8T243u"
APP_DIR="/home/iprice/price_analysis_service"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  iPriceNew Production Update${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Git kontrolü (opsiyonel)
if [ -d ".git" ]; then
    echo -e "${YELLOW}📋 Git durumu:${NC}"
    git status --short
    echo ""
    read -p "Devam etmek istiyor musun? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}İptal edildi.${NC}"
        exit 1
    fi
fi

# 2. rsync ile sadece değişiklikleri gönder
echo -e "${GREEN}📤 Değişiklikler sunucuya gönderiliyor...${NC}"
rsync -avz --delete \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'screenshots/*' \
    --exclude 'logs/*' \
    --exclude 'data/*' \
    --exclude '.env' \
    --exclude 'node_modules' \
    --exclude 'celerybeat-schedule' \
    --exclude '.DS_Store' \
    --exclude '*.log' \
    ./ ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dosyalar güncellendi${NC}"
else
    echo -e "${RED}❌ Dosya transferi başarısız!${NC}"
    exit 1
fi

# 3. Sunucuda restart
echo -e "${GREEN}🔄 Sunucuda servis yeniden başlatılıyor...${NC}"
sshpass -p "$SERVER_PASS" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/iprice/price_analysis_service

# Systemd servisini kullanarak restart
sudo systemctl restart iprice-analysis

echo "⏳ 10 saniye bekleniyor..."
sleep 10

# Durum kontrolü
echo ""
echo "📊 Container Durumu:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}" | grep price_analysis

echo ""
echo "✅ Servis Durumu:"
sudo systemctl status iprice-analysis --no-pager -l | head -15

ENDSSH

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ UPDATE TAMAMLANDI!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}🔗 Test için:${NC}"
echo -e "  curl http://74.234.27.174:8000/health"
echo ""
echo -e "${BLUE}📋 Logları görmek için:${NC}"
echo -e "  ssh ${SERVER_USER}@${SERVER_IP}"
echo -e "  sudo docker-compose logs -f"
echo ""

