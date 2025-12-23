#!/bin/bash

# iPriceNew Deployment Script
# Kullanım: ./deploy.sh [frontend|backend|all]

SSH_USER="iprice_admin"
SSH_HOST="10.20.50.16"
SSH_PASS="PtiPrice2025.*"
REMOTE_DIR="/var/www/iprice"

# Renkli output için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

function deploy_frontend() {
    print_header "Frontend Deployment"
    
    print_info "Frontend dosyaları sunucuya gönderiliyor..."
    rsync -avz --progress \
        -e "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no" \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='.nuxt' \
        --exclude='.output' \
        --exclude='.env' \
        ./ $SSH_USER@$SSH_HOST:$REMOTE_DIR/frontend/
    
    print_info "Deploy script dosyası gönderiliyor..."
    rsync -avz --progress \
        -e "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no" \
        ./deploy-frontend.sh $SSH_USER@$SSH_HOST:$REMOTE_DIR/
    
    print_info "Frontend deployment scripti çalıştırılıyor..."
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST "chmod +x $REMOTE_DIR/deploy-frontend.sh && cd $REMOTE_DIR/frontend && bash ../deploy-frontend.sh"
    
    print_success "Frontend deployment tamamlandı!"
    print_info "🌐 https://portal.iprice.com.tr"
}

function deploy_backend() {
    print_header "Backend Deployment"
    
    print_info "Backend dosyaları sunucuya gönderiliyor..."
    rsync -avz --progress \
        -e "sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no" \
        --exclude='node_modules' \
        --exclude='vendor' \
        --exclude='.git' \
        --exclude='storage/logs/*' \
        --exclude='storage/framework/cache/*' \
        --exclude='storage/framework/sessions/*' \
        --exclude='storage/framework/views/*' \
        ../PANEL/ $SSH_USER@$SSH_HOST:$REMOTE_DIR/backend/
    
    print_info "Backend deployment scripti çalıştırılıyor..."
    sshpass -p "$SSH_PASS" ssh $SSH_USER@$SSH_HOST "cd $REMOTE_DIR/backend && bash ../deploy-backend.sh"
    
    print_success "Backend deployment tamamlandı!"
    print_info "🌐 https://portal.iprice.com.tr/api"
}

function deploy_all() {
    print_header "Full Stack Deployment"
    deploy_backend
    echo ""
    deploy_frontend
    print_success "Tüm deployment işlemleri tamamlandı!"
}

# Ana script
case "$1" in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    all)
        deploy_all
        ;;
    *)
        echo -e "${YELLOW}Kullanım: $0 [frontend|backend|all]${NC}"
        echo ""
        echo "Örnekler:"
        echo "  $0 frontend   # Sadece frontend'i güncelle"
        echo "  $0 backend    # Sadece backend'i güncelle"
        echo "  $0 all        # Her ikisini birden güncelle"
        exit 1
        ;;
esac

