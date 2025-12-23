#!/bin/bash

###############################################################################
# 🗑️  RabbitMQ Queue Purge Script
###############################################################################
# Tüm RabbitMQ queue'lerini temizler
# Kullanım: ./purge_queues.sh [local|azure]
###############################################################################

set -e

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         🗑️  RabbitMQ Queue Purge Script                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Environment seçimi
ENVIRONMENT=${1:-"local"}

if [[ "$ENVIRONMENT" != "local" && "$ENVIRONMENT" != "azure" ]]; then
    echo -e "${RED}❌ Hatalı environment! Kullanım: $0 [local|azure]${NC}"
    exit 1
fi

echo -e "${YELLOW}🌍 Environment: ${ENVIRONMENT}${NC}"
echo ""

# .env dosyasını yükle
if [ -f .env ]; then
    echo -e "${BLUE}📄 .env dosyası yükleniyor...${NC}"
    # Yorum satırlarını ve inline yorumları filtrele, sonra export et
    while IFS= read -r line; do
        # Boş satırları ve yorum satırlarını atla
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Satırda = varsa ve geçerli variable name varsa export et
        if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
            # Inline yorumları temizle
            clean_line=$(echo "$line" | sed 's/#.*$//' | xargs)
            export "$clean_line"
        fi
    done < .env
    echo -e "${GREEN}✅ .env dosyası yüklendi${NC}"
else
    echo -e "${RED}❌ .env dosyası bulunamadı!${NC}"
    exit 1
fi

# RabbitMQ bağlantı ayarları
if [ "$ENVIRONMENT" == "local" ]; then
    RABBITMQ_HOST="${RABBITMQ_HOST_LOCAL}"
    RABBITMQ_PORT="${RABBITMQ_PORT_LOCAL}"
    RABBITMQ_USER="${RABBITMQ_USER_LOCAL}"
    RABBITMQ_PASS="${RABBITMQ_PASS_LOCAL}"
    RABBITMQ_VHOST="${RABBITMQ_VHOST_LOCAL}"
    RABBITMQ_API_PORT="15672"
    echo -e "${GREEN}📍 Local RabbitMQ: ${RABBITMQ_HOST}:${RABBITMQ_PORT} (vhost: ${RABBITMQ_VHOST})${NC}"
else
    # Azure RabbitMQ ayarları (.env'den)
    RABBITMQ_HOST="${RABBITMQ_HOST_AZURE}"
    RABBITMQ_PORT="${RABBITMQ_PORT_AZURE}"
    RABBITMQ_USER="${RABBITMQ_USER_AZURE}"
    RABBITMQ_PASS="${RABBITMQ_PASS_AZURE}"
    RABBITMQ_VHOST="${RABBITMQ_VHOST_AZURE}"
    RABBITMQ_API_PORT="15672"
    echo -e "${BLUE}☁️  Azure RabbitMQ: ${RABBITMQ_HOST}:${RABBITMQ_PORT} (vhost: ${RABBITMQ_VHOST})${NC}"
fi

echo ""

# Queue listesi
QUEUES=(
    # Parser queues
    "scrapy.queue"
    "scrapy.queue.completed"
    "scrapy.queue.error"
    
    "selenium.queue"
    "selenium.queue.completed"
    "selenium.queue.error"
    
    "playwright.queue"
    "playwright.queue.completed"
    "playwright.queue.error"
    
    # Save queue
    "save.queue"
    "save.queue.completed"
    "save.queue.error"
    
    # Test queues (eğer varsa)
    "test.queue"
    "test.queue.completed"
    "test.queue.error"
)

# Onay iste
echo -e "${YELLOW}⚠️  DİKKAT: Aşağıdaki ${#QUEUES[@]} queue temizlenecek:${NC}"
echo ""
for queue in "${QUEUES[@]}"; do
    echo -e "   ${RED}🗑️${NC}  $queue"
done
echo ""

read -p "Devam etmek istiyor musunuz? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo -e "${YELLOW}❌ İşlem iptal edildi${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Queue purge işlemi başlatılıyor...${NC}"
echo ""

# RabbitMQ Management API kullanarak queue purge
API_URL="http://${RABBITMQ_HOST}:${RABBITMQ_API_PORT}/api"

# Purge fonksiyonu
purge_queue() {
    local queue_name=$1
    
    echo -n "🗑️  Purging: ${queue_name} ... "
    
    # vhost'u URL encode et
    local vhost_encoded
    if [ "$RABBITMQ_VHOST" == "/" ]; then
        vhost_encoded="%2F"
    else
        vhost_encoded="${RABBITMQ_VHOST}"
    fi
    
    # Queue bilgisini al
    response=$(curl -s -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
        "${API_URL}/queues/${vhost_encoded}/${queue_name}")
    
    http_code=$?
    
    # Curl başarısız olduysa
    if [ $http_code -ne 0 ]; then
        echo -e "${RED}❌ Connection hatası${NC}"
        return
    fi
    
    # Queue yoksa
    if echo "$response" | grep -q '"error":"Object Not Found"'; then
        echo -e "${YELLOW}⚠️  Queue bulunamadı (skip)${NC}"
        return
    fi
    
    # Mesaj sayısını al
    message_count=$(echo "$response" | grep -o '"messages":[0-9]*' | grep -o '[0-9]*' | head -n1)
    
    # Queue'yu purge et
    purge_response=$(curl -s -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
        -X DELETE \
        -o /dev/null \
        -w "%{http_code}" \
        "${API_URL}/queues/${vhost_encoded}/${queue_name}/contents")
    
    if [ "$purge_response" == "204" ] || [ "$purge_response" == "200" ]; then
        echo -e "${GREEN}✅ Temizlendi (${message_count:-0} mesaj)${NC}"
    else
        echo -e "${RED}❌ Purge hatası (HTTP $purge_response)${NC}"
    fi
}

# Tüm queue'ları purge et
success_count=0
skip_count=0
error_count=0

for queue in "${QUEUES[@]}"; do
    purge_queue "$queue"
    
    # HTTP kod kontrolü için
    if [[ $? -eq 0 ]]; then
        ((success_count++))
    else
        ((error_count++))
    fi
    
    sleep 0.2  # Rate limiting için kısa bekleme
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Purge işlemi tamamlandı!${NC}"
echo ""
echo -e "   ${GREEN}Başarılı:${NC} $success_count queue"
echo -e "   ${RED}Hata:${NC} $error_count queue"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Alternatif: Docker exec ile purge (eğer API çalışmazsa)
echo ""
echo -e "${YELLOW}💡 Alternatif Yöntem (Docker ile):${NC}"
if [ "$ENVIRONMENT" == "local" ]; then
    echo -e "${BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=scrapy.queue${NC}"
    echo -e "${BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=selenium.queue${NC}"
    echo -e "${BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=playwright.queue${NC}"
    echo -e "${BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=save.queue${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Tamamlandı!${NC}"

