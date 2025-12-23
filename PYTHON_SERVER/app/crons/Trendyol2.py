from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import WebDriverException
from contextlib import redirect_stdout
import json
import os
import logging
import time
import re

# Gereksiz loglama mesajlarını engelle
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


def parse_price_to_float(price_str):
    """Fiyat stringini float değere dönüştürür"""
    if not price_str:
        return None
    # Tüm noktalama işaretlerini ve boşlukları kaldır, virgülü noktaya çevir
    price_str = price_str.replace('.', '')  # Binlik ayracı kaldır
    price_str = price_str.replace(',', '.')  # Ondalık ayracı noktaya çevir
    price_str = re.sub(r'[^\d.]', '', price_str)  # Sayı ve nokta dışındaki karakterleri kaldır

    try:
        return float(price_str)
    except ValueError:
        return None


def parse_filtered_product_details():
    """Filtrelenmiş ürünlerin detaylarını çeker"""
    # Filtrelenmiş sonuçları JSON dosyasından oku
    try:
        with open('filtered_marketplace_results.json', 'r', encoding='utf-8') as f:
            filtered_results = json.load(f)

        print(f"'filtered_marketplace_results.json' dosyasından {len(filtered_results)} ürün yüklendi.")
    except FileNotFoundError:
        print("'filtered_marketplace_results.json' dosyası bulunamadı.")
        return []
    except json.JSONDecodeError:
        print("JSON dosyası hatalı, ayrıştırılamadı.")
        return []
    except Exception as e:
        print(f"Dosya okuma hatası: {e}")
        return []

    # Selenium WebDriver'ı yapılandır
    print("Chrome için opsiyonlar ayarlanıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")

    # Docker konteynerindeki renderer sorunu için çözümler
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Ek güvenlik ve performans ayarları
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-tools")

    # Single-process çalıştırma
    chrome_options.add_argument("--single-process")

    # Bellek kullanımını optimize etme
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")

    # Medya desteğini devre dışı bırak
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    # User-Agent ayarı
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')

    # Konsola hataları gösterme
    chrome_options.add_argument("--log-level=3")

    # Binary location, eğer Docker konteynerlerde çalışıyorsanız doğru yol olduğundan emin olun
    try:
        if os.path.exists('/usr/bin/chromium'):
            chrome_options.binary_location = '/usr/bin/chromium'
        elif os.path.exists('/usr/bin/chromium-browser'):
            chrome_options.binary_location = '/usr/bin/chromium-browser'
        elif os.path.exists('/usr/bin/google-chrome'):
            chrome_options.binary_location = '/usr/bin/google-chrome'
    except Exception as e:
        print(f"Binary location kontrolünde hata: {e}")

    # Chromedriver'ın yolunu kontrol et
    chromedriver_path = '/usr/bin/chromedriver'
    if not os.path.exists(chromedriver_path):
        print(f"UYARI: ChromeDriver {chromedriver_path} konumunda bulunamadı!")
        # Alternatif yolları dene
        alternative_paths = [
            '/usr/local/bin/chromedriver',
            '/opt/chromedriver',
            './chromedriver'
        ]
        for path in alternative_paths:
            if os.path.exists(path):
                chromedriver_path = path
                print(f"Alternatif ChromeDriver konumu bulundu: {path}")
                break

    service = Service(
        executable_path=chromedriver_path,
        log_output='chromedriver.log'
    )

    print("Chrome başlatılıyor...")
    try:
        with open(os.devnull, 'w') as devnull:
            with redirect_stdout(devnull):
                # Chrome'u başlatmadan önce 2 saniye bekle
                time.sleep(2)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.set_page_load_timeout(30)
    except WebDriverException as e:
        print(f"Chrome WebDriver hatası: {e}")
        print("Docker içinde kararlı WebDriver kullanımı için şu komutu deneyin:")
        print("apt-get update && apt-get install -y chromium-browser xvfb")
        return []
    except Exception as e:
        print(f"Beklenmeyen Chrome hatası: {e}")
        return []

    # Detaylı ürün bilgilerini saklayacak liste
    detailed_results = []

    try:
        # Her bir ürün için detayları çek
        for product in filtered_results:
            try:
                product_url = product.get('url')
                if not product_url:
                    print(f"Ürün URL'si bulunamadı, atlanıyor: {product}")
                    continue

                print(f"\n{'=' * 80}")
                print(f"Ürün detayları çekiliyor: {product_url}")
                print(f"{'=' * 80}")

                # Ürün sayfasını yükle
                try:
                    driver.get(product_url)
                    time.sleep(2)  # Sayfa yüklenmesi için kısa bir bekleme
                except Exception as e:
                    print(f"Sayfa yükleme hatası: {e}")
                    continue

                # Fiyat bilgisini al - campaign-price-container .campaign-price
                price = None
                try:
                    price_element = driver.find_element(By.CSS_SELECTOR, '.campaign-price-container .campaign-price')
                    price = price_element.text.strip()
                    print(f"campaign-price-container .campaign-price seçicisiyle fiyat bulundu: {price}")
                except Exception:
                    # Alternatif seçici dene: product-price-container .prc-dsc
                    try:
                        price_element = driver.find_element(By.CSS_SELECTOR, '.product-price-container .prc-dsc')
                        price = price_element.text.strip()
                        print(f"product-price-container .prc-dsc seçicisiyle fiyat bulundu: {price}")
                    except Exception:
                        # Diğer potansiyel fiyat seçicileri dene
                        try:
                            price_selectors = [
                                '.price-container .prc-dsc',
                                '.prc-box-dscntd',
                                '.price-info .prc-dsc',
                                '.product-price .discounted-price',
                                '.price-promotion-container .promotion-price'
                            ]

                            for selector in price_selectors:
                                try:
                                    price_element = driver.find_element(By.CSS_SELECTOR, selector)
                                    price = price_element.text.strip()
                                    print(f"Alternatif seçici ({selector}) ile fiyat bulundu: {price}")
                                    break
                                except:
                                    continue
                        except Exception as e:
                            print(f"Fiyat bulma hatası: {e}")

                # Orijinal fiyatı al (üstü çizili fiyat)
                original_price = None
                try:
                    original_price_selectors = [
                        '.product-price-container .prc-org',
                        '.price-container .prc-org',
                        '.prc-box-orgnl',
                        '.price-info .prc-org',
                        '.product-price .original-price',
                    ]

                    for selector in original_price_selectors:
                        try:
                            original_price_element = driver.find_element(By.CSS_SELECTOR, selector)
                            original_price = original_price_element.text.strip()
                            print(f"Orijinal fiyat bulundu ({selector}): {original_price}")
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"Orijinal fiyat bulma hatası: {e}")

                # Satıcı bilgisini al
                seller = None
                try:
                    seller_selectors = [
                        '.seller-info .seller-name',
                        '.merchant-info .merchant-name',
                        '.seller-container .seller-name'
                    ]

                    for selector in seller_selectors:
                        try:
                            seller_element = driver.find_element(By.CSS_SELECTOR, selector)
                            seller = seller_element.text.strip()
                            print(f"Satıcı bulundu ({selector}): {seller}")
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"Satıcı bulma hatası: {e}")

                # Stok durumu kontrolü
                stock_status = "Stok durumu bilinmiyor"
                try:
                    # Sepete ekle butonu var mı?
                    add_to_cart_buttons = driver.find_elements(By.CSS_SELECTOR,
                                                               '.add-to-basket-button-container, .add-to-cart')
                    if add_to_cart_buttons and any(
                            btn.is_displayed() and btn.is_enabled() for btn in add_to_cart_buttons):
                        stock_status = "Stokta var"
                    else:
                        # Stok yok mesajı var mı?
                        out_of_stock_elements = driver.find_elements(By.CSS_SELECTOR, '.pr-out-of-stock, .out-of-stock')
                        if out_of_stock_elements and any(elem.is_displayed() for elem in out_of_stock_elements):
                            stock_status = "Stokta yok"
                except Exception as e:
                    print(f"Stok durumu kontrolü hatası: {e}")

                print(f"Stok durumu: {stock_status}")

                # İndirim oranını hesapla
                discount_rate = None
                if price and original_price:
                    price_value = parse_price_to_float(price)
                    original_price_value = parse_price_to_float(original_price)

                    if price_value and original_price_value and original_price_value > 0:
                        discount_rate = round(100 - (price_value * 100 / original_price_value), 2)
                        print(f"Hesaplanan indirim oranı: %{discount_rate}")

                # Ürün bilgilerine detayları ekle
                product_details = product.copy()
                product_details.update({
                    'price': price,
                    'price_value': parse_price_to_float(price) if price else None,
                    'original_price': original_price,
                    'original_price_value': parse_price_to_float(original_price) if original_price else None,
                    'discount_rate': discount_rate,
                    'seller': seller,
                    'stock_status': stock_status,
                    'parsed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                })

                detailed_results.append(product_details)
                print(f"Ürün detayları başarıyla çekildi.")

            except Exception as e:
                print(f"Ürün detayları çekilirken hata oluştu: {e}")
                # Hataya rağmen, mevcut bilgilerle devam et
                if 'product' in locals():
                    product_details = product.copy()
                    product_details['error'] = str(e)
                    detailed_results.append(product_details)

            # Her istek arasında kısa bir bekleme yap
            time.sleep(3)

    except Exception as e:
        print(f"Genel işlem hatası: {e}")

    finally:
        # Tarayıcıyı kapat
        print("\nTarayıcı kapatılıyor...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Tarayıcı kapatma hatası: {e}")

    # İşlem bitince JSON dosyası oluştur
    try:
        with open('trendyol_detailed_products.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=4)
        print(
            f"\nTüm detaylı sonuçlar 'trendyol_detailed_products.json' dosyasına kaydedildi. Toplam: {len(detailed_results)} ürün")
    except Exception as e:
        print(f"JSON dosyası yazma hatası: {e}")

    return detailed_results


if __name__ == "__main__":
    print("Filtrelenmiş ürünlerin detayları çekiliyor...")
    detailed_results = parse_filtered_product_details()

    print(f"\nİşlem tamamlandı. Toplam {len(detailed_results)} ürünün detayları çekildi.")

    # Sonuçların özeti
    if detailed_results:
        print("\n" + "=" * 100)
        print("SONUÇLAR ÖZETİ")
        print("=" * 100)

        for i, product in enumerate(detailed_results, 1):
            print(
                f"{i}. {product.get('title', 'Başlık Yok')} - {product.get('price', 'Fiyat Yok')} - {product.get('seller', 'Satıcı Yok')}")