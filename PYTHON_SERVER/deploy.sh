#!/bin/bash
# iPriceNew - Hızlı Production Deploy
# TÜM değişiklikleri sunucuya atar ve günceller

set -e

SERVER_IP="10.20.50.16"
SERVER_USER="iprice_admin"
APP_DIR="/var/www/iprice/python_server"

GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   iPriceNew Production Deploy        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# 1. Dosyaları gönder
echo -e "${GREEN}[1/4]${NC} 📤 Dosyalar gönderiliyor..."
rsync -az --delete \
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
    -e "sshpass -p 'PtiPrice2025.*' ssh -o StrictHostKeyChecking=no" \
    ./ ${SERVER_USER}@${SERVER_IP}:${APP_DIR}/ > /dev/null 2>&1

echo -e "${GREEN}      ✓ Dosyalar gönderildi${NC}"

# 2. Sunucuda güncelleme
echo -e "${GREEN}[2/4]${NC} 🔄 Sunucuda güncelleniyor..."
sshpass -p 'PtiPrice2025.*' ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH' > /dev/null 2>&1
cd /var/www/iprice/python_server
mkdir -p screenshots logs data
chmod -R 755 screenshots
docker-compose down
docker-compose build --no-cache
docker-compose up -d
ENDSSH

echo -e "${GREEN}      ✓ Servisler güncellendi${NC}"

# 3. Bekle
echo -e "${GREEN}[3/4]${NC} ⏳ Servisler başlatılıyor..."
sleep 15

# 4. Kontrol
echo -e "${GREEN}[4/4]${NC} 🔍 Durum kontrol ediliyor..."
sshpass -p 'PtiPrice2025.*' ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /var/www/iprice/python_server
docker ps --format "table {{.Names}}\t{{.Status}}" | head -10
ENDSSH

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ DEPLOYMENT TAMAMLANDI!          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}🔗 Test:${NC} curl http://${SERVER_IP}:8000/health"
echo -e "${YELLOW}📊 Logs:${NC} ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker-compose logs -f'"
echo ""

