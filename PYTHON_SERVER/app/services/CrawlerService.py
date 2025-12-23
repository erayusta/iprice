import logging
import os
import sys
import traceback
from datetime import datetime
import json

import dotenv

# Gerekli path'leri ayarla
sys.path.append('/app')
dotenv.load_dotenv('/app/.env')
server_path = os.getenv('SERVER_PATH')

if server_path and os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from app.database import SessionLocal, engine
from app.models import Base
from app.repositories.ImageRepository import ImageRepository
from app.repositories.ProductHistoryRepository import ProductHistoryRepository
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.repositories.CrawlerLogRepository import CrawlerLogRepository
from app.services.PriceParser import PriceParser
from app.services.XmlParser import XmlParser
from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService
from scrapy.crawler import CrawlerProcess
from scrapy import signals

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/crawler_subprocess.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Crawl işlemini gerçekleştiren ana fonksiyon - BOTH CRAWLERS"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 Crawler subprocess başlatıldı... Zaman: {current_time}")

    db_session = None
    crawler_log_repo = None
    xml_parser_log_id = None
    price_parser_log_id = None

    try:
        # Veritabanı oturumu
        db_session = SessionLocal()
        logger.info("✅ Veritabanı oturumu oluşturuldu")

        # Repository'ler
        repositories = {
            'product': ProductRepository(db_session),
            'product_history': ProductHistoryRepository(db_session),
            'image': ImageRepository(db_session),
            'screenshot': ScreenshotRepository(db_session),
            'crawler_log': CrawlerLogRepository(db_session)
        }
        crawler_log_repo = repositories['crawler_log']
        logger.info("✅ Repository'ler oluşturuldu")

        # Servisler
        product_service = ProductService(
            repositories['product'],
            repositories['product_history'],
            repositories['image']
        )
        screenshot_service = ScreenshotService(repositories['screenshot'])
        logger.info("✅ Servisler oluşturuldu")

        # BOTH CRAWLERS için log kayıtları oluştur
        xml_parser_log = crawler_log_repo.start_crawler('XmlParser')
        xml_parser_log_id = xml_parser_log.id
        logger.info(f"✅ XmlParser log kaydı oluşturuldu. ID: {xml_parser_log_id}")

        price_parser_log = crawler_log_repo.start_crawler('PriceParser')
        price_parser_log_id = price_parser_log.id
        logger.info(f"✅ PriceParser log kaydı oluşturuldu. ID: {price_parser_log_id}")

        # Crawler Process
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'LOG_ENABLED': True,
            'ROBOTSTXT_OBEY': False,
            'COOKIES_ENABLED': True,
            'KEEP_ALIVE': True,
            'LOG_LEVEL': 'INFO',
        })
        logger.info("✅ CrawlerProcess oluşturuldu")

        # CALLBACK FONKSİYONU - HER İKİ CRAWLER İÇİN
        def create_spider_callback(crawler_log_id, crawler_name):
            def spider_closed_callback(spider, reason):
                try:
                    logger.info(f"=== 🕷️ {crawler_name} CLOSED CALLBACK ÇALIŞTI ===")
                    logger.info(f"Spider: {spider.name}, Reason: {reason}")

                    # Scrapy'nin kendi istatistiklerini al
                    stats = spider.crawler.stats.get_stats()
                    logger.info(f"📊 Stats alındı: {len(stats)} item")

                    # Spider'dan temel sayaçları al
                    xml_urls_count = getattr(spider, 'xml_urls_count', 0)
                    product_urls_count = getattr(spider, 'product_urls_count', 0)
                    total_urls_visited = getattr(spider, 'total_urls_visited', 0)
                    processed_products_count = getattr(spider, 'processed_products_count', 0)

                    # ← YENİ: Spider'dan detaylı stats'i al
                    url_statuses = getattr(spider, 'url_statuses', [])
                    companies_processed = getattr(spider, 'companies_processed', set())
                    status_404_count = getattr(spider, 'status_404_count', 0)

                    # ← YENİ: Status summary ve error details hesapla
                    status_summary = {}
                    error_details = []

                    for url_status in url_statuses:
                        status_code = str(url_status['status'])
                        if status_code not in status_summary:
                            status_summary[status_code] = 0
                        status_summary[status_code] += 1

                        if url_status['status'] != 200:
                            error_details.append(url_status)

                    # Temel crawler stats
                    crawler_stats = {
                        'processed': stats.get('response_received_count', 0),
                        'updated': product_urls_count,
                        'created': processed_products_count,
                        'downloader/request_count': stats.get('downloader/request_count', 0),
                        'downloader/response_count': stats.get('downloader/response_count', 0),
                        'downloader/response_status_count/200': stats.get('downloader/response_status_count/200', 0),
                        'downloader/response_status_count/404': stats.get('downloader/response_status_count/404', 0),
                        'downloader/exception_count': stats.get('downloader/exception_count', 0),
                        'log_count/ERROR': stats.get('log_count/ERROR', 0),
                        'log_count/WARNING': stats.get('log_count/WARNING', 0),
                        'log_count/INFO': stats.get('log_count/INFO', 0),
                        'elapsed_time_seconds': stats.get('elapsed_time_seconds', 0),

                        # CUSTOM URL STATİSTİKLERİ
                        'custom/xml_urls_count': xml_urls_count,
                        'custom/product_urls_count': product_urls_count,
                        'custom/total_urls_visited': total_urls_visited,
                        'custom/processed_products_count': processed_products_count,

                        # ← YENİ: Detaylı stats
                        'custom/companies_processed': len(companies_processed),
                        'custom/url_status_summary': status_summary,
                        'custom/error_details': error_details,
                        'custom/total_errors': len(error_details),
                        'custom/status_404_count': status_404_count,
                    }

                    # ← YENİ: Debug bilgileri
                    logger.info(f"🔍 CALLBACK DEBUG:")
                    logger.info(f"   - url_statuses boyutu: {len(url_statuses)}")
                    logger.info(f"   - error_details boyutu: {len(error_details)}")
                    logger.info(f"   - status_summary: {status_summary}")
                    logger.info(f"   - companies_processed: {len(companies_processed)}")

                    # Mevcut istatistik logları...
                    logger.info(f"===== 📈 {crawler_name} İSTATİSTİKLERİ =====")
                    logger.info(f"🌐 URL İstatistikleri:")
                    logger.info(f"   - XML URL'leri: {xml_urls_count}")
                    logger.info(f"   - Ürün URL'leri: {product_urls_count}")
                    logger.info(f"   - Toplam ziyaret edilen URL: {total_urls_visited}")
                    logger.info(f"📦 Ürün İstatistikleri:")
                    logger.info(f"   - İşlenen ürün sayısı: {processed_products_count}")
                    logger.info(f"   - Fiyat güncellenen ürün: {product_urls_count}")
                    logger.info(f"🔧 Scrapy İstatistikleri:")
                    logger.info(f"   - Toplam istek: {crawler_stats['downloader/request_count']}")
                    logger.info(f"   - Toplam yanıt: {crawler_stats['downloader/response_count']}")
                    logger.info(f"   - Başarılı (200): {crawler_stats['downloader/response_status_count/200']}")
                    logger.info(f"   - Hata (404): {crawler_stats['downloader/response_status_count/404']}")
                    logger.info(f"⏱️ Süre: {crawler_stats['elapsed_time_seconds']} saniye")
                    logger.info(f"================================")

                    # Veritabanına kaydet
                    if reason == 'finished':
                        stats_json = json.dumps(crawler_stats, indent=2)

                        logger.info(f"💾 {crawler_name} DB güncelleniyor. ID: {crawler_log_id}")
                        logger.info(f"📊 Stats JSON boyutu: {len(stats_json)} karakter")

                        result = crawler_log_repo.complete_crawler(crawler_log_id, {
                            'processed': crawler_stats['downloader/response_count'],
                            'updated': product_urls_count,
                            'created': processed_products_count,
                            'stats_json': stats_json
                        })

                        if result:
                            logger.info(f"✅ {crawler_name} DB başarıyla güncellendi (COMPLETED)")
                        else:
                            logger.error(f"❌ {crawler_name} DB güncelleme başarısız!")

                    else:
                        logger.info(f"❌ {crawler_name} failed ile güncelleniyor. Reason: {reason}")
                        result = crawler_log_repo.fail_crawler(crawler_log_id, f"Spider kapatıldı: {reason}")

                        if result:
                            logger.info(f"✅ {crawler_name} DB başarıyla güncellendi (FAILED)")
                        else:
                            logger.error(f"❌ {crawler_name} DB güncelleme başarısız!")

                except Exception as e:
                    logger.error(f"💥 {crawler_name} Callback hatası: {repr(e)}")
                    logger.error(f"📋 Traceback: {traceback.format_exc()}")

                    # Hata durumunda da DB'yi güncellemeye çalış
                    try:
                        crawler_log_repo.fail_crawler(crawler_log_id, f"Callback error: {str(e)}")
                        logger.info(f"⚠️ {crawler_name} hata durumunda DB güncellendi")
                    except:
                        logger.error(f"💀 {crawler_name} DB güncelleme de başarısız!")

            return spider_closed_callback

        # XmlParser crawler'ını ekle
        logger.info("🔧 XmlParser ekleniyor...")
        process.crawl(
            XmlParser,
            product_service=product_service,
            screenshot_service=screenshot_service,
            crawler_log_id=xml_parser_log_id,
            crawler_log_repo=crawler_log_repo
        )
        logger.info("✅ XmlParser crawler'ı eklendi")

        # PriceParser crawler'ını ekle
        logger.info("🔧 PriceParser ekleniyor...")
        process.crawl(
            PriceParser,
            product_service=product_service,
            screenshot_service=screenshot_service,
            crawler_log_id=price_parser_log_id,
            crawler_log_repo=crawler_log_repo
        )
        logger.info("✅ PriceParser crawler'ı eklendi")

        # Callback'leri bağla
        logger.info("🔗 Callback'ler bağlanıyor...")
        callback_connected_count = 0

        for crawler in process.crawlers:
            if crawler.spidercls == XmlParser:
                xml_callback = create_spider_callback(xml_parser_log_id, "XmlParser")
                crawler.signals.connect(xml_callback, signal=signals.spider_closed)
                callback_connected_count += 1
                logger.info("✅ XmlParser Callback başarıyla bağlandı")

            elif crawler.spidercls == PriceParser:
                price_callback = create_spider_callback(price_parser_log_id, "PriceParser")
                crawler.signals.connect(price_callback, signal=signals.spider_closed)
                callback_connected_count += 1
                logger.info("✅ PriceParser Callback başarıyla bağlandı (detaylı stats ile)")

        logger.info(f"📊 Toplam {callback_connected_count}/2 callback bağlandı")

        if callback_connected_count != 2:
            logger.warning("⚠️ Tüm callback'ler bağlanamadı! Spider'ların kendi closed() metodları kullanılacak")

        # Process'i başlat
        logger.info("🚀 Process başlatılıyor (2 crawler birlikte)...")
        process.start(stop_after_crawl=True)
        logger.info("🎉 Process başarıyla tamamlandı")

    except Exception as e:
        logger.error(f"💥 Process hatası: {repr(e)}")
        logger.error(f"📋 Process hata detayları: {traceback.format_exc()}")

        # Hata durumunda BOTH log kayıtlarını güncelle
        if crawler_log_repo:
            if xml_parser_log_id:
                try:
                    crawler_log_repo.fail_crawler(xml_parser_log_id, str(e))
                    logger.info("⚠️ XmlParser hata durumunda güncellendi")
                except Exception as db_error:
                    logger.error(f"💀 XmlParser DB güncelleme başarısız: {repr(db_error)}")

            if price_parser_log_id:
                try:
                    crawler_log_repo.fail_crawler(price_parser_log_id, str(e))
                    logger.info("⚠️ PriceParser hata durumunda güncellendi")
                except Exception as db_error:
                    logger.error(f"💀 PriceParser DB güncelleme başarısız: {repr(db_error)}")

    finally:
        if db_session:
            try:
                db_session.close()
                logger.info("✅ Veritabanı oturumu kapatıldı")
            except Exception as close_error:
                logger.error(f"⚠️ DB oturum kapatma hatası: {repr(close_error)}")


if __name__ == "__main__":
    main()