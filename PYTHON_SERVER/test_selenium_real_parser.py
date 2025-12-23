#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Real Parser Test
Gerçek parser kodunu kullanarak URL'ye istek atıp ne döndüğünü gösterir
"""

import json
import sys
import os

# Project root'u path'e ekle
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test verisi - Gürgençler (Meta attribute)
TEST_JOB_DATA = {
    "job_id": 181,
    "company_id": 64,
    "product_id": 729,
    "application_id": 2,
    "server_id": 2,
    "server_name": "azure",
    "screenshot": False,
    "marketplace": False,
    "use_proxy": False,
    "proxy_type": None,
    "url": "https://www.gurgencler.com.tr/macbook-air-13-inc-apple-m4-cip-10-cekirdek-cpu-8-cekirdek-gpu-16gb-bellek-256gb-gokyuzu-mavisi-mc6t4tu-a",
    "npm": "MC6T4TU/A",
    "attributes": [
        {
            "company_id": 64,
            "attributes_id": 1,
            "attributes_name": "price",
            "attributes_type": "meta",
            "attributes_value": "unit_sale_price"
        }
    ]
}

# Alternatif test verisi - MediaMarkt (CSS selector)
TEST_JOB_DATA_MEDIAMARKT = {
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


def test_with_real_parser():
    """Gerçek parser ile test"""
    
    print("="*80)
    print("🧪 GERÇEK SELENIUM PARSER TEST")
    print("="*80)
    print(f"\n📡 Test URL: {TEST_JOB_DATA['url']}\n")
    
    try:
        from app.parsers.selenium_parser import SeleniumParser
        
        print("✅ Parser import edildi\n")
        
        # Parser oluştur
        parser = SeleniumParser()
        
        # Job data'yı göster
        print("="*80)
        print("📥 JOB DATA")
        print("="*80)
        print(json.dumps(TEST_JOB_DATA, indent=2, ensure_ascii=False))
        print()
        
        # Attribute'ları transform et
        print("="*80)
        print("🔄 ATTRIBUTE TRANSFORM")
        print("="*80)
        raw_attributes = TEST_JOB_DATA.get('attributes', [])
        transformed = parser._transform_attributes(raw_attributes)
        print("Dönüştürülmüş attributes:")
        print(json.dumps(transformed, indent=2, ensure_ascii=False))
        print()
        
        # Parse işlemini başlat
        print("="*80)
        print("🌐 PARSING İŞLEMİ BAŞLIYOR")
        print("="*80)
        print("⚠️  Bu işlem biraz zaman alabilir (60+ saniye)...")
        print("⚠️  Driver oluşturuluyor, sayfa yükleniyor...\n")
        
        url = TEST_JOB_DATA['url']
        company_id = TEST_JOB_DATA['company_id']
        application_id = TEST_JOB_DATA['application_id']
        server_id = TEST_JOB_DATA['server_id']
        
        # Parse et
        result = parser.parse(
            url=url,
            company_id=company_id,
            application_id=application_id,
            server_id=server_id,
            job_data=TEST_JOB_DATA
        )
        
        # Sonucu göster
        print("\n" + "="*80)
        print("📊 PARSING SONUCU")
        print("="*80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        
        # Sonuç analizi
        print("="*80)
        print("📋 SONUÇ ANALİZİ")
        print("="*80)
        
        if result.get('status') == 'success':
            print("✅ Parsing BAŞARILI!")
            print(f"\n📊 Extract edilen attribute'lar:")
            results = result.get('results', {})
            for attr_name, attr_value in results.items():
                status = "✅" if attr_value else "❌"
                print(f"   {status} {attr_name}: {attr_value}")
            
            print(f"\n📈 HTTP Status Code: {result.get('http_status_code')}")
            print(f"⏰ Timestamp: {result.get('timestamp')}")
            
        else:
            print("❌ Parsing BAŞARISIZ!")
            print(f"\n🚨 Hata: {result.get('error')}")
            print(f"📈 HTTP Status Code: {result.get('http_status_code')}")
        
        print()
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("\n💡 Lütfen Docker container içinde çalıştırın:")
        print("   docker exec -it <container_name> python3 test_selenium_real_parser.py")
        print("\n💡 Veya venv'i aktif edin:")
        print("   source venv/bin/activate")
        print("   python3 test_selenium_real_parser.py")
    
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


def test_gurgencler():
    """Gürgençler için özel test"""
    print("\n" + "="*80)
    print("🧪 GÜRGENÇLER TEST (Meta Attribute)")
    print("="*80)
    
    global TEST_JOB_DATA
    original_data = TEST_JOB_DATA.copy()
    
    # Gürgençler verisi ile değiştir
    TEST_JOB_DATA = {
        "job_id": 181,
        "company_id": 64,
        "product_id": 729,
        "application_id": 2,
        "server_id": 2,
        "server_name": "azure",
        "screenshot": False,
        "marketplace": False,
        "use_proxy": False,
        "proxy_type": None,
        "url": "https://www.gurgencler.com.tr/macbook-air-13-inc-apple-m4-cip-10-cekirdek-cpu-8-cekirdek-gpu-16gb-bellek-256gb-gokyuzu-mavisi-mc6t4tu-a",
        "npm": "MC6T4TU/A",
        "attributes": [
            {
                "company_id": 64,
                "attributes_id": 1,
                "attributes_name": "price",
                "attributes_type": "meta",
                "attributes_value": "unit_sale_price"
            }
        ]
    }
    
    try:
        test_with_real_parser()
    finally:
        # Orijinal veriyi geri yükle
        TEST_JOB_DATA = original_data


if __name__ == "__main__":
    import sys
    
    # Komut satırı argümanı ile test seçimi
    if len(sys.argv) > 1 and sys.argv[1] == "gurgencler":
        test_gurgencler()
    else:
        test_with_real_parser()

