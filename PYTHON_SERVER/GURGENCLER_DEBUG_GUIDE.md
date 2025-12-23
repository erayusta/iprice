# 🔍 Gürgençler Price Extraction Debug Guide

## 📋 Yapılan İyileştirmeler

### 1. ✅ Debug Log'ları Eklendi

**`selenium_parser.py` değişiklikleri:**

#### a) Meta Attribute Detection Log (Line 387)
```python
print(f"✅ META attribute detected: {attr_name} = {attr_value}")
```
- Artık meta attribute tespit edildiğinde log göreceksiniz
- `price = unit_sale_price` mesajını görmeli

#### b) Proxy Kullanım Log'ları (Line 305-315)
```python
if proxy_url:
    print(f"🔒 Undetected Selenium proxy kullanılıyor: {proxy_display}")
    print(f"🔒 Proxy type: {job_data.get('proxy_type')}")
    print(f"🔒 use_proxy flag: {job_data.get('use_proxy')}")
else:
    print(f"⚠️ PROXY YOK! Site direkt erişiliyor")
```
- Proxy kullanılıp kullanılmadığını görebilirsiniz
- Brightdata credentials eksikse anında farkedeceksiniz

#### c) Detailed Attribute Debug (Line 124-127)
```python
for idx, attr in enumerate(raw_attributes):
    print(f"🔍 DEBUG: Attribute #{idx+1} - type: '{attr.get('attributes_type')}' | name: '{attr.get('attributes_name')}' | value: '{attr.get('attributes_value')}'")
```
- RabbitMQ'dan gelen attribute'ların tam içeriğini görebilirsiniz

#### d) Insider Object Debug (Line 636-644)
```python
if meta_value == 'unit_sale_price':
    direct_value = driver.execute_script("""
        if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
            return window.insider_object.product.unit_sale_price;
        }
        return null;
    """)
    print(f"🔍 Direkt unit_sale_price değeri: {direct_value}")
```
- insider_object.product.unit_sale_price değerini direkt görebilirsiniz

---

## 🚀 Production'a Deploy

### Adım 1: Kodu Production Sunucusuna Yükle

```bash
# Lokal makineden production'a push et
cd /Users/onurerdogan/Desktop/PROJE_IPRICE/PYTHON_SERVER

# Git commit (eğer git kullanıyorsanız)
git add app/parsers/selenium_parser.py
git commit -m "feat: Add detailed debug logs for Gürgençler price extraction"
git push origin main

# VEYA: Direkt SCP ile yükle
scp app/parsers/selenium_parser.py root@68.219.209.108:/root/PROJE_IPRICE/PYTHON_SERVER/app/parsers/
```

### Adım 2: Production Container'ı Yeniden Başlat

```bash
# SSH ile sunucuya bağlan
ssh root@68.219.209.108

# Proje klasörüne git
cd /root/PROJE_IPRICE/PYTHON_SERVER  # veya projenin olduğu yer

# Selenium worker'ı yeniden başlat
docker-compose restart selenium-worker

# Veya tüm sistemi yeniden başlat
docker-compose down
docker-compose up -d

# Container'ın çalıştığından emin ol
docker-compose ps | grep selenium-worker
```

---

## 📊 Log İzleme

### 1. Docker Log'larını İzle (Real-time)

```bash
# Selenium worker log'larını canlı izle
docker-compose logs -f selenium-worker

# Veya docker ps ile container ID'sini bulup:
docker ps | grep selenium-worker
docker logs -f <CONTAINER_ID>
```

### 2. Aranacak Log Mesajları

#### ✅ BAŞARILI Durum:
```
📦 Selenium Job işleniyor - Job ID: 212, URL: https://www.gurgencler.com.tr/...
🔍 DEBUG: Attribute #1 - type: 'meta' | name: 'price' | value: 'unit_sale_price'
✅ META attribute detected: price = unit_sale_price
⏳ ✅ Meta attribute tespit edildi, JavaScript object'lerinin yüklenmesi bekleniyor
🛡️ Undetected ChromeDriver başlatılıyor...
🔒 Undetected Selenium proxy kullanılıyor: brd-customer-hl_762***@brd.superproxy.io:33335
🔒 Proxy type: BrightData
🔒 use_proxy flag: True
✅ insider_object yüklendi (2.5 saniye sonra)
🔍 Meta extraction başlıyor: price -> unit_sale_price
🔍 insider_object durumu: True
🔍 Product keys: id, sku, name, taxonomy, currency, unit_price, unit_sale_price, url, product_image_url, stock
🔍 Direkt unit_sale_price değeri: 9999
✅ insider_object.product.unit_sale_price bulundu: 9999
✅ price: 9999
✅ Selenium parsing başarılı
```

#### ❌ HATA Durumları:

**1. Proxy Kullanılmıyor:**
```
⚠️ PROXY YOK! Site direkt erişiliyor (bot detection riski yüksek)
   use_proxy: True
   proxy_type: BrightData
```
**Çözüm:** Brightdata credentials .env dosyasında kontrol edin:
```bash
grep BRIGHTDATA .env
# Olmalı: BRIGHTDATA_USERNAME, BRIGHTDATA_PASSWORD, BRIGHTDATA_ENDPOINT
```

**2. Insider Object Yüklenmiyor:**
```
⚠️ insider_object bulunamadı! Sayfa tam yüklenmemiş olabilir.
🔍 insider_object durumu (2. deneme): False
```
**Çözüm:** 
- Cloudflare challenge olabilir
- Proxy IP ban'lanmış olabilir
- Site JavaScript'leri değiştirmiş olabilir

**3. Meta Attribute Tespit Edilmiyor:**
```
🔍 DEBUG: Attribute #1 - type: 'class' | name: 'price' | value: '.price'
```
**Çözüm:** 
- RabbitMQ job data'da `attributes_type` değeri **'meta'** olmalı
- Panel'den attribute configuration'ı kontrol edin

---

## 🐛 Hata Senaryoları ve Çözümleri

### Senaryo 1: "Attribute'lar parse edilemedi: price (1/1)"

**Muhtemel Sebep:** insider_object JavaScript'te yüklenmeden önce parse yapılıyor

**Log'larda Kontrol Et:**
```bash
# Log'da şu mesajı ara:
grep "insider_object durumu" <LOG_FILE>

# False dönüyorsa bekleme süresini artır (selenium_parser.py Line 132):
for i in range(30):  # 30 -> 60 yap (30 saniye)
```

### Senaryo 2: HTTP 200 ama fiyat NULL

**Muhtemel Sebep:** Cloudflare/bot detection

**Log'larda Kontrol Et:**
```bash
grep "Cloudflare" <LOG_FILE>
grep "PROXY" <LOG_FILE>
```

**Çözüm:**
1. Proxy kullanıldığından emin olun (yukarıdaki log'lara bakın)
2. Brightdata IP'lerini rotate edin (farklı session)
3. User-Agent'ı değiştirin

### Senaryo 3: Proxy Timeout

**Muhtemel Sebep:** Brightdata connection timeout

**Çözüm:**
```bash
# .env dosyasında timeout'u artır:
PROXY_TIMEOUT=30  # Default: 10
```

---

## 📝 Test Adımları

### 1. Lokal Test (Docker ile)

```bash
cd /Users/onurerdogan/Desktop/PROJE_IPRICE/PYTHON_SERVER

# Container'ları başlat
docker-compose up -d

# Selenium worker log'una gir
docker-compose logs -f selenium-worker
```

### 2. Manuel Job Gönderme (Test için)

Python scripti ile RabbitMQ'ya manuel job gönder:

```python
import pika
import json

# RabbitMQ connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='68.219.209.108',
        port=5672,
        virtual_host='azure',
        credentials=pika.PlainCredentials('admin', '41jqJ526lOxP')
    )
)
channel = connection.channel()

# Job data
job_data = {
    "job_id": 999,
    "company_id": 64,
    "product_id": 0,
    "application_id": 2,
    "server_id": 2,
    "server_name": "azure",
    "screenshot": False,
    "marketplace": False,
    "use_proxy": True,
    "proxy_type": "BrightData",
    "url": "https://www.gurgencler.com.tr/airpods-4-aktif-gurultu-engelleme-ozellikli-mxp93tu-a",
    "npm": "TEST",
    "attributes": [
        {
            "attributes_id": 1,
            "attributes_name": "price",
            "attributes_type": "meta",
            "attributes_value": "unit_sale_price"
        }
    ]
}

# Publish
channel.basic_publish(
    exchange='',
    routing_key='selenium.queue',
    body=json.dumps(job_data)
)

print("✅ Test job gönderildi")
connection.close()
```

### 3. Production'da Gerçek Job İzleme

```bash
# SSH ile sunucuya bağlan
ssh root@68.219.209.108

# Real-time log izle
docker-compose logs -f selenium-worker | grep -E "Job ID: 212|PROXY|META|insider_object|price:"

# Son 100 satırı göster
docker-compose logs --tail=100 selenium-worker
```

---

## ✅ Başarı Kriterleri

Parse işleminin başarılı olması için şu mesajları görmelisiniz:

1. ✅ `META attribute detected: price = unit_sale_price`
2. ✅ `Undetected Selenium proxy kullanılıyor`
3. ✅ `insider_object durumu: True`
4. ✅ `Direkt unit_sale_price değeri: 9999`
5. ✅ `price: 9999`
6. ✅ `Selenium parsing başarılı`

---

## 🆘 Acil Durum Komutları

```bash
# Container'ı yeniden başlat (hemen)
docker-compose restart selenium-worker

# Container'ı durdur ve sil (temiz başlangıç)
docker-compose down
docker-compose up -d --build

# Log dosyasını temizle
> logs/selenium_worker.log

# RabbitMQ queue'sunu temizle (dikkatli kullan!)
docker exec -it <rabbitmq_container> rabbitmqctl purge_queue selenium.queue
```

---

## 📞 Destek

Sorun devam ederse, şu bilgileri toplayın:

1. **Container log'ları** (son 200 satır):
   ```bash
   docker-compose logs --tail=200 selenium-worker > selenium_debug.log
   ```

2. **Job data** (RabbitMQ'dan gelen):
   ```json
   {
     "job_id": 212,
     "attributes": [...]
   }
   ```

3. **Hata mesajı**:
   ```
   "Attribute'lar parse edilemedi: price (1/1)"
   ```

4. **Proxy durumu**:
   ```bash
   grep "PROXY" selenium_debug.log
   ```




