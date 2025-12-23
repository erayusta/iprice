#!/usr/bin/env python3
"""
Gürgençler Price Extraction Test
window.insider_object.product.unit_sale_price değerini test eder
"""

import sys
import os

# Python path'e app klasörünü ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.parsers.selenium_parser import SeleniumParser

def test_gurgencler_extraction():
    """Test Gürgençler price extraction"""
    
    # Test job data (RabbitMQ'dan gelen GERÇEK data)
    job_data = {
        "job_id": 212,
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
        "npm": None,
        "attributes": [
            {
                "attributes_id": 1,
                "attributes_name": "price",
                "attributes_type": "meta",
                "attributes_value": "unit_sale_price"
            }
        ]
    }
    
    print("=" * 80)
    print("🧪 GÜRGENÇLER PRICE EXTRACTION TEST")
    print("=" * 80)
    print(f"\n📋 Test Parametreleri:")
    print(f"   URL: {job_data['url']}")
    print(f"   MPN: {job_data['npm']}")
    print(f"   Attribute Type: {job_data['attributes'][0]['attributes_type']}")
    print(f"   Attribute Value: {job_data['attributes'][0]['attributes_value']}")
    print(f"   Proxy: {job_data['use_proxy']} ({job_data['proxy_type']})")
    print("\n" + "=" * 80)
    
    # Parser'ı başlat
    parser = SeleniumParser()
    
    # Parse işlemini başlat
    print("\n🚀 Parse işlemi başlıyor...\n")
    
    try:
        result = parser.parse(
            url=job_data['url'],
            company_id=job_data['company_id'],
            application_id=job_data['application_id'],
            server_id=job_data['server_id'],
            job_data=job_data
        )
        
        print("\n" + "=" * 80)
        print("📊 SONUÇ:")
        print("=" * 80)
        
        if result.get('success'):
            print("✅ Parse başarılı!")
            print(f"\n📦 Parse edilen veriler:")
            
            parsed_data = result.get('parsed_data', {})
            for key, value in parsed_data.items():
                print(f"   {key}: {value}")
            
            # Price kontrolü
            price_value = parsed_data.get('price')
            if price_value:
                print(f"\n💰 Fiyat başarıyla alındı: {price_value}")
                
                # Beklenen değer: 9999 (Gürgençler'den)
                if '9999' in str(price_value) or '9.999' in str(price_value):
                    print("✅ Fiyat doğru! (Beklenen: 9999)")
                else:
                    print(f"⚠️ Fiyat beklenenden farklı (Beklenen: 9999, Alınan: {price_value})")
            else:
                print("❌ Fiyat alınamadı!")
                
        else:
            print("❌ Parse başarısız!")
            print(f"\n🔴 Hata mesajı: {result.get('error_message', 'Bilinmeyen hata')}")
            print(f"🔴 HTTP Kodu: {result.get('http_code', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("📝 Tam Sonuç:")
        print("=" * 80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ HATA!")
        print("=" * 80)
        print(f"Hata: {e}")
        
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_gurgencler_extraction()

