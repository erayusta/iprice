from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, func
from sqlalchemy.sql import func
from app.database import Base

class ProductHistory(Base):
    __tablename__ = 'products_history'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, nullable=False)
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
    cron_source = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)