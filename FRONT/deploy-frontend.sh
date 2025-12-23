#!/bin/bash

# Frontend Deployment Script
cd /var/www/iprice/frontend

echo '🛑 Mevcut container durduruluyor...'
docker-compose down 2>/dev/null || true
docker stop iprice_frontend 2>/dev/null || true
docker rm iprice_frontend 2>/dev/null || true

echo '🔨 Docker image build ediliyor...'
docker build \
  --build-arg NUXT_PUBLIC_API_BASE=http://10.20.50.16/iprice_backend/api \
  --build-arg NUXT_PUBLIC_TRENDYOL_AI_SERVICE=http://localhost:5002 \
  -t frontend-frontend:latest \
  -f Dockerfile .

echo '🚀 Container başlatılıyor...'
docker run -d \
  --name iprice_frontend \
  --restart unless-stopped \
  -p 3000:3000 \
  frontend-frontend:latest

echo '✅ Frontend deployment tamamlandı!'
docker ps | grep iprice_frontend

