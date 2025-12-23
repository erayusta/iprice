import logging
import sys
from typing import Any

import requests
import scrapy

from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService


class CompanyParser(scrapy.Spider):
    name = 'company-parser-trigger'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/api_log')
        ]
    )
    logger = logging.getLogger(__name__)

    custom_settings = {
        'ROTATING_PROXY_LIST': [],
        'DOWNLOADER_MIDDLEWARES': {
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None
        },
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5
    }
    
    
    def __init__(
        self,
        product_service: ProductService,
        screenshot_service: ScreenshotService,
        company_id=None,
        company_name=None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.db_session = None
        self.product_service = product_service
        self.screenshot_service = screenshot_service
        self.company_id = company_id
        self.company_name = company_name
        #self.update_proxy_list()
        
    def update_proxy_list(self):
        try:
            response = requests.get('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')

            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.split('\n') if line.strip()]

                if proxies:
                    self.custom_settings['ROTATING_PROXY_LIST'] = proxies
                    self.logger.info(f"Başarıyla {len(self.custom_settings['ROTATING_PROXY_LIST'])} proxy eklendi")
                else:
                    self.logger.warning("Proxy listesi boş")
            else:
                self.logger.error(f"Github'dan proxy listesi çekilemedi. Status code: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Proxy listesi güncellenirken hata oluştu: {str(e)}")
            # Hata durumunda varsayılan proxy'leri kullan
            self.custom_settings['ROTATING_PROXY_LIST'] = [
                '103.152.112.162:80',
                '196.1.95.117:80',
                '213.52.102.30:80',
                '47.254.47.61:8080',
                '172.67.182.40:80'
            ]

    async def process_company_data(self, company_id: int, company_name: str):
        """
        Firma bazlı processing - Dinamik parsing method ile
        """
        try:
            self.logger.info(f"Processing company: {company_name} (ID: {company_id})")

            # Debug kontrolleri...
            if hasattr(self.product_service, 'get_company_parsing_info'):
                self.logger.info("get_company_parsing_info metodu var")
            else:
                self.logger.error("get_company_parsing_info metodu YOK!")
                return {"status": "error", "message": "get_company_parsing_info metodu bulunamadı"}

            self.logger.info(f"product_service type: {type(self.product_service)}")

            # Adım 1: Company parsing bilgilerini al
            self.logger.info("Calling get_company_parsing_info...")
            parsing_info = self.product_service.get_company_parsing_info(company_id)
            self.logger.info(f"parsing_info result: {parsing_info}")

            if parsing_info['status'] != 'success':
                return {
                    "company_id": company_id,
                    "company_name": company_name,
                    "status": "error",
                    "message": parsing_info['message']
                }

            # Adım 2: Firmaya ait ürünleri çek
            self.logger.info("Getting products...")
            products = self.product_service.get_products_with_urls_by_company_id(company_id)
            self.logger.info(f"Found {len(products) if products else 0} products")

            if not products:
                return {
                    "company_id": company_id,
                    "company_name": company_name,
                    "status": "no_products",
                    "message": "Bu firma için ürün bulunamadı",
                    "product_count": 0,
                    "parsing_method": parsing_info['parsing_method']
                }

            self.logger.info(f"Found {len(products)} products for company: {company_name}")
            self.logger.info(
                f"Parsing method: {parsing_info['parsing_method']} (Application: {parsing_info['application_name']})")

            # Adım 3: Parsing method'a göre işlem yap
            if parsing_info['parsing_method'].lower() == 'selenium':
                self.logger.info("🚀 Starting Selenium processing...")

                # Selenium service'ini import et ve başlat
                from app.services.SeleniumParsingServiceByCompany import SeleniumParsingServiceByCompany
                selenium_service = SeleniumParsingServiceByCompany(self.product_service, self.screenshot_service)

                # Selenium processing'i başlat
                result = await selenium_service.process_company_selenium(company_id, company_name)

                self.logger.info(f"✅ Selenium processing completed with status: {result.get('status')}")
                return result

            elif parsing_info['parsing_method'].lower() == 'scrapy':
                self.logger.info("🕷️ Starting Scrapy processing...")

                # Scrapy işlemi burada yapılacak (şimdilik placeholder)
                return {
                    "company_id": company_id,
                    "company_name": company_name,
                    "status": "scrapy_not_implemented",
                    "parsing_method": parsing_info['parsing_method'],
                    "product_count": len(products),
                    "message": "Scrapy implementation coming soon..."
                }

            else:
                return {
                    "company_id": company_id,
                    "company_name": company_name,
                    "status": "unknown_method",
                    "parsing_method": parsing_info['parsing_method'],
                    "message": f"Unknown parsing method: {parsing_info['parsing_method']}"
                }

        except Exception as e:
            self.logger.error(f"Error in process_company_data: {e}")
            self.logger.error(f"Error type: {type(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "company_id": company_id,
                "company_name": company_name,
                "status": "error",
                "error": str(e)
            }

    def start_requests(self):
        if hasattr(self, 'company_id') and self.company_id is not None:
            products = self.product_service.get_products_with_urls_by_company_id(self.company_id)

            requests = []

            for product in products:
                requests.append(
                    scrapy.Request(
                        url=product.url,
                        callback=self.parse,
                        errback=self.errback,
                        meta={"product_id": product.mpn}
                    )
                )

            return requests
        else:
            self.logger.error("company_id tanımlanmamış!")
            return []

    def parse(self, response):

        self.logger.info(f"Parsing response from: {response.url}")
        self.logger.info(f"Using proxy: {response.meta.get('proxy', 'No proxy info')}")

        is_redirect = len(response.request.meta.get('redirect_urls', [])) > 0
        product_mpn = response.meta['mpn']
        link = response.url
        company_name = self.company_name

        attributes = self.product_service.get_attributes_for_company(company_name)
        attribute_values = []

        if attributes:
            screenshot = self.screenshot_service.capture_screenshot(link, product_mpn)
            self.screenshot_service.create_screenshot_price_parser(product_mpn, screenshot, link, attributes[0]['company_id'])

            if screenshot:
                print(f"Screenshot successfully saved to: {screenshot}")

        for item in attributes:
            if item['attribute_name'] == 'is_redirect':
                value = is_redirect
            else:
                value = response.xpath(f"{item['xpath']}").get() if item['selector_type'] == 'xpath' else response.css(
                    f"{item['xpath']}").get()

            attribute_data = {
                'company_id': item['company_id'],
                'mpn': product_mpn,
                'attribute_id': item['attribute_id'],
                'attribute_name': item['attribute_name'],
                'value': value
            }

            if item['attribute_name'] == 'is_stock':
                attribute_data['value'] = False if value is not None else value

            attribute_values.append(attribute_data)

        self.product_service.create_attribute_values(attribute_values)
        self.logger.info(f"Successfully processed {len(attribute_values)} attributes for MPN: {product_mpn}")

    def errback(self, failure):
        self.logger.error(f"Request failed for URL {failure.request.url}")
        self.logger.error(f"Error: {str(failure.value)}")
        return {'error': str(failure.value), 'url': failure.request.url}

        
    