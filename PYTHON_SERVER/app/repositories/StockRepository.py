from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.model.Stock import Stock


class StockRepository:
    def __init__(self, db_session):
        self.db_session = db_session
        self.logger = None

    def add(self, stock):
        try:
            self.db_session.add(stock)
            self.db_session.commit()
            self.db_session.refresh(stock)
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during commit: {error}")
            raise

    def create_stock_data(self, stock_products: Dict[str, Dict[str, Any]]) -> int:
        updated_or_created_count = 0
        try:
            for mpn, data in stock_products.items():
                existing_record = self.db_session.query(Stock).filter_by(mpn=mpn).first()

                quantity = data['stock_quantity']
                if quantity is None:
                    quantity = 0

                status = 'in stocks' if quantity > 0 else 'out of stocks'

                if existing_record:
                    if existing_record.quantity != quantity or existing_record.status != status:
                        self.update_stock(existing_record, quantity, status)
                        updated_or_created_count += 1
                else:
                    new_record = Stock(
                        mpn=mpn,
                        product_name=data['name'],
                        quantity=quantity,
                        status=status
                    )
                    self.db_session.add(new_record)
                    updated_or_created_count += 1

            self.db_session.commit()
            print(f"Successfully committed changes. {updated_or_created_count} products were updated or created.")

            return updated_or_created_count

        except Exception as e:
            self.db_session.rollback()
            print(f"Error saving stock data: {str(e)}")
            raise

    def update_stock(self, stock, new_stock, status):
        try:
            stock.quantity = new_stock
            stock.status = status
        except Exception as e:
            self.logger.warning(f"Error updating stock: {e}")
            raise