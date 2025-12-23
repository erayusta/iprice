from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time


def get_data_with_modal_scraping(url):
    """Modal scraping ile Selenium scraping - Sadece XPath kullanarak"""

    print("🎯 SELENIUM + MODAL SCRAPING (XPATH ONLY)")
    print("=" * 60)

    print("\n🚀 Chrome ayarları yapılandırılıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-dev-tools')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/chromium'

    service = Service(
        executable_path='/usr/bin/chromedriver',
        log_output='chromedriver.log'
    )

    driver = None
    result = {
        'main_price': None,
        'sale_price': None,
        'third_price': None,
        'fourth_price': None,
        'other_sellers': []
    }

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)

        print(f"\n🌐 Sayfa yükleniyor: {url[:60]}...")
        driver.get(url)

        print("⏳ Sayfa render bekleniyor...")
        time.sleep(3)

        # Ana fiyat elementini bul
        print("🔍 Ana fiyat aranıyor...")
        try:
            # ANA FİYAT XPATH - Buraya ana fiyat xpath'ini yazın
            main_price_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div/div[1]/div[1]'
            # İNDİRİMLİ FİYAT
            sale_price_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div[1]/div[2]'
            # ÜÇÜNCÜ FİYAT
            third_price_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div/div[1]/div[1]'
            # DÖRDÜNCÜ FİYAT
            #fourth_price_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div/span/b'

            main_price_element = driver.find_element(By.XPATH,main_price_xpath)

            sale_price_element = driver.find_element(By.XPATH,sale_price_xpath)

            third_price_element = driver.find_element(By.XPATH,third_price_xpath)

            #fourth_price_element = driver.find_element(By.XPATH,fourth_price_xpath)

            result['main_price'] = main_price_element.text.strip()
            result['sale_price'] = sale_price_element.text.strip()
            result['third_price'] = third_price_element.text.strip()
            #result['fourth_price'] = fourth_price_element.text.strip()

            print(f"✅ Ana fiyat bulundu: {result['main_price']}")
            print(f"✅ İnidirimli Fİyat: {result['sale_price']}")
            print(f"✅ Üçüncü Fiyat: {result['third_price']}")
            print(f"✅ Dördüncü Fiyat: {result['fourth_price']}")
        except TimeoutException:
            print("❌ Ana fiyat bulunamadı")

        # "Tümünü gör butonunu bul ve tıkla
        print("\n🔘 'Tümünü Gör' butonu aranıyor...")
        try:
            # Tümünü Gör BUTONU XPATH - Buraya diğer satıcılar buton xpath'ini yazın
            other_sellers_button_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[3]/div[3]/div[1]/button'

            other_sellers_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, other_sellers_button_xpath))
            )

            # Butona scroll et
            driver.execute_script("arguments[0].scrollIntoView(true);", other_sellers_button)
            time.sleep(1)

            # Butona tıkla
            try:
                other_sellers_button.click()
                print("✅ 'Tümünü Gör' butonuna tıklandı")
            except ElementClickInterceptedException:
                # JavaScript ile tıkla
                driver.execute_script("arguments[0].click();", other_sellers_button)
                print("✅ 'Tümünü Gör' butonuna JS ile tıklandı")

            # Modal'ın açılmasını bekle
            time.sleep(3)

            # Modal içindeki satıcı bilgilerini çek
            print("🔍 Modal içindeki satıcılar aranıyor...")
            try:
                # Önce hangi div'de modal açıldığını bul
                modal_selectors = [
                    '/html/body/div[4]/div',  # ReactModalPortal
                    '/html/body/div[6]/div',  # hb-AxgMb
                    '/html/body/div[4]',  # ReactModalPortal (alt div olmadan)
                    '/html/body/div[6]',  # hb-AxgMb (alt div olmadan)
                    '/html/body/div[8]/div',
                    '/html/body/div[9]/div',
                    '/html/body/div[10]/div',
                    '/html/body/div[7]/div',
                    '/html/body/div[11]/div'
                ]

                modal_container = None
                modal_container_xpath = None

                print("🔍 Modal container aranıyor...")
                for selector in modal_selectors:
                    try:
                        print(f"   Deneniyor: {selector}")
                        modal_container = driver.find_element(By.XPATH, selector)
                        modal_container_xpath = selector
                        print(f"✅ Modal container bulundu: {selector}")
                        break
                    except:
                        print(f"   ❌ {selector} bulunamadı")
                        continue

                if not modal_container:
                    print("❌ Hiçbir modal container bulunamadı")
                    # Tüm div'leri listele
                    print("🔍 Sayfadaki tüm body > div elementleri:")
                    all_divs = driver.find_elements(By.XPATH, '/html/body/div')
                    for idx, div in enumerate(all_divs):
                        try:
                            div_class = div.get_attribute('class') or 'class-yok'
                            print(f"   div[{idx + 1}]: class='{div_class[:50]}...'")
                        except:
                            print(f"   div[{idx + 1}]: hata")
                    return result

                # Modal bulundu, şimdi satıcı listesini ara
                # Modal container'dan div numarasını çıkar
                # Örnek: '/html/body/div[8]/div' -> 'div[8]'
                div_number = modal_container_xpath.split('/')[4]  # 'div[8]'

                # Satıcı listesi xpath'ini oluştur
                sellers_list_xpath = f'/html/body/{div_number}/div/div[3]'
                seller_items_xpath = f'/html/body/{div_number}/div/div[3]/div'

                print(f"🔍 Satıcı listesi aranıyor: {sellers_list_xpath}")

                try:
                    sellers_container = driver.find_element(By.XPATH, sellers_list_xpath)
                    print("✅ Satıcı listesi container bulundu")
                except:
                    print("❌ Satıcı listesi container bulunamadı")
                    # Alternatif yollar dene
                    alternative_paths = [
                        f'/html/body/{div_number}/div/div[2]',
                        f'/html/body/{div_number}/div/div[4]',
                        f'/html/body/{div_number}/div/div[1]'
                    ]

                    for alt_path in alternative_paths:
                        try:
                            sellers_container = driver.find_element(By.XPATH, alt_path)
                            sellers_list_xpath = alt_path
                            seller_items_xpath = f'{alt_path}/div'
                            print(f"✅ Alternatif satıcı listesi bulundu: {alt_path}")
                            break
                        except:
                            continue
                    else:
                        print("❌ Hiçbir satıcı listesi bulunamadı")
                        return result

                # Satıcı item'larını bul
                seller_items = driver.find_elements(By.XPATH, seller_items_xpath)
                print(f"📊 Toplam {len(seller_items)} satıcı öğesi bulundu")

                if len(seller_items) == 0:
                    print("⚠️ Satıcı item'ı bulunamadı, tüm modal içeriği kontrol ediliyor...")
                    modal_text = modal_container.text
                    print(f"Modal içeriği: {modal_text[:200]}...")
                    return result

                # Her satıcı item'ını işle
                processed_sellers = 0
                for i in range(1, len(seller_items) + 1):
                    try:
                        seller_info = {}
                        print(f"\n🔍 Satıcı {i} analiz ediliyor...")

                        # Satıcı xpath'lerini aynı div numarasıyla oluştur
                        seller_name_xpath = f'/html/body/{div_number}/div/div[3]/div[{i}]/div/div[1]/div[1]/a'
                        price_xpath = f'/html/body/{div_number}/div/div[3]/div[{i}]/div/div[1]/div[4]/div/div[2]'
                        shipping_xpath = f'/html/body/{div_number}/div/div[3]/div[{i}]/div/div[1]/div[2]/div'

                        # SATICI ADI
                        try:
                            name_element = driver.find_element(By.XPATH, seller_name_xpath)
                            seller_info['name'] = name_element.text.strip()
                            print(f"✅ Satıcı adı: {seller_info['name']}")
                        except:
                            seller_info['name'] = "Bulunamadı"
                            print(f"❌ Satıcı adı bulunamadı (xpath: {seller_name_xpath})")

                        # FİYAT
                        try:
                            price_element = driver.find_element(By.XPATH, price_xpath)
                            seller_info['price'] = price_element.text.strip()
                            print(f"✅ Fiyat: {seller_info['price']}")
                        except:
                            seller_info['price'] = "Bulunamadı"
                            print(f"❌ Fiyat bulunamadı (xpath: {price_xpath})")

                        # KARGO
                        try:
                            shipping_element = driver.find_element(By.XPATH, shipping_xpath)
                            seller_info['shipping'] = shipping_element.text.strip()
                            print(f"✅ Kargo: {seller_info['shipping']}")
                        except:
                            seller_info['shipping'] = "Bulunamadı"
                            print(f"❌ Kargo bulunamadı (xpath: {shipping_xpath})")

                        # Satıcı bilgilerini kaydet
                        result['other_sellers'].append(seller_info)
                        processed_sellers += 1
                        print(f"✅ Satıcı kaydedildi")

                    except Exception as e:
                        print(f"❌ Satıcı {i} işlem hatası: {e}")
                        continue

                print(f"\n📊 Modal'dan toplam {processed_sellers} satıcı bilgisi çekildi")

            except Exception as e:
                print(f"❌ Modal işleme hatası: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Buton arama/tıklama hatası: {e}")

        # Buton yoksa sayfa satıcıları kontrol et
        print("\n🔍 Sayfa üzerindeki diğer satıcılar kontrol ediliyor...")

        try:
            other_sellers_section_xpath = '//*[@id="container"]/main/div/div[2]/section[1]/div[3]/div[3]/div[1]/span'
            section_elements = driver.find_elements(By.XPATH, other_sellers_section_xpath)

            if section_elements:
                print("✅ Diğer satıcılar bölümü bulundu")
                seller_info = {}

                # Satıcı adı
                try:
                    name_element = driver.find_element(By.XPATH,
                                                       '//*[@id="container"]/main/div/div[2]/section[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[1]/a')
                    seller_info['name'] = name_element.text.strip()
                    print(f"✅ Sayfa satıcı: {seller_info['name']}")
                except:
                    seller_info['name'] = "Bulunamadı"

                # Fiyat
                try:
                    price_element = driver.find_element(By.XPATH,
                                                        '//*[@id="container"]/main/div/div[2]/section[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[4]/div/div')
                    seller_info['price'] = price_element.text.strip()
                    print(f"✅ Sayfa fiyat: {seller_info['price']}")
                except:
                    seller_info['price'] = "Bulunamadı"

                # Kargo
                try:
                    shipping_element = driver.find_element(By.XPATH,
                                                           '//*[@id="container"]/main/div/div[2]/section[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div')
                    seller_info['shipping'] = shipping_element.text.strip()
                    print(f"✅ Sayfa kargo: {seller_info['shipping']}")
                except:
                    seller_info['shipping'] = "Bulunamadı"

                result['other_sellers'].append(seller_info)
                print("✅ Sayfa satıcısı kaydedildi")
            else:
                print("⚠️ Sayfa satıcıları bulunamadı")

        except Exception as page_error:
            print(f"❌ Sayfa hatası: {page_error}")

    except Exception as e:
        print(f"❌ Selenium hatası: {e}")

    finally:
        if driver:
            print("🔒 Chrome kapatılıyor...")
            driver.quit()

        # Sonuçları göster
        print("\n" + "=" * 60)
        print("📊 SONUÇLAR")
        print("=" * 60)

        print(f"ANA FİYAT: {result['main_price'] or 'Bulunamadı'}")
        print(f"İNDİRİMLİ FİYAT: {result['sale_price'] or 'Bulunamadı'}")
        print(f"30 gün de en düşük FİYAT: {result['third_price'] or 'Bulunamadı'}")
        print(f"Premium FİYAT: {result['fourth_price'] or 'Bulunamadı'}")

        print(f"\nDİĞER SATICILAR:")
        if result['other_sellers']:
            for i, seller in enumerate(result['other_sellers'], 1):
                print(f"Satıcı {i}: {seller.get('name', 'Bulunamadı')}")
                print(f"Fiyat {i}: {seller.get('price', 'Bulunamadı')}")
                print(f"Kargo {i}: {seller.get('shipping', 'Bulunamadı')}")
                print()  # Boş satır
        else:
            print("Diğer satıcı bulunamadı")

        return result


def main():
    """Ana test fonksiyonu"""
    url = "https://www.hepsiburada.com/iphone-15-128-gb-siyah-p-HBCV00004X9ZCH"
    result = get_data_with_modal_scraping(url)
    return result


if __name__ == "__main__":
    main()
