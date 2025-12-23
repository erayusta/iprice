from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func


class ProductAttributeValue(Base):
    __tablename__ = 'product_attribute_value'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, index=True)  # 🔥 Job ID eklendi
    product_id = Column(Integer, index=True)  # 🔥 Product ID eklendi
    company_id = Column(Integer, ForeignKey('company.id'))
    attribute_id = Column(Integer, ForeignKey('attribute.id'))
    mpn = Column(String, index=True)
    value = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="product_attribute_value")
    attribute = relationship("Attribute", back_populates="product_attribute_value")