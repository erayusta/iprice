#!/bin/bash
# iPriceNew - Full Production Update (Docker rebuild ile)
# Dockerfile veya requirements.txt değiştiğinde kullan

set -e

SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
SERVER_PASS="jzVGsy8T243u"
APP_DIR="/home/iprice/price_analysis_service"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔧 Full Production Update (Docker Rebuild)${NC}"
echo -e "${YELLOW}⚠️  Bu işlem biraz uzun sürebilir (5-10 dakika)${NC}"
echo ""

# rsync ile gönder
echo -e "${GREEN}📤 Tüm dosyalar gönderiliyor...${NC}"
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
    ./ ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/

# Docker rebuild
echo -e "${GREEN}🐳 Docker rebuild başlıyor...${NC}"
sshpass -p "$SERVER_PASS" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/iprice/price_analysis_service

# Down
sudo docker-compose down

# Build (no cache)
sudo docker-compose build --no-cache

# Up
sudo docker-compose up -d

echo "⏳ Container'lar başlatılıyor, 30 saniye bekleniyor..."
sleep 30

# Durum
echo ""
echo "📊 Container Durumu:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Loglar:"
sudo docker-compose logs --tail=20

ENDSSH

echo ""
echo -e "${GREEN}✅ Full Update tamamlandı!${NC}"
echo -e "Test: curl http://74.234.27.174:8000/health"

