import time
import os
from typing import Dict, Any
from .base import ParserInterface
from app.helper.get_random_agents import get_random_user_agent
from app.services.ProxyManager import get_proxy_manager
import undetected_chromedriver as uc
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io


class SeleniumParser(ParserInterface):
    """
    Selenium-based web scraping parser
    Import'lar lazy loading ile yapılır (app.selenium modül çakışması önlemi)
    """
    
    def __init__(self):
        # Parent constructor
        super().__init__()
        
        # Selenium modüllerini lazy import et
        self._load_selenium()
    
    def _load_selenium(self):
        """Selenium modüllerini yükle"""
        try:
            import selenium.webdriver as wd
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            self.wd = wd
            self.Options = Options
            self.Service = Service
            self.By = By
            self.WebDriverWait = WebDriverWait
            self.EC = EC
            self.TimeoutException = TimeoutException
            self.NoSuchElementException = NoSuchElementException
            
            print("✅ Selenium modülleri yüklendi")
        except Exception as e:
            print(f"❌ Selenium import hatası: {e}")
            raise
    
    def get_parser_name(self) -> str:
        return 'selenium'

    def parse(self, url: str, company_id: int, application_id: int, server_id: int, job_data: dict = None) -> Dict[str, Any]:
        """
        Parse işlemi - Retry mekanizması ile
        Maksimum 3 deneme yapar
        """
        # Job data'yı instance'a kaydet (proxy için)
        self.job_data = job_data
        
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            driver = None
            try:
                if attempt > 1:
                    print(f"🔄 Retry #{attempt}/{max_retries}: {url}")
                    time.sleep(5)  # Retry öncesi 5 saniye bekle
                
                print(f"🌐 Selenium parsing başladı (Deneme {attempt}/{max_retries}): Company: {company_id}, URL: {url}")

                # Attribute'ları job_data'dan al
                if not job_data or 'attributes' not in job_data:
                    return self._error_result(url, company_id, application_id, server_id,
                                              "Job data'da attributes bulunamadı", job_data=job_data)
                
                raw_attributes = job_data.get('attributes', [])
                
                if not raw_attributes:
                    return self._error_result(url, company_id, application_id, server_id,
                                              "Attributes listesi boş", job_data=job_data)
                
                # Attribute'ları dönüştür
                attributes = self._transform_attributes(raw_attributes)
                
                print(f"📋 Attributes dönüştürüldü: {len(attributes)} attribute")

                # Selenium driver'ı başlat
                driver = self._create_driver()
                
                # URL'e git
                print(f"🔗 URL'e gidiliyor: {url}")
                driver.get(url)
                print(f"🔗 URL'e gidildi: {url}")
                
                # Sayfa yüklenene kadar bekle - Artırıldı: 10 → 20 saniye
                # Sayfa yükle
                print(f"⏳ Sayfa yüklenmesi bekleniyor...")
                try:
                    self.WebDriverWait(driver, 20).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    print(f"✅ Sayfa yüklendi (readyState: complete)")
                except Exception as e:
                    print(f"⚠️ Sayfa yükleme timeout ama devam ediliyor: {e}")
                
                # Cloudflare bypass
                self._handle_cloudflare_challenge(driver)
                
                # AJAX bekle - Artırıldı: 5 → 8 saniye (JavaScript yoğun siteler için)
                print(f"⏳ AJAX yüklenmesi bekleniyor (8 saniye)...")
                time.sleep(8)
                print(f"✅ AJAX bekleme tamamlandı")
                
                # JavaScript object'lerinin yüklenmesi için ek bekleme (Gürgençler için)
                # Meta attribute varsa daha fazla bekle (case-insensitive kontrol)
                has_meta_attributes = any(
                    str(attr.get('attributes_type', '')).lower() == 'meta' 
                    for attr in raw_attributes
                )
                
                print(f"🔍 DEBUG: Meta attribute kontrolü - has_meta_attributes: {has_meta_attributes}")
                print(f"🔍 DEBUG: Raw attributes count: {len(raw_attributes)}")
                for idx, attr in enumerate(raw_attributes):
                    print(f"🔍 DEBUG: Attribute #{idx+1} - type: '{attr.get('attributes_type')}' | name: '{attr.get('attributes_name')}' | value: '{attr.get('attributes_value')}'")
                
                if has_meta_attributes:
                    print(f"⏳ ✅ Meta attribute tespit edildi, JavaScript object'lerinin yüklenmesi bekleniyor (15 saniye)...")
                    try:
                        # insider_object yüklenene kadar bekle (max 15 saniye - Gürgençler için)
                        for i in range(30):  # 30 * 0.5 = 15 saniye
                            has_insider = driver.execute_script("""
                                return (window.insider_object && window.insider_object.product) ? true : false;
                            """)
                            if has_insider:
                                print(f"✅ insider_object yüklendi ({i * 0.5:.1f} saniye sonra)")
                                # Ek 2 saniye bekle (product data'nın tam yüklenmesi için)
                                time.sleep(2)
                                break
                            time.sleep(0.5)
                        else:
                            print(f"⚠️ insider_object yüklenmedi (15 saniye timeout) - HTML fallback kullanılacak")
                            # HTML fallback için ek bekleme
                            time.sleep(2)
                    except Exception as wait_e:
                        print(f"⚠️ JavaScript object bekleme hatası: {str(wait_e)[:100]}")
                        # Hata olsa da devam et
                else:
                    # Meta attribute yoksa kısa bekleme
                    try:
                        print(f"⏳ JavaScript object'lerinin yüklenmesi bekleniyor...")
                        for i in range(10):  # 10 * 0.5 = 5 saniye
                            has_insider = driver.execute_script("""
                                return (window.insider_object && window.insider_object.product) ? true : false;
                            """)
                            if has_insider:
                                print(f"✅ insider_object yüklendi ({i * 0.5:.1f} saniye sonra)")
                                break
                            time.sleep(0.5)
                    except Exception as wait_e:
                        print(f"⚠️ JavaScript object bekleme hatası: {str(wait_e)[:100]}")
                
                # 🔍 Gürgençler için özel: JavaScript'ten fiyatı al
                try:
                    js_price = driver.execute_script("""
                        // 1. insider_object'ten dene
                        if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
                            return window.insider_object.product.unit_sale_price;
                        }
                        // 2. dataLayer'dan dene
                        if (window.dataLayer) {
                            for (var i = 0; i < window.dataLayer.length; i++) {
                                if (window.dataLayer[i].product && window.dataLayer[i].product.price) {
                                    return window.dataLayer[i].product.price;
                                }
                            }
                        }
                        // 3. Meta tag'den dene
                        var metaPrice = document.querySelector('meta[property=\"product:price:amount\"]');
                        if (metaPrice) {
                            return metaPrice.getAttribute('content');
                        }
                        return null;
                    """)
                    if js_price:
                        print(f"💰 JavaScript'ten fiyat alındı: {js_price}")
                except Exception as js_e:
                    print(f"⚠️ JavaScript fiyat alma hatası: {str(js_e)[:100]}")
                
                # Attribute'ları parse et
                results = {}  # Initialize results variable
                try:
                    results = self._extract_attributes(driver, attributes)
                    print(f"📊 Parse sonuçları: {results}")
                    
                    # 📸 Screenshot al (eğer flag true ise)
                    screenshot_path = None
                    if job_data.get('screenshot', False):
                        try:
                            screenshot_path = self._take_screenshot(driver, job_data)
                            print(f"📸 Screenshot alındı: {screenshot_path}")
                        except Exception as screenshot_error:
                            print(f"⚠️ Screenshot hatası (devam ediyor): {screenshot_error}")

                    # Başarılı sonuç döndür
                    success_result = self._success_result(
                        url, company_id, application_id, server_id,
                        results, 200, job_data
                    )
                    
                except Exception as attr_error:
                    # Attribute parsing hatası - HTTP 500 değil, detaylı hata mesajı
                    print(f"❌ Attribute parsing hatası: {attr_error}")
                    
                    # Tüm attribute'ları başarısız olarak işaretle
                    failed_attributes = list(attributes.keys())
                    error_message = f"Attribute'lar parse edilemedi: {', '.join(failed_attributes)} ({len(failed_attributes)}/{len(attributes)})"
                    
                    return self._error_result(
                        url, company_id, application_id, server_id,
                        error_message, 200, job_data  # HTTP 200 - site erişilebilir
                    )
                
                # Screenshot path'i ekle
                if screenshot_path:
                    success_result['screenshot_path'] = screenshot_path
                
                # Driver'ı kapat
                if driver:
                    try:
                        driver.quit()
                        print(f"🔚 Driver kapatıldı")
                    except:
                        pass
                
                # Başarılı - retry loop'undan çık
                return success_result

            except self.TimeoutException as e:
                last_error = f"Timeout: {str(e)}"
                print(f"⏰ Selenium timeout (Deneme {attempt}/{max_retries}): {e}")
                
                # Son denemeyse hata döndür
                if attempt == max_retries:
                    return self._error_result(url, company_id, application_id, server_id,
                                              last_error, 408, job_data)
                
            except Exception as e:
                last_error = str(e)
                print(f"❌ Selenium hatası (Deneme {attempt}/{max_retries}): {e}")
                import traceback
                traceback.print_exc()
                
                # Son denemeyse hata döndür - hata türüne göre HTTP kodu belirle
                if attempt == max_retries:
                    http_code = self._determine_http_code_from_error(e)
                    return self._error_result(url, company_id, application_id, server_id,
                                              last_error, http_code, job_data)
                
            finally:
                if driver:
                    try:
                        driver.quit()
                        print(f"🔚 Driver kapatıldı")
                    except:
                        pass
        
        # Tüm denemeler başarısız (buraya hiç gelmemeli ama güvenlik için)
        return self._error_result(url, company_id, application_id, server_id,
                                  f"Tüm denemeler başarısız: {last_error}", 500, job_data)

    def _create_driver(self):
        """
        Undetected Chrome driver oluştur (Anti-bot bypass için)
        
        undetected-chromedriver kullanarak Cloudflare, DataDome ve diğer
        bot detection sistemlerini bypass eder.
        """
        try:
            # Undetected Chrome Options
            options = uc.ChromeOptions()
            
            # Headless mod (v3.5.0+ versiyonlarında daha iyi)
            options.add_argument("--headless=new")  # Yeni headless mod
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")
            
            # Anti-detection ayarları
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            options.add_argument(f"user-agent={get_random_user_agent()}")
            
            # Proxy ayarları - job_data'dan dinamik proxy
            proxy_manager = get_proxy_manager()
            proxy_url = proxy_manager.get_selenium_proxy(job_data=self.job_data)
            
            if proxy_url:
                # Mask password for security
                proxy_display = proxy_url.split('@')[0][:20] + '***@' + proxy_url.split('@')[1] if '@' in proxy_url else proxy_url[:30] + '***'
                print(f"🔒 Undetected Selenium proxy kullanılıyor: {proxy_display}")
                print(f"🔒 Proxy type: {self.job_data.get('proxy_type') if self.job_data else 'N/A'}")
                print(f"🔒 use_proxy flag: {self.job_data.get('use_proxy') if self.job_data else 'N/A'}")
                options.add_argument(f'--proxy-server=http://{proxy_url}')
            else:
                print(f"⚠️ PROXY YOK! Site direkt erişiliyor (bot detection riski yüksek)")
                print(f"   use_proxy: {self.job_data.get('use_proxy') if self.job_data else 'N/A'}")
                print(f"   proxy_type: {self.job_data.get('proxy_type') if self.job_data else 'N/A'}")
            
            # Undetected ChromeDriver oluştur
            print(f"🛡️ Undetected ChromeDriver başlatılıyor...")
            driver = uc.Chrome(
                options=options,
                driver_executable_path='/usr/bin/chromedriver',
                browser_executable_path='/usr/bin/chromium',
                version_main=None,  # Otomatik version detection
                use_subprocess=True,
                headless=True  # Headless mode aktif
            )
            
            # Page load timeout - Artırıldı: 30 → 60 saniye (yavaş siteler için)
            driver.set_page_load_timeout(60)
            
            # WebDriver özelliklerini gizle
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": get_random_user_agent()
            })
            
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ Undetected ChromeDriver hazır")
            return driver
            
        except Exception as e:
            print(f"❌ Undetected driver oluşturma hatası: {e}")
            print(f"⚠️ Fallback: Normal Selenium driver deneniyor...")
            
            # Fallback: Normal Selenium driver
            return self._create_normal_driver()

    def _create_normal_driver(self):
        """
        Normal Selenium driver oluştur (fallback için)
        """
        chrome_options = self.Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
        chrome_options.binary_location = '/usr/bin/chromium'
        
        # Proxy ayarları - job_data'dan dinamik proxy
        proxy_manager = get_proxy_manager()
        proxy_url = proxy_manager.get_selenium_proxy(job_data=self.job_data)
        
        if proxy_url:
            proxy_display = proxy_url.split('@')[0][:20] + '***@' + proxy_url.split('@')[1] if '@' in proxy_url else proxy_url[:30] + '***'
            print(f"🔒 Normal Selenium proxy kullanılıyor: {proxy_display}")
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
        else:
            print(f"⚠️ PROXY YOK (fallback driver)!")
        
        service = self.Service(
            executable_path='/usr/bin/chromedriver',
            log_output='/dev/null'
        )
        
        driver = self.wd.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver

    def _transform_attributes(self, raw_attributes: list) -> Dict[str, Any]:
        """
        Yeni attribute yapısını parser'ın beklediği formata çevir
        """
        attributes = {}
        
        for attr in raw_attributes:
            attr_name = attr.get('attributes_name')
            attr_type = attr.get('attributes_type')
            attr_value = attr.get('attributes_value')
            
            # DEBUG kapalı - gereksiz log
            # print(f"🔍 DEBUG: {attr_name} | {attr_type} | {attr_value}")
            
            # 🆕 Meta/JSON tipindeyse özel işlem (case-insensitive)
            if str(attr_type).lower() == 'meta' and attr_value:
                print(f"✅ META attribute detected: {attr_name} = {attr_value}")
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'meta',
                    'meta_value': attr_value  # value alanındaki key'i kullan
                }
                continue
            
            if not attr_name or not attr_value:
                continue
            
            # Otomatik tespit
            detected_type = attr_type
            if attr_value.startswith('//') or attr_value.startswith('/'):
                detected_type = 'xpath'
            elif attr_value.startswith('#'):
                detected_type = 'id'
            
            # Attribute type'a göre selector type'ı belirle
            if detected_type == 'xpath':
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'xpath'
                }
            elif detected_type == 'id':
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'id'
                }
            else:  # class, css
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'css'
                }
        
        return attributes

    def _take_screenshot(self, driver, job_data: dict) -> str:
        """
        Selenium driver ile screenshot al ve kaydet
        
        Args:
            driver: Selenium WebDriver instance
            job_data: Job data (mpn, company_id, url vb.)
            
        Returns:
            Screenshot dosya yolu (relative path)
        """
        try:
            # Screenshot klasörü
            screenshot_dir = '/app/screenshots'
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Tarih bazlı klasör
            current_date = datetime.now().strftime('%d%m%Y')
            date_folder = os.path.join(screenshot_dir, current_date)
            os.makedirs(date_folder, exist_ok=True)
            
            # Screenshot al
            screenshot_bytes = driver.get_screenshot_as_png()
            
            # PIL ile görüntüyü aç
            image = Image.open(io.BytesIO(screenshot_bytes))
            draw = ImageDraw.Draw(image)
            
            # Timestamp ekle (kırmızı renkte, sol üst köşe)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            draw.text((60, 60), timestamp, font=font, fill='red')
            
            # Dosya adı oluştur
            mpn = job_data.get('npm', 'unknown')
            mpn_safe = mpn.replace("/", '-').replace("\\", '-').replace(" ", '_')
            file_name_timestamp = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000)}"
            filename = f"{mpn_safe}_{file_name_timestamp}.jpg"
            
            # Dosya yolu
            filepath = os.path.join(date_folder, filename)
            relative_path = f"{current_date}/{filename}"
            
            # JPEG olarak kaydet (optimize)
            image.convert('RGB').save(filepath, 'JPEG', quality=85, optimize=True)
            
            print(f"📸 Screenshot kaydedildi: {relative_path}")
            
            # Veritabanına kaydet
            self._save_screenshot_to_db(job_data, relative_path)
            
            return relative_path
            
        except Exception as e:
            print(f"❌ Screenshot alma hatası: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _save_screenshot_to_db(self, job_data: dict, screenshot_path: str):
        """
        Screenshot bilgisini veritabanına kaydet
        
        Args:
            job_data: Job data
            screenshot_path: Screenshot dosya yolu
        """
        try:
            import psycopg2
            
            connection = psycopg2.connect(
                host=os.getenv('SHARED_DB_HOST', '10.20.50.16'),
                database=os.getenv('SHARED_DB_NAME', 'ipricetest'),
                user=os.getenv('SHARED_DB_USER', 'ipricetestuser'),
                password=os.getenv('SHARED_DB_PASS', 'YeniSifre123!'),
                port=os.getenv('SHARED_DB_PORT', '5432')
            )
            
            cursor = connection.cursor()
            
            # Screenshots tablosuna kaydet
            query = """
                INSERT INTO screenshots (company_id, mpn, url, image_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            
            company_id = job_data.get('company_id')
            mpn = job_data.get('npm')
            url = job_data.get('url')
            
            cursor.execute(query, (company_id, mpn, url, screenshot_path))
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"📝 Screenshot DB'ye kaydedildi: {screenshot_path}")
            
        except Exception as e:
            print(f"⚠️ Screenshot DB kayıt hatası: {e}")
            # DB hatası screenshot alma işlemini engellemez
    
    def _extract_meta_json_value(self, driver, meta_key: str) -> Any:
        """Meta/JSON değer çıkar - Gürgençler ve diğer siteler için optimize edilmiş"""
        try:
            from app.helper.meta_extractor import extract_with_selenium
            
            # Meta extraction'ı çağır (otomatik olarak JavaScript ve HTML fallback kullanır)
            result = extract_with_selenium(driver, meta_key)
            
            # Eğer sonuç yoksa ve unit_sale_price ise, sayfa kaynağından tekrar dene
            if not result and meta_key == 'unit_sale_price':
                print(f"⚠️ Meta extraction başarısız, sayfa kaynağından regex ile tekrar deneniyor...")
                try:
                    # Sayfa kaynağını al ve regex ile ara
                    page_source = driver.page_source
                    
                    # Debug: unit_sale_price string'i var mı?
                    if 'unit_sale_price' in page_source.lower():
                        print(f"   🔍 'unit_sale_price' string'i sayfa kaynağında bulundu")
                        # Context göster
                        index = page_source.lower().find('unit_sale_price')
                        if index != -1:
                            start = max(0, index - 150)
                            end = min(len(page_source), index + 150)
                            context = page_source[start:end]
                            print(f"   📄 Context: ...{context}...")
                    
                    # unit_sale_price için daha spesifik pattern'ler dene
                    patterns = [
                        # Önce JSON structure içinde ara
                        r'insider_object["\']?\s*:\s*\{[^}]*?product["\']?\s*:\s*\{[^}]*?unit_sale_price["\']?\s*:\s*([0-9.]+)',
                        r'product["\']?\s*:\s*\{[^}]*?unit_sale_price["\']?\s*:\s*([0-9.]+)',
                        # Sonra genel pattern'ler
                        r'"unit_sale_price"\s*:\s*([0-9.]+)',
                        r"'unit_sale_price'\s*:\s*([0-9.]+)",
                        r'unit_sale_price["\']?\s*[:=]\s*([0-9.]+)',
                    ]
                    
                    for pattern in patterns:
                        import re
                        match = re.search(pattern, page_source, re.IGNORECASE | re.DOTALL)
                        if match:
                            found_value = match.group(1)
                            # Değeri doğrula
                            try:
                                num_value = float(found_value)
                                if 100 <= num_value <= 1000000:  # Makul fiyat aralığı
                                    print(f"✅ Regex ile doğrulanmış değer bulundu: {found_value}")
                                    return str(int(num_value))
                                else:
                                    print(f"⚠️ Regex ile değer bulundu ama aralık dışında: {found_value}")
                            except:
                                print(f"⚠️ Regex ile değer bulundu ama parse edilemedi: {found_value}")
                    
                    print(f"❌ Regex ile uygun değer bulunamadı")
                except Exception as regex_e:
                    print(f"⚠️ Regex extraction hatası: {str(regex_e)[:100]}")
            
            return result
            
        except Exception as e:
            print(f"❌ Meta hatası: {str(e)[:60]}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_attributes(self, driver, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Driver'dan attribute'ları çıkar
        """
        results = {}
        error_count = 0
        
        for attr_name, attr_data in attributes.items():
            selector = attr_data.get('selector', '')
            selector_type = attr_data.get('selector_type', 'css')
            meta_value = attr_data.get('meta_value', '')  # 🆕 Meta key
            
            # Meta/JSON tipi (case-insensitive kontrol)
            if selector_type.lower() == 'meta' and meta_value:
                print(f"🔍 Meta extraction başlıyor: {attr_name} -> {meta_value}")
                print(f"🔍 Current URL: {driver.current_url}")
                print(f"🔍 Page Title: {driver.title[:100]}")
                
                # Meta extraction'dan önce sayfanın hazır olduğundan emin ol
                try:
                    # Ek bekleme - JavaScript object'lerinin yüklenmesi için
                    print(f"⏳ Meta extraction için ek bekleme (5 saniye)...")
                    import time as time_module
                    time_module.sleep(5)
                    
                    # insider_object kontrolü
                    has_insider = driver.execute_script("""
                        return (window.insider_object && window.insider_object.product) ? true : false;
                    """)
                    print(f"🔍 insider_object durumu: {has_insider}")
                    
                    if has_insider:
                        # Product keys'leri göster
                        product_keys = driver.execute_script("""
                            if (window.insider_object && window.insider_object.product) {
                                return Object.keys(window.insider_object.product).join(', ');
                            }
                            return 'N/A';
                        """)
                        print(f"🔍 Product keys: {product_keys}")
                        
                        # Direkt olarak unit_sale_price'ı dene
                        if meta_value == 'unit_sale_price':
                            direct_value = driver.execute_script("""
                                if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
                                    return window.insider_object.product.unit_sale_price;
                                }
                                return null;
                            """)
                            print(f"🔍 Direkt unit_sale_price değeri: {direct_value}")
                    else:
                        print(f"⚠️ insider_object bulunamadı! Sayfa tam yüklenmemiş olabilir.")
                        # Ekstra 5 saniye daha bekle ve tekrar dene
                        print(f"⏳ İkinci deneme için 5 saniye daha bekleniyor...")
                        time_module.sleep(5)
                        has_insider_retry = driver.execute_script("""
                            return (window.insider_object && window.insider_object.product) ? true : false;
                        """)
                        print(f"🔍 insider_object durumu (2. deneme): {has_insider_retry}")
                        
                except Exception as debug_e:
                    print(f"⚠️ Debug kontrolü hatası: {str(debug_e)[:100]}")
                
                meta_result = self._extract_meta_json_value(driver, meta_value)
                
                if meta_result:
                    results[attr_name] = str(meta_result)
                    print(f"✅ {attr_name}: {meta_result}")
                else:
                    print(f"❌ {attr_name} meta bulunamadı: {meta_value}")
                    results[attr_name] = None
                    error_count += 1
                
                continue
            
            if not selector:
                results[attr_name] = None
                error_count += 1
                continue
            
            try:
                # 🔍 Explicit Wait: Elementi maksimum 10 saniye bekle
                from selenium.webdriver.support import expected_conditions as EC
                
                # Log azaltıldı
                pass
                
                try:
                    # Element bekleme timeout'u artırıldı: 10 → 20 saniye
                    if selector_type == 'xpath':
                        element = self.WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((self.By.XPATH, selector))
                        )
                    elif selector_type == 'id':
                        # ID için # işaretini kaldır
                        selector_clean = selector.replace('#', '')
                        element = self.WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((self.By.ID, selector_clean))
                        )
                    else:  # css
                        element = self.WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((self.By.CSS_SELECTOR, selector))
                        )
                    
                    # Element bulundu
                    pass
                except Exception as wait_error:
                    # Timeout olursa JavaScript'ten fiyatı almayı dene (özellikle Gürgençler için)
                    error_type = type(wait_error).__name__
                    print(f"  ⚠️ Explicit wait hatası ({error_type}): {str(wait_error)[:150]}")
                    print(f"  🔍 Selector: {selector} (type: {selector_type})")
                    print(f"  📄 Current URL: {driver.current_url}")
                    print(f"  📝 Page Title: {driver.title[:100]}")
                    
                    # 🤖 JavaScript'ten fiyat almayı dene (price attribute'u için)
                    if attr_name.lower() == 'price':
                        print(f"  💰 JavaScript'ten fiyat alınmaya çalışılıyor...")
                        
                        # JavaScript object'lerinin yüklenmesi için 2 saniye daha bekle
                        import time
                        time.sleep(2)
                        
                        try:
                            js_price = driver.execute_script("""
                                // 1. Meta tag'den dene (en garantili)
                                var metaPrice = document.querySelector('meta[property="product:price:amount"]');
                                if (metaPrice) {
                                    var price = metaPrice.getAttribute('content');
                                    console.log('Meta tag price:', price);
                                    return price;
                                }
                                
                                // 2. insider_object'ten dene
                                if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
                                    console.log('insider_object price:', window.insider_object.product.unit_sale_price);
                                    return window.insider_object.product.unit_sale_price;
                                }
                                
                                // 3. dataLayer'dan dene
                                if (window.dataLayer) {
                                    for (var i = 0; i < window.dataLayer.length; i++) {
                                        if (window.dataLayer[i].product && window.dataLayer[i].product.price) {
                                            console.log('dataLayer price:', window.dataLayer[i].product.price);
                                            return window.dataLayer[i].product.price;
                                        }
                                    }
                                }
                                
                                console.log('Hiçbir kaynaktan fiyat bulunamadı');
                                return null;
                            """)
                            
                            print(f"  🔍 JavaScript'ten dönen değer: {js_price} (type: {type(js_price)})")
                            
                            if js_price:
                                print(f"  ✅ JavaScript'ten fiyat alındı: {js_price}")
                                # Fiyatı formatla: 45999 -> "45.999,00 TL"
                                js_price_float = float(js_price)
                                formatted_price = f"{js_price_float:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                results[attr_name] = formatted_price
                                print(f"  💰 Formatlanmış fiyat: {formatted_price}")
                                continue
                            else:
                                print(f"  ⚠️ JavaScript'ten fiyat alınamadı (null veya boş döndü)")
                        except Exception as js_e:
                            print(f"  ⚠️ JavaScript fiyat alma hatası: {str(js_e)[:100]}")
                    
                    print(f"  🔍 Sayfadaki TÜM .price elementlerini arıyorum...")
                    
                    try:
                        all_price_elements = driver.find_elements(self.By.CSS_SELECTOR, '.price')
                        print(f"  📊 Bulunan .price element sayısı: {len(all_price_elements)}")
                        
                        # Alternatif selector'ları dene
                        alt_selectors = [
                            'span[class*=\"price\"]',
                            'div[class*=\"price\"]', 
                            '.product-price',
                            '.amount',
                            'span',  # TÜM span'ları al
                            'div'    # TÜM div'leri al
                        ]
                        
                        for alt_sel in alt_selectors:
                            try:
                                alt_elements = driver.find_elements(self.By.CSS_SELECTOR, alt_sel)
                                if alt_sel in ['span', 'div']:
                                    # Sadece TL içerenleri göster
                                    tl_elements = [elem for elem in alt_elements if 'TL' in elem.text or '₺' in elem.text or ',' in elem.text]
                                    if tl_elements:
                                        print(f"  ✅ {alt_sel} elementlerinde TL bulundu: {len(tl_elements)} element")
                                        for elem in tl_elements[:5]:
                                            elem_class = elem.get_attribute('class') or 'no-class'
                                            print(f"     class=\"{elem_class}\" text=\"{elem.text[:50]}\"")
                                else:
                                    if alt_elements:
                                        print(f"  ✅ Alternatif selector bulundu: {alt_sel} ({len(alt_elements)} element)")
                                        for elem in alt_elements[:3]:
                                            print(f"     Text: \"{elem.text[:50]}\"")
                            except Exception as alt_e:
                                print(f"  ⚠️ {alt_sel} hatası: {str(alt_e)[:50]}")
                    except Exception as e:
                        print(f"  ❌ Element arama hatası: {str(e)[:100]}")
                    
                    raise wait_error
                
                # Text'i al
                value = element.text.strip() if element.text else None
                
                # Eğer text boşsa, value attribute'unu dene
                if not value:
                    value = element.get_attribute('value')
                
                # Hala boşsa, innerHTML'i dene
                if not value:
                    value = element.get_attribute('innerHTML')
                
                # Eğer hala boşsa ve price attribute'u ise JavaScript'ten dene
                if not value and attr_name.lower() == 'price':
                    print(f"  ⚠️ {attr_name}: Element bulundu ama değer boş, JavaScript fallback deneniyor...")
                    try:
                        import time
                        time.sleep(2)  # JavaScript yüklenmesi için bekle
                        
                        js_price = driver.execute_script("""
                            // 1. Meta tag'den dene
                            var metaPrice = document.querySelector('meta[property="product:price:amount"]');
                            if (metaPrice) {
                                return metaPrice.getAttribute('content');
                            }
                            
                            // 2. insider_object'ten dene
                            if (window.insider_object && window.insider_object.product && window.insider_object.product.unit_sale_price) {
                                return window.insider_object.product.unit_sale_price;
                            }
                            
                            // 3. dataLayer'dan dene
                            if (window.dataLayer) {
                                for (var i = 0; i < window.dataLayer.length; i++) {
                                    if (window.dataLayer[i].product && window.dataLayer[i].product.price) {
                                        return window.dataLayer[i].product.price;
                                    }
                                }
                            }
                            
                            return null;
                        """)
                        
                        if js_price:
                            print(f"  ✅ JavaScript'ten fiyat alındı: {js_price}")
                            try:
                                js_price_float = float(js_price)
                                formatted_price = f"{js_price_float:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
                                value = formatted_price
                            except:
                                value = str(js_price)
                    except Exception as js_e:
                        print(f"  ⚠️ JavaScript fallback hatası: {str(js_e)[:100]}")
                
                results[attr_name] = value
                
                if value:
                    print(f"  ✓ {attr_name}: {value}")
                else:
                    print(f"  ⚠️ {attr_name}: Boş değer (selector: {selector})")
                    error_count += 1
                
            except self.NoSuchElementException:
                print(f"  ✗ {attr_name}: Element bulunamadı (selector: {selector})")
                results[attr_name] = None
                error_count += 1
            except Exception as e:
                error_msg = str(e)
                # Sadece ilk 100 karakteri göster
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                print(f"  ⚠️ {attr_name}: Hata - {error_msg}")
                results[attr_name] = None
                error_count += 1
        
        # Eğer tüm attribute'lar başarısız olduysa, exception fırlat
        if error_count == len(attributes) and error_count > 0:
            # Detaylı hata mesajı oluştur
            failed_details = []
            for attr_name, attr_data in attributes.items():
                result_value = results.get(attr_name)
                selector = attr_data.get('selector', 'N/A')
                selector_type = attr_data.get('selector_type', 'N/A')
                
                if result_value is None:
                    failed_details.append(f"{attr_name} (selector: {selector}, type: {selector_type}) -> bulunamadı")
                elif result_value == '':
                    failed_details.append(f"{attr_name} (selector: {selector}, type: {selector_type}) -> boş değer")
            
            error_details = " | ".join(failed_details)
            raise Exception(f"Tüm attribute'lar parse edilemedi ({error_count}/{len(attributes)}): {error_details}")
        
        return results
    
    def _determine_http_code_from_error(self, error: Exception) -> int:
        """Hata türüne göre uygun HTTP status kodu döndür"""
        error_str = str(error).lower()
        
        # Connection hataları
        if any(keyword in error_str for keyword in ['connection refused', 'connection reset', 'connection aborted']):
            return 503  # Service Unavailable
        
        # DNS hataları
        if any(keyword in error_str for keyword in ['dns', 'name resolution', 'no such host']):
            return 503  # Service Unavailable
        
        # Timeout hataları (zaten ayrı handle ediliyor ama güvenlik için)
        if any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return 408  # Request Timeout
        
        # SSL/TLS hataları
        if any(keyword in error_str for keyword in ['ssl', 'certificate', 'tls']):
            return 503  # Service Unavailable
        
        # Proxy hataları
        if any(keyword in error_str for keyword in ['proxy', 'tunnel']):
            return 503  # Service Unavailable
        
        # Diğer network hataları
        if any(keyword in error_str for keyword in ['network', 'unreachable', 'no route']):
            return 503  # Service Unavailable
        
        # Varsayılan olarak 500 (Internal Server Error)
        return 500
    
    def _handle_cloudflare_challenge(self, driver):
        """
        🔒 Cloudflare Challenge Handler
        Cloudflare bot korumasını bypass eder
        """
        try:
            # Cloudflare challenge sayfası kontrolü
            page_title = driver.title.lower()
            page_source = driver.page_source.lower()
            
            # Cloudflare challenge tespiti
            cloudflare_indicators = [
                'cloudflare',
                'challenge',
                'verifying you are human',
                'gerçek kişi olduğunuzu doğrulayın',
                'insan olduğunuzu doğrulayın',
                'challenges.cloudflare.com'
            ]
            
            is_cloudflare_challenge = any(indicator in page_source for indicator in cloudflare_indicators)
            
            if is_cloudflare_challenge:
                print(f"🔒 Cloudflare Challenge tespit edildi!")
                
                # 2 saniye bekle (sayfa tam yüklensin)
                time.sleep(2)
                
                # Checkbox selector'ları (birden fazla dene)
                checkbox_selectors = [
                    'input[type="checkbox"]',  # CSS selector
                    '//input[@type="checkbox"]',  # XPath
                    '//*[@id="uMtSJ0"]/div/label/input',  # Verilen XPath
                    'label input[type="checkbox"]',  # Label içindeki checkbox
                    '.cf-challenge-running input[type="checkbox"]',  # Cloudflare class
                    'input[type="checkbox"]:not([disabled])',  # Aktif checkbox
                    'input[type="checkbox"][name="cf-turnstile-response"]',  # Turnstile checkbox
                    '.cf-turnstile input[type="checkbox"]',  # Turnstile container
                    'iframe[src*="challenges.cloudflare.com"]',  # Cloudflare iframe
                    'iframe[src*="turnstile"]'  # Turnstile iframe
                ]
                
                checkbox_found = False
                
                for selector in checkbox_selectors:
                    try:
                        if selector.startswith('//'):
                            # XPath selector
                            element = driver.find_element(self.By.XPATH, selector)
                        else:
                            # CSS selector
                            element = driver.find_element(self.By.CSS_SELECTOR, selector)
                        
                        if element and element.is_displayed() and element.is_enabled():
                            print(f"✅ Checkbox bulundu: {selector}")
                            
                            # Checkbox'a tıkla
                            driver.execute_script("arguments[0].click();", element)
                            print(f"🔒 Cloudflare checkbox tıklandı!")
                            
                            checkbox_found = True
                            break
                            
                    except Exception as e:
                        continue
                
                if not checkbox_found:
                    print(f"⚠️ Cloudflare checkbox bulunamadı, iframe ve JavaScript ile dene...")
                    
                    # Önce iframe'leri kontrol et
                    try:
                        iframes = driver.find_elements(self.By.TAG_NAME, "iframe")
                        for iframe in iframes:
                            try:
                                if "challenges.cloudflare.com" in iframe.get_attribute("src") or "turnstile" in iframe.get_attribute("src"):
                                    print(f"🔒 Cloudflare iframe bulundu, switch yapılıyor...")
                                    driver.switch_to.frame(iframe)
                                    
                                    # Iframe içinde checkbox ara
                                    iframe_checkboxes = driver.find_elements(self.By.CSS_SELECTOR, "input[type='checkbox']")
                                    for cb in iframe_checkboxes:
                                        if cb.is_displayed() and cb.is_enabled():
                                            cb.click()
                                            print(f"🔒 Iframe içinde checkbox tıklandı!")
                                            checkbox_found = True
                                            break
                                    
                                    driver.switch_to.default_content()
                                    if checkbox_found:
                                        break
                            except:
                                continue
                    except:
                        pass
                    
                    if not checkbox_found:
                        # JavaScript ile checkbox bul ve tıkla
                        js_script = """
                        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        for (var i = 0; i < checkboxes.length; i++) {
                            if (checkboxes[i].offsetParent !== null) { // visible check
                                checkboxes[i].click();
                                console.log('Checkbox clicked via JS');
                                break;
                            }
                        }
                        """
                        driver.execute_script(js_script)
                        print(f"🔒 JavaScript ile checkbox tıklandı!")
                
                # Challenge tamamlanmasını bekle (optimize edildi: 10 → 15 saniye)
                print(f"⏳ Cloudflare challenge tamamlanması bekleniyor...")
                
                for attempt in range(30):  # 30 deneme = 15 saniye
                    time.sleep(0.5)
                    
                    # Sayfa değişti mi kontrol et
                    current_url = driver.current_url
                    current_title = driver.title.lower()
                    
                    # Challenge tamamlandı mı?
                    if not any(indicator in driver.page_source.lower() for indicator in cloudflare_indicators):
                        print(f"✅ Cloudflare challenge başarıyla tamamlandı!")
                        return
                    
                    # URL değişti mi?
                    if 'challenge' not in current_url.lower():
                        print(f"✅ Cloudflare challenge tamamlandı, yönlendirildi!")
                        return
                
                print(f"⚠️ Cloudflare challenge timeout (15 saniye)")
                
            else:
                print(f"✅ Cloudflare challenge tespit edilmedi")
                
        except Exception as e:
            print(f"⚠️ Cloudflare challenge handler hatası: {e}")
            # Hata olsa da devam et
