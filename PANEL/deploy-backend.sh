#!/bin/bash

# Backend Deployment Script
cd /var/www/iprice/backend

echo '🛑 Mevcut container durduruluyor...'
docker-compose down 2>/dev/null || true

echo '📦 Composer bağımlılıkları yükleniyor...'
docker-compose run --rm app composer install --no-dev --optimize-autoloader

echo '🔧 Laravel cache temizleniyor...'
docker-compose run --rm app php artisan config:clear
docker-compose run --rm app php artisan cache:clear
docker-compose run --rm app php artisan route:clear
docker-compose run --rm app php artisan view:clear

echo '📝 Environment dosyası kontrol ediliyor...'
if [ ! -f .env ]; then
    echo '⚠️  .env dosyası bulunamadı! .env.example kopyalanıyor...'
    cp .env.example .env
    echo '⚠️  Lütfen .env dosyasını düzenleyin!'
fi

echo '🗄️  Veritabanı migration çalıştırılıyor...'
docker-compose run --rm app php artisan migrate --force

echo '🔨 Cache yeniden oluşturuluyor...'
docker-compose run --rm app php artisan config:cache
docker-compose run --rm app php artisan route:cache
docker-compose run --rm app php artisan view:cache

echo '🚀 Container'lar başlatılıyor...'
docker-compose up -d

echo '⏳ Servislerin hazır olması bekleniyor...'
sleep 10

echo '✅ Backend deployment tamamlandı!'
docker-compose ps
