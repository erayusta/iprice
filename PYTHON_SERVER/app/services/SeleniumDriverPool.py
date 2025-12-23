# app/services/SeleniumDriverPool.py
from queue import Queue
from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging


class SeleniumDriverPool:
    def __init__(self, pool_size=4):
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
        self._initialize_drivers(pool_size)

    def _create_driver(self):
        """Tek bir driver instance'ı oluştur"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.binary_location = '/usr/bin/chromium'

        # Performans için ekstra ayarlar - resimler yüklenmesin
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,  # Resimleri yükleme
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)

        service = Service(executable_path='/usr/bin/chromedriver')

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(20)

        return driver

    def _initialize_drivers(self, pool_size):
        """Pool'u başlat"""
        for i in range(pool_size):
            try:
                driver = self._create_driver()
                self.pool.put(driver)
                self.logger.info(f"Driver {i + 1}/{pool_size} oluşturuldu")
            except Exception as e:
                self.logger.error(f"Driver oluşturulamadı: {e}")

    def get_driver(self):
        """Pool'dan bir driver al"""
        return self.pool.get()

    def return_driver(self, driver):
        """Driver'ı pool'a geri ver"""
        try:
            # Driver hala çalışıyor mu kontrol et
            driver.title  # Basit bir kontrol
            self.pool.put(driver)
        except:
            # Driver bozuksa yenisini oluştur
            self.logger.warning("Driver bozuk, yenisi oluşturuluyor")
            try:
                driver.quit()
            except:
                pass
            new_driver = self._create_driver()
            self.pool.put(new_driver)

    def close_all(self):
        """Tüm driver'ları kapat"""
        while not self.pool.empty():
            try:
                driver = self.pool.get_nowait()
                driver.quit()
            except:
                pass
        self.logger.info("Tüm driver'lar kapatıldı")