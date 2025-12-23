#!/bin/bash
# iPriceNew - Otomatik Deployment Script (sshpass ile)
# sshpass kurulu olmalı: brew install hudochenkov/sshpass/sshpass (macOS)
# veya: sudo apt install sshpass (Linux)

set -e

# Sunucu bilgileri
SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
SERVER_PASS="jzVGsy8T243u"
APP_DIR="/home/iprice/price_analysis_service"

# Renkler
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 iPriceNew Auto Deployment (with password)${NC}"

# sshpass kontrolü
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️ sshpass kurulu değil!${NC}"
    echo -e "Kurulum için:"
    echo -e "  macOS: ${BLUE}brew install hudochenkov/sshpass/sshpass${NC}"
    echo -e "  Linux: ${BLUE}sudo apt install sshpass${NC}"
    exit 1
fi

# 1. Dosyaları sıkıştır
echo -e "${GREEN}📦 Sıkıştırılıyor...${NC}"
tar -czf /tmp/price_analysis.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='screenshots/*' \
    --exclude='logs/*' \
    --exclude='data/*' \
    --exclude='.env' \
    --exclude='node_modules' \
    --exclude='celerybeat-schedule' \
    .

# 2. Sunucuya gönder
echo -e "${GREEN}📤 Sunucuya gönderiliyor...${NC}"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no /tmp/price_analysis.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no deploy_to_ubuntu.sh ${SERVER_USER}@${SERVER_IP}:/tmp/
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no iprice-analysis.service ${SERVER_USER}@${SERVER_IP}:/tmp/

# 3. Sunucuda deployment
echo -e "${GREEN}🚀 Deployment başlatılıyor...${NC}"
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e
APP_DIR="/home/iprice/price_analysis_service"

# Docker kurulumu (eğer yoksa)
if ! command -v docker &> /dev/null; then
    chmod +x /tmp/deploy_to_ubuntu.sh
    sudo /tmp/deploy_to_ubuntu.sh
fi

# Uygulama dizini
mkdir -p $APP_DIR
cd $APP_DIR

# Dosyaları aç
tar -xzf /tmp/price_analysis.tar.gz -C $APP_DIR

# Dizinler
mkdir -p logs screenshots data app/proxies

# .env
if [ ! -f ".env" ]; then
    cp azure.env.example .env
fi

# Docker
docker-compose down || true
docker-compose up -d --build

# Systemd
sudo cp /tmp/iprice-analysis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iprice-analysis
sudo systemctl restart iprice-analysis

echo "✅ Deployment tamamlandı!"
ENDSSH

echo -e "${GREEN}✅ Başarılı!${NC}"
rm -f /tmp/price_analysis.tar.gz

