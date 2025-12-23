import time
import logging
import random

from typing import Dict, Optional, List, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.orm import Session
import threading

from app.services.base.CrawlerServiceInterface import CrawlerServiceInterface
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ImageRepository import ImageRepository
from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.helper.standardize_price import standardize_price


class HepsiburadaSeleniumService(CrawlerServiceInterface):
    SPECIAL_ATTRIBUTE_NAMES = {
        'other_seller_button', 'seller_container_xpath',
        'seller_name_in_modal', 'seller_price_in_modal', 'sub_price'
    }

    use_selenium = True

    def __init__(
            self,
            product_repository: ProductRepository,
            image_repository: ImageRepository,
            screenshot_repository: ScreenshotRepository,
            db_session: Session,
            hepsiburada_company_id: int = 7,
            hepsiburada_server_id: int = 2,
            min_delay: float = 3.0,
            max_delay: float = 8.0,
            refresh_strategy: str = 'restart',
            refresh_after_requests: int = 50
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.product_repository = product_repository
        self.image_repository = image_repository
        self.screenshot_repository = screenshot_repository
        self.db_session = db_session
        self.company_id = hepsiburada_company_id
        self.company_server_id = hepsiburada_server_id

        self.driver: Optional[webdriver.Chrome] = None
        self.driver_lock = threading.Lock()

        self.min_delay = min_delay
        self.max_delay = max_delay
        self.refresh_strategy = refresh_strategy.lower()
        self.refresh_after_requests = refresh_after_requests
        self.request_counter = 0

        all_targets = self.product_repository.get_scrape_targets_by_company_id(self.company_id)
        self.simple_extract_targets = []
        self.special_targets = {}

        for target in all_targets:
            if target['name'] in self.SPECIAL_ATTRIBUTE_NAMES:
                self.special_targets[target['name']] = target
            else:
                self.simple_extract_targets.append(target)
        self.logger.info(
            f"✅ Hepsiburada: {len(self.simple_extract_targets)} standart, {len(self.special_targets)} özel hedef yüklendi.")
        self.logger.info(
            f"🧠 Davranış Modu: {self.refresh_after_requests} istekte bir '{self.refresh_strategy}' stratejisi uygulanacak.")

    def _initialize_driver(self) -> webdriver.Chrome:
        if self.driver is None:
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

            service = Service(executable_path='/usr/bin/chromedriver', log_output='chromedriver.log')

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("✅ Chrome başarıyla başlatıldı ve yeniden kullanıma hazır.")
        return self.driver

    def extract_product_data(self, url: str, mpn: str, company: str) -> Dict[str, any]:
        self._log_extraction_start(url, mpn, company)

        with self.driver_lock:
            try:
                self.request_counter += 1
                if self.request_counter > 1 and (self.request_counter % self.refresh_after_requests == 0):
                    if self.refresh_strategy == 'restart':
                        self.logger.info(
                            f"🔄 Periyodik yenileme: {self.refresh_after_requests} istek sonrası tarayıcı yeniden başlatılıyor...")
                        self.cleanup(close_session=False)
                    elif self.refresh_strategy == 'cookies':
                        self.logger.info(
                            f"🍪 Periyodik temizlik: {self.refresh_after_requests} istek sonrası çerezler siliniyor...")
                        if self.driver:
                            self.driver.delete_all_cookies()

                driver = self._initialize_driver()
                driver.get(url)
                time.sleep(3)

                # DOĞRU ÇAĞRI: _get_dynamic_data metodu, hazır driver ile çağrılıyor
                raw_result = self._get_dynamic_data(driver, mpn)
                standardized_result = self._standardize_output(raw_result)
                self._log_extraction_success(standardized_result, mpn)

                bekleme_suresi = random.uniform(self.min_delay, self.max_delay)
                self.logger.info(f"--- Bir sonraki istek öncesi insani bekleme: {bekleme_suresi:.2f} saniye ---")
                time.sleep(bekleme_suresi)

                return standardized_result

            except Exception as e:
                self._log_extraction_error(e, url, mpn)
                self.logger.error("Kritik hata sonrası driver temizleniyor...")
                self.cleanup(close_session=False)
                return {'price': None, 'is_stock': False, 'title': None, 'is_redirect': False, 'other_sellers': []}

    def _standardize_output(self, raw_result: Dict) -> Dict[str, any]:
        main_price = raw_result.get('price')
        other_sellers = raw_result.get('other_sellers', [])
        standardized_price = standardize_price(main_price) if main_price else None

        standardized_sellers = []
        for seller in other_sellers:
            seller_copy = seller.copy()
            seller_copy['price'] = standardize_price(seller.get('price'))
            standardized_sellers.append(seller_copy)

        return {
            'price': standardized_price,
            'is_stock': bool(standardized_price),
            'title': None,  # Gerekirse bu da dinamik çekilebilir
            'is_redirect': False,
            'other_sellers': standardized_sellers
        }

    def _get_dynamic_data(self, driver: webdriver.Chrome, mpn: str) -> Dict:
        """
        Kendisine verilen HAZIR driver nesnesini kullanarak sayfadaki verileri kazır.
        """
        self.logger.info("🎯 Sayfadan dinamik veri çekiliyor...")

        scraped_data = {'other_sellers': []}
        wait = WebDriverWait(driver, 10)

        # Standart attribute'leri kazıma
        self.logger.info(f"--- {len(self.simple_extract_targets)} Standart Attribute Aranıyor ---")
        for target in self.simple_extract_targets:
            try:
                element = driver.find_element(By.XPATH, target['xpath'])
                value = element.text.strip()
                if value:
                    self.logger.info(f"✅ {target['name']} bulundu: {value}")
                    self.product_repository.create_attribute_value(
                        company_id=self.company_id,
                        attribute_id=target['id'],
                        mpn=mpn,
                        value=value
                    )
                    scraped_data[target['name']] = value
            except NoSuchElementException:
                self.logger.debug(f"❌ {target['name']} XPath ile bulunamadı.")
            except Exception as e:
                self.logger.warning(f"💥 {target['name']} işlenirken hata: {e}")

        # Özel işlemleri (buton tıklama vs.) yapma
        self.logger.info("--- Özel İşlemler Aranıyor ---")
        button_target = self.special_targets.get('other_seller_button')
        if button_target:
            try:
                self.logger.info("🔘 'Diğer Satıcılar' butonu aranıyor...")
                button = wait.until(EC.element_to_be_clickable((By.XPATH, button_target['xpath'])))
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                button.click()
                self.logger.info("✅ Butona tıklandı. Modal işlemcisi başlatılıyor...")
                time.sleep(3)

                sellers = self._extract_sellers_and_save_to_db(driver, wait, mpn, self.special_targets)
                scraped_data['other_sellers'] = sellers
            except Exception as e:
                self.logger.error(f"❌ 'other_seller_button' işlemi sırasında kritik hata: {e}")

        return scraped_data

    def _extract_sellers_and_save_to_db(self, driver: webdriver.Chrome, wait: WebDriverWait, mpn: str, config: Dict) -> \
    List[Dict[str, Any]]:

        sellers = []

        container_xpath_str = config.get('seller_container_xpath', {}).get('xpath')
        item_rel_xpath = config.get('seller_item_relative_xpath', {}).get('xpath')
        name_rel_xpath = config.get('seller_name_relative_xpath', {}).get('xpath')
        price_rel_xpath = config.get('seller_price_relative_xpath', {}).get('xpath')
        sub_price_attr = config.get('sub_price')

        if not all([container_xpath_str, item_rel_xpath, name_rel_xpath, price_rel_xpath, sub_price_attr]):
            self.logger.warning("DB'de modal kazıma için gerekli konfigürasyonlardan biri veya daha fazlası eksik: "
                                "'seller_container_xpath', 'seller_item_relative_xpath', "
                                "'seller_name_relative_xpath', 'seller_price_relative_xpath', 'sub_price'. "
                                "İşlem atlanıyor.")
            return sellers

        possible_container_xpaths = [path.strip() for path in container_xpath_str.split(';')]
        modal_container = None

        self.logger.info("🔍 Olası modal container'lar aranıyor...")
        for path in possible_container_xpaths:
            try:
                modal_container = driver.find_element(By.XPATH, path)
                self.logger.info(f"✅ Modal container bulundu. XPath: {path}")
                break
            except NoSuchElementException:
                self.logger.debug(f"   ❌ {path} bulunamadı, sonraki deneniyor.")
                continue

        if not modal_container:
            self.logger.error("❌ Olası tüm XPath'ler denendi ancak modal container bulunamadı.")
            return sellers

        # --------------------------------------------------------------------
        try:
            seller_items = modal_container.find_elements(By.XPATH, item_rel_xpath)
            self.logger.info(f"📊 {len(seller_items)} adet potansiyel satıcı öğesi bulundu.")
            if not seller_items:
                self.logger.warning("Modal container bulundu ancak içinde satıcı öğesi bulunamadı. "
                                    f"('seller_item_relative_xpath' = {item_rel_xpath})")
                return sellers
        except Exception as e:
            self.logger.error(f"Satıcı öğelerini ararken hata oluştu ('{item_rel_xpath}'): {e}")
            return sellers

        # Adım 4: Her bir satıcı "item"ını işle
        # --------------------------------------------------------------------
        for item_element in seller_items:
            try:
                # Adım 4a: Satıcı Adını ve Fiyatını çek
                seller_name = item_element.find_element(By.XPATH, name_rel_xpath).text.strip()
                raw_price = item_element.find_element(By.XPATH, price_rel_xpath).text.strip()

                if not seller_name or not raw_price:
                    continue

                # Adım 4b: Fiyatı standartlaştır
                processed_price = standardize_price(raw_price)
                self.logger.info(f"-> Bulunan Satıcı: '{seller_name}', Fiyat: '{raw_price}' -> '{processed_price}'")

                # Adım 4c: Satıcıyı DB'de bul veya oluştur
                company_id = self._get_company_id_by_name(seller_name)

                if not company_id:
                    self.logger.info(f"'{seller_name}' DB'de bulunamadı, yeni şirket kaydı oluşturuluyor...")
                    new_seller_data = {
                        'name': seller_name,
                        'is_marketplace': False,
                        'server_id': self.company_server_id,
                        'logo': None,
                        'is_screenshot': False,
                        'marketplace_id': self.company_id
                    }
                    # create_company metodunun yeni oluşturulan company nesnesini döndürdüğünü varsayıyoruz.
                    new_company = self.product_repository.create_company(new_seller_data)
                    company_id = new_company.id
                    self.logger.info(f"✅ Yeni şirket '{seller_name}' oluşturuldu. ID: {company_id}")

                # Adım 4d: Fiyat attribute'ünü veritabanına kaydet
                self.product_repository.create_attribute_value(
                    company_id=company_id,
                    attribute_id=sub_price_attr['id'],
                    mpn=mpn,
                    value=processed_price
                )

                # Adım 4e: Sonuç listesine ekle
                sellers.append({'name': seller_name, 'price': processed_price})

            except NoSuchElementException:
                self.logger.debug("Bir satıcı öğesi beklenen yapıda değildi, atlanıyor.")
                continue
            except Exception as e:
                self.logger.error(f"Bir satıcı öğesi işlenirken beklenmedik bir hata oluştu: {e}")
                continue

        self.logger.info(f"✅ Modal'dan toplam {len(sellers)} satıcı bilgisi başarıyla işlendi ve kaydedildi.")
        return sellers

    def _get_company_id_by_name(self, seller_name: str) -> Optional[int]:
        try:
            company = self.product_repository.get_company_by_name(seller_name)
            return company.id if company else None
        except Exception as e:
            self.logger.error(f"Company ID bulma hatası: {e}")
            return None

    def cleanup(self, close_session: bool = True):
        with self.driver_lock:
            if self.driver:
                self.logger.info(f"🧹 Selenium Service cleanup: Chrome kapatılıyor... (DB Session Kapatılsın mı: {close_session})")
                try:
                    self.driver.quit()
                except Exception as e:
                    self.logger.error(f"💥 Driver kapatılırken hata oluştu: {e}")
                finally:
                    self.driver = None

        if close_session and self.db_session and self.db_session.is_active:
            self.db_session.close()