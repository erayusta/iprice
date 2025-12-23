# app/model/Server.py
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    environment = Column(String)
    status = Column(Boolean, default=False)
    default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Company ilişkisini kaldırdık
    # company = relationship("Company", back_populates="servers")