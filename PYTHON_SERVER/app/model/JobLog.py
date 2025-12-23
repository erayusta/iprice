from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.database import Base

class JobLog(Base):
    __tablename__ = 'job_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    company_id = Column(Integer)
    status = Column(Enum('pending', 'running', 'success', 'failed', name='job_status_enum'), default='pending')
    total_urls = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)