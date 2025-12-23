#!/usr/bin/env python3
"""
🔒 Proxy Manager Test Script
=============================
Proxy ayarlarınızı test edin ve istatistikleri görün

Kullanım:
    python test_proxy.py
"""

import sys
import os

# Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ProxyManager import get_proxy_manager
import requests
from datetime import datetime


def print_header(text):
    """Başlık yazdır"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_proxy_manager():
    """Proxy Manager'ı test et"""
    
    print_header("🔒 PROXY MANAGER TEST")
    print(f"Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Proxy manager oluştur
    proxy_manager = get_proxy_manager()
    
    # 1. Ayarları göster
    print_header("📋 AYARLAR (.env)")
    print(f"Proxy Enabled: {proxy_manager.enabled}")
    print(f"Proxy Type: {proxy_manager.proxy_type}")
    print(f"Free Proxy File: {proxy_manager.free_proxy_file}")
    print(f"Free Proxy Test: {proxy_manager.free_proxy_test_enabled}")
    print(f"Smartproxy User: {proxy_manager.smartproxy_user or '(boş)'}")
    print(f"Smartproxy Endpoint: {proxy_manager.smartproxy_endpoint}")
    print(f"Custom Proxy URL: {proxy_manager.custom_proxy_url or '(boş)'}")
    
    # 2. İstatistikleri göster
    print_header("📊 İSTATİSTİKLER")
    stats = proxy_manager.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 3. Proxy al ve test et
    if not proxy_manager.enabled:
        print_header("⚠️ PROXY KAPALI")
        print("Proxy kullanımı .env'de kapalı!")
        print("Etkinleştirmek için .env'de PROXY_ENABLED=true yapın")
        return
    
    print_header("🔍 PROXY TEST")
    
    # Tüm proxy tiplerini test et
    test_types = {
        'none': 'Proxy Yok',
        'free': 'Free Proxy',
        'smartproxy': 'Smartproxy',
        'custom': 'Custom Proxy'
    }
    
    for proxy_type, name in test_types.items():
        print(f"\n🧪 Test: {name}")
        print("-" * 60)
        
        try:
            # Proxy al
            proxy_url = proxy_manager.get_proxy(force_type=proxy_type)
            
            if proxy_url:
                print(f"✅ Proxy alındı: {proxy_url}")
                
                # Proxy ile istek at
                print("📡 Test isteği gönderiliyor...")
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
                start_time = datetime.now()
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    timeout=15
                )
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    print(f"✅ Başarılı! (Süre: {duration:.2f}s)")
                    print(f"   IP: {response.json().get('origin', 'N/A')}")
                else:
                    print(f"❌ Hata: HTTP {response.status_code}")
                    
            else:
                print(f"ℹ️ Proxy yok (type: {proxy_type})")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout! Proxy yanıt vermedi (15s)")
        except requests.exceptions.ProxyError as e:
            print(f"❌ Proxy hatası: {e}")
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    # 4. Scrapy ayarları göster
    print_header("🕷️ SCRAPY AYARLARI")
    scrapy_settings = proxy_manager.get_scrapy_settings()
    if scrapy_settings:
        for key, value in scrapy_settings.items():
            print(f"{key}: {value}")
    else:
        print("Scrapy proxy ayarı yok (proxy kapalı)")
    
    # 5. Selenium proxy göster
    print_header("🌐 SELENIUM PROXY")
    selenium_proxy = proxy_manager.get_selenium_proxy()
    if selenium_proxy:
        print(f"Selenium Proxy: {selenium_proxy}")
    else:
        print("Selenium proxy yok (proxy kapalı)")
    
    print_header("✅ TEST TAMAMLANDI")
    print()


def test_free_proxy_list():
    """Free proxy listesini test et"""
    
    print_header("📋 FREE PROXY LİSTESİ TEST")
    
    proxy_manager = get_proxy_manager()
    
    if proxy_manager.proxy_type != 'free':
        print("⚠️ Free proxy seçili değil!")
        print("Test etmek için .env'de PROXY_TYPE=free yapın")
        return
    
    print(f"Toplam proxy: {len(proxy_manager._free_proxy_list)}")
    print("\n🧪 İlk 5 proxy test ediliyor...\n")
    
    for i in range(min(5, len(proxy_manager._free_proxy_list))):
        proxy = proxy_manager._free_proxy_list[i]
        print(f"{i+1}. {proxy}")
        
        is_working = proxy_manager._test_proxy(proxy)
        if is_working:
            print(f"   ✅ Çalışıyor!")
        else:
            print(f"   ❌ Çalışmıyor")
    
    print("\n" + "=" * 60)


def show_usage():
    """Kullanım örnekleri göster"""
    
    print_header("📚 KULLANIM ÖRNEKLERİ")
    
    examples = """
1️⃣ Proxy'i Aç/Kapa
   .env dosyasında:
   PROXY_ENABLED=true   # Aç
   PROXY_ENABLED=false  # Kapat

2️⃣ Free Proxy Kullan
   .env dosyasında:
   PROXY_ENABLED=true
   PROXY_TYPE=free
   FREE_PROXY_TEST=false  # Hızlı ama riskli
   FREE_PROXY_TEST=true   # Yavaş ama güvenli

3️⃣ Smartproxy Kullan
   .env dosyasında:
   PROXY_ENABLED=true
   PROXY_TYPE=smartproxy
   SMARTPROXY_USER=your_username
   SMARTPROXY_PASS=your_password

4️⃣ Kod İçinden Kullanım
   Python kodunda:
   
   from app.services.ProxyManager import get_proxy_manager
   
   proxy_manager = get_proxy_manager()
   
   # .env'deki ayara göre proxy al
   proxy = proxy_manager.get_proxy()
   
   # Belirli bir tip proxy al
   free_proxy = proxy_manager.get_proxy(force_type='free')
   smart_proxy = proxy_manager.get_proxy(force_type='smartproxy')
   no_proxy = proxy_manager.get_proxy(force_type='none')
   
   # Requests için
   proxies = proxy_manager.get_proxy_dict()
   response = requests.get(url, proxies=proxies)
   
   # İstatistikler
   stats = proxy_manager.get_stats()
   print(stats)

5️⃣ Docker İçinde Test
   docker exec -it price_analysis_service-app-1 python test_proxy.py
"""
    
    print(examples)
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Ana test
        test_proxy_manager()
        
        # Kullanım örnekleri
        show_usage()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test iptal edildi")
    except Exception as e:
        print(f"\n\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()

