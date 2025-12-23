import time
import logging
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from app.services.base.CrawlerServiceInterface import CrawlerServiceInterface
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ImageRepository import ImageRepository
from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.helper.standardize_price import standardize_price


class PazaramaService(CrawlerServiceInterface):

    def extract_product_data(self, url: str, mpn: str, company: str) -> Dict[str, any]:
        pass

    use_selenium = True

    def __init__(
            self,
            product_repository: ProductRepository,
            image_repository: ImageRepository,
            screenshot_repository: ScreenshotRepository,
    ):
        super().__init__()
        self.product_repository = product_repository
        self.image_repository = image_repository
        self.screenshot_repository = screenshot_repository

    def extract_product_data(self, url: str, mpn: str, company: str) -> Dict[str, any]:
        """
        Hızlı Pazarama extraction
        """
        self._log_extraction_start(url, mpn, company)

        self.logger.info('Burada başladı!!!')

        try:
            # Hızlı modal scraping
            raw_result = self._get_fast_data_with_modal_scraping(url)

            # Çıktıyı standardize et
            standardized_result = self._standardize_output(raw_result)

            self._log_extraction_success(standardized_result, mpn)
            return standardized_result

        except Exception as e:
            self._log_extraction_error(e, url, mpn)
            return {
                'price': None,
                'is_stock': False,
                'title': None,
                'is_redirect': False,
                'other_sellers': []
            }

    def _standardize_output(self, raw_result: Dict) -> Dict[str, any]:
        """
        Raw result'ı interface formatına çevirir
        """
        main_price = raw_result.get('main_price')
        other_sellers = raw_result.get('other_sellers', [])

        # Ana fiyatı standardize et
        standardized_price = None
        is_stock = False

        if main_price:
            standardized_price = standardize_price(main_price)
            is_stock = True

        # Diğer satıcıların fiyatlarını standardize et
        standardized_sellers = []
        for seller in other_sellers:
            if seller.get('price'):
                seller_copy = seller.copy()
                seller_copy['price'] = standardize_price(seller['price'])
                standardized_sellers.append(seller_copy)
            else:
                standardized_sellers.append(seller)

        return {
            'price': standardized_price,
            'is_stock': is_stock,
            'title': None,
            'is_redirect': False,
            'other_sellers': standardized_sellers
        }

    def _get_fast_data_with_modal_scraping(self, url):
        """
        Hızlı kodunuzdaki mantığı takip eden optimize edilmiş scraping
        Monitör sistemini kaldırıp sadece core scraping'e odaklanır
        """
        self.logger.info("🎯 HIZLI SELENIUM + MODAL SCRAPING")

        # Chrome ayarları (hızlı kodunuzdaki gibi)
        self.logger.info("🚀 Chrome ayarları yapılandırılıyor...")
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
        result = {'main_price': None, 'other_sellers': []}

        try:
            # Chrome başlat
            start_time = time.time()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 10)

            # Sayfa yükle
            self.logger.info(f"🌐 Sayfa yükleniyor: {url[:60]}...")
            driver.get(url)

            # Render bekle
            self.logger.info("⏳ Sayfa render bekleniyor...")
            time.sleep(3)

            # Ana fiyat ara
            self.logger.info("🔍 Ana fiyat aranıyor...")
            try:
                main_price_element = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div/div[1]'))
                )
                result['main_price'] = main_price_element.text.strip()
                self.logger.info(f"✅ Ana fiyat bulundu: {result['main_price']}")
            except TimeoutException:
                self.logger.warning("❌ Ana fiyat bulunamadı")

            # "Diğer Satıcılar" butonunu bul ve tıkla - TEK DENEME
            self.logger.info("🔘 'Diğer Satıcılar' butonu aranıyor...")

            # Tek bir selector ile hızlı arama (timeout 5 saniye)
            other_sellers_button = None
            try:
                # En yaygın selector'ı ilk dene
                other_sellers_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='M6iJLUpgHKlEPzGcOggE']"))
                )
                self.logger.info("✅ Buton bulundu")
            except TimeoutException:
                # Alternatif selector (sadece 1 tane daha)
                try:
                    other_sellers_button = driver.find_element(By.XPATH,
                                                               "//button[contains(text(), 'Diğer Satıcılar')]")
                    self.logger.info("✅ Buton alternatif selector ile bulundu")
                except:
                    self.logger.warning("❌ 'Diğer Satıcılar' butonu bulunamadı")
                    other_sellers_button = None

            # Buton bulunduysa işleme devam et
            if other_sellers_button:
                try:
                    # Butona scroll et ve tıkla
                    driver.execute_script("arguments[0].scrollIntoView(true);", other_sellers_button)
                    time.sleep(1)

                    try:
                        other_sellers_button.click()
                        self.logger.info("✅ 'Diğer Satıcılar' butonuna tıklandı")
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", other_sellers_button)
                        self.logger.info("✅ 'Diğer Satıcılar' butonuna JS ile tıklandı")

                    # Modal açılmasını bekle
                    time.sleep(2)

                    # Modal'dan satıcıları çek
                    self.logger.info("🔍 Modal içindeki satıcılar aranıyor...")
                    result['other_sellers'] = self._extract_sellers_fast(driver, wait)

                except Exception as e:
                    self.logger.error(f"❌ Buton tıklama hatası: {e}")

            extraction_time = time.time() - start_time
            self.logger.info(f"✅ Hızlı extraction tamamlandı ({extraction_time:.1f}s)")

        except Exception as e:
            self.logger.error(f"💥 Hızlı selenium hatası: {e}")

        finally:
            if driver:
                self.logger.debug("🔒 Chrome kapatılıyor...")
                driver.quit()

        return result

    def _extract_sellers_fast(self, driver, wait):
        """
        Hızlı kodunuzdaki mantığı takip eden seller extraction
        Gereksiz debug çıktıları kaldırılmış, sadece core işlemler
        """
        sellers = []

        try:
            # Modal container'ı bul (hızlı kodunuzdaki selector'lar)
            modal_selectors = [
                "div[class*='hb-fzplVX']",
                "div[class*='modal']",
                "[role='dialog']",
                "div[class*='overlay']"
            ]

            modal_found = False
            modal_container = None

            for modal_selector in modal_selectors:
                try:
                    modal_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector)))
                    modal_found = True
                    self.logger.debug(f"✅ Modal bulundu: {modal_selector}")
                    break
                except TimeoutException:
                    continue

            if not modal_found:
                self.logger.warning("❌ Modal bulunamadı")
                return sellers

            # Spesifik modal container'ı bul
            try:
                modal_container = driver.find_element(By.CSS_SELECTOR,
                                                      "div[class*='hb-fzplVX'][class*='gaxx'][class*='s5hixy3jjg3'][class*='XrCxGG290pJRpsP9fhlZ']")
                self.logger.debug("✅ Spesifik modal container bulundu")
            except:
                modal_container = driver.find_element(By.CSS_SELECTOR, "div[class*='hb-fzplVX']")
                self.logger.debug("✅ Genel modal container bulundu")

            # Satıcı item'larını bul
            seller_selectors = [
                "div[class*='VwUAvtsSpdiwukfc0VGp'][class*='IsAfBKbg4xH3kdMRzVZO'][class*='mnWNji9_P_vYbkjHXtoH']",
                "div.VwUAvtsSpdiwukfc0VGp.IsAfBKbg4xH3kdMRzVZO.mnWNji9_P_vYbkjHXtoH",
                "div[class*='VwUAvtsSpdiwukfc0VGp']",
                "div[class*='IsAfBKbg4xH3kdMRzVZO']",
                "div[class*='mnWNji9_P_vYbkjHXtoH']"
            ]

            seller_items = []
            for selector in seller_selectors:
                try:
                    items = modal_container.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        seller_items = items
                        self.logger.info(f"✅ Satıcı item'ları bulundu: {len(items)} öğe")
                        break
                except:
                    continue

            if not seller_items:
                # Fallback: Modal içindeki tüm div'leri al
                seller_items = modal_container.find_elements(By.CSS_SELECTOR, "div")
                self.logger.debug(f"🔍 Fallback: Modal içinde {len(seller_items)} div bulundu")

            # Her satıcı item'ını işle (hızlı yaklaşım - ilk 15 öğe)
            processed_sellers = 0
            for i, item in enumerate(seller_items[:15]):
                try:
                    seller_info = {}
                    item_text = item.text.strip()

                    if not item_text or len(item_text) < 10:
                        continue

                    # Basitleştirilmiş veri çekme (hızlı kodunuzdaki gibi)
                    # Satıcı adı - basit yaklaşım
                    try:
                        lines = item_text.split('\n')
                        if lines:
                            potential_name = lines[0].strip()
                            if (potential_name and len(potential_name) > 2 and len(potential_name) < 50 and
                                    '₺' not in potential_name and 'TL' not in potential_name and
                                    '.' not in potential_name and ',' not in potential_name):
                                seller_info['name'] = potential_name
                    except:
                        pass

                    # Fiyat - basit yaklaşım
                    try:
                        for line in item_text.split('\n'):
                            if ('₺' in line or 'TL' in line) and any(char.isdigit() for char in line):
                                seller_info['price'] = line.strip()
                                break
                    except:
                        pass

                    # Rating - basit yaklaşım
                    try:
                        for line in item_text.split('\n'):
                            line = line.strip()
                            if len(line) < 5 and (',' in line or ('.' in line and line.replace('.', '').isdigit())):
                                seller_info['rating'] = line
                                break
                    except:
                        pass

                    # Teslimat/Kargo bilgisi - basit yaklaşım
                    try:
                        for line in item_text.split('\n'):
                            if any(word in line.lower() for word in
                                   ['kargo', 'teslimat', 'günü', 'haziran', 'sipariş', 'ücretsiz']):
                                seller_info['shipment'] = line.strip()
                                break
                    except:
                        pass

                    # En az fiyat varsa kaydet
                    if seller_info.get('price'):
                        sellers.append(seller_info)
                        processed_sellers += 1
                        self.logger.debug(f"✅ Satıcı {i + 1} kaydedildi")
                    elif len(item_text) > 20:
                        # Ham veri olarak kaydet
                        lines = item_text.split('\n')
                        for line in lines:
                            if '₺' in line or 'TL' in line:
                                seller_info['price'] = line.strip()
                                break

                        if not seller_info.get('price'):
                            seller_info['raw_text'] = item_text[:100] + "..."

                        sellers.append(seller_info)
                        processed_sellers += 1

                except Exception as e:
                    self.logger.debug(f"⚠️ Satıcı {i + 1} işlem hatası: {e}")
                    continue

            self.logger.info(f"✅ Toplam {processed_sellers} satıcı extract edildi")

        except Exception as e:
            self.logger.error(f"💥 Modal satıcı extraction hatası: {e}")

        return sellers

    def cleanup(self):
        """Cleanup işlemi"""
        pass