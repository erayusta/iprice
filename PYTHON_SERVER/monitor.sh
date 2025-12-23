#!/bin/bash

# ================================
# 📊 Worker Monitoring Script
# ================================
# Worker'ları ve sistem kaynaklarını izlemek için

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  📊 Worker Monitor${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Worker durumları
show_workers() {
    echo -e "${CYAN}🔹 WORKER DURUMLARI${NC}"
    echo ""
    
    # Scrapy
    local scrapy_count=$(docker-compose ps | grep "scrapy-worker" | grep "Up" | wc -l | xargs)
    local scrapy_total=$(docker-compose ps | grep "scrapy-worker" | wc -l | xargs)
    echo -e "  🕷️  Scrapy Workers:    ${GREEN}$scrapy_count${NC}/$scrapy_total çalışıyor"
    
    # Selenium
    local selenium_count=$(docker-compose ps | grep "selenium-worker" | grep "Up" | wc -l | xargs)
    local selenium_total=$(docker-compose ps | grep "selenium-worker" | wc -l | xargs)
    echo -e "  🌐 Selenium Workers:  ${GREEN}$selenium_count${NC}/$selenium_total çalışıyor"
    
    # Playwright
    local playwright_count=$(docker-compose ps | grep "playwright-worker" | grep "Up" | wc -l | xargs)
    local playwright_total=$(docker-compose ps | grep "playwright-worker" | wc -l | xargs)
    echo -e "  🎭 Playwright Workers: ${GREEN}$playwright_count${NC}/$playwright_total çalışıyor"
    
    # Save Worker
    local save_count=$(docker-compose ps | grep "save-worker" | grep "Up" | wc -l | xargs)
    local save_total=$(docker-compose ps | grep "save-worker" | wc -l | xargs)
    echo -e "  💾 Save Workers:       ${GREEN}$save_count${NC}/$save_total çalışıyor"
    
    local total_running=$((scrapy_count + selenium_count + playwright_count + save_count))
    local total_all=$((scrapy_total + selenium_total + playwright_total + save_total))
    
    echo ""
    echo -e "  📊 Toplam: ${GREEN}$total_running${NC}/$total_all worker aktif"
    echo ""
}

# Kaynak kullanımı
show_resources() {
    echo -e "${CYAN}🔹 KAYNAK KULLANIMI${NC}"
    echo ""
    
    # Docker stats (1 saniyelik)
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "scrapy-worker|selenium-worker|playwright-worker|save-worker" | head -20
    
    echo ""
}

# Queue durumları
show_queues() {
    echo -e "${CYAN}🔹 QUEUE DURUMLARI${NC}"
    echo ""
    
    # API üzerinden queue durumlarını al
    local base_url="http://localhost:8000/v1"
    
    echo -e "  🕷️  Scrapy Queue:"
    curl -s "$base_url/queue-status/scrapy.queue" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"     Bekleyen: {data.get('message_count', 'N/A')} mesaj\")" || echo "     ❌ API'ye erişilemiyor"
    
    echo -e "  🌐 Selenium Queue:"
    curl -s "$base_url/queue-status/selenium.queue" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"     Bekleyen: {data.get('message_count', 'N/A')} mesaj\")" || echo "     ❌ API'ye erişilemiyor"
    
    echo -e "  🎭 Playwright Queue:"
    curl -s "$base_url/queue-status/playwright.queue" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"     Bekleyen: {data.get('message_count', 'N/A')} mesaj\")" || echo "     ❌ API'ye erişilemiyor"
    
    echo ""
}

# Ana döngü
if [ "$1" = "watch" ]; then
    # Sürekli izleme modu
    while true; do
        clear
        echo -e "${BLUE}================================${NC}"
        echo -e "${BLUE}  📊 Worker Monitor (Auto-refresh)${NC}"
        echo -e "${BLUE}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
        echo -e "${BLUE}================================${NC}"
        echo ""
        
        show_workers
        show_resources
        show_queues
        
        echo -e "${YELLOW}⏱️  Her 5 saniyede bir güncelleniyor... (Çıkmak için Ctrl+C)${NC}"
        sleep 5
    done
else
    # Tek seferlik gösterim
    show_workers
    show_resources
    show_queues
    
    echo -e "${YELLOW}💡 Sürekli izleme için: ./monitor.sh watch${NC}"
    echo ""
fi

