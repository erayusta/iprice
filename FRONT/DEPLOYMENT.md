# 🚀 iPriceNew Deployment Guide

## 📋 Hazırlanan Deployment Sistemleri

### 1. **Manuel Deployment (Lokal Bilgisayardan)**

Lokal bilgisayarınızdan tek komutla güncelleme yapabilirsiniz.

#### Kullanım:

```bash
# Frontend'i güncelle (React/Vue/Nuxt değişiklikleri)
./deploy.sh frontend

# Backend'i güncelle (Laravel/PHP değişiklikleri)
./deploy.sh backend

# Her ikisini birden güncelle
./deploy.sh all
```

#### Ne Yapar?
- ✅ Dosyaları sunucuya gönderir (rsync)
- ✅ Docker container'ları yeniden build eder
- ✅ Composer/npm bağımlılıklarını günceller
- ✅ Cache'leri temizler ve yeniden oluşturur
- ✅ Servisleri yeniden başlatır

---

### 2. **Hızlı Güncelleme (Quick Update)**

Sadece kod değişiklikleri varsa, rebuild yapmadan hızlıca günceller.

#### Kullanım:

```bash
# Frontend kodunu hızlıca güncelle (bağımlılık değişmedi)
./quick-update.sh frontend

# Backend kodunu hızlıca güncelle (bağımlılık değişmedi)
./quick-update.sh backend
```

#### Ne Zaman Kullanılır?
- ✅ Sadece Vue/React component değişiklikleri (Frontend rebuild gerekli)
- ✅ Sadece PHP/Laravel controller/model değişiklikleri
- ✅ CSS/JavaScript değişiklikleri
- ❌ package.json veya composer.json değişmediyse

#### Ne Zaman Kullanılmaz?
- ❌ npm/composer bağımlılıkları değiştiyse
- ❌ Docker yapılandırması değiştiyse
- ❌ .env dosyası değiştiyse
→ Bu durumlarda `./deploy.sh` kullanın

---

### 3. **Sunucuda Direkt Deployment**

Sunucuya SSH ile bağlanıp direkt güncelleme yapabilirsiniz.

#### Kullanım:

```bash
# Sunucuya bağlan
ssh iprice@74.234.27.174

# Frontend güncelle
cd /var/www/iprice
./deploy-frontend.sh

# Backend güncelle
cd /var/www/iprice
./deploy-backend.sh
```

---

## 🔄 Otomatik Deployment (GitHub Webhook - Opsiyonel)

GitHub'a kod push ettiğinizde otomatik deployment yapılabilir.

### Kurulum Adımları:

#### 1. GitHub Webhook Ayarları:

1. GitHub repo'nuza gidin
2. **Settings** > **Webhooks** > **Add webhook**
3. Aşağıdaki bilgileri girin:

```
Payload URL: http://74.234.27.174:9000/webhook
Content type: application/json
Secret: iprice_webhook_secret_2025
Events: Just the push event
```

#### 2. Sunucuda Webhook Listener Başlat:

```bash
# Sunucuya bağlan
ssh iprice@74.234.27.174

# Webhook listener'ı başlat (port 9000)
cd /var/www/iprice
while true; do nc -l -p 9000 -c './webhook.sh'; done &
```

#### 3. Test Et:

```bash
# GitHub'a kod push et
git add .
git commit -m "Test deployment"
git push origin main

# Webhook loglarını kontrol et
ssh iprice@74.234.27.174
tail -f /var/www/iprice/webhook.log
```

---

## 📊 Deployment Senaryoları

### Senaryo 1: Frontend'de Component Değişikliği

```bash
# 1. Lokal değişiklikleri yap
cd iprice-frontend/components
vim MyComponent.vue

# 2. Hızlı güncelle (30 saniye)
./quick-update.sh frontend
```

### Senaryo 2: Backend'de API Değişikliği

```bash
# 1. Lokal değişiklikleri yap
cd iprice-backend/app/Http/Controllers
vim MyController.php

# 2. Hızlı güncelle (15 saniye)
./quick-update.sh backend
```

### Senaryo 3: npm/composer Bağımlılık Ekleme

```bash
# 1. Bağımlılık ekle
cd iprice-frontend
npm install new-package

# 2. Tam deployment yap (2-3 dakika)
./deploy.sh frontend
```

### Senaryo 4: Her İki Tarafı Güncelle

```bash
# Tek komutla her ikisini güncelle
./deploy.sh all
```

---

## 🛠️ Troubleshooting

### Deployment Başarısız Olursa:

```bash
# 1. Sunucuda logları kontrol et
ssh iprice@74.234.27.174
docker logs iprice_frontend --tail=50
docker logs iprice_backend_app --tail=50

# 2. Container durumlarını kontrol et
docker ps -a

# 3. Manuel restart
cd /var/www/iprice/frontend
docker-compose -f docker-compose.prod.yml restart

cd /var/www/iprice/backend
docker-compose -f docker-compose.prod.yml restart
```

### Permission Hataları:

```bash
# Sunucuda dosya izinlerini düzelt
ssh iprice@74.234.27.174
sudo chown -R iprice:iprice /var/www/iprice
chmod +x /var/www/iprice/*.sh
```

### Docker Build Hataları:

```bash
# Cache'siz yeniden build
ssh iprice@74.234.27.174
cd /var/www/iprice/frontend
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📝 Deployment Checklist

### Frontend Deployment Öncesi:

- [ ] Lokal testler geçti mi?
- [ ] Build hataları var mı?
- [ ] API endpoint'leri doğru mu?
- [ ] Environment variables güncel mi?

### Backend Deployment Öncesi:

- [ ] Database migration gerekli mi?
- [ ] .env dosyası güncel mi?
- [ ] Composer dependencies çözüldü mü?
- [ ] Cache temizlendi mi?

---

## 🎯 Hızlı Referans

```bash
# Hızlı güncellemeler (30 saniye)
./quick-update.sh frontend
./quick-update.sh backend

# Tam deployment (2-3 dakika)
./deploy.sh frontend
./deploy.sh backend
./deploy.sh all

# Sunucuda direkt
ssh iprice@74.234.27.174
cd /var/www/iprice
./deploy-frontend.sh
./deploy-backend.sh
```

---

## 🔗 Faydalı Linkler

- **Frontend:** https://portal.iprice.com.tr
- **Backend API:** https://portal.iprice.com.tr/api
- **RabbitMQ Management:** http://74.234.27.174:15672

---

## 🆘 Destek

Herhangi bir sorun olursa:

1. Container loglarını kontrol edin
2. Nginx loglarını kontrol edin: `sudo tail -f /var/log/nginx/error.log`
3. Deployment script loglarını kontrol edin
4. İletişime geçin

---

**Son Güncelleme:** 21 Ekim 2025
**Versiyon:** 1.0.0

