from sqlalchemy.exc import SQLAlchemyError

from app.model.Screenshot import Screenshot


class ScreenshotRepository:
    def __init__(self, db_session):
        self.db_session = db_session
        self.logger = None

    def add(self, screenshot):
        try:
            self.db_session.add(screenshot)
            self.db_session.commit()
            self.db_session.refresh(screenshot)
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during commit: {error}")
            raise

    def create_screenshot(self, product, screenshot, company_id):
        new_record = Screenshot(
            mpn=product.mpn,
            company_id=company_id,
            url=product.link,
            image_name=screenshot,
        )
        self.add(new_record)

    def create_screenshot_price_parser(self, mpn, screenshot, company_id, link):
        new_record = Screenshot(
            mpn=mpn,
            company_id=company_id,
            url=link,
            image_name=screenshot,
        )

        self.add(new_record)
