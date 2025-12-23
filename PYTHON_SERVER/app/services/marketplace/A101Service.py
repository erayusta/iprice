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
from app.services.base import CrawlerServiceInterface
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ImageRepository import ImageRepository
from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.helper.standardize_price import standardize_price


class A101Service(CrawlerServiceInterface):

    use_selenium = True

    def __init__(
            self,
            product_repository: ProductRepository,
            image_repository: ImageRepository,
            screenshot_repository: ScreenshotRepository,
            db_session: Session,
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

        self.min_delay = min_delay
        self.max_delay = max_delay
        self.refresh_strategy = refresh_strategy.lower()
        self.refresh_after_requests = refresh_after_requests
        self.request_counter = 0

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