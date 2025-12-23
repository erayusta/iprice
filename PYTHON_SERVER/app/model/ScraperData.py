from app.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func


class ScraperData(Base):
    __tablename__ = 'scraper_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_id = Column(String, index=True)
    job_id = Column(Integer, nullable=True, index=True)
    data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

