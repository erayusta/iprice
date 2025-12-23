from __future__ import annotations

import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

server_path = os.getenv('SERVER_PATH')
if server_path and os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.repositories.ProductRepository import ProductRepository
from app.model.Company import Company
from app.helper.standardize_price import standardize_price


class AmazonScraper:

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

        # --- YENİ EKLENEN ARGÜMANLAR ---
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # ------------------------------------

        # User agent'ı sunucudaki gerçek Chrome versiyonu ile güncelleyin.
        # Sunucuda `chromium --version` komutu ile versiyonu öğrenip buraya yazın.
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')  # Versiyonu güncelleyin!
        chrome_options.binary_location = '/usr/bin/chromium'

        service = Service(executable_path='/usr/bin/chromedriver', log_output='chromedriver.log')
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            # Otomasyonu gizlemek için ek bir script çalıştırın
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(">>> Tarayıcı başarıyla başlatıldı.")
            return driver
        except WebDriverException as e:
            print(f"HATA: Chrome WebDriver başlatılamadı: {e}")
            raise

    def get_product_info(self, url: str) -> dict:

        product_data = {"main_seller": {}, "other_sellers": []}
        try:
            self.driver.get(url)
            time.sleep(3)

            try:
                CSS_MAIN_PRICE = '.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay .a-price-whole'
                product_data["main_seller"]["price"] = self.driver.find_element(By.CSS_SELECTOR,
                                                                                CSS_MAIN_PRICE).text.strip()
            except NoSuchElementException:
                product_data["main_seller"]["price"] = None

            try:
                XPATH_MAIN_SELLER = '//*[@id="bylineInfo"]'
                product_data["main_seller"]["seller_name"] = self.driver.find_element(By.XPATH,
                                                                                      XPATH_MAIN_SELLER).text.strip()
            except NoSuchElementException:
                product_data["main_seller"]["seller_name"] = None

            # --- DİĞER SATICILARI İŞLE (DURUMA GÖRE) ---
            print("ℹ️ Diğer satıcılar için sayfa yapısı kontrol ediliyor...")

            XPATH_OTHER_SELLERS_BUTTON = '//*[@id="aod-ingress-link"]'

            try:
                XPATH_SEE_ALL_PRODUCTS = '//*[@id="aod-offer-list"]/div'

                see_all_button = self.driver.find_element(By.XPATH, XPATH_SEE_ALL_PRODUCTS)

                self.driver.execute_script("arguments[0].click();", see_all_button)

                print("✅ 'Tüm Ürünleri Gör' butonuna tıklandı.")
                time.sleep(1)

            except NoSuchElementException:
                print("ℹ️ 'Tüm Ürünleri Gör' butonu bulunamadı.")
            except Exception as e:
                print(f"❌ Butona tıklanırken bir hata oluştu: {e}")

            other_sellers_buttons = self.driver.find_elements(By.XPATH, XPATH_OTHER_SELLERS_BUTTON)

            if other_sellers_buttons:
                print("✅ Diğer satıcılar butonu bulundu. Pop-up yöntemi kullanılıyor...")
                try:
                    button = other_sellers_buttons[0]
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(4)

                    XPATH_SELLER_BOXES_IN_POPUP = '//*[@id="aod-offer"]'
                    seller_boxes = self.driver.find_elements(By.XPATH, XPATH_SELLER_BOXES_IN_POPUP)

                    print(f"    -> Pop-up içinden {len(seller_boxes)} adet satıcı bulundu.")
                    for i, seller_box in enumerate(seller_boxes, 1):
                        seller_info = {}
                        try:
                            seller_element = seller_box.find_element(By.XPATH, ".//div[@id='aod-offer-soldBy']//a")
                            seller_info["seller_name"] = seller_element.text.strip()
                        except Exception:
                            seller_info["seller_name"] = f"Satıcı {i}"
                        try:
                            price_xpath = f'//*[@id="aod-price-{i}"]/div/span[2]/span[2]/span[1]'
                            seller_info["price"] = self.driver.find_element(By.XPATH, price_xpath).text.strip()
                        except Exception:
                            seller_info["price"] = None

                        product_data["other_sellers"].append(seller_info)

                except Exception as e:
                    print(f"❌ Pop-up açılırken veya işlenirken bir hata oluştu: {e}")
            return product_data

        except WebDriverException as e:
            print(f"  -> HATA: Sayfa yüklenirken veya işlenirken ciddi bir hata oluştu: {e}")
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

    MARKETPLACE_COMPANY_ID = 26  # Amzon için ID
    PRICE_ATTRIBUTE_ID = 1  # "price" attribute ID'si

    marketplace_company = db_session.query(Company).filter_by(id=MARKETPLACE_COMPANY_ID).first()
    if not marketplace_company:
        print(f"HATA: ID'si {MARKETPLACE_COMPANY_ID} olan ana pazaryeri (Amazon) veritabanında bulunamadı.")
        db_session.close()
        exit()

    print(f"Veritabanından company_id={MARKETPLACE_COMPANY_ID} (Amazon) için URL'ler çekiliyor...")
    products_to_scrape = repo.get_products_with_urls_by_company_id(company_id=MARKETPLACE_COMPANY_ID)

    if not products_to_scrape:
        print("\nİşlenecek URL bulunamadığı için program sonlandırılıyor.")
        db_session.close()
        exit()

    scraper = AmazonScraper()
    records_to_save = []

    try:
        print(f"\nToplam {len(products_to_scrape)} adet ürün için fiyat çekme işlemi başlıyor...")
        for product in products_to_scrape:
            print("------------------------------------------")
            print(f"İşleniyor (MPN: {product.mpn}): {product.url}")

            product_info = scraper.get_product_info(product.url)

            # --- 1. ANA SATICIYI VERİTABANINDA BUL VEYA OLUŞTUR ---
            main_seller_name = product_info.get("main_seller", {}).get("seller_name")
            main_seller_company = None

            if main_seller_name:
                try:
                    main_seller_company = repo.get_seller_by_name_and_marketplace(main_seller_name,
                                                                                  MARKETPLACE_COMPANY_ID)
                    if not main_seller_company:
                        print(
                            f"    -> Yeni ana satıcı '{main_seller_name}' Trendyol pazaryeri için veritabanına ekleniyor...")
                        new_seller_data = {
                            'name': main_seller_name, 'is_marketplace': False, 'logo': None, 'is_screenshot': False,
                            'marketplace_id': marketplace_company.id,
                            'application_id': marketplace_company.application_id
                        }
                        main_seller_company = repo.create_company(new_seller_data, marketplace_company.server_id)
                except Exception as e:
                    print(f"HATA: Ana satıcı '{main_seller_name}' işlenirken sorun oluştu: {e}")
                    continue
            else:
                print("    -> UYARI: Ürün için ana satıcı adı bulunamadı. Bu ürüne ait veriler kaydedilemeyecek.")
                continue

            # --- 2. ANA SATICI İÇİN FİYAT VE STOK BİLGİLERİNİ KAYDET ---
            if main_seller_company:
                # Fiyat bilgisi
                sell_price = product_info.get("main_seller", {}).get("sell_price")
                original_price = product_info.get("main_seller", {}).get("price")
                final_price = sell_price if sell_price else original_price

                if final_price:
                    print(
                        f"  -> Ana Satıcı: {main_seller_company.name} (ID: {main_seller_company.id}), Fiyat: {final_price}")
                    records_to_save.append({
                        'company_id': main_seller_company.id,
                        'attribute_id': PRICE_ATTRIBUTE_ID,
                        'mpn': product.mpn,
                        'value': standardize_price(final_price),
                        'attribute_name': 'price'
                    })

                '''
                # Stok bilgisi
                is_out_of_stock = product_info.get("main_seller", {}).get("out_of_stock", False)
                stock_value = 'true' if is_out_of_stock else 'false'
                stock_status_text = "Stok Tükendi" if is_out_of_stock else "Stokta Mevcut"

                print(f"  -> Stok Durumu: {stock_status_text} (Değer: {stock_value})")
                records_to_save.append({
                    'company_id': main_seller_company.id,
                    'attribute_id': STOCK_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': stock_value,
                    'attribute_name': 'out_of_stock_status'
                })
                '''

            # --- 3. DİĞER SATICILARI İŞLE ---
            other_sellers = product_info.get("other_sellers", [])
            if other_sellers:
                print(f"  -> {len(other_sellers)} adet diğer satıcı bulundu. İşleniyor...")
                for seller_data in other_sellers:
                    seller_name = seller_data.get("seller_name")
                    seller_price = seller_data.get("price")

                    if not (seller_name and seller_price): continue
                    if seller_name == main_seller_name: continue

                    seller_company = repo.get_seller_by_name_and_marketplace(seller_name, MARKETPLACE_COMPANY_ID)
                    if not seller_company:
                        print(
                            f"    -> Yeni diğer satıcı '{seller_name}' Trendyol pazaryeri için veritabanına ekleniyor...")
                        new_seller_data = {
                            'name': seller_name, 'is_marketplace': False, 'logo': None, 'is_screenshot': False,
                            'marketplace_id': marketplace_company.id,
                            'application_id': marketplace_company.application_id
                        }
                        try:
                            seller_company = repo.create_company(new_seller_data, marketplace_company.server_id)
                        except Exception as e:
                            print(f"HATA: Diğer satıcı {seller_name} oluşturulamadı: {e}")
                            continue

                    print(
                        f"    -> '{seller_name}' (ID: {seller_company.id}) için fiyat kaydediliyor: {seller_price}")
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
                print(
                    f"\n{len(records_to_save)} adet kayıt veritabanına işlenmek üzere Repository'e gönderiliyor...")
                repo.create_attribute_values(records_to_save)
                print("Kayıt işlemi Repository tarafından tamamlandı.")
            except Exception as e:
                print(f"HATA: Repository üzerinden kayıt sırasında sorun oluştu: {e}")
                db_session.rollback()
        else:
            print("\nKaydedilecek yeni veri bulunamadı.")

        db_session.close()
        print("\nVeritabanı oturumu kapatıldı. Program sonlandı.")
