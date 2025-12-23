from celery import Celery
from celery.schedules import crontab
import os
import logging
# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/app/logs/proxy_fetcher.log"),
        logging.StreamHandler()
    ]
)

# Redis bağlantı bilgileri (environment variables üzerinden alınıyor)
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Celery uygulaması oluştur
celery = Celery(
    'app.celery_worker',  # Doğru namespace
    broker=broker_url,
    backend=result_backend
)

celery.conf.update(
    timezone='Europe/Istanbul',
    enable_utc=True,
    imports=['app.tasks.summary_tasks', 'app.tasks.stock_sync']
)

celery.conf.beat_schedule = {
    'product-attribute-value-history-5-minutes': {
        'task': 'app.tasks.summary_tasks.generate_summary',
        'schedule': 300.0,
        'options': {'queue': 'summary'}
    },
    'sync-woocommerce-products-twice-daily': {
        'task': 'app.tasks.stock_sync.sync_woocommerce_products',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'stock_sync'}
    }
}

# PostgreSQL bağlantı bilgileri (environment variables kullanılabilir)
DB_CONFIG = dict(

    host=os.environ.get('POSTGRES_HOST', '10.20.50.16'),
    port=os.environ.get('POSTGRES_PORT', 5432),
    user=os.environ.get('SHARED_DB_USER', 'ipricetestuser'),
    password=os.environ.get('SHARED_DB_PASS', 'YeniSifre123!'),
    dbname=os.environ.get('SHARED_DB_NAME', 'ipricetest')
)

# API URL
PROXY_API_BASE_URL = 'https://proxylist.geonode.com/api/proxy-list'
LIMIT_PER_PAGE = 500