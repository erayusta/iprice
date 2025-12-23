from typing import Any
import requests
import scrapy
import time
import datetime

from app.helper.standardize_price import standardize_price
from app.services.PazaramaService import PazaramaService
from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService
from app.services.CrawlerServiceFactory import CrawlerServiceFactory


class PriceParser(scrapy.Spider):
    name = 'PriceParser'

    # PERFORMANS AYARLARI - XmlParser ile uyumlu
    custom_settings = {
        'CONCURRENT_REQUESTS': 32,  # Biraz daha düşük (farklı siteler)
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'DOWNLOAD_DELAY': 0.1,  # Çok küçük delay
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'RETRY_ENABLED': False,
        'REDIRECT_ENABLED': True,  # PriceParser için redirect gerekli
        'COOKIES_ENABLED': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.1,
        'AUTOTHROTTLE_MAX_DELAY': 1,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8.0,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(
            self,
            product_service: ProductService,
            screenshot_service: ScreenshotService,
            crawler_log_id=None,
            crawler_log_repo=None,
            **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.db_session = None
        self.product_service = product_service
        self.screenshot_service = screenshot_service
        self.crawler_log_id = crawler_log_id
        self.crawler_log_repo = crawler_log_repo

        # SERVICE FACTORY EKLEME
        self.service_factory = CrawlerServiceFactory(
            product_repository=product_service.product_repository,
            image_repository=product_service.image_repository,
            screenshot_repository=screenshot_service.screenshot_repository,
            product_service=product_service  # ← YENİ: ProductService'i geç
        )

        # URL SAYAÇLARI - XmlParser ile aynı sistem
        self.processed_products_count = 0
        self.total_urls_visited = 0
        self.xml_urls_count = 0  # PriceParser'da 0 olacak
        self.product_urls_count = 0

        # BATCH İŞLEME
        self.attribute_batch = []
        self.batch_size = 100  # Attribute'lar için batch size

        # PERFORMANCE TRACKING
        self.start_time = time.time()
        self.companies_processed = set()

        self.failed_urls = []  # Başarısız URL'ler
        self.error_summary = {}  # Hata türü sayıları
        self.success_count = 0  # Başarılı istekler
        self.redirect_urls = []  # Redirect olan URL'ler
        self.blocked_urls = []  # 403/404 olan URL'ler

        self.status_404_count = 0
        self.status_404_urls = []

        self.url_statuses = []

    def start_requests(self):
        try:
            self.logger.info("🚀 PriceParser başlatılıyor...")
            self.logger.info(f"🎯 Registered companies: {self.service_factory.get_registered_companies()}")

            products = self.product_service.get_products_with_urls()
            total_products = len(products)

            self.logger.info(f"📦 Toplam {total_products} ürün URL'i bulundu")
            self.logger.info(f"⚡ Concurrent requests: {self.custom_settings['CONCURRENT_REQUESTS']}")

            for i, (company, product_url, server) in enumerate(products, 1):
                # Progress tracking
                if i % 100 == 0:
                    self.logger.info(f"⚙️ Hazırlanan request: {i}/{total_products}")

                url = product_url.url
                if url.startswith('http://'):
                    url = url.replace('http://', 'https://')
                    self.logger.debug(f"URL HTTP'den HTTPS'e çevrildi: {product_url.url} -> {url}")

                company_name = product_url.company.name
                product_mpn = product_url.mpn

                # Company için application_id kontrol et
                company_obj = self.product_service.get_company_by_name(company_name)
                application_id = getattr(company_obj, 'application_id', None) if company_obj else None

                # Crawler tipi belirleme
                should_use_special_service = (
                        application_id == 4 or  # selenium
                        application_id == 'selenium'
                )

                # ← YENİ: EĞER ÖZEL SERVİS GEREKİYORSA, SCRAPY REQUEST YAPMA
                if should_use_special_service:
                    self.logger.info(
                        f"🎯 {company_name} (app_id: {application_id}) - Direkt selenium service kullanılacak")

                    # Direkt selenium service çağır
                    try:
                        service = self.service_factory.get_service(company_name)
                        if service:
                            self.logger.info(f"🔄 {company_name} selenium service ile extraction başlıyor...")

                            # Service'den veri çek
                            extracted_data = service.extract_product_data(
                                url=url,
                                mpn=product_mpn,
                                company=company_name
                            )

                            if extracted_data:
                                # Veriyi attribute format'ına çevir
                                attribute_values = self._convert_service_data_to_attributes(
                                    extracted_data,
                                    company_name,
                                    product_mpn
                                )

                                # Batch'e ekle
                                if attribute_values:
                                    self.attribute_batch.extend(attribute_values)
                                    self.processed_products_count += 1

                                    # Batch dolu ise kaydet
                                    if len(self.attribute_batch) >= self.batch_size:
                                        self._save_attribute_batch()

                                self.logger.info(
                                    f"✅ {company_name} service extraction tamamlandı - {len(attribute_values)} attribute")
                                self.product_urls_count += 1
                                self.success_count += 1

                                # URL durumunu başarılı olarak kaydet
                                self.url_statuses.append({
                                    'url': url,
                                    'company': company_name,
                                    'mpn': product_mpn,
                                    'status': 200,  # Success
                                    'error_type': 'Selenium Success',
                                    'timestamp': time.time()
                                })

                            else:
                                self.logger.warning(f"⚠️ {company_name} service'den veri alınamadı")
                                # Hata durumunu kaydet
                                self.url_statuses.append({
                                    'url': url,
                                    'company': company_name,
                                    'mpn': product_mpn,
                                    'status': 'SELENIUM_ERROR',
                                    'error_type': 'Selenium No Data',
                                    'timestamp': time.time()
                                })
                        else:
                            self.logger.error(f"❌ {company_name} service bulunamadı!")

                    except Exception as service_error:
                        self.logger.error(f"💥 {company_name} service hatası: {service_error}")
                        # Service hata durumunu kaydet
                        self.url_statuses.append({
                            'url': url,
                            'company': company_name,
                            'mpn': product_mpn,
                            'status': 'SELENIUM_ERROR',
                            'error_type': f'Selenium Error: {str(service_error)}',
                            'timestamp': time.time()
                        })

                    # Scrapy request yapmadan devam et
                    continue

                # ← NORMAL SCRAPY REQUEST (sadece scrapy companies için)
                meta_info = {
                    'mpn': product_mpn,
                    'company': company_name,
                    'product_index': i,
                    'total_products': total_products,
                    'application_id': application_id,
                    'should_use_special_service': should_use_special_service
                }

                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.errback,
                    dont_filter=True,
                    meta=meta_info,
                    priority=1
                )
        except Exception as e:
            self.logger.error(f"💥 start_requests sırasında hata: {str(e)}")

    def _process_selenium_urls(self, selenium_products):
        """Selenium URL'lerini sırayla işle"""
        try:
            total_selenium = len(selenium_products)
            self.logger.info(f"🤖 {total_selenium} selenium URL'i işlenecek...")

            for i, (company, product_url, server) in enumerate(selenium_products, 1):
                url = product_url.url
                if url.startswith('http://'):
                    url = url.replace('http://', 'https://')

                company_name = product_url.company.name
                product_mpn = product_url.mpn

                self.logger.info(f"🎯 {company_name} ({i}/{total_selenium}) - Selenium extraction başlıyor...")

                try:
                    service = self.service_factory.get_service(company_name)
                    if service:
                        # Service'den veri çek
                        start_time = time.time()
                        extracted_data = service.extract_product_data(
                            url=url,
                            mpn=product_mpn,
                            company=company_name
                        )
                        extraction_time = time.time() - start_time

                        if extracted_data:
                            # Veriyi attribute format'ına çevir
                            attribute_values = self._convert_service_data_to_attributes(
                                extracted_data,
                                company_name,
                                product_mpn
                            )

                            # Batch'e ekle
                            if attribute_values:
                                self.attribute_batch.extend(attribute_values)
                                self.processed_products_count += 1

                                # Batch dolu ise kaydet
                                if len(self.attribute_batch) >= self.batch_size:
                                    self._save_attribute_batch()

                            self.logger.info(
                                f"✅ {company_name} extraction tamamlandı - {len(attribute_values)} attribute ({extraction_time:.1f}s)")
                            self.product_urls_count += 1
                            self.success_count += 1

                            # URL durumunu başarılı olarak kaydet
                            self.url_statuses.append({
                                'url': url,
                                'company': company_name,
                                'mpn': product_mpn,
                                'status': 200,
                                'error_type': 'Selenium Success',
                                'extraction_time': extraction_time,
                                'timestamp': time.time()
                            })

                        else:
                            self.logger.warning(f"⚠️ {company_name} service'den veri alınamadı")
                            self.url_statuses.append({
                                'url': url,
                                'company': company_name,
                                'mpn': product_mpn,
                                'status': 'SELENIUM_NO_DATA',
                                'error_type': 'Selenium No Data',
                                'timestamp': time.time()
                            })
                    else:
                        self.logger.error(f"❌ {company_name} service bulunamadı!")

                except Exception as service_error:
                    self.logger.error(f"💥 {company_name} service hatası: {service_error}")
                    self.url_statuses.append({
                        'url': url,
                        'company': company_name,
                        'mpn': product_mpn,
                        'status': 'SELENIUM_ERROR',
                        'error_type': f'Selenium Error: {str(service_error)}',
                        'timestamp': time.time()
                    })

            self.logger.info(f"✅ Tüm selenium URL'leri işlendi ({total_selenium}/{total_selenium})")

        except Exception as e:
            self.logger.error(f"💥 Selenium URL processing genel hatası: {e}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")

    def parse(self, response):
        try:
            self.total_urls_visited += 1

            company_name = response.meta['company']
            product_mpn = response.meta['mpn']
            application_id = response.meta.get('application_id')
            should_use_special_service = response.meta.get('should_use_special_service', False)

            self.url_statuses.append({
                'url': response.url,
                'company': company_name,
                'mpn': product_mpn,
                'status': response.status,
                'error_type': f'HTTP {response.status}',
                'timestamp': time.time()
            })

            if response.status == 404:
                self.status_404_count += 1
                self.logger.warning(f"❌ 404 - URL bulunamadı: {response.url}")
                self.logger.warning(f"   Company: {company_name}, MPN: {product_mpn}")
                return

            self.product_urls_count += 1
            self.success_count += 1

            # Progress tracking
            if self.product_urls_count % 50 == 0:
                elapsed = time.time() - self.start_time
                self.logger.info(f"🔄 İşlenen ürün: {self.product_urls_count} | Süre: {elapsed:.1f}s")

            # Company tracking
            self.companies_processed.add(company_name)

            # ← YENİ PART: APPLICATION_ID'YE GÖRE PARSER SEÇİMİ
            if should_use_special_service:
                self.logger.info(f"🎯 {company_name} (app_id: {application_id}) - Özel service kullanılacak")
                return self._parse_with_special_service(response)
            else:
                self.logger.debug(f"🕷️ {company_name} (app_id: {application_id}) - Normal scrapy kullanılacak")
                return self._parse_with_scrapy(response)

        except Exception as e:
            self.logger.error(f"💥 Parse hatası: {str(e)}")

    def _parse_with_special_service(self, response):
        """Özel service ile parsing"""
        try:
            company_name = response.meta['company']
            product_mpn = response.meta['mpn']

            # Özel service'i al
            service = self.service_factory.get_service(company_name)
            if not service:
                self.logger.warning(f"⚠️ {company_name} için service bulunamadı, scrapy ile devam ediliyor")
                return self._parse_with_scrapy(response)

            self.logger.info(f"🎯 {company_name} özel service ile işleniyor: {service.get_service_name()}")

            # Service'den veri çek
            extracted_data = service.extract_product_data(
                url=response.url,
                mpn=product_mpn,
                company=company_name
            )

            if extracted_data:
                # Veriyi attribute format'ına çevir
                attribute_values = self._convert_service_data_to_attributes(
                    extracted_data,
                    company_name,
                    product_mpn
                )

                # Batch'e ekle
                if attribute_values:
                    self.attribute_batch.extend(attribute_values)
                    self.processed_products_count += 1

                    # Batch dolu ise kaydet
                    if len(self.attribute_batch) >= self.batch_size:
                        self._save_attribute_batch()

                self.logger.info(f"✅ {company_name} service extraction tamamlandı - {len(attribute_values)} attribute")
            else:
                self.logger.warning(f"⚠️ {company_name} service'den veri alınamadı")

        except Exception as e:
            self.logger.error(f"💥 Special service parse hatası ({company_name}): {str(e)}")
            # Hata durumunda scrapy ile dene
            return self._parse_with_scrapy(response)

    def _parse_with_scrapy(self, response):
        """Mevcut scrapy logic - DEGİŞİKLİK YOK"""
        try:
            redirect_times = response.request.meta.get('redirect_times', 0)
            redirect_urls = response.request.meta.get('redirect_urls', [])

            self.logger.debug(f"🌐 Parsing: {response.url}")

            is_redirect = redirect_times > 0 or len(redirect_urls) > 0
            company_name = response.meta['company']
            product_mpn = response.meta['mpn']

            # Mevcut şirketi al (marketplace)
            current_company = self.product_service.get_company_by_name(company_name)
            if not current_company:
                self.logger.error(f"❌ Company not found: {company_name}")
                return

            marketplace_id = current_company.id

            attributes = self.product_service.get_attributes_for_company(company_name)
            if not attributes:
                self.logger.warning(f"⚠️ No attributes found for company: {company_name}")
                return

            attribute_values = []

            # Attribute dictionary oluştur
            attribute_dict = {}
            for attr in attributes:
                attribute_dict[attr['attribute_name']] = attr

            # Her öznitelik için işlem
            for item in attributes:
                try:
                    if item['attribute_name'] == 'is_redirect':
                        value = is_redirect
                        attribute_data = {
                            'company_id': item['company_id'],
                            'mpn': product_mpn,
                            'attribute_id': item['attribute_id'],
                            'attribute_name': item['attribute_name'],
                            'value': value
                        }
                        attribute_values.append(attribute_data)

                    elif item['attribute_name'] == 'price':
                        value = response.xpath(f"{item['xpath']}").get() if item[
                                                                                'selector_type'] == 'xpath' else response.css(
                            f"{item['xpath']}").get()
                        if value:
                            value = standardize_price(value)
                            attribute_data = {
                                'company_id': item['company_id'],
                                'mpn': product_mpn,
                                'attribute_id': item['attribute_id'],
                                'attribute_name': item['attribute_name'],
                                'value': value
                            }
                            attribute_values.append(attribute_data)

                    elif item['attribute_name'] == 'multi_price':
                        # Multi price processing
                        merchant_blocks = response.xpath(f"{item['xpath']}") if item[
                                                                                    'selector_type'] == 'xpath' else response.css(
                            f"{item['xpath']}")

                        price_xpath = attribute_dict.get('sub_price', {}).get('xpath', '')
                        seller_xpath = attribute_dict.get('seller', {}).get('xpath', '')
                        price_selector_type = attribute_dict.get('price', {}).get('selector_type', 'css')
                        seller_selector_type = attribute_dict.get('seller', {}).get('selector_type', 'css')

                        for index, block in enumerate(merchant_blocks):
                            price = None
                            seller_name = None

                            if price_xpath:
                                price = block.xpath(
                                    f"{price_xpath}").get() if price_selector_type == 'xpath' else block.css(
                                    f"{price_xpath}").get()
                                if price:
                                    price = standardize_price(price)

                            if seller_xpath:
                                seller_name = block.xpath(
                                    f"{seller_xpath}").get() if seller_selector_type == 'xpath' else block.css(
                                    f"{seller_xpath}").get()

                            if seller_name and price:
                                seller_company = self.product_service.get_company_by_name(seller_name)

                                if not seller_company:
                                    new_seller = {
                                        'name': seller_name,
                                        'is_marketplace': False,
                                        'server_id': current_company.server_id,
                                        'logo': None,
                                        'is_screenshot': False,
                                        'marketplace_id': marketplace_id
                                    }
                                    seller_company = self.product_service.create_company(new_seller,
                                                                                         current_company.server_id)
                                    self.logger.info(f"✅ New seller created: {seller_name}")

                                attribute_data = {
                                    'company_id': seller_company.id,
                                    'mpn': product_mpn,
                                    'attribute_id': attribute_dict['price']['attribute_id'],
                                    'attribute_name': 'price',
                                    'value': price
                                }
                                attribute_values.append(attribute_data)

                    elif item['attribute_name'] == 'is_stock':
                        value = response.xpath(f"{item['xpath']}").get() if item[
                                                                                'selector_type'] == 'xpath' else response.css(
                            f"{item['xpath']}").get()
                        value = True if value is not None else False

                        attribute_data = {
                            'company_id': item['company_id'],
                            'mpn': product_mpn,
                            'attribute_id': item['attribute_id'],
                            'attribute_name': item['attribute_name'],
                            'value': value
                        }
                        attribute_values.append(attribute_data)

                    elif item['attribute_name'] == 'seller':
                        # Skip seller attribute
                        continue

                    else:
                        # Diğer attribute'lar
                        value = response.xpath(f"{item['xpath']}").get() if item[
                                                                                'selector_type'] == 'xpath' else response.css(
                            f"{item['xpath']}").get()

                        attribute_data = {
                            'company_id': item['company_id'],
                            'mpn': product_mpn,
                            'attribute_id': item['attribute_id'],
                            'attribute_name': item['attribute_name'],
                            'value': value
                        }
                        attribute_values.append(attribute_data)

                except Exception as attr_error:
                    self.logger.error(f"💥 Attribute işleme hatası ({item['attribute_name']}): {attr_error}")

            # BATCH'e ekle
            self.attribute_batch.extend(attribute_values)
            self.processed_products_count += 1

            # Batch dolu ise kaydet
            if len(self.attribute_batch) >= self.batch_size:
                self._save_attribute_batch()

        except Exception as e:
            self.logger.error(f"💥 Scrapy parse hatası: {str(e)}")

    def _convert_service_data_to_attributes(self, service_data, company_name, product_mpn):
        """Service'den gelen veriyi attribute format'ına çevir"""
        try:
            current_company = self.product_service.get_company_by_name(company_name)
            if not current_company:
                self.logger.error(f"❌ Company not found: {company_name}")
                return []

            # Bu company için mevcut attribute'ları al
            attributes = self.product_service.get_attributes_for_company(company_name)
            if not attributes:
                self.logger.warning(f"⚠️ No attributes found for company: {company_name}")
                return []

            # Attribute dictionary oluştur (mevcut kodunuzdaki gibi)
            attribute_dict = {}
            for attr in attributes:
                attribute_dict[attr['attribute_name']] = attr

            attribute_values = []

            # Service'den gelen veriyi attribute'larla eşleştir
            for key, value in service_data.items():
                if key == 'other_sellers':
                    # Diğer satıcıları işle
                    attribute_values.extend(
                        self._process_other_sellers(value, product_mpn, current_company, attribute_dict)
                    )
                elif value is not None and key in attribute_dict:
                    # Normal attribute'ları işle
                    attr_info = attribute_dict[key]
                    attribute_values.append({
                        'company_id': attr_info['company_id'],
                        'mpn': product_mpn,
                        'attribute_id': attr_info['attribute_id'],
                        'attribute_name': key,
                        'value': value
                    })

            return attribute_values

        except Exception as e:
            self.logger.error(f"💥 Service data conversion hatası: {e}")
            return []

    def _process_other_sellers(self, other_sellers, product_mpn, marketplace_company, attribute_dict):
        """Service'den gelen other_sellers'ı işle"""
        attribute_values = []

        try:
            # Price attribute'ını attribute_dict'ten al
            price_attribute_info = attribute_dict.get('price')
            if not price_attribute_info:
                self.logger.warning("⚠️ Price attribute bulunamadı, other_sellers işlenemiyor")
                return attribute_values

            for seller_data in other_sellers:
                seller_name = seller_data.get('name')
                seller_price = seller_data.get('price')

                if seller_name and seller_price:
                    # Seller company'yi bul veya oluştur
                    seller_company = self.product_service.get_company_by_name(seller_name)

                    if not seller_company:
                        new_seller = {
                            'name': seller_name,
                            'is_marketplace': False,
                            'server_id': marketplace_company.server_id,
                            'logo': None,
                            'is_screenshot': False,
                            'marketplace_id': marketplace_company.id
                        }
                        seller_company = self.product_service.create_company(
                            new_seller,
                            marketplace_company.server_id
                        )
                        self.logger.info(f"✅ New seller created from service: {seller_name}")

                    # Price attribute'ını kullan
                    attribute_values.append({
                        'company_id': seller_company.id,
                        'mpn': product_mpn,
                        'attribute_id': price_attribute_info['attribute_id'],
                        'attribute_name': 'price',
                        'value': seller_price
                    })

        except Exception as e:
            self.logger.error(f"💥 Other sellers processing hatası: {e}")

        return attribute_values

    def _save_attribute_batch(self):
        """Attribute batch'ini toplu olarak kaydet - DEĞİŞİKLİK YOK"""
        if not self.attribute_batch:
            return

        try:
            self.product_service.create_attribute_values(self.attribute_batch)
            saved_count = len(self.attribute_batch)
            self.logger.info(f"💾 Attribute batch kaydedildi: {saved_count} kayıt")

            # Batch'i temizle
            self.attribute_batch.clear()

        except Exception as e:
            self.logger.error(f"💥 Attribute batch kaydetme hatası: {e}")
            self.attribute_batch.clear()

    def errback(self, failure):
        """Error handling - APPLICATION_ID KONTROLÜ EKLENDİ"""
        self.total_urls_visited += 1

        # META BİLGİLERİNİ AL
        company_name = failure.request.meta.get('company', 'Unknown')
        product_mpn = failure.request.meta.get('mpn', 'Unknown')
        application_id = failure.request.meta.get('application_id')
        should_use_special_service = failure.request.meta.get('should_use_special_service', False)

        # ← YENİ: EĞER ÖZEL SERVİS GEREKİYORSA, SCRAPY HATASI ALMAYALIM
        if should_use_special_service:
            self.logger.info(
                f"🎯 {company_name} (app_id: {application_id}) - Scrapy 403 hatası, özel service ile tekrar deneniyor...")

            # Özel service ile işle
            try:
                service = self.service_factory.get_service(company_name)
                if service:
                    self.logger.info(f"🔄 {company_name} selenium service ile extraction başlıyor...")

                    # Service'den veri çek
                    extracted_data = service.extract_product_data(
                        url=failure.request.url,
                        mpn=product_mpn,
                        company=company_name
                    )

                    if extracted_data:
                        # Veriyi attribute format'ına çevir
                        attribute_values = self._convert_service_data_to_attributes(
                            extracted_data,
                            company_name,
                            product_mpn
                        )

                        # Batch'e ekle
                        if attribute_values:
                            self.attribute_batch.extend(attribute_values)
                            self.processed_products_count += 1

                            # Batch dolu ise kaydet
                            if len(self.attribute_batch) >= self.batch_size:
                                self._save_attribute_batch()

                        self.logger.info(
                            f"✅ {company_name} service extraction tamamlandı - {len(attribute_values)} attribute")
                        self.product_urls_count += 1
                        self.success_count += 1

                        # URL durumunu başarılı olarak kaydet
                        self.url_statuses.append({
                            'url': failure.request.url,
                            'company': company_name,
                            'mpn': product_mpn,
                            'status': 200,  # Success
                            'error_type': 'Selenium Success',
                            'timestamp': time.time()
                        })

                        return  # Başarılı, normal error handling'e geçme
                    else:
                        self.logger.warning(f"⚠️ {company_name} service'den veri alınamadı")
                else:
                    self.logger.error(f"❌ {company_name} service bulunamadı!")

            except Exception as service_error:
                self.logger.error(f"💥 {company_name} service hatası: {service_error}")
                # Service hatası durumunda da normal error handling'e geç

        # NORMAL ERROR HANDLING (scrapy companies için)
        # HATA DETAYLARINI BELİRLE
        error_details = {
            'status': None,  # Kategorik durum (DNS_ERROR, TIMEOUT vs.)
            'status_code': None,  # Gerçek HTTP kodu (404, 403 vs.)
            'error_type': "Unknown Error",
            'error_message': str(failure.value)
        }

        if hasattr(failure.value, 'response') and failure.value.response:
            # HTTP hatası (403, 404, 500, vs)
            http_code = failure.value.response.status
            error_details['status'] = f"HTTP_{http_code}"
            error_details['status_code'] = http_code
            error_details['error_type'] = f"HTTP {http_code}"

        elif "redirect" in str(failure.value).lower():
            error_details['status'] = "REDIRECT"
            error_details['status_code'] = None  # HTTP kodu yok
            error_details['error_type'] = "Max Redirect"

        elif "timeout" in str(failure.value).lower():
            error_details['status'] = "TIMEOUT"
            error_details['status_code'] = None  # HTTP kodu yok
            error_details['error_type'] = "Timeout"

        elif "dns" in str(failure.value).lower():
            error_details['status'] = "DNS_ERROR"
            error_details['status_code'] = None  # HTTP kodu yok
            error_details['error_type'] = "DNS Error"

        else:
            error_details['status'] = "CONNECTION_ERROR"
            error_details['status_code'] = None  # HTTP kodu yok
            error_details['error_type'] = "Connection Error"

        # URL DURUMUNU KAYDET
        self.url_statuses.append({
            'url': failure.request.url,
            'company': company_name,
            'mpn': product_mpn,
            'status': error_details['status'],
            'status_code': error_details['status_code'],
            'error_type': error_details['error_type'],
            'error_message': error_details['error_message'],
            'timestamp': time.time()
        })

        self.logger.error(f"💥 {error_details['error_type']} - URL: {failure.request.url}")
        self.logger.error(f"   Company: {company_name}, MPN: {product_mpn}")

        return {
            'error': error_details['error_message'],
            'url': failure.request.url,
            'status': error_details['status'],
            'status_code': error_details['status_code']
        }

    def closed(self, reason):
        """Spider kapandığında otomatik çalışır - SERVICE CLEANUP EKLENDİ"""
        try:
            # Kalan batch'i kaydet
            if self.attribute_batch:
                self.logger.info("📝 Son attribute batch kaydediliyor...")
                self._save_attribute_batch()

            # ← YENİ: SERVICE CLEANUP
            self.logger.info("🧹 Service factory cleanup başlıyor...")
            self.service_factory.cleanup_all()

            # Mevcut closed logic - değişiklik yok
            self.logger.info(f"=== 🕷️ PRICEPARSER CLOSED METHOD ÇALIŞTI ===")
            self.logger.info(f"Spider: {self.name}, Reason: {reason}")

            # Süre hesaplama
            total_time = time.time() - self.start_time

            status_summary = {}
            error_details = []

            self.logger.info(f"🔍 DEBUG: url_statuses liste boyutu: {len(self.url_statuses)}")

            for url_status in self.url_statuses:
                status_code = str(url_status['status'])

                if status_code not in status_summary:
                    status_summary[status_code] = 0
                status_summary[status_code] += 1

                if url_status['status'] != 200:
                    error_details.append(url_status)

            self.logger.info(f"🔍 DEBUG: status_summary: {status_summary}")
            self.logger.info(f"🔍 DEBUG: error_details boyutu: {len(error_details)}")

            # LOG'DA ÖZET GÖSTER
            self.logger.info(f"📊 URL DURUM ÖZETİ:")
            for status, count in status_summary.items():
                self.logger.info(f"   - {status}: {count} adet")

            if error_details:
                self.logger.info(f"❌ HATALI URL'LER (ilk 10):")
                for i, error in enumerate(error_details[:10]):
                    self.logger.info(f"   {i + 1}. {error['error_type']} - {error['company']} - {error['mpn']}")

            self.logger.info(f"📊 TOPLAM URL İSTATİSTİKLERİ:")
            self.logger.info(f"   - Toplam URL: {self.total_urls_visited}")
            self.logger.info(f"   - İşlenen ürün: {self.processed_products_count}")
            self.logger.info(f"   - İşlenen şirket: {len(self.companies_processed)}")
            self.logger.info(f"   - Toplam süre: {total_time:.2f} saniye")

            # DB logging kısmı - değişiklik yok
            if self.crawler_log_id and self.crawler_log_repo:
                stats = self.crawler.stats.get_stats()

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
                    'custom/companies_processed': len(self.companies_processed),
                    'custom/url_status_summary': status_summary,
                    'custom/error_details': error_details,
                    'custom/total_errors': len(error_details),
                    'custom/status_404_count': self.status_404_count,
                }

                if reason == 'finished':
                    import json
                    try:
                        stats_json = json.dumps(crawler_stats, indent=2)

                        self.crawler_log_repo.complete_crawler(self.crawler_log_id, {
                            'processed': crawler_stats['downloader/response_count'],
                            'updated': self.product_urls_count,
                            'created': self.processed_products_count,
                            'stats_json': stats_json
                        })
                        self.logger.info("✅ DB başarıyla güncellendi (finished)")

                    except Exception as json_error:
                        self.logger.error(f"💥 JSON serialize hatası: {str(json_error)}")
                        crawler_stats_simple = {k: v for k, v in crawler_stats.items() if
                                                not k.startswith('custom/error_details')}
                        stats_json = json.dumps(crawler_stats_simple, indent=2)
                        self.crawler_log_repo.complete_crawler(self.crawler_log_id, {
                            'processed': crawler_stats['downloader/response_count'],
                            'updated': self.product_urls_count,
                            'created': self.processed_products_count,
                            'stats_json': stats_json
                        })
                        self.logger.info("⚠️ DB error_details olmadan güncellendi")
            else:
                self.logger.warning("⚠️ crawler_log_id veya crawler_log_repo None!")

        except Exception as e:
            self.logger.error(f"💥 Spider closed method hatası: {repr(e)}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")