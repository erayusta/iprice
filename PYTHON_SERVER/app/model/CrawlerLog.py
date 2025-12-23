from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from app.database import Base
import enum


class CrawlerStatus(enum.Enum):
    started = "started"
    completed = "completed"
    failed = "failed"


class CrawlerLog(Base):
    __tablename__ = "crawler_logs"

    id = Column(Integer, primary_key=True, index=True)
    crawler_name = Column(String(50), nullable=False)
    status = Column(Enum(CrawlerStatus), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    total_products_processed = Column(Integer, default=0)
    total_products_updated = Column(Integer, default=0)
    total_products_created = Column(Integer, default=0)
    execution_time_seconds = Column(Integer, nullable=True)
    stats_json = Column(Text, nullable=True)