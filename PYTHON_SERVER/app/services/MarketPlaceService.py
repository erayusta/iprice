import logging
import os

from selenium.common import WebDriverException
from contextlib import redirect_stdout
from app.repositories.ProductRepository import ProductRepository
from app.services.CheckDifferenceService import CheckDifferenceService

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json

logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


class MarketPlaceService:
    def __init__(
            self,
            product_repository: ProductRepository,
            check_difference_service: CheckDifferenceService
    ):
        self.logger = None
        self.product_repository = product_repository
        self.check_difference_service = check_difference_service

    def get_product_links_and_titles(self):
        products = self.product_repository.get_in_stock_with_new_products_orm()

        all_results = []  # Tüm sonuçları saklayacak liste
        filtered_results = []  # Filtrelenmiş sonuçları saklayacak liste

        print("Chrome için opsiyonlar ayarlanıyor...")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")
        chrome_options.binary_location = '/usr/bin/chromium'
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        chrome_options.binary_location = '/usr/bin/chromium'

        service = Service(
            executable_path='/usr/bin/chromedriver',
            log_output='chromedriver.log'
        )
        print("Chrome başlatılıyor...")
        try:
            with open(os.devnull, 'w') as devnull:
                with redirect_stdout(devnull):
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.set_page_load_timeout(30)
        except WebDriverException as e:
            print(f"Chrome WebDriver hatası: {e}")
            return []
        except Exception as e:
            print(f"Beklenmeyen Chrome hatası: {e}")
            return []

        for product in products:
            product_results = []  # Her MPN için sonuçları saklayacak liste
            filtered_product_results = []  # Her MPN için filtrelenmiş sonuçları saklayacak liste

            try:
                # MPN'i al
                product_mpn = product.mpn

                print(f"\n{'=' * 80}")
                print(f"MPN: {product_mpn} için arama yapılıyor...")
                print(f"{'=' * 80}")

                # Arama sorgusunu URL'ye kodlayalım
                encoded_query = product_mpn.replace(" ", "%20")
                print(encoded_query)
                url = f'https://www.trendyol.com/sr?q={encoded_query}&qt={encoded_query}&st={encoded_query}&os=1'
                print(f"Sayfa yükleniyor: {url}")
                driver.get(url)

                print(f"Şu anki URL: {driver.current_url}")
                is_ready = driver.execute_script("return document.readyState")
                print(f"Sayfa durumu: {is_ready}")

                print("\nÜrün container'ı aranıyor...")
                try:
                    wait = WebDriverWait(driver, 15)
                    container = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "prdct-cntnr-wrppr"))
                    )

                    product_cards = container.find_elements(By.CLASS_NAME, "p-card-wrppr")
                    print(f"Bulunan ürün kartı sayısı: {len(product_cards)}")

                    # Her karttan başlık ve link bilgilerini al
                    for card in product_cards:
                        try:
                            # URL'yi al
                            link_element = card.find_element(By.TAG_NAME, "a")
                            product_url = link_element.get_attribute('href')

                            # Başlık bileşenlerini al
                            product_title = ""

                            try:
                                # Ürün container'ını bul
                                title_container = card.find_element(By.CLASS_NAME, "prdct-desc-cntnr")

                                # Marka adını al
                                try:
                                    brand_element = title_container.find_element(By.CLASS_NAME, "prdct-desc-cntnr-ttl")
                                    brand = brand_element.text.strip()
                                    product_title += brand + " "
                                except Exception as e:
                                    print(f"Marka adı alınamadı: {e}")

                                # Ürün adını al
                                try:
                                    name_element = title_container.find_element(By.CLASS_NAME, "prdct-desc-cntnr-name")
                                    name = name_element.text.strip()
                                    product_title += name + " "
                                except Exception as e:
                                    print(f"Ürün adı alınamadı: {e}")

                                # Alt açıklama metnini al
                                try:
                                    desc_element = title_container.find_element(By.CLASS_NAME, "product-desc-sub-text")
                                    desc = desc_element.text.strip()
                                    product_title += desc
                                except Exception as e:
                                    print(f"Alt açıklama alınamadı: {e}")

                            except Exception as e:
                                print(f"Başlık container'ı bulunamadı: {e}")

                                # Alternatif olarak tüm metin içeriğini almayı dene
                                try:
                                    product_title = card.text.strip()
                                except:
                                    product_title = "Başlık alınamadı"

                            # Başlık boşsa, URL'den çıkarmayı dene
                            if not product_title or product_title == "":
                                try:
                                    product_title = product_url.split("/")[-1].split("-p-")[0].replace("-", " ").title()
                                except:
                                    product_title = "Başlık alınamadı"

                            product_title = product_title.strip()

                            # Ürün bilgilerini oluştur
                            product_info = {
                                "mpn": product_mpn,
                                "url": product_url,
                                "title": product_title,
                                "db_title": product.title
                            }

                            # Tüm sonuçlara ekle
                            product_results.append(product_info)

                            # Filtreleme yap
                            is_similar, similarity_score = self.check_difference_service.checkDifference(product_title, product.title)

                            product_info['similarity_score'] = similarity_score

                            if is_similar:
                                filtered_product_results.append(product_info)
                                print("-" * 80)
                                print(f"URL: {product_url}")
                                print(f"Başlık: {product_title}")
                                print(f"Başlık: {product.title}")
                                print("Sonuç: TUTULDU")
                            else:
                                print("-" * 80)
                                print(f"URL: {product_url}")
                                print(f"Başlık: {product_title}")
                                print(f"Başlık: {product.title}")
                                print("Sonuç: ELENDİ")

                        except Exception as e:
                            print(f"Kart işleme hatası: {e}")
                            continue

                except Exception as e:
                    print(f"Container bulma hatası: {e}")
                    print("\nSayfa kaynağından bir parça:")
                    print(driver.page_source[:1000])

                # Bu MPN için bulunan sonuçları ana listelere ekle
                all_results.extend(product_results)
                filtered_results.extend(filtered_product_results)

                print(f"\nMPN: {product_mpn} için toplam {len(product_results)} sonuç bulundu.")
                print(f"MPN: {product_mpn} için filtreleme sonrası {len(filtered_product_results)} sonuç kaldı.")

            except Exception as e:
                print(f"MPN: {product_mpn} için genel hata: {e}")
                continue  # Bir hata oluşursa diğer MPN'lere devam et

            # İşlem tamamlandıktan sonra JSON dosyalarını güncelle
            try:
                with open('all_marketplace_results.json', 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=4)

                with open('filtered_marketplace_results.json', 'w', encoding='utf-8') as f:
                    json.dump(filtered_results, f, ensure_ascii=False, indent=4)

                print(
                    f"Sonuçlar JSON dosyalarına kaydedildi. Toplam: {len(all_results)}, Filtrelenmiş: {len(filtered_results)}")
            except Exception as e:
                print(f"JSON dosyası yazma hatası: {e}")

        # Tarayıcıyı kapat
        print("\nTarayıcı kapatılıyor...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Tarayıcı kapatma hatası: {e}")

        return filtered_results