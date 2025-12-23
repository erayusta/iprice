# 🔧 Deployment Troubleshooting Guide

## ⚠️ Yaygın Sorunlar ve Çözümleri

### 1. **Backend 500 Hatası - "Class translator does not exist"**

#### Belirti:
```
Frontend console:
GET https://portal.iprice.com.tr/api/... 500 (Internal Server Error)

Backend log:
ReflectionException: Class "translator" does not exist
```

#### Neden:
Laravel'in bootstrap cache'i bozulmuş veya eski service provider referansları var.

#### Çözüm:

```bash
# Sunucuya bağlan
ssh iprice@74.234.27.174

# Cache'leri manuel temizle
docker exec iprice_backend_app bash -c 'rm -rf bootstrap/cache/*.php storage/framework/cache/data/* storage/framework/views/*'

# Container'ları restart et
cd /var/www/iprice/backend
docker-compose -f docker-compose.prod.yml restart app nginx

# Bekle ve yeni cache oluştur
sleep 5
docker exec iprice_backend_app php artisan config:cache
docker exec iprice_backend_app php artisan route:cache
```

#### Önlem:
`quick-update.sh` scripti artık otomatik olarak bootstrap cache'i temizliyor.

---

### 2. **Frontend'de API Base URL Hatalı**

#### Belirti:
Frontend hala `localhost:8082` API'sine istek atıyor.

#### Neden:
Environment değişkeni build-time'da set edilmemiş.

#### Çözüm:

```bash
# Frontend'i tam deployment ile yeniden build et
./deploy.sh frontend
```

**Not:** `quick-update.sh` sadece kod değişikliklerini gönderir, environment değişkenlerini güncellemez.

---

### 3. **Permission Denied Hatası**

#### Belirti:
```
rsync: permission denied
docker: permission denied
```

#### Çözüm:

```bash
# Sunucuda
ssh iprice@74.234.27.174
sudo chown -R iprice:iprice /var/www/iprice
chmod +x /var/www/iprice/*.sh

# Lokal
chmod +x deploy.sh quick-update.sh
```

---

### 4. **Docker Build Hatası**

#### Belirti:
```
ERROR: failed to solve: failed to compute cache key
```

#### Çözüm:

```bash
# Sunucuda cache'siz build
ssh iprice@74.234.27.174
cd /var/www/iprice/frontend  # veya backend
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

### 5. **Composer/NPM Bağımlılık Hatası**

#### Belirti:
```
Class not found
Module not found
```

#### Neden:
`quick-update.sh` kullandınız ama bağımlılıklar değişmiş.

#### Çözüm:

```bash
# quick-update yerine deploy kullanın
./deploy.sh backend  # veya frontend
```

---

### 6. **SSL Sertifikası Hatası**

#### Belirti:
```
SSL certificate problem
NET::ERR_CERT_AUTHORITY_INVALID
```

#### Çözüm:

```bash
# Sertifikayı yenile
ssh iprice@74.234.27.174
sudo certbot renew --nginx
```

---

### 7. **Container Sürekli Restart Ediyor**

#### Kontrol:

```bash
ssh iprice@74.234.27.174
docker ps -a  # Container durumlarını göster
docker logs iprice_frontend --tail=50  # Logları kontrol et
docker logs iprice_backend_app --tail=50
```

#### Çözüm:

Container loglarına göre hatayı düzeltin. Genellikle:
- .env dosyası eksik/hatalı
- Port çakışması
- Memory yetersiz

---

### 8. **API 401 Unauthenticated**

#### Belirti:
Tüm API istekleri 401 dönüyor.

#### Neden:
Normal! Authentication gerekiyor.

#### Çözüm:
Önce login olun:

```bash
# Login
POST https://portal.iprice.com.tr/api/auth/login
{
  "email": "your@email.com",
  "password": "yourpassword"
}

# Token'ı kaydedin ve sonraki isteklerde kullanın
Authorization: Bearer YOUR_TOKEN
```

---

### 9. **Frontend Değişiklikleri Görünmüyor**

#### Neden:
Browser cache.

#### Çözüm:

1. **Hard refresh:** `Ctrl+Shift+R` (Windows/Linux) veya `Cmd+Shift+R` (Mac)
2. **DevTools açık:** F12 → Network tab → "Disable cache" işaretle
3. **Incognito mode:** Yeni incognito pencere aç

---

### 10. **Backend Değişiklikleri Görünmüyor**

#### Kontrol:

```bash
ssh iprice@74.234.27.174

# Dosya güncel mi?
cat /var/www/iprice/backend/app/Http/Controllers/YourController.php

# Cache var mı?
docker exec iprice_backend_app php artisan route:list | grep your-route
```

#### Çözüm:

```bash
# Manuel cache temizle
docker exec iprice_backend_app bash -c 'rm -rf bootstrap/cache/*.php'
cd /var/www/iprice/backend
docker-compose -f docker-compose.prod.yml restart app
```

---

## 🚨 Acil Durum - Her Şeyi Sıfırla

Hiçbir şey çalışmıyorsa, tamamen sıfırlayın:

```bash
ssh iprice@74.234.27.174

# Backend'i sıfırla
cd /var/www/iprice/backend
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Frontend'i sıfırla
cd /var/www/iprice/frontend
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Nginx'i restart et
sudo systemctl restart nginx
```

---

## 📊 Monitoring Komutları

### Container Durumu:

```bash
ssh iprice@74.234.27.174
docker ps -a
docker stats  # CPU/Memory kullanımı
```

### Logları İzle:

```bash
# Real-time log izle
docker logs iprice_frontend -f
docker logs iprice_backend_app -f
docker logs iprice_backend_nginx -f

# Nginx access log
sudo tail -f /var/log/nginx/access.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Disk Kullanımı:

```bash
df -h  # Disk durumu
docker system df  # Docker disk kullanımı
docker system prune -a  # Kullanılmayan image'ları temizle (DİKKATLİ!)
```

---

## 🔍 Debug Checklist

Backend sorunu için:

- [ ] Container çalışıyor mu? `docker ps`
- [ ] Logları kontrol et `docker logs iprice_backend_app --tail=50`
- [ ] Laravel log kontrol et `docker exec iprice_backend_app tail -50 storage/logs/laravel.log`
- [ ] Cache temiz mi? `docker exec iprice_backend_app ls -la bootstrap/cache/`
- [ ] .env dosyası var mı? `docker exec iprice_backend_app cat .env`
- [ ] Database bağlantısı var mı? `docker exec iprice_backend_app php artisan tinker --execute="DB::connection()->getPdo();"`

Frontend sorunu için:

- [ ] Container çalışıyor mu? `docker ps`
- [ ] Logları kontrol et `docker logs iprice_frontend --tail=50`
- [ ] API URL doğru mu? `curl https://portal.iprice.com.tr | grep apiBase`
- [ ] Browser cache temiz mi? Hard refresh yaptın mı?
- [ ] Console'da hata var mı? F12 → Console tab

---

## 📞 Yardım Alma

Sorun çözemezseniz:

1. **Logları topla:**
```bash
ssh iprice@74.234.27.174
docker logs iprice_backend_app --tail=100 > backend.log
docker logs iprice_frontend --tail=100 > frontend.log
docker ps -a > containers.log
```

2. **Screenshot al:** Browser console ve network tab

3. **İletişime geç:** Log dosyalarını ve screenshot'ları paylaş

---

**Son Güncelleme:** 21 Ekim 2025

