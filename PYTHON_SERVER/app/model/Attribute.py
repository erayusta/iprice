from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func


class Attribute(Base):
    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product_attributes = relationship("ProductAttribute", back_populates="attribute", cascade="all, delete-orphan")
    product_attribute_value = relationship("ProductAttributeValue", back_populates="attribute", cascade="all, delete-orphan")
    product_attribute_value_summary = relationship("ProductAttributeValueSummary", back_populates="attribute", cascade="all, delete-orphan")


    """
    is_resale = Column(Boolean, default=False)
    is_display_product = Column(Boolean, default=False)
    shipment_duration = Column(Integer)
    is_sale_price = Column(Integer)
    is_outlet = Column(Boolean, default=False)
    is_education_sale = Column(Boolean, default=False)
    price = Column(Integer)
    sale_price = Column(Integer)
    education_price = Column(Integer)
    """