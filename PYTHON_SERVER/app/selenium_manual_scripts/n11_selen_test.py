from __future__ import annotations

import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

server_path = os.getenv('SERVER_PATH')

if server_path and os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.repositories.ProductRepository import ProductRepository
from app.model.Company import Company
from app.helper.standardize_price import standardize_price


class N11Scraper:
    """
    N11 web sitesinden ana satıcı ve diğer satıcıların bilgilerini çeken sınıf.
    """

    def __init__(self):
        self.driver = self._initialize_driver()
        self.main_price_css_selector = ".newPrice"
        self.main_seller_xpath = '//*[@id="unf-p-id"]/div/div[2]/div[2]/div[2]/div[1]/div[1]/a'
        self.other_sellers_list_xpath = '//*[@id="unf-sell"]/div[2]/div'
        self.other_seller_name_xpath = './/div/div[1]/div/a'
        self.other_seller_price_css = ".b-p-new"

    def _initialize_driver(self):
        print(">>> Tarayıcı (Headless Chrome) başlatılıyor...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--ignore-certificate-errors')
        service = Service(executable_path='/usr/bin/chromedriver')

        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(">>> Tarayıcı başarıyla başlatıldı.")
            return driver
        except Exception as e:
            print(f"HATA: WebDriver başlatılamadı. Hata: {e}")
            raise

    def get_product_info(self, url: str) -> dict:
        """Verilen URL'den ana satıcı ve diğer satıcıların bilgilerini çeker."""
        product_data = {"main_seller": {}, "other_sellers": []}

        try:
            if not url.endswith("#unf-sell"):
                url += "#unf-sell"

            self.driver.get(url)
            time.sleep(4)

            try:
                price = self.driver.find_element(By.CSS_SELECTOR, self.main_price_css_selector).text
                product_data["main_seller"]["price"] = price.strip()
            except Exception:
                product_data["main_seller"]["price"] = None
            try:
                seller = self.driver.find_element(By.XPATH, self.main_seller_xpath).text
                product_data["main_seller"]["seller_name"] = seller.strip()
            except Exception:
                product_data["main_seller"]["seller_name"] = None

            seller_boxes = self.driver.find_elements(By.XPATH, self.other_sellers_list_xpath)
            for seller_box in seller_boxes:
                seller_info = {}
                try:
                    seller_name = seller_box.find_element(By.XPATH, self.other_seller_name_xpath).text
                    seller_info["seller_name"] = seller_name.strip()
                except Exception:
                    seller_info["seller_name"] = None
                try:
                    seller_price = seller_box.find_element(By.CSS_SELECTOR, self.other_seller_price_css).text
                    seller_info["price"] = seller_price.strip()
                except Exception:
                    seller_info["price"] = None
                try:
                    link_xpath = ''
                    seller_info["link"] = ''
                except Exception:
                    seller_info["link"] = None

                if seller_info.get("seller_name") and seller_info.get("price"):
                    product_data["other_sellers"].append(seller_info)

            return product_data
        except Exception as e:
            print(f"  -> HATA: Sayfa işlenirken genel bir hata oluştu: {e}")
            return product_data

    def close_scraper(self):
        """Tarayıcıyı güvenli bir şekilde kapatır."""
        if self.driver:
            print("\n>>> Tüm işlemler bitti. Tarayıcı kapatılıyor.")
            self.driver.quit()


if __name__ == "__main__":
    db_user, db_pass, db_host, db_port, db_name = os.getenv('SHARED_DB_USER', 'ipricetestuser'), os.getenv('SHARED_DB_PASS', 'YeniSifre123!'), os.getenv('SHARED_DB_HOST', '10.20.50.16'), os.getenv('SHARED_DB_PORT', '5432'), os.getenv('SHARED_DB_NAME', 'ipricetest')
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    repo = ProductRepository(db_session=db_session)

    MARKETPLACE_COMPANY_ID = 155
    PRICE_ATTRIBUTE_ID = 1

    marketplace_company = db_session.query(Company).filter_by(id=MARKETPLACE_COMPANY_ID).first()
    if not marketplace_company:
        print(
            f"HATA: ID'si {MARKETPLACE_COMPANY_ID} olan ana pazaryeri (N11) veritabanında bulunamadı. Script durduruluyor.")
        db_session.close()
        exit()

    print(f"Veritabanından company_id={MARKETPLACE_COMPANY_ID} (N11) için URL'ler çekiliyor...")
    products_to_scrape = repo.get_products_with_urls_by_company_id(company_id=MARKETPLACE_COMPANY_ID)

    if not products_to_scrape:
        print("\nİşlenecek URL bulunamadığı için program sonlandırılıyor.")
        db_session.close()
        exit()

    scraper = N11Scraper()
    records_to_save = []

    try:
        print(f"\nToplam {len(products_to_scrape)} adet ürün için fiyat çekme işlemi başlıyor...")

        for product in products_to_scrape:
            print("------------------------------------------")
            print(f"İşleniyor (MPN: {product.mpn}): {product.url}")

            product_info = scraper.get_product_info(product.url)

            main_price = product_info.get("main_seller", {}).get("price")
            if main_price:
                print(f"  -> Ana Satıcı Fiyatı Bulundu: {main_price}")
                records_to_save.append({
                    'company_id': MARKETPLACE_COMPANY_ID,
                    'attribute_id': PRICE_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': standardize_price(main_price),
                    'attribute_name': 'price'
                })

            other_sellers = product_info.get("other_sellers", [])
            if other_sellers:
                print(f"  -> {len(other_sellers)} adet diğer satıcı bulundu. İşleniyor...")
                for seller_data in other_sellers:
                    seller_name = seller_data.get("seller_name")
                    seller_price = seller_data.get("price")

                    if not (seller_name and seller_price):
                        continue

                    seller_company = repo.get_seller_by_name_and_marketplace(seller_name, MARKETPLACE_COMPANY_ID)

                    if not seller_company:
                        print(f"    -> Yeni satıcı '{seller_name}' veritabanına ekleniyor...")
                        new_seller_data = {
                            'name': seller_name,
                            'is_marketplace': False,
                            'logo': None,
                            'is_screenshot': False,
                            'marketplace_id': marketplace_company.id,
                            'application_id': marketplace_company.application_id
                        }
                        try:
                            # =================================================================
                            # HATA BURADAYDI, DÜZELTİLDİ: server_id ayrı bir argüman olarak eklendi
                            seller_company = repo.create_company(new_seller_data, marketplace_company.server_id)
                            # =================================================================
                            print(f"    -> '{seller_name}' başarıyla oluşturuldu (ID: {seller_company.id}).")
                        except Exception as create_error:
                            print(f"    -> HATA: '{seller_name}' oluşturulurken sorun çıktı: {create_error}")
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
        scraper.close_scraper()

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