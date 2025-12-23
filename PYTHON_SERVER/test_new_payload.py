#!/usr/bin/env python3
"""
Yeni Payload Yapısı Test Scripti
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/v1/parse-url"

# Yeni payload yapısı
test_payload = {
    "job_id": 20,
    "company_id": 2,
    "product_id": 2991,
    "application_id": 2,
    "server_id": 1,
    "server_name": "/local",
    "screenshot": False,
    "marketplace": False,
    "url": "https://www.troyestore.com/apple-macbook-air-13-m4-cip-10-cekirdekli-cpu-8-cekirdekli-gpu-16gb-bellek-256gb-ssd-gece-yarisi_217959",
    "npm": "MW123TU/A",
    "attributes": [
        {
            "company_id": 2,
            "attributes_id": 1,
            "attributes_name": "price",
            "attributes_type": "class",
            "attributes_value": ".p-price span"
        },
        {
            "company_id": 2,
            "attributes_id": 5,
            "attributes_name": "product_title",
            "attributes_type": "xpath",
            "attributes_value": "//h1[contains(@class, 'product-title') or contains(@class, 'title')]/text()"
        },
        {
            "company_id": 2,
            "attributes_id": 6,
            "attributes_name": "is_stock",
            "attributes_type": "class",
            "attributes_value": ".sticky-action-area"
        },
        {
            "company_id": 2,
            "attributes_id": 7,
            "attributes_name": "is_redirect",
            "attributes_type": "class",
            "attributes_value": "a"
        }
    ],
    "parser_type": "scrapy"  # Opsiyonel - default scrapy
}


def test_api():
    """API'ye test payload'ı gönder"""
    print("=" * 80)
    print("🧪 YENİ PAYLOAD YAPISI TEST")
    print("=" * 80)
    
    print("\n📦 Payload:")
    print(json.dumps(test_payload, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("📤 API'ye gönderiliyor...")
    print("=" * 80)
    
    try:
        response = requests.post(
            API_URL,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n✅ HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n📥 Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n" + "=" * 80)
            print("✅ TEST BAŞARILI!")
            print("=" * 80)
            print("\n💡 Sonraki Adımlar:")
            print("   1. Worker loglarını kontrol edin:")
            print("      docker-compose logs -f scrapy-worker")
            print("\n   2. RabbitMQ panelinde queue'ları kontrol edin:")
            print("      http://68.219.209.108:15672")
            print("      - scrapy.queue: İş kuyruğu")
            print("      - scrapy.queue.completed: Başarılı sonuçlar")
            print("      - scrapy.queue.error: Hatalı sonuçlar")
            print("\n   3. Job ID ile sonuçları takip edin:")
            print(f"      Job ID: {result.get('job_id')}")
            print("=" * 80)
            
        else:
            print(f"\n❌ API Hatası:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ BAĞLANTI HATASI!")
        print("API servisi çalışmıyor olabilir.")
        print("\nÇözüm:")
        print("  docker-compose ps")
        print("  docker-compose up -d")
        
    except Exception as e:
        print(f"\n❌ TEST HATASI: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_products():
    """Birden fazla ürün test et"""
    print("\n" + "=" * 80)
    print("🔄 ÇOKLU ÜRÜN TESTİ")
    print("=" * 80)
    
    test_products = [
        {
            "job_id": 21,
            "product_id": 2992,
            "url": "https://www.example.com/product1",
            "npm": "PROD001"
        },
        {
            "job_id": 22,
            "product_id": 2993,
            "url": "https://www.example.com/product2",
            "npm": "PROD002"
        },
        {
            "job_id": 23,
            "product_id": 2994,
            "url": "https://www.example.com/product3",
            "npm": "PROD003"
        }
    ]
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Ürün gönderiliyor - Job ID: {product['job_id']}")
        
        payload = test_payload.copy()
        payload.update(product)
        
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Gönderildi - Queue Job ID: {result.get('queue_job_id')}")
            else:
                print(f"   ❌ Hata: {response.status_code}")
        except Exception as e:
            print(f"   ❌ İstek hatası: {e}")
    
    print("\n" + "=" * 80)
    print("✅ ÇOKLU TEST TAMAMLANDI")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--multiple":
        test_multiple_products()
    else:
        test_api()
    
    print("\n")

