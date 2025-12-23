#!/bin/bash

# iPriceNew Quick Update Script
# Sadece kod değişikliklerini gönderir, rebuild yapmaz (daha hızlı)

SSH_USER="iprice"
SSH_HOST="74.234.27.174"
SSH_PASS="jzVGsy8T243u"
REMOTE_DIR="/var/www/iprice"

# Renkli output için
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function quick_update_frontend() {
    echo -e "${BLUE}🚀 Frontend Quick Update${NC}"
    
    # Sadece değişen dosyaları gönder
    rsync -avz --progress \
        -e "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no" \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='.nuxt' \
        --exclude='.output' \
        ./iprice-frontend/ $SSH_USER@$SSH_HOST:$REMOTE_DIR/frontend/
    
    # Frontend için rebuild gerekli (Nuxt.js production'da dosya değişiklikleri otomatik yansımaz)
    echo -e "${YELLOW}🔨 Frontend rebuild yapılıyor...${NC}"
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST \
        "cd $REMOTE_DIR/frontend && docker-compose -f docker-compose.prod.yml down && \
         docker-compose -f docker-compose.prod.yml build --no-cache && \
         docker-compose -f docker-compose.prod.yml up -d"
    
    echo -e "${GREEN}✅ Frontend güncellendi!${NC}"
}

function quick_update_backend() {
    echo -e "${BLUE}🚀 Backend Quick Update${NC}"
    
    # Sadece değişen dosyaları gönder
    rsync -avz --progress \
        -e "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no" \
        --exclude='node_modules' \
        --exclude='vendor' \
        --exclude='.git' \
        --exclude='storage/logs/*' \
        --exclude='storage/framework/cache/*' \
        ./iprice-backend/ $SSH_USER@$SSH_HOST:$REMOTE_DIR/backend/
    
    # Cache temizle
    echo -e "${YELLOW}🧹 Cache temizleniyor...${NC}"
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST \
        "docker exec iprice_backend_app bash -c 'rm -rf bootstrap/cache/*.php storage/framework/cache/data/* storage/framework/views/*'"
    
    # Container'ları restart et
    echo -e "${YELLOW}♻️  Container restart ediliyor...${NC}"
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST \
        "cd $REMOTE_DIR/backend && docker-compose -f docker-compose.prod.yml restart app nginx"
    
    # Yeni cache'leri oluştur
    echo -e "${YELLOW}📦 Yeni cache'ler oluşturuluyor...${NC}"
    sleep 3
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST \
        "docker exec iprice_backend_app php artisan config:cache && \
         docker exec iprice_backend_app php artisan route:cache"
    
    echo -e "${GREEN}✅ Backend güncellendi!${NC}"
}

case "$1" in
    frontend)
        quick_update_frontend
        ;;
    backend)
        quick_update_backend
        ;;
    *)
        echo -e "${YELLOW}Kullanım: $0 [frontend|backend]${NC}"
        echo ""
        echo "Frontend için rebuild yapar (Nuxt.js production'da gerekli)."
        echo "Backend için sadece restart yapar."
        echo "Composer/npm bağımlılıkları değiştiyse './deploy.sh' kullanın."
        echo ""
        echo "Örnekler:"
        echo "  $0 frontend   # Frontend kodunu hızlıca güncelle"
        echo "  $0 backend    # Backend kodunu hızlıca güncelle"
        exit 1
        ;;
esac

