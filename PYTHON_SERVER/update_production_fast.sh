#!/bin/bash
# iPriceNew - Hızlı Production Update (sshpass ile)
# Tek komut update

set -e

SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
SERVER_PASS="jzVGsy8T243u"
APP_DIR="/home/iprice/price_analysis_service"

GREEN='\033[0;32m'
BLUE='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🚀 Hızlı Production Update Başlıyor...${NC}"

# rsync ile gönder
echo -e "${GREEN}📤 Dosyalar gönderiliyor...${NC}"
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

# Restart
echo -e "${GREEN}🔄 Restart ediliyor...${NC}"
sshpass -p "$SERVER_PASS" ssh ${SERVER_USER}@${SERVER_IP} "cd ${APP_DIR} && sudo systemctl restart iprice-analysis && sleep 5 && sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep price_analysis"

echo -e "${GREEN}✅ Update tamamlandı!${NC}"
echo -e "Test: curl http://74.234.27.174:8000/health"

