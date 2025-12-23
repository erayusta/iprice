from sqlalchemy import Column, Integer, String
from app.database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mpn = Column(String, index=True)
    image_url = Column(String)
