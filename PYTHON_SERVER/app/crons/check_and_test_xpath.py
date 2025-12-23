import os
import sys
import time
import scrapy

import dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # root dizine çık
from app.helper.standardize_price import standardize_price

dotenv.load_dotenv('../.env')
server_path = os.getenv('SERVER_PATH')


from scrapy.crawler import CrawlerProcess


class MediaMarktSpider(scrapy.Spider):
    name = 'mediamarkt'
    start_urls = [
        'https://www.sneaksup.com/settlement-backpack-11407-00007-os-001'
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 5,  # 5 saniye bekle
        'COOKIES_ENABLED': True,
        'DOWNLOAD_TIMEOUT': 180,
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'HTTPCACHE_ENABLED': False,
        'HTTPCACHE_IGNORE_HTTP_CODES': [503, 504, 505, 500, 400, 404, 403],
        # Proxy ayarları
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
        },
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):

        price = response.css('detail-price font-weight-bold font-size-lg').get()


        #price2 = response.css('')

        #stok_var_elementi = response.css('a#GelinceHaberVer[style*="display: none"]')

        #price = response.css('.text-4xl text-black font-bold -mt-1::text').get()

        #print(stock_quantity)

        print(standardize_price(price))


process = CrawlerProcess()
process.crawl(MediaMarktSpider)
process.start()