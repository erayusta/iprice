from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func


class ProductURL(Base):
    __tablename__ = 'product_url'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    url = Column(String, nullable=False)
    mpn = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="product_urls")