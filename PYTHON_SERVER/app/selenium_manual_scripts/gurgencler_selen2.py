from __future__ import annotations

import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Veritabanı ve Repository için gerekli importlar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ==============================================================================
# LÜTFEN DİKKAT:
# Aşağıdaki import yollarının kendi projenizin dosya yapısına göre
# doğru olduğundan emin olun.
server_path = os.getenv('SERVER_PATH')
if server_path and os.path.exists(server_path):
    sys.path.append(server_path)
    print("Sunucu ortamı algılandı, sunucu yolu kullanılıyor.")
from app.repositories.ProductRepository import ProductRepository
from app.helper.standardize_price import standardize_price


class GurgencScraper:
    """
    Gürgençler web sitesinden ürün fiyat ve stok bilgilerini Selenium kullanarak çeken sınıf.
    """

    def __init__(self):
        self.driver = self._initialize_driver()
        self.price_css = ".price-box.price-final_price .price"
        self.out_of_stock_css = "button.out-of-stock-btn"
        self.in_stock_id = "product-addtocart-button"
        self.cookie_accept_id = "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"

    def _initialize_driver(self):
        print(">>> Tarayıcı (Headless Chrome) başlatılıyor...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

        service = Service(executable_path='/usr/bin/chromedriver')
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(">>> Tarayıcı başarıyla başlatıldı.")
            return driver
        except Exception as e:
            print(f"HATA: WebDriver başlatılamadı. Hata: {e}")
            raise

    def get_details_from_url(self, url: str) -> tuple[str | None, str | None]:
        """
        Verilen bir URL'den fiyat ve stok metnini çeker.
        Önce çerezleri kabul eder, sonra stok durumunu kontrol eder.
        """
        try:
            self.driver.get(url)

            # --- Çerezleri Kabul Et ---
            try:
                cookie_wait = WebDriverWait(self.driver, 5)
                accept_button = cookie_wait.until(
                    EC.element_to_be_clickable((By.ID, self.cookie_accept_id))
                )
                self.driver.execute_script("arguments[0].click();", accept_button)
                print("  -> Çerezler kabul edildi.")
            except TimeoutException:
                pass

            # --- 1. ADIM: Stokta Yok Durumunu Kontrol Et ---
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.out_of_stock_css))
                )
                return None, "Stokta Yok"
            except TimeoutException:
                pass

            # --- 2. ADIM: Ürün Stokta Varsa Fiyatı Çek ---
            wait = WebDriverWait(self.driver, 15)

            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.price_css))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_element)
            time.sleep(0.5)

            price = price_element.text.strip()

            wait.until(
                EC.presence_of_element_located((By.ID, self.in_stock_id))
            )

            return price, "Stokta Var"

        except TimeoutException:
            print(f"  -> HATA: Element bulunamadı (Timeout) - {url}")
            return None, "Belirsiz"
        except WebDriverException as e:
            if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                print(f"  -> HATA: Ağ Hatası, adres çözümlenemedi - {url}")
            else:
                print(f"  -> HATA: WebDriver hatası - {e} - {url}")
            return None, None
        except Exception as e:
            print(f"  -> HATA: Beklenmedik bir sorun oluştu: {e} - {url}")
            return None, None

    def close_scraper(self):
        """Tarayıcıyı güvenli bir şekilde kapatır."""
        if self.driver:
            print("\n>>> Tüm işlemler bitti. Tarayıcı kapatılıyor.")
            self.driver.quit()


if __name__ == "__main__":
    # --- Veritabanı ve Repository Kurulumu ---
    db_host = os.getenv("SHARED_DB_HOST", "10.20.50.16")
    db_user = os.getenv("SHARED_DB_USER", "ipricetestuser")
    db_pass = os.getenv("SHARED_DB_PASS", "YeniSifre123!")
    db_name = os.getenv("SHARED_DB_NAME", "ipricetest")
    db_port = os.getenv("SHARED_DB_PORT", "5432")
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    db_session = None
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        repo = ProductRepository(db_session=db_session)
    except Exception as e:
        print(f"HATA: Veritabanı bağlantısı kurulamadı: {e}")
        if db_session: db_session.close()
        exit()

    # --- Sabit Değişkenler ---
    COMPANY_ID_TO_SCRAPE = 4
    PRICE_ATTRIBUTE_ID = 1
    STOCK_ATTRIBUTE_ID = 6

    # 1. URL'leri ProductRepository üzerinden çek
    print(f"Veritabanından company_id={COMPANY_ID_TO_SCRAPE} için URL'ler çekiliyor...")
    products_to_scrape = repo.get_products_with_urls_by_company_id(company_id=COMPANY_ID_TO_SCRAPE)

    if not products_to_scrape:
        print("\nİşlenecek URL bulunamadığı için program sonlandırılıyor.")
        db_session.close()
        exit()

    scraper = GurgencScraper()
    records_to_save = []

    try:
        print(f"\nToplam {len(products_to_scrape)} adet ürün için veri çekme işlemi başlıyor...")
        for product in products_to_scrape:
            print("------------------------------------------")
            print(f"İşleniyor (MPN: {product.mpn}): {product.url}")

            price, stock = scraper.get_details_from_url(product.url)

            if price:
                print(f"  -> BAŞARILI: Fiyat bulundu -> {price}")
                records_to_save.append({
                    'company_id': COMPANY_ID_TO_SCRAPE,
                    'attribute_id': PRICE_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': standardize_price(price),
                    'attribute_name': 'price'
                })

            # YENİ: Stok değerini True/False olarak ayarla
            if stock and stock != "Belirsiz":
                print(f"  -> BAŞARILI: Stok durumu bulundu -> {stock}")

                # "Stokta Yok" ise True, "Stokta Var" ise False
                stock_value = True if stock == "Stokta Yok" else False

                records_to_save.append({
                    'company_id': COMPANY_ID_TO_SCRAPE,
                    'attribute_id': STOCK_ATTRIBUTE_ID,
                    'mpn': product.mpn,
                    'value': stock_value,  # Değer True/False olarak ayarlandı
                    'attribute_name': 'stock'
                })

            time.sleep(1.5)

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
                if db_session: db_session.rollback()
        else:
            print("\nKaydedilecek yeni veri bulunamadı.")

        if db_session:
            db_session.close()
            print("\nVeritabanı oturumu kapatıldı. Program sonlandı.")
