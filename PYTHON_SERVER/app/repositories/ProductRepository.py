from __future__ import annotations

import logging
import os
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.helper.standardize_price import standardize_price
from app.model import Company, Attribute
from app.model.Application import Application
from app.model.Image import Image
from app.model.Product import Product
from app.model.ProductAttribute import ProductAttribute
from app.model.ProductAttributeValue import ProductAttributeValue
from app.model.ProductURL import ProductURL
from app.model.Server import Server

server_name = os.getenv('SERVER')


class ProductRepository:
    def __init__(self, db_session):
        self.logger = logging.getLogger(__name__)
        self.server_name = server_name
        self.db_session = db_session

    def get_all(self):
        return self.db_session.query(Product).all()

    def find_by_mpn(self, mpn):
        return self.db_session.query(Product).filter_by(mpn=mpn).first()

    def add(self, product):
        try:
            self.db_session.add(product)
            self.db_session.commit()
            self.db_session.refresh(product)
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during commit: {error}")
            raise

    def create_product(self, product_data):
        new_product = Product(
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
        )

        self.add(new_product)

        return new_product

    def update_product_web_price(self, product, web_price):
        try:
            product.web_price = web_price
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error updating product with web_price: {e}")

    def update_product_merchant_price(self, product, merchant_price):
        try:
            product.merchant_price = merchant_price
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            self.logger.error(f"Error updating product with web_price: {e}")

    def delete_all_products(self):
        try:
            self.db_session.query(Image).delete()
            self.db_session.query(Product).delete()
            self.db_session.commit()  # Need to commit here
        except Exception as e:
            self.db_session.rollback()  # Need to rollback on error
            raise e

    # application_id = 5 => scrapy
    def get_companies_with_urls_by_server(self):
        return self.db_session.query(Company, ProductURL, Server) \
            .join(ProductURL, Company.id == ProductURL.company_id) \
            .join(Server, Company.server_id == Server.id) \
            .filter(Server.environment == self.server_name) \
            .filter(Company.is_marketplace == False) \
            .filter(Company.application_id == 5)  \
            .all()

    def get_products_with_urls_by_company_id(self, company_id):
        return self.db_session.query(ProductURL) \
            .join(Company) \
            .filter(ProductURL.company_id == company_id) \
            .all()

    def get_company_with_application(self, company_id: int):
        try:
            result = self.db_session.query(Company).filter(
                Company.id == company_id
            ).first()

            if result:
                return {
                    'company_id': result.id,
                    'company_name': result.name,
                    'application_id': result.application_id
                }
            return None

        except Exception as e:
            self.logger.error(f"Error querying company: {e}")
            return None

    def get_application_parsing_method(self, application_id: int):
        """
        Application tablosundan parsing method'u getir
        """
        try:
            result = self.db_session.query(Application).filter(
                Application.id == application_id
            ).first()

            if result:
                return {
                    'application_id': result.id,
                    'application_name': result.name,
                    'parsing_method': result.name  # name field'ında "scrapy" veya "selenium"
                }
            return None

        except Exception as e:
            self.logger.error(f"Error querying application: {e}")
            return None

    def get_attributes_for_company(self, company):
        attributes = self.db_session.query(
            ProductAttribute,
            Company.name.label('company_name'),
            Attribute.name.label('attribute_name'),
            Company.is_marketplace.label('is_marketplace'),
        ) \
            .join(Company) \
            .join(Attribute, ProductAttribute.attribute_id == Attribute.id) \
            .filter(Company.name == company) \
            .all()

        return [{
            'id': attr.ProductAttribute.id,
            'attribute_id': attr.ProductAttribute.attribute_id,
            'attribute_name': attr.attribute_name,
            'xpath': attr.ProductAttribute.xpath,
            'company_id': attr.ProductAttribute.company_id,
            'company_name': attr.company_name,
            'selector_type': attr.ProductAttribute.selector_type,
            'is_marketplace': attr.is_marketplace,
        } for attr in attributes]

    def get_company_by_name(self, company_name):
        return self.db_session.query(Company).filter(Company.name == company_name).first()

    def create_company(self, company_data, server_id):
        company = Company(
            name=company_data['name'],
            is_marketplace=company_data['is_marketplace'],
            server_id=server_id,
            logo=company_data['logo'],
            is_screenshot=company_data['is_screenshot'],
            marketplace_id=company_data['marketplace_id']
        )
        self.db_session.add(company)
        self.db_session.commit()
        return company

    def create_attribute_values(self, attribute_values):
        value_records = []

        # 1. AŞAMA: Önceki kodunuzla aynı, tüm veriler hafızada hazırlanıyor.
        for data in attribute_values:
            if data['attribute_name'] == 'is_price':
                value = standardize_price(data['value'])
            else:
                value = data['value']

            value_records.append(
                ProductAttributeValue(
                    company_id=data['company_id'],
                    attribute_id=data['attribute_id'],
                    mpn=data['mpn'],
                    value=value
                )
            )

        # 2. AŞAMA: Hazırlanan verileri parçalara bölerek veritabanına kaydet.
        BATCH_SIZE = 100  # Her seferinde 100 kayıt işlenecek.
        total_records = len(value_records)

        print(f"Toplam {total_records} adet kayıt veritabanına işlenecek...")

        try:
            # Hafızadaki listeyi 100'lük gruplara ayırarak işle
            for i in range(0, total_records, BATCH_SIZE):
                batch = value_records[i:i + BATCH_SIZE]

                # Sadece o 100'lük grubu veritabanına gönder
                self.db_session.bulk_save_objects(batch)

                print(f"  -> İşlendi: {i + len(batch)} / {total_records}")

            # Tüm parçalar başarıyla kaydedildikten sonra işlemi onayla
            self.db_session.commit()
            print("Veritabanı kayıt işlemi başarıyla tamamlandı.")

        except Exception as e:
            print(f"HATA: Kayıt sırasında bir sorun oluştu: {e}")
            self.db_session.rollback()  # Hata olursa tüm işlemleri geri al
            raise

    def get_all_proxies(self, limit=100):
        query = text("""
            SELECT ip, port, protocols
            FROM proxies
            WHERE protocols @> '["http"]'
            ORDER BY up_time DESC, response_time ASC
            LIMIT :limit
            """)

        return self.db_session.execute(query, {"limit": limit}).fetchall()

    # ProductRepository sınıfına şu metodları ekleyin:

    def create_products_batch(self, products_data_list):
        """Birden fazla ürünü tek seferde kaydet"""
        new_products = []

        for product_data in products_data_list:
            new_product = Product(
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
            )
            new_products.append(new_product)

        try:
            # Bulk insert - çok daha hızlı
            self.db_session.bulk_save_objects(new_products, return_defaults=True)
            self.db_session.commit()

            # ID'leri almak için yeniden sorgula
            mpn_list = [p['mpn'] for p in products_data_list]
            saved_products = self.db_session.query(Product).filter(Product.mpn.in_(mpn_list)).all()

            return saved_products
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during batch insert: {error}")
            raise

    def delete_all_products(self):
        """Tüm ürünleri daha hızlı sil"""
        try:
            # Önce bağlı tabloları temizle
            self.db_session.query(Image).delete()
            # TRUNCATE kullan (daha hızlı)
            self.db_session.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE"))
            self.db_session.commit()
        except Exception as e:
            # TRUNCATE başarısız olursa normal DELETE kullan
            try:
                self.db_session.rollback()
                self.db_session.query(Product).delete()
                self.db_session.commit()
            except Exception as ex:
                self.db_session.rollback()
                raise ex

    # ProductRepository.py içine eklenecek 1. yeni metod

    def get_scrape_targets_by_company_id(self, company_id: int):
        """
        Bir şirkete ait tüm kazıma hedeflerini (attribute ve xpath) veritabanından çeker.
        Bu metod, HepsiburadaSeleniumService'in _load_scrape_configuration'ının yerine geçer.
        """
        self.logger.info(f"Repository: company_id={company_id} için kazıma hedefleri sorgulanıyor...")

        query = text("""
            SELECT
                a.id AS attribute_id,
                a.name AS attribute_name,
                pa.xpath
            FROM product_attribute pa
            JOIN attribute a ON pa.attribute_id = a.id
            WHERE pa.company_id = :company_id
        """)
        try:
            results = self.db_session.execute(query, {'company_id': company_id}).fetchall()
            return [
                {'id': row.attribute_id, 'name': row.attribute_name, 'xpath': row.xpath}
                for row in results
            ]
        except Exception as e:
            self.logger.error(f"💥 Kazıma hedefleri sorgulanırken hata: {e}")
            return []

    # ProductRepository.py içine eklenecek 2. yeni metod

    def create_attribute_value(self, company_id: int, attribute_id: int, mpn: str, value: str):
        """
        ProductAttributeValue tablosuna tek bir yeni kayıt ekler.
        Bu metod, ProductAttributeValueManager'ın yerine geçer.
        """
        try:
            new_value = ProductAttributeValue(
                company_id=company_id,
                attribute_id=attribute_id,
                mpn=mpn,
                value=value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db_session.add(new_value)
            self.db_session.commit()
        except Exception as e:
            self.logger.error(f"❌ Yeni attribute değeri kaydetme hatası: {e}")
            self.db_session.rollback()
            # Hatanın yukarıya bildirilmesi önemli olabilir
            raise e


    # YENİ METOT: Satıcıyı isme ve pazaryerine göre arar
    def get_seller_by_name_and_marketplace(self, seller_name: str, marketplace_id: int) -> Company | None:
        """
        Bir satıcıyı (company) ismine ve ait olduğu marketplace_id'ye göre arar.
        Bu, farklı pazaryerlerindeki aynı isimli satıcıları ayırt etmeyi sağlar.
        """
        return self.db_session.query(Company).filter_by(
            name=seller_name,
            marketplace_id=marketplace_id
        ).first()