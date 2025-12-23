#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Detaylı Test - Tam Yanıt Gösterimi
"""

import json
import sys
import os
import time

sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TEST_URL = "https://www.mediamarkt.com.tr/tr/product/_apple-airpods-bluetooth-kulak-ici-kulaklik-mxp63tua-1239693.html"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_detailed_response():
    """Detaylı yanıt testi"""
    
    print_section("🔍 SELENIUM DETAYLI TEST")
    print(f"📡 URL: {TEST_URL}\n")
    
    try:
        from app.parsers.selenium_parser import SeleniumParser
        
        # Test job data
        job_data = {
            "job_id": 178,
            "company_id": 31,
            "product_id": 113,
            "application_id": 2,
            "server_id": 2,
            "url": TEST_URL,
            "npm": "MXP63TU/A",
            "attributes": [
                {
                    "attributes_name": "price",
                    "attributes_type": "class",
                    "attributes_value": ".sc-94eb08bc-0.dqaOrX"
                }
            ]
        }
        
        print_section("📋 TEST VERİSİ")
        print(json.dumps(job_data, indent=2, ensure_ascii=False))
        
        # Parser oluştur
        parser = SeleniumParser()
        
        print_section("🌐 PARSING BAŞLIYOR")
        print("⏳ Lütfen bekleyin (60-90 saniye sürebilir)...\n")
        
        start_time = time.time()
        
        result = parser.parse(
            url=TEST_URL,
            company_id=31,
            application_id=2,
            server_id=2,
            job_data=job_data
        )
        
        elapsed_time = time.time() - start_time
        
        print_section("📊 PARSING SONUCU")
        print(f"⏱️  Süre: {elapsed_time:.2f} saniye\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print_section("✅ SONUÇ ÖZETİ")
        
        if result.get('status') == 'success':
            print("✅ ✅ ✅ BAŞARILI ✅ ✅ ✅\n")
            
            results = result.get('results', {})
            print("📊 Extract Edilen Değerler:")
            for attr_name, attr_value in results.items():
                status_icon = "✅" if attr_value else "❌"
                print(f"   {status_icon} {attr_name}: {attr_value}")
            
            print(f"\n📈 HTTP Status: {result.get('http_status_code')}")
            print(f"🔧 Parser: {result.get('parser_used')}")
            print(f"🆔 Job ID: {result.get('job_id')}")
            print(f"📦 Product ID: {result.get('product_id')}")
            print(f"🏷️  NPM: {result.get('npm')}")
            
        else:
            print("❌ ❌ ❌ BAŞARISIZ ❌ ❌ ❌\n")
            print(f"🚨 Hata: {result.get('error')}")
            print(f"📈 HTTP Status: {result.get('http_status_code')}")
        
        print_section("💡 SONRAKI ADIMLAR")
        
        if result.get('status') == 'success':
            print("""
1. ✅ Parse başarılı! Değerler çıkarıldı.
2. 📤 Bu sonuç save.queue'ya gönderilecek
3. 💾 SaveWorker DB'ye kaydedecek
4. 🎉 İşlem tamamlandı!
            """)
        else:
            print("""
1. ❌ Parse başarısız oldu
2. 🔍 Hatayı kontrol edin:
   - Selector doğru mu?
   - Sayfa yüklendi mi?
   - Element bulunabildi mi?
3. 📝 Logs tablosuna kaydedildi
            """)
        
    except Exception as e:
        print_section("❌ HATA")
        print(f"🚨 {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_response()

