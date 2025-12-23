import logging
from scrapy import signals

class LogRetryMiddleware:
    def __init__(self):
        self.logger = None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        self.logger = logging.getLogger(__name__)

    def process_exception(self, request, exception, spider):
        # Retry öncesi exception yakalandığında
        proxy = request.meta.get('proxy', 'No proxy info')
        self.logger.debug(f"Request failed with exception: {exception} | URL: {request.url} | Proxy: {proxy}")
        return None  # Diğer middleware'lerin de çalışmasına izin ver

    def process_request(self, request, spider):
        # Her istek için
        if 'retry_times' in request.meta:
            proxy = request.meta.get('proxy', 'No proxy info')
            self.logger.debug(f"Retry #{request.meta['retry_times']} for URL: {request.url} | Proxy: {proxy}")
        return None