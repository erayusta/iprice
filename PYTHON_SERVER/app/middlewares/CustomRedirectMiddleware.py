import logging
from w3lib.url import safe_url_string
from six.moves.urllib.parse import urljoin
import scrapy


class CustomRedirectMiddleware:
    """HTTP proxyleri ile HTTPS yönlendirmelerini handle eden middleware"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        return middleware

    def process_request(self, request, spider):
        # HTTP isteklerini proaktif olarak HTTPS'e dönüştür
        if request.url.startswith('http://') and not request.url.startswith('http://localhost'):
            https_url = request.url.replace('http://', 'https://')
            self.logger.debug(f"Proaktif olarak HTTP→HTTPS dönüşümü: {request.url} → {https_url}")
            return request.replace(url=https_url)
        return None

    def process_response(self, request, response, spider):
        # 3xx yanıtı ve Location başlığı varsa yönlendirme
        if response.status in [301, 302, 303, 307, 308] and 'Location' in response.headers:
            location = safe_url_string(response.headers['Location'].decode('utf-8'))
            redirected_url = urljoin(request.url, location)

            # Yönlendirme loglaması
            self.logger.debug(f"Redirecting from {request.url} to {redirected_url}")

            # Yeni bir istek oluştur
            redirected = request.replace(url=redirected_url)

            # Meta bilgilerini koru
            for key in list(request.meta.keys()):
                if key != 'download_timeout':  # timeout değerini sıfırlamak için bu hariç tüm meta bilgilerini kopyala
                    redirected.meta[key] = request.meta[key]

            # Yönlendirme bilgilerini güncelle
            if 'redirect_urls' not in redirected.meta:
                redirected.meta['redirect_urls'] = []
            redirected.meta['redirect_urls'].append(request.url)

            # Yönlendirme sayacını artır
            redirected.meta['redirect_times'] = request.meta.get('redirect_times', 0) + 1

            # Timeout değerini uzat (bu özellikle HTTPS yönlendirmeleri için önemli)
            redirected.meta['download_timeout'] = 60  # Yönlendirme için daha uzun bir timeout

            # Max yönlendirme kontrolü
            if redirected.meta['redirect_times'] <= 5:  # Max 5 yönlendirme
                return redirected
            else:
                self.logger.warning(f"Max redirects reached for {request.url}")
                # Max yönlendirme sayısına ulaşıldığında son URL'ye gidip parse et
                redirected.meta['max_redirects_reached'] = True
                redirected.dont_filter = True
                return redirected

        # 403 Forbidden hataları için tekrar deneme
        if response.status == 403:
            # Kullanıcı ajanı değiştirerek yeniden dene
            self.logger.debug(f"403 Forbidden: {request.url} - Farklı user-agent ile yeniden deneniyor")

            # 403 retry sayacını kontrol et
            retry_403_count = request.meta.get('retry_403', 0)

            # Maksimum yeniden deneme kontrolü
            if retry_403_count < 2:  # 403 hatası için en fazla 2 kez tekrar dene
                # Kopya istek oluştur
                new_request = request.replace(dont_filter=True)

                # Farklı bir user-agent dene
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                ]

                import random
                new_request.headers['User-Agent'] = random.choice(user_agents)

                # Retry sayacını artır
                new_request.meta['retry_403'] = retry_403_count + 1

                return new_request

        return response