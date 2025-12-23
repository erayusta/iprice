#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Worker Debug Script
RabbitMQ'dan gelen veriyi nasıl işlediğini gösterir
"""

import json
import sys
import os

# Project root'u path'e ekle
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy import - sadece transform için gerekli
try:
    from app.parsers.selenium_parser import SeleniumParser
    PARSER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Parser import edilemedi: {e}")
    print("   (Bu normal, sadece akışı göstereceğiz)")
    PARSER_AVAILABLE = False


def print_section(title: str):
    """Görsel ayrıcı"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_selenium_worker_flow():
    """Selenium Worker'ın veri işleme akışını test et"""
    
    # Örnek RabbitMQ mesajı (kullanıcının verdiği format)
    sample_job_data = {
        "job_id": 178,
        "company_id": 31,
        "product_id": 113,
        "application_id": 2,
        "server_id": 2,
        "server_name": "azure",
        "screenshot": False,
        "marketplace": False,
        "use_proxy": False,
        "proxy_type": None,
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
    
    print_section("📥 GELEN RABBITMQ MESAJI")
    print(json.dumps(sample_job_data, indent=2, ensure_ascii=False))
    
    print_section("🔄 ADIM 1: BaseWorker._callback() -> RabbitMQ'dan veri alınıyor")
    print("""
    BaseWorker._callback() metodu:
    1. RabbitMQ'dan JSON mesajını alır
    2. json.loads(body) ile parse eder
    3. self.process_job(job_data) çağırır
    """)
    
    print_section("🔄 ADIM 2: SeleniumWorker.process_job() -> Veri çıkarılıyor")
    print("""
    SeleniumWorker.process_job() metodu şu alanları çıkarır:
    - url = job_data['url']
    - company_id = job_data['company_id']
    - application_id = job_data['application_id']
    - server_id = job_data['server_id']
    - job_id = job_data.get('job_id')
    - product_id = job_data.get('product_id')
    - npm = job_data.get('npm')
    - attributes = job_data.get('attributes', [])
    """)
    
    # Gerçek veri çıkarma işlemini göster
    url = sample_job_data['url']
    company_id = sample_job_data['company_id']
    application_id = sample_job_data['application_id']
    server_id = sample_job_data['server_id']
    job_id = sample_job_data.get('job_id')
    product_id = sample_job_data.get('product_id')
    npm = sample_job_data.get('npm')
    attributes = sample_job_data.get('attributes', [])
    
    print(f"✅ Çıkarılan veriler:")
    print(f"   URL: {url}")
    print(f"   Company ID: {company_id}")
    print(f"   Application ID: {application_id}")
    print(f"   Server ID: {server_id}")
    print(f"   Job ID: {job_id}")
    print(f"   Product ID: {product_id}")
    print(f"   NPM: {npm}")
    print(f"   Attributes sayısı: {len(attributes)}")
    print(f"   Attributes: {json.dumps(attributes, indent=2, ensure_ascii=False)}")
    
    print_section("🔄 ADIM 3: SeleniumParser.parse() -> Attribute'lar dönüştürülüyor")
    print("""
    SeleniumParser._transform_attributes() metodu:
    RabbitMQ'dan gelen attribute formatını parser'ın beklediği formata çevirir.
    
    GELEN FORMAT:
    {
        "attributes_name": "price",
        "attributes_type": "class",
        "attributes_value": ".sc-94eb08bc-0.dqaOrX"
    }
    
    DÖNÜŞTÜRÜLMÜŞ FORMAT:
    {
        "price": {
            "selector": ".sc-94eb08bc-0.dqaOrX",
            "selector_type": "css"
        }
    }
    """)
    
    # Transform işlemini göster
    if PARSER_AVAILABLE:
        try:
            parser = SeleniumParser()
            transformed_attributes = parser._transform_attributes(attributes)
            
            print(f"✅ Dönüştürülmüş attributes:")
            print(json.dumps(transformed_attributes, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ Transform hatası: {e}")
            transformed_attributes = {
                "price": {
                    "selector": ".sc-94eb08bc-0.dqaOrX",
                    "selector_type": "css"
                }
            }
            print(f"✅ Örnek dönüştürülmüş attributes:")
            print(json.dumps(transformed_attributes, indent=2, ensure_ascii=False))
    else:
        transformed_attributes = {
            "price": {
                "selector": ".sc-94eb08bc-0.dqaOrX",
                "selector_type": "css"
            }
        }
        print(f"✅ Örnek dönüştürülmüş attributes:")
        print(json.dumps(transformed_attributes, indent=2, ensure_ascii=False))
    
    print_section("🔄 ADIM 4: Selenium Driver ile sayfa açılıyor")
    print("""
    SeleniumParser.parse() metodu:
    1. Undetected ChromeDriver oluşturur (_create_driver)
    2. driver.get(url) ile sayfayı açar
    3. Sayfa yüklenmesini bekler (20 saniye timeout)
    4. Cloudflare challenge kontrolü yapar
    5. AJAX yüklenmesi için 8 saniye bekler
    """)
    
    print_section("🔄 ADIM 5: Attribute'lar extract ediliyor")
    print("""
    SeleniumParser._extract_attributes() metodu:
    Her attribute için:
    1. Selector tipine göre element bulur (CSS/XPath/ID)
    2. WebDriverWait ile elementi bekler (20 saniye timeout)
    3. Element.text ile değeri alır
    4. Eğer text boşsa, value attribute'unu veya innerHTML'i dener
    5. Sonuçları results dict'ine ekler
    
    Örnek: price attribute'u için
    - Selector: ".sc-94eb08bc-0.dqaOrX"
    - Selector Type: CSS
    - Element bulunur ve text'i alınır
    """)
    
    print_section("🔄 ADIM 6: Sonuç formatlanıyor")
    print("""
    SeleniumParser._success_result() metodu başarılı sonucu şu formatta döndürür:
    {
        "url": "...",
        "company_id": 31,
        "application_id": 2,
        "server_id": 2,
        "status": "success",
        "parser_used": "selenium",
        "results": {
            "price": "45.999,00 TL"  // Extract edilen değer
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
    """)
    
    print_section("🔄 ADIM 7: Save Queue'ya gönderiliyor")
    print("""
    SeleniumWorker.process_job() metodu:
    Eğer result.get('status') == 'success' ise:
    - self._publish_to_save_queue(result) çağırılır
    - Parse sonucu save.queue'ya gönderilir
    - DB kayıt işlemi için hazırlanır
    
    Eğer başarısız ise:
    - selenium.queue.error'a gönderilir
    """)
    
    print_section("💡 KULLANIM İPUÇLARI")
    print("""
    1. Worker'ı çalıştırmak için:
       python -m app.workers.selenium_worker
       
    2. Log'ları görmek için worker'ın çıktısını takip edin
       
    3. Hata durumunda:
       - selenium.queue.error queue'suna bakın
       - Logs tablosuna kaydedilir
       
    4. Başarılı durumda:
       - save.queue'ya gönderilir
       - SaveWorker bu queue'dan alır ve DB'ye kaydeder
    """)


def test_with_real_parser():
    """Gerçek parser ile test (sadece attribute transform)"""
    print_section("🧪 GERÇEK PARSER İLE TEST (Sadece Transform)")
    
    if not PARSER_AVAILABLE:
        print("⚠️ Parser mevcut değil, transform mantığını manuel gösteriyoruz...")
        _manual_transform_example()
        return
    
    sample_attributes = [
        {
            "company_id": 31,
            "attributes_id": 1,
            "attributes_name": "price",
            "attributes_type": "class",
            "attributes_value": ".sc-94eb08bc-0.dqaOrX"
        }
    ]
    
    try:
        parser = SeleniumParser()
        transformed = parser._transform_attributes(sample_attributes)
        
        print("Dönüştürülmüş attributes:")
        print(json.dumps(transformed, indent=2, ensure_ascii=False))
        
        # Her attribute için detaylı bilgi
        for attr_name, attr_data in transformed.items():
            print(f"\n📋 Attribute: {attr_name}")
            print(f"   Selector: {attr_data.get('selector')}")
            print(f"   Selector Type: {attr_data.get('selector_type')}")
    except Exception as e:
        print(f"⚠️ Transform testi başarısız: {e}")
        _manual_transform_example()


def _manual_transform_example():
    """Manuel transform örneği göster"""
    print("\n📝 Transform mantığı:")
    print("""
    Gelen attribute:
    {
        "attributes_name": "price",
        "attributes_type": "class",
        "attributes_value": ".sc-94eb08bc-0.dqaOrX"
    }
    
    Dönüştürülmüş:
    {
        "price": {
            "selector": ".sc-94eb08bc-0.dqaOrX",
            "selector_type": "css"  // class -> css otomatik tespit
        }
    }
    
    Transform kuralları:
    - attributes_type == "class" -> selector_type = "css"
    - attributes_type == "xpath" -> selector_type = "xpath"
    - attributes_value // ile başlıyorsa -> "xpath"
    - attributes_value # ile başlıyorsa -> "id"
    """)


if __name__ == "__main__":
    print("\n" + "🧪"*40)
    print("SELENIUM WORKER DEBUG TEST")
    print("🧪"*40)
    
    try:
        # Sadece akışı göster (gerçek scraping yapmadan)
        test_selenium_worker_flow()
        
        # Transform testi
        test_with_real_parser()
        
        print_section("✅ TEST TAMAMLANDI")
        print("""
        Not: Bu script sadece akışı gösterir, gerçek scraping yapmaz.
        Gerçek test için RabbitMQ'ya mesaj gönderin veya worker'ı çalıştırın.
        """)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

