import logging

import time
from datetime import datetime

from sqlalchemy import text

from app.model.Image import Image
from app.model.Product import Product
from app.model.ProductHistory import ProductHistory
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ProductHistoryRepository import ProductHistoryRepository
from app.repositories.ImageRepository import ImageRepository
from app.helper.standardize_price import standardize_price


def _get_parsing_method_by_application_id(application_id: int) -> str:
    application_parsing_map = {
        1: "scrapy",
        2: "selenium",
        3: "scrapy",
    }

    return application_parsing_map.get(application_id, "scrapy")


class ProductService:
    def __init__(
            self,
            product_repository: ProductRepository,
            product_history_repository: ProductHistoryRepository,
            image_repository: ImageRepository
    ):
        self.logger = logging.getLogger(__name__)
        self.product_repository = product_repository
        self.product_history_repository = product_history_repository
        self.image_repository = image_repository

        self.current_process_id = self.product_history_repository.get_new_process_id()

    def save_product(self, product_data, image_url, additional_image_links):
        new_product = self.product_repository.create_product(product_data)

        all_image_links = []
        if image_url:
            all_image_links.append(image_url)
        if additional_image_links:
            all_image_links.extend(additional_image_links)

        if all_image_links:
            existing_images = self.image_repository.get_image_by_mpn(new_product.mpn)
            existing_urls = set()

            if existing_images:
                if isinstance(existing_images, list):
                    existing_urls = set(img.url if hasattr(img, 'url') else img for img in existing_images)
                else:
                    existing_urls = {existing_images}

            new_images = []
            for url in all_image_links:
                if url and url not in existing_urls:  # URL geçerli ve mevcut değilse
                    image = self.image_repository.create_image(url, new_product.mpn)
                    new_images.append(image)

            if new_images:
                self.image_repository.add_images_batch(new_images)

        self.product_history_repository.create_product_history(
            product_data,
            self.current_process_id,
            'xml_cron'
        )

        return new_product.id

    # YENİ METOD: Batch kayıt için
    def save_products_batch(self, products_data_list):
        """Birden fazla ürünü tek seferde kaydet - performans optimizasyonu"""
        if not products_data_list:
            return []

        # Tüm ürünleri toplu olarak kaydet
        new_products = self.product_repository.create_products_batch(products_data_list)

        # Image ve history verilerini topla
        all_images = []
        all_histories = []

        for product, data in zip(new_products, products_data_list):
            # Image verilerini topla
            image_urls = []
            if data.get('image_url'):
                image_urls.append(data['image_url'])
            if data.get('additional_images'):
                image_urls.extend(data['additional_images'])

            # Mevcut image'ları kontrol et
            if image_urls:
                existing_images = self.image_repository.get_image_by_mpn(product.mpn)
                existing_urls = set()

                if existing_images:
                    if isinstance(existing_images, list):
                        existing_urls = set(img.url if hasattr(img, 'url') else img for img in existing_images)
                    else:
                        existing_urls = {existing_images}

                # Yeni image'ları ekle
                for url in image_urls:
                    if url and url not in existing_urls:
                        all_images.append({
                            'url': url,
                            'mpn': product.mpn
                        })

            # History kaydını hazırla
            all_histories.append({
                'product': product,
                'product_data': data,
                'process_id': self.current_process_id,
                'source': 'xml_cron'
            })

        # Toplu image kaydı
        if all_images:
            self.image_repository.create_images_batch(all_images)

        # Toplu history kaydı
        if all_histories:
            self.product_history_repository.create_histories_batch(all_histories)

        return [p.id for p in new_products]

    def find_by_mpn_code(self, mpn):
        return self.product_repository.find_by_mpn(mpn)

    def get_all_products(self):
        return self.product_repository.get_all()

    def update_product_with_web_price(self, product, web_price):
        return self.product_repository.update_product_web_price(product, standardize_price(web_price))

    def create_product_history_with_web_price(self, product, web_price):
        return self.product_history_repository.create_product_history_with_web_price_object(
            product,
            self.current_process_id,
            web_price,
            'xml_cron'
        )

    def create_product_history_with_merchant_price(self, google_merchant_data):
        no_mpn_in_db = 0

        for product in google_merchant_data:
            if product.get('mpn') is None:
                product['mpn'] = 'bundle'

            old_product = self.product_repository.find_by_mpn(product['mpn'])

            if old_product is None:
                print(f"No product found with this MPN code: {product['mpn']}")
                no_mpn_in_db += 1
                continue

            print(f"mpn code: {old_product.mpn} saving to db")

            if product.get('salePrice') is None:
                self.product_history_repository.create_product_history_with_merchant_price_object(
                    old_product,
                    self.current_process_id,
                    product['price']['value'],
                    'merchant_cron'
                )
            else:
                self.product_history_repository.create_product_history_with_merchant_price_object(
                    old_product,
                    self.current_process_id,
                    product['salePrice']['value'],
                    'merchant_cron'
                )

        return no_mpn_in_db

    def update_product_prices(self, product_data):
        updated_count = 0

        for mpn, price_data in product_data.items():
            product = self.product_repository.find_by_mpn(mpn)
            if product:
                self.product_repository.update_product_merchant_price(
                    product,
                    standardize_price(price_data['merchant_price'])
                )
                updated_count += 1

        return updated_count

    def delete_all_products(self):
        self.product_repository.delete_all_products()

    def get_products_with_urls(self):
        return self.product_repository.get_companies_with_urls_by_server()

    def get_products_with_urls_by_company_id(self, company_id):
        return self.product_repository.get_products_with_urls_by_company_id(company_id)

    def get_company_info_with_application(self, company_id: int):
        try:
            company_info = self.product_repository.get_company_with_application(company_id)

            if not company_info:
                return None

            return {
                'company_id': company_info.id,
                'company_name': company_info.name,
                'application_id': company_info.application_id.name,
                'parsing_method': _get_parsing_method_by_application_id(company_info.application_id)
            }

        except Exception as e:
            self.logger.error(f"Error getting company info: {e}")
            return None

    # Bu metodu ProductService sınıfına ekle

    def get_company_parsing_info(self, company_id: int):
        try:
            print(f"Getting parsing info for company_id: {company_id}")

            company_info = self.product_repository.get_company_with_application(company_id)
            print(f"Company info result: {company_info}")

            if not company_info:
                return {
                    'status': 'error',
                    'message': f'Company bulunamadı: {company_id}'
                }

            # application_id kontrolü
            if company_info.get('application_id') is None:
                return {
                    'status': 'error',
                    'message': f'Company {company_id} için application_id tanımlanmamış'
                }

            print(f"Application ID: {company_info['application_id']}")

            # Application tablosundan parsing method'u çek
            parsing_info = self.product_repository.get_application_parsing_method(
                company_info['application_id']
            )
            print(f"Parsing info result: {parsing_info}")

            if not parsing_info:
                return {
                    'status': 'error',
                    'message': f'Application bulunamadı: {company_info["application_id"]}'
                }

            return {
                'status': 'success',
                'company_id': company_info['company_id'],
                'company_name': company_info['company_name'],
                'application_id': company_info['application_id'],
                'parsing_method': parsing_info['parsing_method'],
                'application_name': parsing_info['application_name']
            }

        except Exception as e:
            print(f"Error getting parsing info: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_attributes_for_company(self, company):
        return self.product_repository.get_attributes_for_company(company)

    def create_attribute_values(self, attribute_values):
        return self.product_repository.create_attribute_values(attribute_values)

    def get_all_proxies(self, limit=100):
        return self.product_repository.get_all_proxies()

    def get_company_by_name(self, seller):
        return self.product_repository.get_company_by_name(seller)

    def create_company(self, new_seller, server_id):
        return self.product_repository.create_company(new_seller, server_id)

    def get_pazarama_urls(self):
        return self.product_repository.get_pazarama_urls()

    def save_products_bulk(self, batch_products, batch_images, batch_histories):
        """
        BULK INSERT - Binlerce ürünü tek seferde kaydet
        ÇOK DAHA HIZLI: 1600 ürün ~5 saniyede
        """
        try:
            start_time = time.time()
            saved_count = 0

            # 1. BULK PRODUCT INSERT
            if batch_products:
                self.logger.info(f"💾 Bulk product insert: {len(batch_products)} ürün")

                # Product nesnelerini hazırla
                product_objects = []
                for product_data in batch_products:
                    product = Product(
                        mpn=product_data['mpn'],
                        title=product_data['title'],
                        description=product_data['description'],
                        price=standardize_price(product_data['price']),
                        sale_price=standardize_price(product_data['sale_price']),
                        condition=product_data['condition'],
                        availability=product_data['availability'],
                        brand=product_data['brand'],
                        gtin=product_data['gtin'],
                        link=product_data['link'],
                        product_type=product_data.get('product_type'),
                        product_status=product_data.get('product_status'),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    product_objects.append(product)

                # SQLAlchemy bulk insert
                self.product_repository.db_session.bulk_save_objects(product_objects)
                saved_count = len(product_objects)

                self.logger.info(f"✅ Products bulk insert tamamlandı: {saved_count} ürün")

            # 2. BULK IMAGE INSERT
            if batch_images:
                self.logger.info(f"🖼️ Bulk image insert: {len(batch_images)} resim")

                image_objects = []
                for image_data in batch_images:
                    image = Image(
                        image_url=image_data['url'],
                        mpn=image_data['mpn'],
                    )
                    image_objects.append(image)

                self.image_repository.db_session.bulk_save_objects(image_objects)
                self.logger.info(f"✅ Images bulk insert tamamlandı: {len(image_objects)} resim")

            # 3. BULK HISTORY INSERT
            if batch_histories:
                self.logger.info(f"📚 Bulk history insert: {len(batch_histories)} kayıt")

                history_objects = []
                for history_data in batch_histories:
                    pd = history_data['product_data']
                    history = ProductHistory(
                        mpn=pd['mpn'],
                        title=pd['title'],
                        price=standardize_price(pd['price']),
                        sale_price=standardize_price(pd['sale_price']),
                        availability=pd['availability'],
                        process_id=self.current_process_id,
                        cron_source=history_data['source'],
                        created_at=datetime.now()
                    )
                    history_objects.append(history)

                self.product_history_repository.db_session.bulk_save_objects(history_objects)
                self.logger.info(f"✅ Histories bulk insert tamamlandı: {len(history_objects)} kayıt")

            # 4. TEK SEFERDE COMMIT
            self.product_repository.db_session.commit()

            end_time = time.time()
            total_time = end_time - start_time

            self.logger.info(f"🎉 BULK INSERT BAŞARILI!")
            self.logger.info(f"   - Toplam süre: {total_time:.2f} saniye")
            self.logger.info(f"   - Hız: {saved_count / total_time:.0f} ürün/saniye")

            return saved_count

        except Exception as e:
            self.logger.error(f"💥 Bulk insert hatası: {repr(e)}")
            self.product_repository.db_session.rollback()
            raise e

    def _standardize_price(self, price_str):
        """Fiyat standardizasyonu"""
        if not price_str:
            return None

        try:
            # "1,234.56 TL" -> 1234.56
            clean_price = price_str.replace(',', '').replace(' TL', '').replace('TL', '')
            return float(clean_price)
        except:
            return None

    # ProductService.py dosyasında:

    def delete_all_products_truncate(self):
        """
        SÜPER HIZLI SİLME - TRUNCATE ile
        History korunur, sadece products ve images silinir
        ~1 saniyede tamamlanır
        """
        try:
            self.logger.info("⚡ TRUNCATE ile süper hızlı silme başlıyor...")
            start_time = time.time()

            # TRUNCATE - En hızlı silme yöntemi
            # RESTART IDENTITY - Auto increment'i sıfırlar
            # CASCADE - Foreign key bağımlılıklarını halleder

            self.product_repository.db_session.execute(text("TRUNCATE TABLE images RESTART IDENTITY CASCADE"))
            self.logger.info("🖼️ Images tablosu TRUNCATE edildi")

            self.product_repository.db_session.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE"))
            self.logger.info("📦 Products tablosu TRUNCATE edildi")

            # HISTORY TABLOSU DOKUNULMADı - KORUNDU!
            self.logger.info("📚 Product_histories tablosu korundu (TRUNCATE edilmedi)")

            self.product_repository.db_session.commit()

            end_time = time.time()
            self.logger.info(f"🚀 TRUNCATE tamamlandı: {end_time - start_time:.2f} saniye")

        except Exception as e:
            self.logger.error(f"💥 TRUNCATE hatası: {repr(e)}")
            self.product_repository.db_session.rollback()

            # Fallback: Normal DELETE
            self.logger.info("🔄 TRUNCATE başarısız, normal DELETE deneniyor...")
            try:
                from app.model.Image import Image
                from app.model.Product import Product

                self.product_repository.db_session.query(Image).delete()
                self.product_repository.db_session.query(Product).delete()
                self.product_repository.db_session.commit()

                fallback_end = time.time()
                self.logger.info(f"✅ Fallback DELETE tamamlandı: {fallback_end - start_time:.2f} saniye")

            except Exception as fallback_error:
                self.logger.error(f"💀 Fallback DELETE de başarısız: {repr(fallback_error)}")
                self.product_repository.db_session.rollback()
                raise fallback_error

    def update_web_prices_bulk(self, web_price_batch):
        """
        Web fiyatlarını toplu olarak güncelle
        50 ürün tek seferde ~1 saniye
        """
        try:
            if not web_price_batch:
                return 0

            update_count = 0
            history_objects = []

            for item in web_price_batch:
                product = item['product']
                web_price = item['web_price']

                if web_price:
                    # Product'ı güncelle
                    standardized_price = self._standardize_price(web_price)

                    # Tek tek update yerine bulk update
                    self.product_repository.db_session.execute(
                        text("UPDATE products SET web_price = :price, updated_at = NOW() WHERE id = :id"),
                        {"price": standardized_price, "id": product.id}
                    )

                    # History için hazırla
                    history = ProductHistory(
                        mpn=product.mpn,
                        title=product.title,
                        price=product.price,
                        sale_price=standardize_price(product.sale_price),
                        web_price=standardize_price(web_price),
                        cron_source='web_crawl',
                        process_id=self.current_process_id,
                        created_at=datetime.now()
                    )
                    history_objects.append(history)
                    update_count += 1

            # Bulk history insert
            if history_objects:
                self.product_history_repository.db_session.bulk_save_objects(history_objects)

            # Tek commit
            self.product_repository.db_session.commit()

            return update_count

        except Exception as e:
            self.logger.error(f"💥 Bulk web price update hatası: {repr(e)}")
            self.product_repository.db_session.rollback()
            return 0