import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.model.JobLog import JobLog


class JobLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_status(self, job_log_id: int, status: str):
        job = self.db.query(JobLog).filter(JobLog.id == job_log_id).first()
        if job:
            job.status = status
            self.db.commit()

    def update_on_finish(self, job_log_id: int, status: str, url_count, message: str):
        try:
            job = self.db.query(JobLog).filter(JobLog.id == job_log_id).first()
            if job:
                job.status = status

                # JSON string olarak kaydet
                if isinstance(url_count, dict):
                    job.total_urls = json.dumps(url_count)
                elif isinstance(url_count, (int, float)):
                    # Sadece sayı gelirse basit format
                    job.total_urls = json.dumps({"processed_count": int(url_count)})
                else:
                    job.total_urls = json.dumps({"processed_count": 0})

                job.message = message
                job.finished_at = datetime.now()

                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e