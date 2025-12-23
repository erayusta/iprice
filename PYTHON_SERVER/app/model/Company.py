# app/model/Company.py
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_marketplace = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    logo = Column(String)
    is_screenshot = Column(Boolean, default=False)
    marketplace_id = Column(Integer, ForeignKey('company.id'), nullable=True)
    server_id = Column(Integer)  # Şimdilik foreign key kaldırıldı
    application_id = Column(Integer, ForeignKey('application.id'), nullable=True)  # Bu satır var mı?


    # Self-referential relationship
    marketplace = relationship("Company",
                               foreign_keys=marketplace_id,  # Liste yerine direkt sütun
                               remote_side=[id],
                               backref="sellers")

    # Diğer ilişkiler
    product_urls = relationship("ProductURL", back_populates="company", cascade="all, delete-orphan")
    product_attributes = relationship("ProductAttribute", back_populates="company", cascade="all, delete-orphan")
    product_attribute_value = relationship("ProductAttributeValue", back_populates="company",
                                           cascade="all, delete-orphan")
    product_attribute_value_summary = relationship("ProductAttributeValueSummary", back_populates="company",
                                                   cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="company", cascade="all, delete-orphan")
    #application = relationship("Application", back_populates="company", cascade="all, delete-orphan")

    # Server ilişkisini kaldırdık
    # servers = relationship("Server", back_populates="company", cascade="all, delete-orphan")