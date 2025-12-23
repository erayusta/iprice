import os
import sys
import dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import WebDriverException
from contextlib import redirect_stdout
from app.helper.standardize_price import standardize_price

import time

from app.repositories.ProductRepository import ProductRepository

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # root dizine çık
dotenv.load_dotenv('../.env')
server_path = os.getenv('SERVER_PATH')

class PazaramaService:
    def __init__(
            self,
            product_repository: ProductRepository,
    ):
        self.product_repository = product_repository

    def scrape_pazarama_urls(self, urls):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
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
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        chrome_options.binary_location = '/usr/bin/chromium'

        service = Service(
            executable_path='/usr/bin/chromedriver',
            log_output='chromedriver.log'
        )

        # Her URL için sonuçları tutacak sözlük
        all_results = {}

        # URL yoksa boş sözlük döndür
        if not urls:
            print("İşlenecek URL bulunamadı.")
            return all_results

        print(f"Chrome başlatılıyor... İşlenecek URL sayısı: {len(urls)}")
        try:
            with open(os.devnull, 'w') as devnull:
                with redirect_stdout(devnull):
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.set_page_load_timeout(30)
        except WebDriverException as e:
            print(f"Chrome WebDriver hatası: {e}")
            return all_results
        except Exception as e:
            print(f"Beklenmeyen Chrome hatası: {e}")
            return all_results

        try:
            for url in urls:
                print(f"\n{url} için veri çekiliyor...")

                try:
                    # Sayfayı yükle
                    driver.get(url)

                    # Sayfanın tamamen yüklenmesini bekle (5 saniye)
                    time.sleep(5)

                    # JS ile yüklenen içeriğin gelmesini bekle
                    try:
                        # product__seller-row sınıfının yüklenmesini bekle (30 saniye kadar)
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".product__seller-row"))
                        )
                    except:
                        print(f"[{url}] Satıcı bloğu bulunamadı veya yüklenemedi.")
                        all_results[url] = []
                        continue

                    # Ana satıcı bloğunu bul - XPath kullanarak sınıfları daha güvenli bir şekilde eşleştir
                    seller_row_xpath = "//div[contains(@class, 'flex') and contains(@class, 'flex-wrap') and contains(@class, 'product__seller-row')]"
                    try:
                        seller_row = driver.find_element(By.XPATH, seller_row_xpath)
                    except:
                        print(f"[{url}] product__seller-row bulunamadı")
                        all_results[url] = []
                        continue

                    # Bu blok içindeki tüm w-1/2 pb-4 sınıfına sahip blokları bul
                    blocks_xpath = ".//div[contains(@class, 'w-1/2') and contains(@class, 'pb-4')]"
                    seller_blocks = seller_row.find_elements(By.XPATH, blocks_xpath)
                    print(f"[{url}] Bulunan w-1/2 pb-4 satıcı bloğu sayısı: {len(seller_blocks)}")

                    # URL için sonuçları tutacak liste
                    url_results = []

                    for block in seller_blocks:
                        try:
                            # Satıcı adını !text-gray-600 !font-bold mr-2 sınıfından al
                            seller_xpath = ".//div[contains(@class, '!text-gray-600') and contains(@class, '!font-bold') and contains(@class, 'mr-2')]"
                            seller_element = None

                            try:
                                seller_element = block.find_element(By.XPATH, seller_xpath)
                            except:
                                # Ünlem işaretleri olmazsa dene
                                alt_seller_xpath = ".//div[contains(@class, 'text-gray-600') and contains(@class, 'font-bold') and contains(@class, 'mr-2')]"
                                try:
                                    seller_element = block.find_element(By.XPATH, alt_seller_xpath)
                                except:
                                    # Daha genel bir yaklaşım dene
                                    divs = block.find_elements(By.TAG_NAME, 'div')
                                    for div in divs:
                                        class_attr = div.get_attribute('class')
                                        if class_attr and ('text-gray-600' in class_attr or '!text-gray-600' in class_attr):
                                            seller_element = div
                                            break

                            seller = seller_element.text.strip() if seller_element else None

                            # Fiyatı al - önce text-black font-bold text-lg leading-none sınıfından dene
                            price_xpath = ".//span[contains(@class, 'text-black') and contains(@class, 'font-bold') and contains(@class, 'text-lg') and contains(@class, 'leading-none')]"
                            price_element = None

                            try:
                                price_element = block.find_element(By.XPATH, price_xpath)
                            except:
                                # Bulunamazsa w-1/2 text-lg text-gray-600 font-bold mr-4 flex flex-col sınıfından dene
                                price_container_xpath = ".//div[contains(@class, 'w-1/2') and contains(@class, 'text-lg') and contains(@class, 'text-gray-600') and contains(@class, 'font-bold') and contains(@class, 'mr-4') and contains(@class, 'flex') and contains(@class, 'flex-col')]"
                                try:
                                    price_container = block.find_element(By.XPATH, price_container_xpath)
                                    # Bu konteynır içindeki span'ları bul
                                    price_spans = price_container.find_elements(By.TAG_NAME, 'span')

                                    # TL içeren span'ı bul
                                    for span in price_spans:
                                        if 'TL' in span.text:
                                            price_element = span
                                            break
                                except:
                                    # Blok içindeki tüm span'ları kontrol et
                                    spans = block.find_elements(By.TAG_NAME, 'span')
                                    for span in spans:
                                        if 'TL' in span.text and not 'SEPETTE' in span.text:
                                            price_element = span
                                            break

                            price = price_element.text.strip() if price_element else None

                            # Satıcı ve fiyat bulunduysa sonuçlara ekle
                            if seller and price:
                                price = standardize_price(price)
                                url_results.append({
                                    'seller': seller,
                                    'price': price
                                })
                                print(f"[{url}] Satıcı: {seller}, Fiyat: {price}")
                            else:
                                print(f"[{url}] Satıcı veya fiyat bulunamadı. Satıcı: {seller}, Fiyat: {price}")

                        except Exception as e:
                            print(f"[{url}] Satıcı bloğu işlenirken hata: {e}")

                    print(f"[{url}] Toplam {len(url_results)} satıcı/fiyat çifti bulundu")
                    all_results[url] = url_results

                except Exception as e:
                    print(f"[{url}] URL işlenirken hata: {e}")
                    all_results[url] = []

            return all_results

        finally:
            # WebDriver'ı kapat
            driver.quit()




    '''
    if __name__ == "__main__":
    # Veritabanından URL'leri çek
    urls = get_pazarama_urls_from_db()

    if not urls:
        print("İşlenecek URL bulunamadı. Program sonlandırılıyor.")
        sys.exit(0)

    # URL'lerden veri çek
    results = scrape_pazarama_urls(urls)

    # Özet rapor
    total_urls = len(urls)
    processed_urls = len(results)
    total_sellers = sum(len(sellers) for sellers in results.values())

    print(f"\n--- ÖZET RAPOR ---")
    print(f"Toplam URL: {total_urls}")
    print(f"İşlenen URL: {processed_urls}")
    print(f"Toplam bulunan satıcı: {total_sellers}")
    print(f"-------------------")
    '''