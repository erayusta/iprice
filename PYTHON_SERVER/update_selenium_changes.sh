#!/bin/bash
# iPriceNew - Selenium Parser Timeout ve Screenshot Güncellemesi
# Kullanım: ./update_selenium_changes.sh

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
CYAN='\033[0;96m'
NC='\033[0m'

# Sunucu bilgileri
SERVER_IP="74.234.27.174"
SERVER_USER="iprice"
APP_DIR="/home/iprice/price_analysis_service"

echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Selenium Parser Timeout & Screenshot Update ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Değişiklik özeti
echo -e "${BLUE}📋 Güncellenecek Değişiklikler:${NC}"
echo -e "  ${GREEN}✓${NC} Timeout süreleri artırıldı (30→60, 10→20 saniye)"
echo -e "  ${GREEN}✓${NC} Retry mekanizması eklendi (3 deneme)"
echo -e "  ${GREEN}✓${NC} Screenshot alma özelliği entegre edildi"
echo -e "  ${GREEN}✓${NC} Cloudflare bypass optimize edildi"
echo ""

# Onay
read -p "$(echo -e ${YELLOW}Devam etmek istiyor musunuz? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ İptal edildi.${NC}"
    exit 1
fi

# 1. Git durumu göster
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  1/6: Git Durumu Kontrol Ediliyor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ -d ".git" ]; then
    git status --short
    echo ""
fi

# 2. Değişiklikleri rsync ile gönder
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  2/6: Dosyalar Sunucuya Gönderiliyor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# rsync komutu
rsync -avz --progress \
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
    echo -e "${GREEN}✅ Dosyalar başarıyla gönderildi${NC}"
else
    echo -e "${RED}❌ Dosya transferi başarısız!${NC}"
    exit 1
fi

# 3. Sunucuda işlemler yap
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  3/6: Sunucuda Güncelleme Yapılıyor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

APP_DIR="/home/iprice/price_analysis_service"
cd $APP_DIR

echo -e "${GREEN}📦 1. Gerekli dizinler kontrol ediliyor...${NC}"
mkdir -p screenshots logs data
chmod -R 755 screenshots

echo -e "${GREEN}📸 2. Screenshot klasör yapısı hazırlanıyor...${NC}"
# Bugünün tarihli klasörünü oluştur
TODAY=$(date +%d%m%Y)
mkdir -p screenshots/$TODAY
chmod -R 755 screenshots/$TODAY
echo -e "${GREEN}   ✓ screenshots/$TODAY klasörü hazır${NC}"

echo -e "${GREEN}🐳 3. Docker containers güncelleniyor...${NC}"
# Sadece selenium-worker'ı rebuild et (değişiklik burada)
docker-compose stop selenium-worker
docker-compose build --no-cache selenium-worker
docker-compose up -d selenium-worker

echo -e "${YELLOW}⏳ 10 saniye bekleniyor (container başlasın)...${NC}"
sleep 10

ENDSSH

# 4. Servis durumu kontrol et
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  4/6: Servis Durumu Kontrol Ediliyor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd /home/iprice/price_analysis_service

echo ""
echo -e "${GREEN}📊 Container Durumu:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|selenium|save|playwright"

echo ""
echo -e "${GREEN}🔍 Selenium Worker Logs (Son 20 satır):${NC}"
docker logs --tail 20 price_analysis_service-selenium-worker-1 2>&1 | tail -20

ENDSSH

# 5. Test komutları
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  5/6: Sistem Testleri${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /home/iprice/price_analysis_service

echo ""
echo -e "${YELLOW}🧪 Test 1: Health Check${NC}"
curl -s http://localhost:8000/health | head -5 || echo -e "${RED}❌ Health check başarısız${NC}"

echo ""
echo -e "${YELLOW}🧪 Test 2: Screenshot Klasörü${NC}"
if [ -d "screenshots/$(date +%d%m%Y)" ]; then
    echo -e "${GREEN}✓ Screenshot klasörü mevcut: screenshots/$(date +%d%m%Y)${NC}"
    ls -lh screenshots/$(date +%d%m%Y) | head -5 || echo "  (henüz screenshot yok)"
else
    echo -e "${RED}✗ Screenshot klasörü bulunamadı${NC}"
fi

echo ""
echo -e "${YELLOW}🧪 Test 3: RabbitMQ Queue Durumu${NC}"
docker exec price_analysis_service-rabbitmq-1 rabbitmqctl list_queues name messages consumers 2>/dev/null | grep -E "selenium|save|playwright" || echo -e "${YELLOW}⚠️ RabbitMQ komut çalışmadı${NC}"

ENDSSH

# 6. Özet ve dokümantasyon
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  6/6: Güncelleme Özeti${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ GÜNCELLEME TAMAMLANDI!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}📝 Yapılan Değişiklikler:${NC}"
echo -e "  ${GREEN}✓${NC} Selenium parser timeout'ları artırıldı"
echo -e "  ${GREEN}✓${NC} 3 deneme retry mekanizması eklendi"
echo -e "  ${GREEN}✓${NC} Screenshot alma özelliği aktif"
echo -e "  ${GREEN}✓${NC} Cloudflare bypass optimize edildi"
echo ""

echo -e "${CYAN}🔗 Erişim Bilgileri:${NC}"
echo -e "  • API:           ${BLUE}http://${SERVER_IP}:8000${NC}"
echo -e "  • Health Check:  ${BLUE}http://${SERVER_IP}:8000/health${NC}"
echo -e "  • Docs:          ${BLUE}http://${SERVER_IP}:8000/docs${NC}"
echo ""

echo -e "${CYAN}📊 İzleme Komutları:${NC}"
echo -e "  • Live Logs:         ${YELLOW}ssh ${SERVER_USER}@${SERVER_IP} 'cd ${APP_DIR} && docker-compose logs -f selenium-worker'${NC}"
echo -e "  • Container Durum:   ${YELLOW}ssh ${SERVER_USER}@${SERVER_IP} 'docker ps'${NC}"
echo -e "  • Screenshot Klasör: ${YELLOW}ssh ${SERVER_USER}@${SERVER_IP} 'ls -lh ${APP_DIR}/screenshots/\$(date +%d%m%Y)'${NC}"
echo ""

echo -e "${CYAN}🧪 Test Önerileri:${NC}"
echo -e "  1. Timeout veren bir URL'i tekrar test edin"
echo -e "  2. screenshot=true flag'i ile test job gönderin"
echo -e "  3. Loglarda 'Retry' ve 'Screenshot' mesajlarını arayın"
echo ""

echo -e "${CYAN}📚 Dokümantasyon:${NC}"
echo -e "  • Detaylı bilgi için: ${BLUE}cat TIMEOUT_VE_SCREENSHOT_GUNCELLEME.md${NC}"
echo ""

echo -e "${YELLOW}⚠️  Önemli Notlar:${NC}"
echo -e "  • Timeout'lar artırıldığı için işlemler daha uzun sürebilir"
echo -e "  • Screenshot'lar disk alanı kullanır, periyodik temizlik yapın"
echo -e "  • Retry mekanizması max 3× süre uzatabilir"
echo ""

echo -e "${GREEN}🎉 Başarıyla güncellendi! Kolay gelsin!${NC}"
echo ""

