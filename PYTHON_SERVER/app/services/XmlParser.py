import time
from typing import Any
import scrapy
from scrapy.http import XmlResponse
from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService


class XmlParser(scrapy.Spider):
    name = 'xml-feed-parser'
    start_urls = ['https://www.pt.com.tr/wp-content/uploads/wpwoof-feed/xml/iprice.xml']

    # PERFORMANS AYARLARI - ÖNEMLİ!
    custom_settings = {
        'CONCURRENT_REQUESTS': 64,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'RETRY_ENABLED': False,
        'REDIRECT_ENABLED': False,
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0,
        'AUTOTHROTTLE_MAX_DELAY': 0.5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
    }

    def __init__(
            self,
            product_service: ProductService,
            screenshot_service: ScreenshotService,
            crawler_log_id=None,
            crawler_log_repo=None,
            **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.db_session = None
        self.product_service = product_service
        self.screenshot_service = screenshot_service
        self.crawler_log_id = crawler_log_id
        self.crawler_log_repo = crawler_log_repo

        # URL sayaçları
        self.processed_products_count = 0
        self.total_urls_visited = 0
        self.xml_urls_count = 0
        self.product_urls_count = 0

        # FIX 1: Web price batch initialize et!
        self.web_price_batch = []  # None değil, boş liste!
        self.batch_size = 50  # None değil, sayı!

    def parse(self, response: XmlResponse, **kwargs):
        ns = {
            'g': 'http://base.google.com/ns/1.0'
        }

        # XML URL sayacını arttır
        self.xml_urls_count += 1
        self.total_urls_visited += 1
        self.logger.info(f"🌐 XML URL işlendi: {response.url}")

        items = response.xpath('//item')
        total_items = len(items)
        self.logger.info(f"📦 XML'den {total_items} ürün bulundu")

        # SÜPER HIZLI TRUNCATE - History korunur
        self.logger.info("⚡ TRUNCATE ile süper hızlı silme...")
        start_delete = time.time()

        self.product_service.delete_all_products_truncate()

        end_delete = time.time()
        self.logger.info(f"🚀 TRUNCATE tamamlandı: {end_delete - start_delete:.2f} saniye")

        batch_products = []
        batch_images = []
        batch_histories = []

        self.logger.info("⚡ BATCH MODE: Tüm ürünler hafızada toplanıyor...")

        for i, item in enumerate(items, 1):
            if i % 100 == 0:  # Her 100 üründe progress
                self.logger.info(f"⚙️ Hazırlanan ürün: {i}/{total_items}")

            product_data = {
                'title': item.xpath('g:title/text()',namespaces=ns).get(),
                'mpn': item.xpath('g:mpn/text()', namespaces=ns).get(),
                'gtin': item.xpath('g:gtin/text()', namespaces=ns).get(),
                'availability': item.xpath('g:availability/text()', namespaces=ns).get(),
                'price': item.xpath('g:price/text()', namespaces=ns).get(),
                'sale_price': item.xpath('g:sale_price/text()', namespaces=ns).get(),
                'condition': item.xpath('g:condition/text()', namespaces=ns).get(),
                'description': item.xpath('g:description/text()', namespaces=ns).get(),
                'brand': item.xpath('g:brand/text()', namespaces=ns).get(),
                'link': item.xpath('g:link/text()', namespaces=ns).get(),
                'product_type': item.xpath('g:product_type/text()', namespaces=ns).get(),
                'product_status': item.xpath('g:custom_label_4/text()', namespaces=ns).get(),
            }

            batch_products.append(product_data)

            image_url = item.xpath('g:image_link/text()', namespaces=ns).get()
            additional_image_links = item.xpath('g:additional_image_link/text()', namespaces=ns).getall()

            all_image_links = []
            if image_url:
                all_image_links.append(image_url)
            if additional_image_links:
                all_image_links.extend(additional_image_links)

            if all_image_links:
                for url in all_image_links:
                    if url:
                        batch_images.append({
                            'url': url,
                            'mpn': product_data['mpn']
                        })

            # History batch'e ekle
            batch_histories.append({
                'product_data': product_data,
                'source': 'xml_cron'
            })

        self.logger.info(f"💾 BULK INSERT başlıyor: {len(batch_products)} ürün...")
        start_time = time.time()

        saved_count = self.product_service.save_products_bulk(
            batch_products,
            batch_images,
            batch_histories
        )

        end_time = time.time()
        self.processed_products_count = saved_count

        self.logger.info(f"✅ BULK INSERT tamamlandı!")
        self.logger.info(f"   - Kaydedilen ürün: {saved_count}")
        self.logger.info(f"   - Süre: {end_time - start_time:.2f} saniye")
        self.logger.info(f"   - Hız: {saved_count / (end_time - start_time):.0f} ürün/saniye")

        self.logger.info("🚀 İkinci aşama: Web fiyat güncellemesi başlıyor...")
        for request in self.update_web_price():
            yield request

    def update_web_price(self):
        """Web fiyatlarını güncelle - SÜPER HIZLI"""
        all_products = self.product_service.get_all_products()

        # FIX 2: Geçerli URL filtreleme geri ekle!
        valid_products = [p for p in all_products if p.link and p.link.startswith('http')]

        self.logger.info(f"🔄 PARALEL web fiyat güncellemesi: {len(valid_products)} ürün")
        self.logger.info(f"⚡ Concurrent requests: 64 (çok hızlı)")

        # FIX 3: Sadece geçerli URL'lere git!
        for product in valid_products:
            yield scrapy.Request(
                url=product.link,
                callback=self.get_price_from_link_and_update,
                meta={'product': product},
                dont_filter=True,
                errback=self.handle_error,
                priority=1
            )

    def get_price_from_link_and_update(self, response):
        """Web fiyatını al ve BATCH'e ekle"""
        try:
            self.product_urls_count += 1
            self.total_urls_visited += 1

            # Her 50'de bir progress
            if self.product_urls_count % 50 == 0:
                self.logger.info(f"🌐 İşlenen URL: {self.product_urls_count}")

            # Fiyat parse et
            web_price = (
                    response.xpath(
                        '(//span[contains(@class, "woocommerce-Price-amount amount")])[2]//bdi/text()').get() or
                    response.xpath('//span[contains(@class, "woocommerce-Price-amount")]//bdi/text()').get()
            )

            my_product = response.meta['product']

            # BATCH'e ekle - tek tek DB'ye yazma!
            self.web_price_batch.append({
                'product': my_product,
                'web_price': web_price,
                'success': web_price is not None
            })

            # Batch dolu ise kaydet
            if len(self.web_price_batch) >= self.batch_size:
                self._save_web_price_batch()

        except Exception as e:
            self.logger.error(f"💥 Fiyat güncelleme hatası: {e}")

    def _save_web_price_batch(self):
        """Web fiyat batch'ini toplu olarak kaydet"""
        if not self.web_price_batch:
            return

        try:
            # Batch'i toplu olarak kaydet
            success_count = self.product_service.update_web_prices_bulk(self.web_price_batch)

            self.logger.info(f"💾 Batch kaydedildi: {success_count}/{len(self.web_price_batch)} başarılı")

            # Batch'i temizle
            self.web_price_batch.clear()

        except Exception as e:
            self.logger.error(f"💥 Batch kaydetme hatası: {e}")
            self.web_price_batch.clear()

    def handle_error(self, failure):
        """Hata yakalama fonksiyonu"""
        self.logger.error(f"💥 Request hatası: {failure.value}, URL: {failure.request.url}")

    def closed(self, reason):
        """Spider kapandığında otomatik çalışır"""
        try:
            # FIX 4: Kalan batch'i kaydet!
            if self.web_price_batch:
                self.logger.info("📝 Son batch kaydediliyor...")
                self._save_web_price_batch()

            self.logger.info(f"=== 🕷️ SPIDER CLOSED METHOD ÇALIŞTI ===")
            self.logger.info(f"Spider: {self.name}, Reason: {reason}")
            self.logger.info(f"📊 TOPLAM URL İSTATİSTİKLERİ:")
            self.logger.info(f"   - XML URL'leri: {self.xml_urls_count}")
            self.logger.info(f"   - Ürün URL'leri: {self.product_urls_count}")
            self.logger.info(f"   - Toplam URL: {self.total_urls_visited}")
            self.logger.info(f"   - İşlenen ürün: {self.processed_products_count}")

            if self.crawler_log_id and self.crawler_log_repo:
                # Stats al
                stats = self.crawler.stats.get_stats()

                # Kendi sayaçlarımızı ekle
                crawler_stats = {
                    'processed': stats.get('response_received_count', 0),
                    'updated': self.product_urls_count,
                    'created': self.processed_products_count,
                    'downloader/request_count': stats.get('downloader/request_count', 0),
                    'downloader/response_count': stats.get('downloader/response_count', 0),
                    'downloader/response_status_count/200': stats.get('downloader/response_status_count/200', 0),
                    'downloader/response_status_count/404': stats.get('downloader/response_status_count/404', 0),
                    'elapsed_time_seconds': stats.get('elapsed_time_seconds', 0),

                    # CUSTOM STATİSTİKLER
                    'custom/xml_urls_count': self.xml_urls_count,
                    'custom/product_urls_count': self.product_urls_count,
                    'custom/total_urls_visited': self.total_urls_visited,
                    'custom/processed_products_count': self.processed_products_count,
                }

                self.logger.info(f"📈 DETAYLI İSTATİSTİKLER:")
                self.logger.info(f"   - Scrapy total request: {crawler_stats['downloader/request_count']}")
                self.logger.info(f"   - Scrapy total response: {crawler_stats['downloader/response_count']}")
                self.logger.info(f"   - Başarılı (200): {crawler_stats['downloader/response_status_count/200']}")
                self.logger.info(f"   - Hata (404): {crawler_stats['downloader/response_status_count/404']}")
                self.logger.info(f"   - Süre: {crawler_stats['elapsed_time_seconds']} saniye")

                # DB güncelle
                if reason == 'finished':
                    import json
                    stats_json = json.dumps(crawler_stats, indent=2)
                    self.crawler_log_repo.complete_crawler(self.crawler_log_id, {
                        'processed': crawler_stats['downloader/response_count'],
                        'updated': self.product_urls_count,
                        'created': self.processed_products_count,
                        'stats_json': stats_json
                    })
                    self.logger.info("✅ DB başarıyla güncellendi (finished)")
                else:
                    self.crawler_log_repo.fail_crawler(self.crawler_log_id, f"Spider kapatıldı: {reason}")
                    self.logger.info("❌ DB başarıyla güncellendi (failed)")
            else:
                self.logger.warning("⚠️ crawler_log_id veya crawler_log_repo None!")

        except Exception as e:
            self.logger.error(f"💥 Spider closed method hatası: {repr(e)}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")