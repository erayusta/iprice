"""
Proxy Database Model
====================
Veritabanındaki proxies tablosu için SQLAlchemy modeli.

Özellikler:
- Multi-protocol desteği (HTTP, HTTPS, SOCKS4, SOCKS5)
- Performans metrikleri (response_time, latency, working_percent)
- Akıllı durum yönetimi (is_active, failure_count)
- Coğrafi bilgiler (country, city, region)
"""

from app.database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func


class Proxy(Base):
    """Proxy Model - Her proxy kaydı için veritabanı şeması"""
    
    __tablename__ = 'proxies'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Proxy Identifier (External ID from source)
    proxy_id = Column(String, unique=True, index=True, nullable=True)
    
    # Connection Info
    ip = Column(String, nullable=False, index=True)
    port = Column(Integer, nullable=False)
    
    # Geographic Info
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    
    # Technical Details
    anonymity_level = Column(String, nullable=True)  # elite, anonymous, transparent
    isp = Column(String, nullable=True)
    asn = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    
    # Performance Metrics
    speed = Column(Integer, nullable=True)
    latency = Column(Float, nullable=True)  # ms
    response_time = Column(Float, nullable=True)  # ms
    
    # Protocol Support
    protocols = Column(JSON, nullable=True)  # ["http", "https", "socks4", "socks5"]
    
    # Health & Status
    working_percent = Column(Float, default=100.0)  # Başarı yüzdesi
    up_time = Column(Float, nullable=True)  # Uptime percentage
    up_time_success_count = Column(Integer, default=0)
    up_time_try_count = Column(Integer, default=0)
    
    # ✅ YENİ ALANLAR - Akıllı Proxy Yönetimi
    is_active = Column(Boolean, default=True, index=True)  # Kullanıma uygun mu?
    failure_count = Column(Integer, default=0)  # Kaç kez başarısız oldu?
    last_used_at = Column(DateTime(timezone=True), nullable=True)  # Son kullanım zamanı
    
    # Timestamps
    last_checked = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        """String representation"""
        return f"<Proxy(ip={self.ip}:{self.port}, country={self.country}, active={self.is_active})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'proxy_id': self.proxy_id,
            'ip': self.ip,
            'port': self.port,
            'country': self.country,
            'city': self.city,
            'protocols': self.protocols,
            'anonymity_level': self.anonymity_level,
            'working_percent': self.working_percent,
            'response_time': self.response_time,
            'is_active': self.is_active,
            'failure_count': self.failure_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_url(self, protocol='http'):
        """Proxy URL formatını döndür"""
        return f"{protocol}://{self.ip}:{self.port}"
    
    def supports_protocol(self, protocol):
        """Belirli bir protokolü destekliyor mu?"""
        if not self.protocols:
            return False
        return protocol.lower() in [p.lower() for p in self.protocols]

