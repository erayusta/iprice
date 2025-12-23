from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


def get_product_links():
    print("Chrome için opsiyonlar ayarlanıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
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

    # Belirtilen IP ve port üzerinden istek atmak için proxy ayarı
    chrome_options.add_argument(f'--proxy-server=http://139.59.1.14:80')

    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/chromium'

    service = Service(
        executable_path='/usr/bin/chromedriver',
        log_output='chromedriver.log'
    )

    print("Chrome başlatılıyor...")
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Chrome başlatma hatası: {e}")
        return []

    try:
        url = 'https://www.trendyol.com/sr?q=MQKP3TU%2FA&qt=MQKP3TU%2FA&st=MQKP3TU%2FA&os=1'
        print(f"Sayfa yükleniyor: {url}")
        driver.get(url)

        print(f"Şu anki URL: {driver.current_url}")
        is_ready = driver.execute_script("return document.readyState")
        print(f"Sayfa durumu: {is_ready}")

        unique_links = set()

        print("\nÜrün container'ı aranıyor...")
        try:
            wait = WebDriverWait(driver, 15)
            container = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "prdct-cntnr-wrppr"))
            )

            # Ürün kartlarını bul
            product_cards = container.find_elements(By.CLASS_NAME, "p-card-wrppr")
            print(f"Bulunan ürün kartı sayısı: {len(product_cards)}")

            # Her karttan bir link al (tekrarları önle)
            for card in product_cards:
                try:
                    link = card.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute('href')
                    if href:
                        unique_links.add(href)
                except Exception as e:
                    print(f"Kart link hatası: {e}")
                    continue

        except Exception as e:
            print(f"Container bulma hatası: {e}")
            print("\nAlternatif yöntem deneniyor...")

            try:
                product_cards = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")

                for card in product_cards:
                    try:
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute('href')
                        if href:
                            unique_links.add(href)
                    except:
                        continue

            except Exception as e2:
                print(f"Alternatif yöntemde de hata oluştu: {e2}")
                print("\nSayfa kaynağından bir parça:")
                print(driver.page_source[:1000])

        print(f"\nBenzersiz link sayısı: {len(unique_links)}")
        for href in unique_links:
            print(f"Ürün URL: {href}")

    except Exception as e:
        print(f"Genel hata: {e}")
        return []

    finally:
        print("Tarayıcı kapatılıyor...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Tarayıcı kapatma hatası: {e}")

    # Link listesini bir dosyaya kaydet
    with open('product_urls.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique_links), f, ensure_ascii=False, indent=4)

    return list(unique_links)


# Özel HTTP proxy middleware
class CustomProxyMiddleware(HttpProxyMiddleware):
    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://139.59.1.14:80'


# Şimdi Scrapy spider'ını tanımlayalım
class TrendyolSpider(scrapy.Spider):
    name = 'trendyol'

    def __init__(self, urls=None, *args, **kwargs):
        super(TrendyolSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls or []
        if not self.start_urls and os.path.exists('product_urls.json'):
            with open('product_urls.json', 'r', encoding='utf-8') as f:
                self.start_urls = json.load(f)

        # Eğer başlangıç URL'leri yoksa uyarı ver
        if not self.start_urls:
            self.logger.error("Başlangıç URL'leri bulunamadı!")

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'proxy': 'http://139.59.1.14:80'}  # Her istek için proxy belirt
            )

    def parse(self, response):
        price = response.xpath(
            '/html/body/div[1]/div[6]/main/div/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[3]/div/div/span/text()').get()
        print(price)

        yield {
            'url': response.url,
            'price': price
        }


# Ana çalıştırma fonksiyonu
def run_scraper():
    # Önce Selenium ile ürün URL'lerini al
    product_urls = get_product_links()

    # Scrapy ayarlarını yapılandır
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,  # Trendyol'u aşırı yüklememek için
        'COOKIES_ENABLED': True,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'trendyol_products.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_LEVEL': 'INFO',
        # Proxy middleware'i etkinleştir
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
            '__main__.CustomProxyMiddleware': 750,
        },
        # Sabit proxy ayarı (alternatif yöntem)
        'HTTP_PROXY': 'http://139.59.1.14:80',
        'HTTPS_PROXY': 'http://139.59.1.14:80',
    })

    # Scrapy sürecini başlat
    process = CrawlerProcess(settings)
    process.crawl(TrendyolSpider, urls=product_urls)
    process.start()


if __name__ == "__main__":
    run_scraper()