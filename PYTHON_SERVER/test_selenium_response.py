#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Response Test
Belirli bir URL'ye selenium ile istek atıp ne döndüğünü gösterir
"""

import time
import json
import sys
import os

# Test URL'i
TEST_URL = "https://www.mediamarkt.com.tr/tr/product/_apple-airpods-bluetooth-kulak-ici-kulaklik-mxp63tua-1239693.html"

def test_selenium_response():
    """Selenium ile URL'ye istek at ve yanıtı göster"""
    
    print("="*80)
    print("🔍 SELENIUM RESPONSE TEST")
    print("="*80)
    print(f"\n📡 Test URL: {TEST_URL}\n")
    
    try:
        # Selenium modüllerini import et
        print("📦 Selenium modülleri yükleniyor...")
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        print("✅ Modüller yüklendi\n")
        
        # Driver oluştur
        print("🚗 ChromeDriver oluşturuluyor...")
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent ekle
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = None
        try:
            driver = uc.Chrome(
                options=options,
                driver_executable_path='/usr/bin/chromedriver',
                browser_executable_path='/usr/bin/chromium',
                version_main=None,
                use_subprocess=True,
                headless=True
            )
            driver.set_page_load_timeout(60)
            
            # WebDriver özelliklerini gizle
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Driver oluşturuldu\n")
            
            # URL'e git
            print(f"🌐 URL'e gidiliyor: {TEST_URL}")
            start_time = time.time()
            driver.get(TEST_URL)
            load_time = time.time() - start_time
            print(f"✅ Sayfa yüklendi ({load_time:.2f} saniye)\n")
            
            # Sayfa bilgileri
            print("="*80)
            print("📄 SAYFA BİLGİLERİ")
            print("="*80)
            print(f"📍 Current URL: {driver.current_url}")
            print(f"📝 Page Title: {driver.title}")
            print(f"📏 Page Source Length: {len(driver.page_source)} karakter")
            print(f"📊 Page Source İlk 500 karakter:")
            print("-" * 80)
            print(driver.page_source[:500])
            print("-" * 80)
            print()
            
            # Sayfa yüklenmesini bekle
            print("⏳ Sayfa tam yükleniyor...")
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                print("✅ Sayfa tam yüklendi\n")
            except TimeoutException:
                print("⚠️ Sayfa yükleme timeout\n")
            
            # AJAX için bekle
            print("⏳ AJAX yüklenmesi bekleniyor (8 saniye)...")
            time.sleep(8)
            print("✅ Bekleme tamamlandı\n")
            
            # JavaScript çalıştır - fiyat bilgisi al
            print("="*80)
            print("💰 JAVASCRIPT İLE FİYAT BİLGİSİ")
            print("="*80)
            
            js_results = {}
            
            # 1. Meta tag'den fiyat
            try:
                meta_price = driver.execute_script("""
                    var metaPrice = document.querySelector('meta[property="product:price:amount"]');
                    return metaPrice ? metaPrice.getAttribute('content') : null;
                """)
                js_results['meta_price'] = meta_price
                print(f"📌 Meta Tag Price: {meta_price}")
            except Exception as e:
                print(f"❌ Meta tag hatası: {e}")
            
            # 2. insider_object'ten fiyat
            try:
                insider_price = driver.execute_script("""
                    if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
                        return window.insider_object.product.unit_sale_price;
                    }
                    return null;
                """)
                js_results['insider_price'] = insider_price
                print(f"📌 Insider Object Price: {insider_price}")
            except Exception as e:
                print(f"❌ Insider object hatası: {e}")
            
            # 3. dataLayer'dan fiyat
            try:
                datalayer_price = driver.execute_script("""
                    if (window.dataLayer) {
                        for (var i = 0; i < window.dataLayer.length; i++) {
                            if (window.dataLayer[i].product && window.dataLayer[i].product.price) {
                                return window.dataLayer[i].product.price;
                            }
                        }
                    }
                    return null;
                """)
                js_results['datalayer_price'] = datalayer_price
                print(f"📌 DataLayer Price: {datalayer_price}")
            except Exception as e:
                print(f"❌ DataLayer hatası: {e}")
            
            print()
            
            # CSS Selector ile fiyat arama
            print("="*80)
            print("🔍 CSS SELECTOR İLE ELEMENT ARAMA")
            print("="*80)
            
            # Test selector'ı
            test_selector = ".sc-94eb08bc-0.dqaOrX"
            print(f"\n📌 Test Selector: {test_selector}")
            
            try:
                # Element'i bul
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, test_selector))
                )
                print(f"✅ Element bulundu!")
                print(f"   Tag: {element.tag_name}")
                print(f"   Text: {element.text[:100] if element.text else 'Boş'}")
                print(f"   InnerHTML: {element.get_attribute('innerHTML')[:100] if element.get_attribute('innerHTML') else 'Boş'}")
                print(f"   Class: {element.get_attribute('class')}")
            except TimeoutException:
                print(f"❌ Element bulunamadı (timeout)")
                
                # Alternatif selector'ları dene
                print("\n🔍 Alternatif selector'lar deneniyor...")
                alt_selectors = [
                    '.price',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    '.product-price',
                    '.amount',
                    'span.sc-94eb08bc-0',
                    '[class*="price"]'
                ]
                
                for alt_sel in alt_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, alt_sel)
                        if elements:
                            print(f"   ✅ '{alt_sel}' → {len(elements)} element bulundu")
                            for i, elem in enumerate(elements[:3]):
                                text = elem.text[:50] if elem.text else 'Boş'
                                print(f"      [{i+1}] Text: {text}")
                    except Exception as e:
                        print(f"   ❌ '{alt_sel}' → Hata: {str(e)[:50]}")
                        
            except Exception as e:
                print(f"❌ Element arama hatası: {e}")
            
            print()
            
            # Sayfadaki tüm fiyat benzeri elementleri listele
            print("="*80)
            print("📊 SAYFADAKI FİYAT BENZERİ ELEMENTLER")
            print("="*80)
            
            price_keywords = ['price', 'fiyat', 'tl', '₺', 'amount', 'tutar']
            found_elements = []
            
            for keyword in price_keywords:
                try:
                    # Class içinde keyword araması
                    elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{keyword}')]")
                    if elements:
                        print(f"\n📌 '{keyword}' içeren class'lar ({len(elements)} element):")
                        for i, elem in enumerate(elements[:5]):
                            try:
                                text = elem.text.strip()[:80] if elem.text else 'Boş'
                                classes = elem.get_attribute('class') or 'no-class'
                                print(f"   [{i+1}] Class: {classes[:60]}")
                                print(f"       Text: {text}")
                            except:
                                pass
                except Exception as e:
                    pass
            
            print()
            
            # Sayfa kaynak kodunda fiyat ara
            print("="*80)
            print("🔎 PAGE SOURCE'DA FİYAT ARAMA")
            print("="*80)
            
            page_source = driver.page_source.lower()
            price_patterns = ['45.999', '45999', 'price', 'fiyat', 'unit_sale_price']
            
            for pattern in price_patterns:
                if pattern in page_source:
                    # Pattern'in etrafındaki context'i bul
                    index = page_source.find(pattern)
                    if index != -1:
                        start = max(0, index - 50)
                        end = min(len(page_source), index + 100)
                        context = page_source[start:end]
                        print(f"\n📌 '{pattern}' bulundu:")
                        print(f"   Context: ...{context}...")
            
            print()
            
            # Sonuç özeti
            print("="*80)
            print("📋 SONUÇ ÖZETİ")
            print("="*80)
            print(f"✅ URL'e başarıyla erişildi")
            print(f"✅ Sayfa yüklendi: {driver.title}")
            print(f"✅ JavaScript çalıştırıldı")
            print(f"✅ Element araması yapıldı")
            print(f"\n📊 JavaScript Sonuçları:")
            print(json.dumps(js_results, indent=2, ensure_ascii=False))
            
        finally:
            if driver:
                print("\n🔚 Driver kapatılıyor...")
                driver.quit()
                print("✅ Driver kapatıldı")
    
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("\n💡 Docker container içinde çalıştırmanız gerekiyor:")
        print("   docker exec -it <container_name> python3 test_selenium_response.py")
    
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_selenium_response()

