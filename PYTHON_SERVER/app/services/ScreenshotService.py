# app/services/ScreenshotService.py
import os
import io
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import threading

from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.services.SeleniumDriverPool import SeleniumDriverPool

logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

DOCKER_SCREENSHOT_PATH = '/app/screenshots'
os.makedirs(DOCKER_SCREENSHOT_PATH, exist_ok=True)


class ScreenshotService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton pattern - tek instance kullan
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, screenshot_repository: ScreenshotRepository):
        if not hasattr(self, 'initialized'):
            self.screenshot_repository = screenshot_repository
            self.driver_pool = SeleniumDriverPool(pool_size=4)
            self.font_cache = None
            self._load_font()
            self.initialized = True
            self.logger = logging.getLogger(__name__)

    def _load_font(self):
        """Font'u bir kere yükle ve cache'le"""
        try:
            self.font_cache = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except IOError:
            try:
                self.font_cache = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                                                     36)
            except IOError:
                self.font_cache = ImageFont.load_default()

    def create_screenshot(self, product, path):
        return self.screenshot_repository.create_screenshot(product, path, company_id=18)

    def capture_screenshot(self, url, mpn, output_folder=DOCKER_SCREENSHOT_PATH):
        """Optimize edilmiş screenshot alma"""
        driver = None
        try:
            # Date-based folder
            current_date = datetime.now().strftime('%d%m%Y')
            date_folder = os.path.join(output_folder, current_date)
            os.makedirs(date_folder, exist_ok=True)

            # Driver'ı pool'dan al
            driver = self.driver_pool.get_driver()

            # Sayfayı yükle
            driver.get(url)

            # Sayfanın yüklenmesini bekle
            try:
                # Fiyat elementinin yüklenmesini bekle (max 10 saniye)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "woocommerce-Price-amount"))
                )
            except:
                # Element bulunamazsa bile devam et
                pass

            # JavaScript'in yüklenmesi için kısa bekleme
            driver.execute_script("return document.readyState") == "complete"

            # Screenshot al
            screenshot = driver.get_screenshot_as_png()

            # Görüntüyü işle
            image = Image.open(io.BytesIO(screenshot))
            draw = ImageDraw.Draw(image)

            # Timestamp ekle
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            draw.text((60, 60), timestamp, font=self.font_cache, fill='red')

            # Dosya adını oluştur
            file_name_timestamp = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000)}"
            mpn_safe = mpn.replace("/", '-').replace("\\", '-').replace(" ", '_')
            filename = f"{mpn_safe}_{file_name_timestamp}.jpg"
            relative_path = f"{current_date}/{filename}"
            filepath = os.path.join(date_folder, filename)

            # Kaydet (optimize edilmiş JPEG)
            image.save(filepath, 'JPEG', quality=85, optimize=True)

            if os.path.exists(filepath):
                return relative_path
            else:
                self.logger.error(f"File was not created at {filepath}")
                return None

        except Exception as e:
            self.logger.error(f"Screenshot error for {url}: {str(e)}")
            return None
        finally:
            if driver:
                # Driver'ı pool'a geri ver
                self.driver_pool.return_driver(driver)

    def close_driver_pool(self):
        """Spider kapanırken çağrılacak"""
        if hasattr(self, 'driver_pool'):
            self.driver_pool.close_all()