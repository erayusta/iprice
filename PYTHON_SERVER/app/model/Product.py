from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    mpn = Column(String, index=True)
    gtin = Column(String, index=True)
    availability = Column(String, index=True)
    price = Column(String, index=True)
    sale_price = Column(String, index=True)
    web_price = Column(String, index=True)
    merchant_price = Column(String, index=True)
    condition = Column(String)
    description = Column(String)
    brand = Column(String)
    link = Column(String)
    product_type = Column(String)
    product_status = Column(String)
    is_hero = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())