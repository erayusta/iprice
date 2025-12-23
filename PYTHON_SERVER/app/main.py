import logging
import os
import sys
import time
import subprocess
import schedule
from datetime import datetime

import dotenv

dotenv.load_dotenv('../.env')
server_path = os.getenv('SERVER_PATH')
server = os.getenv('SERVER')

if os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/crawler.log')
    ]
)
logger = logging.getLogger(__name__)


def run_crawler():
    """Crawler işlemini ayrı bir process'te çalıştıran fonksiyon"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Crawler başlatılıyor... Zaman: {current_time}")

    try:
        # Crawler'ı ayrı bir process olarak çalıştır
        result = subprocess.run(
            [sys.executable, "/app/app/services/CrawlerService.py"],
            check=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            logger.info(f"Crawler çıktısı: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Crawler hata çıktısı: {result.stderr.strip()}")

        logger.info(f"Crawler tamamlandı. Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Crawler subprocess hatası: {str(e)}")
        if e.stderr:
            logger.error(f"Subprocess hata çıktısı: {e.stderr}")
    except Exception as e:
        logger.error(f"Crawler çalıştırma sırasında hata: {str(e)}")
        import traceback
        logger.error(f"Hata detayları: {traceback.format_exc()}")


def main():
    """Ana program - scheduler'ı başlatır ve çalışır durumda tutar"""
    logger.info("Crawler scheduler başlatıldı - konteyner çalışır durumda kalacak")

    # Crawler'ı her gün 3 kez çalıştıracak şekilde zamanla
    schedule.every().day.at("06:00").do(run_crawler)
    schedule.every().day.at("14:00").do(run_crawler)
    schedule.every().day.at("22:00").do(run_crawler)

    # Başlangıçta bir kez çalıştır
    logger.info("Başlangıç crawler işi çalıştırılıyor")
    run_crawler()

    # Scripti sürekli çalışır durumda tut
    logger.info("Scheduler aktif ve bir sonraki planlanmış çalışma için bekliyor")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Her dakika kontrol et


if __name__ == "__main__":
    main()