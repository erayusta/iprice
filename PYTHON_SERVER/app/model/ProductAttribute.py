from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func


class ProductAttribute(Base):
    __tablename__ = 'product_attribute'

    id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    xpath = Column(Integer, nullable=False)
    selector_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="product_attributes")
    attribute = relationship("Attribute", back_populates="product_attributes")