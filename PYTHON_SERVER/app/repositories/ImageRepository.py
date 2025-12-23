from sqlalchemy.exc import SQLAlchemyError

from app.model.Image import Image

class ImageRepository:
    def __init__(self, db_session):
        self.logger = None
        self.db_session = db_session

    def create_image(self, image_url, mpn):
        image = Image(
            image_url=image_url,
            mpn=mpn,
        )

        return image

    def add_image(self, image):
        try:
            self.db_session.add(image)
            self.db_session.commit()
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during commit: {error}")
            raise

    def get_image_by_mpn(self, mpn):
        return self.db_session.query(Image).filter_by(mpn=mpn).all()

    def add_images_batch(self, images):
        """Birden fazla resmi tek bir transaction içinde ekler"""
        try:
            self.db_session.add_all(images)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise e

    def create_images_batch(self, images_data):
        """Birden fazla image kaydını tek seferde oluştur ve ekle"""
        image_records = []

        for data in images_data:
            image = Image(
                image_url=data['url'],
                mpn=data['mpn']
            )
            image_records.append(image)

        try:
            self.db_session.bulk_save_objects(image_records)
            self.db_session.commit()
        except SQLAlchemyError as error:
            self.db_session.rollback()
            print(f"Error during batch image insert: {error}")
            raise