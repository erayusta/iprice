#!/bin/bash
# ========================================
# 🚀 DOCKER COMPOSE SCALE SCRIPT
# ========================================
# Kullanım: ./scale.sh [scrapy] [selenium] [playwright] [save]
# Örnek: ./scale.sh 10 10 10 5
# 
# Parametresiz çalıştırma: ./scale.sh (default değerler)
# ========================================

set -e

# Renkli output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default değerler
DEFAULT_SCRAPY=3
DEFAULT_SELENIUM=5
DEFAULT_PLAYWRIGHT=5
DEFAULT_SAVE=2

# Parametrelerden al veya default kullan
SCRAPY_COUNT=${1:-$DEFAULT_SCRAPY}
SELENIUM_COUNT=${2:-$DEFAULT_SELENIUM}
PLAYWRIGHT_COUNT=${3:-$DEFAULT_PLAYWRIGHT}
SAVE_COUNT=${4:-$DEFAULT_SAVE}

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🚀 Docker Compose Scale Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Scale Ayarları:${NC}"
echo -e "  Scrapy Workers:     ${GREEN}${SCRAPY_COUNT}${NC}"
echo -e "  Selenium Workers:   ${GREEN}${SELENIUM_COUNT}${NC}"
echo -e "  Playwright Workers: ${GREEN}${PLAYWRIGHT_COUNT}${NC}"
echo -e "  Save Workers:       ${GREEN}${SAVE_COUNT}${NC}"
echo ""

# Toplam RAM tahmini
SCRAPY_RAM=$((SCRAPY_COUNT * 512))
SELENIUM_RAM=$((SELENIUM_COUNT * 1024))
PLAYWRIGHT_RAM=$((PLAYWRIGHT_COUNT * 1024))
SAVE_RAM=$((SAVE_COUNT * 512))
TOTAL_RAM=$((SCRAPY_RAM + SELENIUM_RAM + PLAYWRIGHT_RAM + SAVE_RAM))

echo -e "${YELLOW}Tahmini RAM Kullanımı:${NC}"
echo -e "  Scrapy:     ${SCRAPY_RAM} MB"
echo -e "  Selenium:   ${SELENIUM_RAM} MB"
echo -e "  Playwright: ${PLAYWRIGHT_RAM} MB"
echo -e "  Save:       ${SAVE_RAM} MB"
echo -e "  ${BLUE}TOPLAM:     ${TOTAL_RAM} MB (~$((TOTAL_RAM / 1024)) GB)${NC}"
echo ""

# RAM uyarısı
if [ $TOTAL_RAM -gt 16000 ]; then
    echo -e "${RED}⚠️  UYARI: Toplam RAM kullanımı 16GB'ı aşıyor!${NC}"
    echo -e "${YELLOW}Sisteminizde yeterli RAM olmayabilir.${NC}"
    echo ""
fi

# Onay iste
read -p "$(echo -e ${GREEN}Devam edilsin mi? [Y/n]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
    echo -e "${RED}İptal edildi.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Container'lar kapatılıyor...${NC}"
docker-compose down

echo ""
echo -e "${BLUE}Container'lar başlatılıyor ve scale ediliyor...${NC}"

docker-compose up -d \
  --scale scrapy-worker=$SCRAPY_COUNT \
  --scale selenium-worker=$SELENIUM_COUNT \
  --scale playwright-worker=$PLAYWRIGHT_COUNT \
  --scale save-worker=$SAVE_COUNT

echo ""
echo -e "${GREEN}✅ Scale işlemi tamamlandı!${NC}"
echo ""

# Container durumunu göster
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}📊 Container Durumu:${NC}"
echo -e "${BLUE}========================================${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Log takibi için:${NC}"
echo -e "  ${GREEN}docker-compose logs -f --tail=100${NC}"
echo ""
echo -e "${YELLOW}Belirli bir worker için:${NC}"
echo -e "  ${GREEN}docker-compose logs -f scrapy-worker${NC}"
echo -e "  ${GREEN}docker-compose logs -f selenium-worker${NC}"
echo -e "  ${GREEN}docker-compose logs -f playwright-worker${NC}"
echo -e "  ${GREEN}docker-compose logs -f save-worker${NC}"
echo -e "${BLUE}========================================${NC}"
