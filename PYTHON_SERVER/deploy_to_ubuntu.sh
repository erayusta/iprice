#!/bin/bash
# iPriceNew Price Analysis Service - Ubuntu Deployment Script
# Kullanım: Bu script'i Ubuntu sunucuda çalıştırın

set -e  # Hata durumunda dur

echo "🚀 iPriceNew Price Analysis Service - Ubuntu Kurulum Başlıyor..."

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Sistem Güncelleme
echo -e "${GREEN}📦 Sistem güncelleniyor...${NC}"
sudo apt update -y
sudo apt upgrade -y

# 2. Gerekli Paketleri Kur
echo -e "${GREEN}📦 Gerekli paketler kuruluyor...${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    postgresql-client

# 3. Docker Kurulumu
echo -e "${GREEN}🐳 Docker kuruluyor...${NC}"
if ! command -v docker &> /dev/null; then
    # Docker GPG key ekle
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Docker repository ekle
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Docker yükle
    sudo apt update -y
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Docker'ı kullanıcı için etkinleştir
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker kuruldu!${NC}"
else
    echo -e "${YELLOW}⚠️ Docker zaten kurulu${NC}"
fi

# 4. Docker Compose Kurulumu
echo -e "${GREEN}🐳 Docker Compose kuruluyor...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose kuruldu!${NC}"
else
    echo -e "${YELLOW}⚠️ Docker Compose zaten kurulu${NC}"
fi

# 5. Uygulama Dizinini Oluştur
echo -e "${GREEN}📁 Uygulama dizini oluşturuluyor...${NC}"
APP_DIR="/home/iprice/price_analysis_service"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
echo -e "${YELLOW}📋 Sonraki adımlar:${NC}"
echo -e "1. Uygulamayı $APP_DIR dizinine yükleyin"
echo -e "2. .env dosyasını yapılandırın"
echo -e "3. docker-compose up -d ile başlatın"
echo -e "4. Systemd servisini etkinleştirin"
echo ""
echo -e "${GREEN}🔧 Docker ve Docker Compose sürümleri:${NC}"
docker --version
docker-compose --version
echo ""
echo -e "${RED}⚠️ ÖNEMLI: Docker grubuna ekleme işleminin geçerli olması için lütfen logout/login yapın!${NC}"
echo -e "${YELLOW}Veya şu komutu çalıştırın: newgrp docker${NC}"

