import scrapy
import requests
from typing import Any


from app.services.CheckDifferenceService import CheckDifferenceService
from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService
from app.services.MarketPlaceService import MarketPlaceService


class MarketPlaceParser(scrapy.Spider):
    name = 'MarketPlaceParser'

    custom_settings = {
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5
    }

    '''
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
    '''

    def __init__(
            self,
            product_service: ProductService,
            screenshot_service: ScreenshotService,
            market_place_service: MarketPlaceService,
            check_difference_service: CheckDifferenceService,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.db_session = None
        self.product_service = product_service
        self.screenshot_service = screenshot_service
        self.market_place_service = market_place_service
        self.check_difference_service = check_difference_service
        #self.update_proxy_list()

        #self.logger.info(f"Current proxy list size: {len(self.custom_settings['ROTATING_PROXY_LIST'])}")
        #self.logger.info(f"Middleware settings: {self.custom_settings['DOWNLOADER_MIDDLEWARES']}")

    def update_proxy_list(self):
        try:
            response = requests.get('https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt')

            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.split('\n') if line.strip()]

                if proxies:
                    self.custom_settings['ROTATING_PROXY_LIST'] = proxies
                    self.logger.info(f"Başarıyla {len(proxies)} proxy eklendi")
                    self.logger.info(f"İlk 5 proxy: {proxies[:5]}")  # İlk 5 proxy'i log'a yaz
                else:
                    self.logger.warning("Proxy listesi boş")
            else:
                self.logger.error(f"Github'dan proxy listesi çekilemedi. Status code: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Proxy listesi güncellenirken hata oluştu: {str(e)}")
            default_proxies = [
                '190.52.100.248:999',
                '67.43.228.251:6575',
                '72.10.160.170:8097',
                '181.78.21.38:999',
                '176.105.220.74:3129'
            ]
            self.custom_settings['ROTATING_PROXY_LIST'] = default_proxies
            self.logger.info(f"Varsayılan {len(default_proxies)} proxy kullanılıyor")

    def start_requests(self):
        urls = self.market_place_service.get_product_links_and_titles()

        for url in urls:
            yield scrapy.Request(
                url=url['url'],
                callback=self.parse,
                errback=self.errback,
                dont_filter=True,
                meta={
                    'mpn': url['mpn'],
                    'company': url.company.name
                }
            )

    def parse(self, response):

        self.logger.info(f"Parsing response from: {response.url}")
        self.logger.info(f"Using proxy: {response.meta.get('proxy', 'No proxy info')}")

    def errback(self, failure):
        self.logger.error(f"Request failed for URL {failure.request.url}")
        self.logger.error(f"Error: {str(failure.value)}")
        return {'error': str(failure.value), 'url': failure.request.url}



