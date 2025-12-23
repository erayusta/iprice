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

# Veritabanı ve Repository için gerekli importlar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ==============================================================================
# LÜTFEN DİKKAT:
# Aşağıdaki import yollarının kendi projenizin dosya yapısına göre
# doğru olduğundan emin olun.

server_path = os.getenv('SERVER_PATH')

if os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.repositories.ProductRepository import ProductRepository
from app.helper.standardize_price import standardize_price


# Repository'nizin `standardize_price` metodunu kullandığını varsayıyoruz.
# Eğer bu fonksiyon farklı bir yerdeyse, yolu ona göre güncelleyin.
# from app.helper.standardize_price import standardize_price
# ==============================================================================



class A101Scraper:
    """
    A101 web sitesinden ürün fiyatlarını Selenium kullanarak çeken sınıf.
    Tarayıcıyı bir kez başlatır ve verilen URL listesini işler.
    """

    def __init__(self):
        self.driver = self._initialize_driver()
        # Fiyat elementinin XPath'i
        self.price_xpath = "//*[@id='ProductPrice']/div"

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

        # ChromeDriver'ınızın sistemdeki yolunu buraya girin
        service = Service(executable_path='/usr/bin/chromedriver')

        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(">>> Tarayıcı başarıyla başlatıldı.")
            return driver
        except Exception as e:
            print(f"HATA: WebDriver başlatılamadı. Hata: {e}")
            raise

    def get_price_from_url(self, url: str) -> str | None:
        """Verilen bir URL'den fiyat metnini çeker."""
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 15)
            price_element = wait.until(EC.visibility_of_element_located((By.XPATH, self.price_xpath)))
            return price_element.text.strip()
        except TimeoutException:
            print(f"  -> HATA: Fiyat elementi bulunamadı (Timeout) - {url}")
            return None
        except Exception as e:
            print(f"  -> HATA: Fiyat çekilirken beklenmedik bir sorun oluştu: {e}")
            return None

    def close_scraper(self):
        """Tarayıcıyı güvenli bir şekilde kapatır."""
        if self.driver:
            print("\n>>> Tüm işlemler bitti. Tarayıcı kapatılıyor.")
            self.driver.quit()


if __name__ == "__main__":

    # --- Veritabanı ve Repository Kurulumu ---
    # Kendi veritabanı bilgilerinizi buraya girin.
    db_host = os.getenv("SHARED_DB_HOST", "10.20.50.16")
    db_user = os.getenv("SHARED_DB_USER", "ipricetestuser")
    db_pass = os.getenv("SHARED_DB_PASS", "YeniSifre123!")
    db_name = os.getenv("SHARED_DB_NAME", "ipricetest")
    db_port = os.getenv("SHARED_DB_PORT", "5432")
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # ProductRepository'i veritabanı oturumu ile başlat
    repo = ProductRepository(db_session=db_session)

    # --- Sabit Değişkenler ---
    COMPANY_ID_TO_SCRAPE = 28
    # "price" attribute'ünün `attribute` tablosundaki ID'si (Bu ID'yi DB'den kontrol edin!)
    PRICE_ATTRIBUTE_ID = 1

    # 1. URL'leri ProductRepository üzerinden çek
    print(f"Veritabanından company_id={COMPANY_ID_TO_SCRAPE} için URL'ler çekiliyor...")
    products_to_scrape = repo.get_products_with_urls_by_company_id(company_id=COMPANY_ID_TO_SCRAPE)

    if not products_to_scrape:
        print("\nİşlenecek URL bulunamadığı için program sonlandırılıyor.")
        db_session.close()
        exit()

    scraper = A101Scraper()
    records_to_save = []

    try:
        print(f"\nToplam {len(products_to_scrape)} adet ürün için fiyat çekme işlemi başlıyor...")

        for product in products_to_scrape:
            print("------------------------------------------")
            print(f"İşleniyor (MPN: {product.mpn}): {product.url}")

            raw_price = scraper.get_price_from_url(product.url)

            if raw_price:
                print(f"  -> BAŞARILI: Ham fiyat bulundu -> {raw_price}")

                # `create_attribute_values` metodunun beklediği formatta veri hazırla.
                # Repository'deki metodunuz 'attribute_name' anahtarını kullanarak
                # fiyatı standardize ettiği için, ham fiyatı ('value') ve attribute'ün
                # adını ('attribute_name') yolluyoruz.
                records_to_save.append({
                    'company_id': COMPANY_ID_TO_SCRAPE,
                    'attribute_id': PRICE_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': standardize_price(raw_price),
                    'attribute_name': 'price'
                })

            time.sleep(1.5)

    except Exception as e:
        print(f"Ana program döngüsünde bir hata oluştu: {e}")
    finally:
        # Ne olursa olsun tarayıcıyı ve veritabanı oturumunu kapat
        scraper.close_scraper()

        # 2. Toplanan tüm sonuçları ProductRepository üzerinden veritabanına kaydet
        if records_to_save:
            try:
                print(f"\n{len(records_to_save)} adet kayıt veritabanına işlenmek üzere Repository'e gönderiliyor...")
                repo.create_attribute_values(records_to_save)
                print("Kayıt işlemi Repository tarafından tamamlandı.")
            except Exception as e:
                print(f"HATA: Repository üzerinden kayıt sırasında sorun oluştu: {e}")
                db_session.rollback()  # Hata durumunda işlemi geri al
        else:
            print("\nKaydedilecek yeni veri bulunamadı.")

        db_session.close()
        print("\nVeritabanı oturumu kapatıldı. Program sonlandı.")