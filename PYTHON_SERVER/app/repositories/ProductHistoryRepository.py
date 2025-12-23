from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.helper.standardize_price import standardize_price
from app.model.ProductHistory import ProductHistory
from sqlalchemy import func


class ProductHistoryRepository:
    def __init__(self, db_session):
        self.logger = None
        self.db_session = db_session

    def get_last_process_id(self):
        return self.db_session.query(func.max(ProductHistory.process_id)).scalar()

    def add(self, product_history):
        try:
            self.db_session.add(product_history)
            self.db_session.commit()
            self.db_session.refresh(product_history)
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during commit: {error}")
            raise

    def create_product_history_with_merchant_price_object(self, product_data, process_id, merchant_price, cron_source):
        existing_history = self.db_session.query(ProductHistory).filter_by(mpn=product_data.mpn,
                                                                           process_id=process_id).first()

        if existing_history:
            print(
                f"Warning: Product history already exists for product_id {product_data.id} and process_id {process_id}")
            return

        product_history = ProductHistory(
            process_id=process_id,
            mpn=product_data.mpn,
            title=product_data.title,
            description=product_data.description,
            price=standardize_price(product_data.price),
            sale_price=standardize_price(product_data.sale_price),
            merchant_price=standardize_price(merchant_price),
            condition=product_data.condition,
            availability=product_data.availability,
            brand=product_data.brand,
            gtin=product_data.gtin,
            link=product_data.link,
            cron_source=cron_source,
            created_at=func.now()
        )
        self.add(product_history)

    def create_product_history_with_web_price_object(self, product_data, process_id, web_price, cron_source):
        product_history = ProductHistory(
            process_id=process_id,
            mpn=product_data.mpn,
            title=product_data.title,
            description=product_data.description,
            price=standardize_price(product_data.price),
            sale_price=standardize_price(product_data.sale_price),
            web_price=standardize_price(web_price),
            condition=product_data.condition,
            availability=product_data.availability,
            brand=product_data.brand,
            gtin=product_data.gtin,
            link=product_data.link,
            cron_source=cron_source,
            created_at=func.now()
        )
        self.add(product_history)

    def create_product_history(self, product_data, process_id, cron_source):
        product_history = ProductHistory(
            process_id=process_id,
            title=product_data['title'],
            mpn=product_data['mpn'],
            gtin=product_data['gtin'],
            availability=product_data['availability'],
            price=standardize_price(product_data['price']),
            sale_price=standardize_price(product_data['sale_price']),
            condition=product_data['condition'],
            description=product_data['description'],
            brand=product_data['brand'],
            link=product_data['link'],
            product_type=product_data.get('product_type'),
            cron_source=cron_source,
            created_at=func.now()
        )
        self.add(product_history)

    def create_histories_batch(self, histories_data):
        """Birden fazla history kaydını tek seferde ekle - DÜZELTME"""
        history_records = []
        current_time = datetime.now()  # Python datetime kullan

        for data in histories_data:
            product = data['product']
            product_data = data['product_data']

            history = ProductHistory(
                process_id=data['process_id'],
                mpn=product.mpn,
                title=product.title,
                description=product.description,
                price=standardize_price(product_data['price']),
                sale_price=standardize_price(product_data['sale_price']),
                condition=product.condition,
                availability=product.availability,
                brand=product.brand,
                gtin=product.gtin,
                link=product.link,
                product_type=product_data.get('product_type'),
                cron_source=data['source'],
                created_at=current_time  # datetime.now() kullan
            )
            history_records.append(history)

        try:
            self.db_session.bulk_save_objects(history_records)
            self.db_session.commit()
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during batch history insert: {error}")
            raise

    def get_new_process_id(self):
        last_process_id = self.get_last_process_id() or 0
        return last_process_id + 1