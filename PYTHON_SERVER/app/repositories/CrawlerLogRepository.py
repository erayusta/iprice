# app/repositories/CrawlerLogRepository.py
from datetime import datetime
from app.model.CrawlerLog import CrawlerLog, CrawlerStatus


class CrawlerLogRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get(self, crawler_log_id):
        """ID'ye göre crawler log kaydını getir"""
        return self.db_session.query(CrawlerLog).filter(CrawlerLog.id == crawler_log_id).first()

    def start_crawler(self, crawler_name):
        """Crawler başladığında log kaydı oluştur"""
        crawler_log = CrawlerLog(
            crawler_name=crawler_name,
            status=CrawlerStatus.started,
            started_at=datetime.now()
        )
        self.db_session.add(crawler_log)
        self.db_session.commit()
        self.db_session.refresh(crawler_log)
        return crawler_log

    def complete_crawler(self, crawler_log_id, stats):
        """Crawler tamamlandığında log kaydını güncelle"""
        crawler_log = self.db_session.query(CrawlerLog).filter(CrawlerLog.id == crawler_log_id).first()

        if crawler_log:
            crawler_log.status = CrawlerStatus.completed
            crawler_log.completed_at = datetime.now()
            crawler_log.total_products_processed = stats.get('processed', 0)
            crawler_log.total_products_updated = stats.get('updated', 0)
            crawler_log.total_products_created = stats.get('created', 0)

            # İstatistikleri JSON olarak sakla
            if 'stats_json' in stats:
                crawler_log.stats_json = stats['stats_json']

            # Çalışma süresini hesapla
            if crawler_log.started_at:
                execution_time = (crawler_log.completed_at - crawler_log.started_at).total_seconds()
                crawler_log.execution_time_seconds = int(execution_time)

            self.db_session.commit()
            self.db_session.refresh(crawler_log)
        return crawler_log

    def fail_crawler(self, crawler_log_id, error_message):
        """Crawler başarısız olduğunda log kaydını güncelle"""
        crawler_log = self.db_session.query(CrawlerLog).filter(CrawlerLog.id == crawler_log_id).first()

        if crawler_log:
            crawler_log.status = CrawlerStatus.failed
            crawler_log.completed_at = datetime.now()
            crawler_log.error_message = error_message

            # Çalışma süresini hesapla
            if crawler_log.started_at:
                execution_time = (crawler_log.completed_at - crawler_log.started_at).total_seconds()
                crawler_log.execution_time_seconds = int(execution_time)

            self.db_session.commit()
            self.db_session.refresh(crawler_log)
        return crawler_log