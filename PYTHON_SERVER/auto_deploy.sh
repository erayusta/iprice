#!/bin/bash
# iPriceNew - Otomatik Deployment Script
# Local bilgisayardan çalıştırın

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
DOMAIN="panel.iprice.com.tr"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  iPriceNew Auto Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Dosyaları sıkıştır
echo -e "${GREEN}📦 Dosyalar sıkıştırılıyor...${NC}"
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

echo -e "${GREEN}✅ Dosyalar sıkıştırıldı: $(du -h /tmp/price_analysis.tar.gz | cut -f1)${NC}"

# 2. Sunucuya gönder
echo -e "${GREEN}📤 Dosyalar sunucuya gönderiliyor...${NC}"
scp -o StrictHostKeyChecking=no /tmp/price_analysis.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

# 3. Deploy script'ini gönder
echo -e "${GREEN}📤 Deploy script gönderiliyor...${NC}"
scp -o StrictHostKeyChecking=no deploy_to_ubuntu.sh ${SERVER_USER}@${SERVER_IP}:/tmp/
scp -o StrictHostKeyChecking=no iprice-analysis.service ${SERVER_USER}@${SERVER_IP}:/tmp/

# 4. Sunucuda kurulum yap
echo -e "${GREEN}🚀 Sunucuda kurulum başlatılıyor...${NC}"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/home/iprice/price_analysis_service"

echo -e "${GREEN}📦 1. Temel paketler kuruluyor...${NC}"
# Deploy script'i çalıştır (eğer Docker yoksa)
if ! command -v docker &> /dev/null; then
    chmod +x /tmp/deploy_to_ubuntu.sh
    sudo /tmp/deploy_to_ubuntu.sh
else
    echo -e "${YELLOW}⚠️ Docker zaten kurulu${NC}"
fi

echo -e "${GREEN}📁 2. Uygulama dizini hazırlanıyor...${NC}"
# Backup oluştur (eğer varsa)
if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Mevcut uygulama yedekleniyor...${NC}"
    sudo cp -r $APP_DIR ${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S) || true
    sudo rm -rf $APP_DIR
fi

# Yeni dizin oluştur
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${GREEN}📦 3. Dosyalar açılıyor...${NC}"
tar -xzf /tmp/price_analysis.tar.gz -C $APP_DIR

echo -e "${GREEN}📁 4. Gerekli dizinler oluşturuluyor...${NC}"
mkdir -p logs screenshots data app/proxies
chmod -R 755 logs screenshots data

echo -e "${GREEN}📝 5. .env dosyası kontrol ediliyor...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ .env dosyası bulunamadı, azure.env.example'dan kopyalanıyor...${NC}"
    cp azure.env.example .env
    echo -e "${RED}⚠️ ÖNEMLI: .env dosyasını düzenlemeyi unutmayın!${NC}"
    echo -e "${YELLOW}Komut: nano $APP_DIR/.env${NC}"
fi

echo -e "${GREEN}🐳 6. Docker Compose ile başlatılıyor...${NC}"
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

echo -e "${GREEN}⚙️ 7. Systemd servisi yapılandırılıyor...${NC}"
sudo cp /tmp/iprice-analysis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iprice-analysis.service
sudo systemctl start iprice-analysis.service

echo -e "${GREEN}🔥 8. Firewall yapılandırılıyor...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp
    sudo ufw allow 8000/tcp  # API portu
    sudo ufw --force enable
    echo -e "${GREEN}✅ Firewall yapılandırıldı${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ DEPLOYMENT TAMAMLANDI!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📊 Durum Kontrolleri:${NC}"
echo -e "  • Docker Containers: ${GREEN}$(docker ps --format '{{.Names}}' | wc -l)${NC} container çalışıyor"
echo -e "  • Systemd Service: ${GREEN}$(sudo systemctl is-active iprice-analysis)${NC}"
echo ""
echo -e "${YELLOW}🔗 Erişim:${NC}"
echo -e "  • API: ${BLUE}http://74.234.27.174:8000${NC}"
echo -e "  • Health: ${BLUE}http://74.234.27.174:8000/health${NC}"
echo ""
echo -e "${YELLOW}📝 Sonraki Adımlar:${NC}"
echo -e "  1. .env dosyasını düzenle: ${BLUE}nano $APP_DIR/.env${NC}"
echo -e "  2. Servisi yeniden başlat: ${BLUE}sudo systemctl restart iprice-analysis${NC}"
echo -e "  3. Logları izle: ${BLUE}docker-compose logs -f${NC}"
echo ""
echo -e "${YELLOW}🔍 Kontrol Komutları:${NC}"
echo -e "  • Containers: ${BLUE}docker ps${NC}"
echo -e "  • Logs: ${BLUE}docker-compose logs -f${NC}"
echo -e "  • Service: ${BLUE}sudo systemctl status iprice-analysis${NC}"
echo -e "  • API Test: ${BLUE}curl http://localhost:8000/health${NC}"
echo ""
echo -e "${GREEN}Tebrikler! Deployment başarılı! 🎉${NC}"

ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment tamamlandı!${NC}"
echo ""
echo -e "${YELLOW}⚠️ Sonraki adımlar için sunucuya bağlan:${NC}"
echo -e "${BLUE}ssh ${SERVER_USER}@${SERVER_IP}${NC}"
echo ""

# Temizlik
rm -f /tmp/price_analysis.tar.gz

echo -e "${GREEN}🎉 Başarıyla tamamlandı!${NC}"

