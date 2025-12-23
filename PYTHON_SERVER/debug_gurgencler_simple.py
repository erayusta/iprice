#!/usr/bin/env python3
"""
Simple Debug Script - Gürgençler Price Extraction
Sadece kritik noktaları test et
"""

import os
import sys

# Set env variables
os.environ['PROXY_ENABLED'] = 'true'
os.environ['PROXY_TYPE'] = 'brightdata'

# Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Job data (RabbitMQ'dan gelen)
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
print("🔍 DEBUG: GÜRGENÇLER PRICE EXTRACTION")
print("=" * 80)

# 1. Proxy Manager Kontrolü
print("\n📌 1. PROXY MANAGER KONTROLÜ")
print("-" * 80)
try:
    from app.services.ProxyManager import get_proxy_manager
    
    proxy_manager = get_proxy_manager()
    proxy_url = proxy_manager.get_proxy(job_data=job_data)
    
    print(f"✅ Proxy Manager çalışıyor")
    print(f"   use_proxy: {job_data.get('use_proxy')}")
    print(f"   proxy_type: {job_data.get('proxy_type')}")
    print(f"   Dönen proxy: {proxy_url[:50] if proxy_url else 'None'}...")
    
    if not proxy_url:
        print("❌ HATA: Proxy URL boş!")
        print("   Brightdata credentials .env dosyasında mı?")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ HATA: Proxy Manager başlatılamadı: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Attribute Transform Kontrolü
print("\n📌 2. ATTRIBUTE TRANSFORM KONTROLÜ")
print("-" * 80)

raw_attributes = job_data.get('attributes', [])
print(f"Raw attributes: {raw_attributes}")

# Transform logic (selenium_parser.py'den)
attributes = {}
for attr in raw_attributes:
    attr_name = attr.get('attributes_name')
    attr_type = attr.get('attributes_type')
    attr_value = attr.get('attributes_value')
    
    print(f"\n   Attribute:")
    print(f"      name: {attr_name}")
    print(f"      type: {attr_type}")
    print(f"      value: {attr_value}")
    
    # Meta type kontrolü
    if str(attr_type).lower() == 'meta' and attr_value:
        attributes[attr_name] = {
            'selector': attr_value,
            'selector_type': 'meta',
            'meta_value': attr_value
        }
        print(f"   ✅ META attribute detected: {attr_name} -> {attr_value}")
    else:
        print(f"   ⚠️ NOT a meta attribute!")

print(f"\nTransformed attributes: {attributes}")

if not attributes:
    print("❌ HATA: Attributes boş!")
    sys.exit(1)

# 3. Meta Attribute Kontrolü
print("\n📌 3. META ATTRIBUTE KONTROLÜ")
print("-" * 80)

has_meta_attributes = any(
    str(attr.get('attributes_type', '')).lower() == 'meta' 
    for attr in raw_attributes
)

print(f"Has meta attributes: {has_meta_attributes}")

if not has_meta_attributes:
    print("❌ HATA: Meta attribute bulunamadı!")
    print("   attributes_type değeri 'meta' olmalı")
    sys.exit(1)

# 4. Meta Extractor Test
print("\n📌 4. META EXTRACTOR TEST (JavaScript Snippet)")
print("-" * 80)

js_snippet = """
// 1. insider_object kontrolü
if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
    console.log('✅ insider_object.product.unit_sale_price:', window.insider_object.product.unit_sale_price);
    return window.insider_object.product.unit_sale_price;
}

// 2. Meta tag kontrolü
var metaPrice = document.querySelector('meta[property="product:price:amount"]');
if (metaPrice) {
    console.log('✅ Meta tag price:', metaPrice.getAttribute('content'));
    return metaPrice.getAttribute('content');
}

console.log('❌ Fiyat bulunamadı');
return null;
"""

print("JavaScript snippet (Selenium'da çalıştırılacak):")
print(js_snippet)

print("\n" + "=" * 80)
print("✅ TÜM KONTROLER BAŞARILI!")
print("=" * 80)
print("\nSONRAKİ ADIM:")
print("1. Selenium parser'ı bu job_data ile çalıştırın")
print("2. Selenium log'larını kontrol edin:")
print("   - 'Meta attribute tespit edildi' mesajı var mı?")
print("   - 'insider_object durumu: True' var mı?")
print("   - 'unit_sale_price değeri' ne gösteriyor?")
print("\n3. Eğer insider_object False ise:")
print("   - Cloudflare challenge olabilir")
print("   - Proxy çalışmıyor olabilir")
print("   - JavaScript yüklenmiyor olabilir")




