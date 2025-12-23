# 🔄 Selenium Worker Veri İşleme Akışı

Bu dokümantasyon, RabbitMQ'dan gelen verinin Selenium servisi tarafından nasıl işlendiğini detaylı olarak açıklar.

## 📥 Gelen Veri Formatı

RabbitMQ'dan gelen örnek mesaj:

```json
{
  "job_id": 178,
  "company_id": 31,
  "product_id": 113,
  "application_id": 2,
  "server_id": 2,
  "server_name": "azure",
  "screenshot": false,
  "marketplace": false,
  "use_proxy": false,
  "proxy_type": null,
  "url": "https://www.mediamarkt.com.tr/tr/product/_apple-airpods-bluetooth-kulak-ici-kulaklik-mxp63tua-1239693.html",
  "npm": "MXP63TU/A",
  "attributes": [
    {
      "company_id": 31,
      "attributes_id": 1,
      "attributes_name": "price",
      "attributes_type": "class",
      "attributes_value": ".sc-94eb08bc-0.dqaOrX"
    }
  ]
}
```

## 🔄 İşleme Akışı

### ADIM 1: RabbitMQ'dan Mesaj Alınıyor

**Dosya:** `app/workers/base_worker.py`

```python
def _callback(self, ch, method, properties, body):
    # 1. JSON mesajını parse et
    job_data = json.loads(body)
    
    # 2. Worker'ın process_job metodunu çağır
    result = self.process_job(job_data)
    
    # 3. Sonuca göre ACK/NACK yap
    if result.get('status') == 'success':
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

**Önemli:** 
- Her mesaj için 1-3 saniye random delay var (rate limiting)
- `prefetch_count=1` olduğu için aynı anda sadece 1 mesaj işlenir

---

### ADIM 2: SeleniumWorker Veriyi İşliyor

**Dosya:** `app/workers/selenium_worker.py`

```python
def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
    # Verileri çıkar
    url = job_data['url']
    company_id = job_data['company_id']
    application_id = job_data['application_id']
    server_id = job_data['server_id']
    job_id = job_data.get('job_id')
    product_id = job_data.get('product_id')
    npm = job_data.get('npm')
    
    # Parser'ı al ve parse et
    parser = ParserFactory.get_parser('selenium')
    result = parser.parse(url, company_id, application_id, server_id, job_data=job_data)
    
    # Başarılı ise save.queue'ya gönder
    if result.get('status') == 'success':
        self._publish_to_save_queue(result)
    
    return result
```

**Çıkarılan Veriler:**
- `url`: Ürün sayfası URL'i
- `company_id`: Şirket ID'si
- `application_id`: Uygulama ID'si
- `server_id`: Sunucu ID'si
- `job_id`: İş ID'si (opsiyonel)
- `product_id`: Ürün ID'si (opsiyonel)
- `npm`: Ürün NPM kodu (opsiyonel)
- `attributes`: Parse edilecek attribute'lar listesi

---

### ADIM 3: Attribute'lar Dönüştürülüyor

**Dosya:** `app/parsers/selenium_parser.py`

**Gelen Format (RabbitMQ):**
```json
{
  "attributes_name": "price",
  "attributes_type": "class",
  "attributes_value": ".sc-94eb08bc-0.dqaOrX"
}
```

**Dönüştürülmüş Format (Parser):**
```json
{
  "price": {
    "selector": ".sc-94eb08bc-0.dqaOrX",
    "selector_type": "css"
  }
}
```

**Transform Kuralları:**
- `attributes_type == "class"` → `selector_type = "css"`
- `attributes_type == "xpath"` → `selector_type = "xpath"`
- `attributes_type == "id"` → `selector_type = "id"`
- `attributes_type == "meta"` → `selector_type = "meta"` (özel işlem)
- `attributes_value` `//` ile başlıyorsa → otomatik `"xpath"`
- `attributes_value` `#` ile başlıyorsa → otomatik `"id"`

**Kod:**
```python
def _transform_attributes(self, raw_attributes: list) -> Dict[str, Any]:
    attributes = {}
    for attr in raw_attributes:
        attr_name = attr.get('attributes_name')
        attr_type = attr.get('attributes_type')
        attr_value = attr.get('attributes_value')
        
        # Selector type belirleme mantığı
        if attr_type == 'meta':
            attributes[attr_name] = {
                'selector': attr_value,
                'selector_type': 'meta',
                'meta_value': attr_value
            }
        elif attr_type == 'xpath' or attr_value.startswith('//'):
            attributes[attr_name] = {
                'selector': attr_value,
                'selector_type': 'xpath'
            }
        elif attr_type == 'id' or attr_value.startswith('#'):
            attributes[attr_name] = {
                'selector': attr_value,
                'selector_type': 'id'
            }
        else:  # class, css
            attributes[attr_name] = {
                'selector': attr_value,
                'selector_type': 'css'
            }
    
    return attributes
```

---

### ADIM 4: Selenium Driver Oluşturuluyor

**Dosya:** `app/parsers/selenium_parser.py` → `_create_driver()`

**Özellikler:**
- Undetected ChromeDriver kullanılır (anti-bot bypass)
- Headless mod aktif (`--headless=new`)
- Random user agent
- Proxy desteği (job_data'dan dinamik)
- WebDriver özellikleri gizlenir

**Kod:**
```python
def _create_driver(self):
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    
    # Proxy ayarları
    proxy_url = proxy_manager.get_selenium_proxy(job_data=self.job_data)
    if proxy_url:
        options.add_argument(f'--proxy-server=http://{proxy_url}')
    
    driver = uc.Chrome(options=options, ...)
    driver.set_page_load_timeout(60)
    
    # WebDriver gizleme
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver
```

---

### ADIM 5: Sayfa Açılıyor ve Yükleniyor

**Dosya:** `app/parsers/selenium_parser.py` → `parse()`

**İşlemler:**
1. `driver.get(url)` ile sayfa açılır
2. Sayfa yüklenmesi beklenir (20 saniye timeout)
3. Cloudflare challenge kontrolü yapılır (`_handle_cloudflare_challenge`)
4. AJAX yüklenmesi için 8 saniye beklenir
5. JavaScript'ten fiyat alınmaya çalışılır (backup için)

**Kod:**
```python
driver.get(url)

# Sayfa yüklenene kadar bekle
WebDriverWait(driver, 20).until(
    lambda d: d.execute_script('return document.readyState') == 'complete'
)

# Cloudflare bypass
self._handle_cloudflare_challenge(driver)

# AJAX bekle
time.sleep(8)
```

---

### ADIM 6: Attribute'lar Extract Ediliyor

**Dosya:** `app/parsers/selenium_parser.py` → `_extract_attributes()`

**Her Attribute İçin:**
1. Selector tipine göre element bulunur (CSS/XPath/ID)
2. `WebDriverWait` ile element beklenir (20 saniye timeout)
3. Element bulunursa:
   - `element.text` ile değer alınır
   - Eğer boşsa `element.get_attribute('value')` denenir
   - Hala boşsa `element.get_attribute('innerHTML')` denenir
4. Sonuç `results` dict'ine eklenir

**Özel Durumlar:**
- **Meta/JSON tipi:** `_extract_meta_json_value()` kullanılır
- **Price attribute için:** JavaScript'ten fiyat alınmaya çalışılır (backup)
- **Element bulunamazsa:** `None` değeri kaydedilir

**Kod:**
```python
def _extract_attributes(self, driver, attributes: Dict[str, Any]) -> Dict[str, Any]:
    results = {}
    
    for attr_name, attr_data in attributes.items():
        selector = attr_data.get('selector')
        selector_type = attr_data.get('selector_type')
        
        # Meta tipi özel işlem
        if selector_type == 'meta':
            meta_result = self._extract_meta_json_value(driver, meta_value)
            results[attr_name] = str(meta_result) if meta_result else None
            continue
        
        # Element bul
        if selector_type == 'xpath':
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
        elif selector_type == 'id':
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, selector.replace('#', '')))
            )
        else:  # css
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        
        # Değeri al
        value = element.text.strip() if element.text else None
        if not value:
            value = element.get_attribute('value')
        if not value:
            value = element.get_attribute('innerHTML')
        
        results[attr_name] = value
    
    return results
```

---

### ADIM 7: Sonuç Formatlanıyor

**Dosya:** `app/parsers/base.py` → `_success_result()`

**Başarılı Sonuç Formatı:**
```json
{
  "url": "https://www.mediamarkt.com.tr/...",
  "company_id": 31,
  "application_id": 2,
  "server_id": 2,
  "status": "success",
  "parser_used": "selenium",
  "results": {
    "price": "45.999,00 TL"
  },
  "http_status_code": 200,
  "timestamp": 1234567890.123,
  "job_id": 178,
  "product_id": 113,
  "npm": "MXP63TU/A",
  "server_name": "azure",
  "screenshot": false,
  "marketplace": false,
  "attributes": [...]  // Orijinal attributes listesi
}
```

**Hata Sonucu Formatı:**
```json
{
  "url": "https://www.mediamarkt.com.tr/...",
  "company_id": 31,
  "application_id": 2,
  "server_id": 2,
  "status": "error",
  "parser_used": "selenium",
  "error": "Attribute'lar parse edilemedi: price",
  "http_status_code": 200,
  "timestamp": 1234567890.123,
  "job_id": 178,
  "product_id": 113,
  "npm": "MXP63TU/A"
}
```

---

### ADIM 8: Save Queue'ya Gönderiliyor

**Dosya:** `app/workers/base_worker.py` → `_publish_to_save_queue()`

**Başarılı Durumda:**
- Parse sonucu `save.queue`'ya gönderilir
- `SaveWorker` bu queue'dan alır ve DB'ye kaydeder

**Başarısız Durumda:**
- Hata sonucu `selenium.queue.error`'a gönderilir
- `logs` tablosuna kaydedilir

**Kod:**
```python
def _publish_to_save_queue(self, result: Dict[str, Any]):
    save_payload = {
        **result,  # Tüm parse sonuçlarını dahil et
        'queue_job_id': str(uuid.uuid4()),
        'save_timestamp': datetime.now().isoformat()
    }
    
    self.channel.basic_publish(
        exchange='',
        routing_key='save.queue',
        body=json.dumps(save_payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )
```

---

## 🐛 Debug İpuçları

### 1. Worker Log'larını İzleme

```bash
# Docker container içinde
docker exec -it <container_name> tail -f /app/logs/worker.log

# Veya direkt worker çıktısını izle
docker logs -f <selenium_worker_container>
```

### 2. Test Scripti Çalıştırma

```bash
cd PYTHON_SERVER
python3 test_selenium_worker_debug.py
```

### 3. RabbitMQ Queue'larını İzleme

```bash
# Queue mesajlarını görmek için
docker exec -it <rabbitmq_container> rabbitmqctl list_queues

# Belirli bir queue'dan mesaj okumak için
docker exec -it <rabbitmq_container> rabbitmqadmin get queue=selenium.queue
```

### 4. Sık Karşılaşılan Sorunlar

**Sorun:** Attributes parse edilemiyor
- **Çözüm:** Selector'ların doğru olduğundan emin olun
- **Kontrol:** `_extract_attributes()` metodunda log'lara bakın

**Sorun:** Element bulunamıyor
- **Çözüm:** Timeout süresini artırın (şu an 20 saniye)
- **Kontrol:** Sayfa yüklenmesi için yeterli süre beklendiğinden emin olun

**Sorun:** Cloudflare challenge
- **Çözüm:** `_handle_cloudflare_challenge()` metodunu kontrol edin
- **Kontrol:** Undetected ChromeDriver kullanıldığından emin olun

---

## 📋 Özet

**Veri Akışı:**
```
RabbitMQ → BaseWorker._callback() 
       → SeleniumWorker.process_job() 
       → SeleniumParser.parse() 
       → _transform_attributes() 
       → _create_driver() 
       → driver.get(url) 
       → _extract_attributes() 
       → _success_result() 
       → save.queue
```

**Ana Dosyalar:**
- `app/workers/base_worker.py` - Base worker ve RabbitMQ callback
- `app/workers/selenium_worker.py` - Selenium worker implementasyonu
- `app/parsers/selenium_parser.py` - Selenium parsing mantığı
- `app/parsers/base.py` - Parser base class ve result formatting

**Önemli Metodlar:**
- `SeleniumWorker.process_job()` - Ana işleme metodu
- `SeleniumParser.parse()` - Parse işlemi
- `SeleniumParser._transform_attributes()` - Attribute dönüştürme
- `SeleniumParser._extract_attributes()` - Attribute extraction
- `SeleniumParser._create_driver()` - Driver oluşturma

