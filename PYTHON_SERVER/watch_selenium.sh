#!/bin/bash

# Selenium Parser ve Worker Log İzleme Scripti
# Kullanım: ./watch_selenium.sh [worker|test|docker]

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MODE=${1:-test}

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🔍 Selenium Parser İzleme${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

case $MODE in
    worker)
        echo -e "${YELLOW}📦 Worker modu: Selenium worker'ı direkt çalıştırıyor...${NC}"
        echo -e "${BLUE}Worker loglarını göreceksiniz.${NC}"
        echo ""
        cd "$(dirname "$0")"
        source venv/bin/activate 2>/dev/null || echo "⚠️  Venv bulunamadı, devam ediliyor..."
        cd app
        python3 -m workers.selenium_worker
        ;;
    
    test)
        echo -e "${YELLOW}🧪 Test modu: Test scripti çalıştırılıyor...${NC}"
        echo -e "${BLUE}Parser loglarını göreceksiniz.${NC}"
        echo ""
        cd "$(dirname "$0")"
        source venv/bin/activate 2>/dev/null || echo "⚠️  Venv bulunamadı, devam ediliyor..."
        python3 test_selenium_real_parser.py
        ;;
    
    docker)
        echo -e "${YELLOW}🐳 Docker modu: Docker container logları izleniyor...${NC}"
        echo -e "${BLUE}Son 100 satır gösteriliyor, canlı izleme aktif.${NC}"
        echo ""
        cd "$(dirname "$0")"
        docker-compose -p price_analysis_service logs -f --tail=100 selenium-worker
        ;;
    
    *)
        echo -e "${YELLOW}Kullanım:${NC}"
        echo "  ./watch_selenium.sh worker  - Worker'ı direkt çalıştır ve izle"
        echo "  ./watch_selenium.sh test     - Test scripti ile parser'ı izle (varsayılan)"
        echo "  ./watch_selenium.sh docker  - Docker container loglarını izle"
        echo ""
        echo -e "${GREEN}Örnek:${NC}"
        echo "  ./watch_selenium.sh test"
        exit 1
        ;;
esac

