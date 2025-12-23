from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func


class Application(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #company = relationship("Company", back_populates="application")