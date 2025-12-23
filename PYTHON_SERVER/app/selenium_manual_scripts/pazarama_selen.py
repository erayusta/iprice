from __future__ import annotations

import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ==============================================================================
# Proje yollarınız ve importlarınız
server_path = os.getenv('SERVER_PATH')
if server_path and os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.repositories.ProductRepository import ProductRepository
from app.model.Company import Company
from app.helper.standardize_price import standardize_price


# ==============================================================================


class PazaramaScraper:
    """
    Pazarama web sitesinden ürün ve satıcı bilgilerini çeken sınıf.
    İÇERİSİNDEKİ KAZIMA MANTIĞI SİZİN SAĞLADIĞINIZ KOD İLE BİREBİR AYNIDIR.
    """

    def __init__(self):
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        print(">>> Tarayıcı (Headless Chrome) başlatılıyor...")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        chrome_options.binary_location = '/usr/bin/chromium'

        service = Service(executable_path='/usr/bin/chromedriver', log_output='chromedriver.log')
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            print(">>> Tarayıcı başarıyla başlatıldı.")
            return driver
        except WebDriverException as e:
            print(f"HATA: Chrome WebDriver başlatılamadı: {e}")
            raise

    def get_product_info(self, url: str) -> dict:
        """
        Verilen URL'den ana satıcı, diğer satıcılar ve stok durumunu çeker.
        Bu fonksiyonun mantığına dokunulmamıştır.
        """
        product_data = {"main_seller": {}, "other_sellers": []}
        try:
            self.driver.get(url)
            time.sleep(4)

            # Ana Satıcı Bilgilerini Çekme
            CSS_MAIN_PRICE = '.text-4xl.text-black.font-bold.-mt-1'
            XPATH_MAIN_SELLER = '//*[@id="app"]/div[1]/div[1]/div[3]/div[2]/div[3]/div[5]/a[1]/div[1]/p/span[2]'
            try:
                price = self.driver.find_element(By.CSS_SELECTOR, CSS_MAIN_PRICE).text
                product_data["main_seller"]["price"] = price.strip()
            except Exception:
                product_data["main_seller"]["price"] = None
                print("  -> Ana fiyat bulunamadı, stok durumu kontrol ediliyor...")
                try:
                    OUT_OF_STOCK_SELECTOR = ".text-center.rounded.border-solid.border.whitespace-normal.w-fit.py-2.px-12.leading-3.mt-2.font-semibold.\\!w-56.\\!p-3.\\!-mt-3"
                    self.driver.find_element(By.CSS_SELECTOR, OUT_OF_STOCK_SELECTOR)
                    product_data["main_seller"]["out_of_stock"] = True
                    print("    -> 'Stok Tükendi' bilgisi bulundu.")
                except Exception:
                    product_data["main_seller"]["out_of_stock"] = False
                    print("    -> 'Stok Tükendi' bilgisi de bulunamadı.")

            try:
                seller = self.driver.find_element(By.XPATH, XPATH_MAIN_SELLER).text
                product_data["main_seller"]["seller_name"] = seller.strip()
            except Exception:
                product_data["main_seller"]["seller_name"] = None

            # Diğer Satıcılar Mantığı
            XPATH_OTHER_SELLERS_BUTTON = '//*[@id="product-detail-all-seller"]/div[2]/div[2]/button'
            try:
                button = self.driver.find_element(By.XPATH, XPATH_OTHER_SELLERS_BUTTON)
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(5)
            except Exception:
                print("ℹ️ 'Other Sellers' butonu bulunamadı, görünür satıcılar aranacak.")
                pass

            XPATH_OTHER_SELLERS_LIST = '//*[@id="product-detail-all-seller"]/div[2]/div[1]'
            try:
                seller_container = self.driver.find_element(By.XPATH, XPATH_OTHER_SELLERS_LIST)
                seller_boxes = seller_container.find_elements(By.XPATH, './div')
                for i, seller_box in enumerate(seller_boxes, 1):
                    seller_info = {}
                    try:
                        seller_xpath = f'//*[@id="product-detail-all-seller"]/div[2]/div[1]/div[{i}]/div/div[1]/div/div'
                        seller_info["seller_name"] = seller_box.find_element(By.XPATH, seller_xpath).text.strip()
                    except Exception:
                        seller_info["seller_name"] = None
                    try:
                        price_xpath = f'//*[@id="product-detail-all-seller"]/div[2]/div[1]/div[{i}]/div/div[2]/div[1]/span'
                        seller_info["price"] = seller_box.find_element(By.XPATH, price_xpath).text.strip()
                    except Exception:
                        seller_info["price"] = None
                    try:
                        link_xpath = f''
                        seller_info['link'] = ''
                    except Exception:
                        seller_info["link"] = None

                    if seller_info.get("seller_name") and seller_info.get("price"):
                        product_data["other_sellers"].append(seller_info)
            except Exception:
                print(f"❌ Diğer satıcılar listesi bulunamadı veya işlenemedi.")

            return product_data
        except Exception as e:
            print(f"  -> HATA: Sayfa işlenirken genel bir hata oluştu: {e}")
            return product_data

    def close(self):
        """Tarayıcıyı güvenli bir şekilde kapatır."""
        if self.driver:
            print("\n>>> İşlem bitti. Tarayıcı kapatılıyor.")
            self.driver.quit()


if __name__ == "__main__":
    db_user, db_pass, db_host, db_port, db_name = os.getenv('SHARED_DB_USER', 'ipricetestuser'), os.getenv('SHARED_DB_PASS', 'YeniSifre123!'), os.getenv('SHARED_DB_HOST', '10.20.50.16'), os.getenv('SHARED_DB_PORT', '5432'), os.getenv('SHARED_DB_NAME', 'ipricetest')
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    repo = ProductRepository(db_session=db_session)

    # --- Sabit Değişkenler ---
    MARKETPLACE_COMPANY_ID = 25  # Pazarama için ID (DB'den kontrol edin)
    PRICE_ATTRIBUTE_ID = 1  # "price" attribute ID'si
    STOCK_ATTRIBUTE_ID = 6  # "stok" attribute ID'si

    marketplace_company = db_session.query(Company).filter_by(id=MARKETPLACE_COMPANY_ID).first()
    if not marketplace_company:
        print(f"HATA: ID'si {MARKETPLACE_COMPANY_ID} olan ana pazaryeri (Pazarama) veritabanında bulunamadı.")
        db_session.close()
        exit()

    print(f"Veritabanından company_id={MARKETPLACE_COMPANY_ID} (Pazarama) için URL'ler çekiliyor...")
    products_to_scrape = repo.get_products_with_urls_by_company_id(company_id=MARKETPLACE_COMPANY_ID)

    if not products_to_scrape:
        print("\nİşlenecek URL bulunamadığı için program sonlandırılıyor.")
        db_session.close()
        exit()

    scraper = PazaramaScraper()
    records_to_save = []

    try:
        print(f"\nToplam {len(products_to_scrape)} adet ürün için fiyat çekme işlemi başlıyor...")
        for product in products_to_scrape:
            print("------------------------------------------")
            print(f"İşleniyor (MPN: {product.mpn}): {product.url}")

            product_info = scraper.get_product_info(product.url)

            # 1. Ana Fiyat veya Stok Durumunu Kaydet
            main_price = product_info.get("main_seller", {}).get("price")
            main_seller_name = product_info.get("main_seller", {}).get("seller_name")
            is_out_of_stock = product_info.get("main_seller", {}).get("out_of_stock", False)

            if main_price:
                print(f"  -> Ana Satıcı: {main_seller_name}, Fiyat: {main_price}")
                records_to_save.append({
                    'company_id': MARKETPLACE_COMPANY_ID,
                    'attribute_id': PRICE_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': standardize_price(main_price),
                    'attribute_name': 'price'
                })
            elif is_out_of_stock:
                print(f"  -> Stok Tükendi olarak işaretleniyor.")
                records_to_save.append({
                    'company_id': MARKETPLACE_COMPANY_ID,
                    'attribute_id': STOCK_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': 'true',
                    'attribute_name': 'out_of_stock'
                })

            # 2. Diğer Satıcıları İşle
            other_sellers = product_info.get("other_sellers", [])
            if other_sellers:
                print(f"  -> {len(other_sellers)} adet diğer satıcı bulundu. İşleniyor...")
                for seller_data in other_sellers:
                    seller_name = seller_data.get("seller_name")
                    seller_price = seller_data.get("price")

                    if not (seller_name and seller_price): continue

                    # Ana satıcı ile aynı isimde olan diğer satıcıları atla (tekrarı önlemek için)
                    if seller_name == main_seller_name: continue

                    seller_company = repo.get_seller_by_name_and_marketplace(seller_name, MARKETPLACE_COMPANY_ID)
                    if not seller_company:
                        print(f"    -> Yeni satıcı '{seller_name}' Pazarama pazaryeri için veritabanına ekleniyor...")
                        new_seller_data = {
                            'name': seller_name, 'is_marketplace': False, 'logo': None, 'is_screenshot': False,
                            'marketplace_id': marketplace_company.id,
                            'application_id': marketplace_company.application_id
                        }
                        try:
                            seller_company = repo.create_company(new_seller_data, marketplace_company.server_id)
                        except Exception as e:
                            print(f"HATA: {seller_name} oluşturulamadı: {e}")
                            continue

                    print(f"    -> '{seller_name}' (ID: {seller_company.id}) için fiyat kaydediliyor: {seller_price}")
                    records_to_save.append({
                        'company_id': seller_company.id,
                        'attribute_id': PRICE_ATTRIBUTE_ID,
                        'mpn': product.mpn,
                        'value': standardize_price(seller_price),
                        'attribute_name': 'price'
                    })
            time.sleep(2)

    except Exception as e:
        print(f"Ana program döngüsünde bir hata oluştu: {e}")
    finally:
        scraper.close()
        if records_to_save:
            try:
                print(f"\n{len(records_to_save)} adet kayıt veritabanına işlenmek üzere Repository'e gönderiliyor...")
                repo.create_attribute_values(records_to_save)
                print("Kayıt işlemi Repository tarafından tamamlandı.")
            except Exception as e:
                print(f"HATA: Repository üzerinden kayıt sırasında sorun oluştu: {e}")
                db_session.rollback()
        else:
            print("\nKaydedilecek yeni veri bulunamadı.")

        db_session.close()
        print("\nVeritabanı oturumu kapatıldı. Program sonlandı.")