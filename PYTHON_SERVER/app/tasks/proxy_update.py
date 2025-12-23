"""
Proxy Update Task
=================
6 saatte bir otomatik proxy listesi güncelleme task'ı.

Kaynaklar:
- ProxyScrape API (HTTP, SOCKS4, SOCKS5)
- GeoNode API (detaylı metadata ile)
- GitHub TheSpeedX/SOCKS-List (HTTP, SOCKS4, SOCKS5)

Kullanım:
- Celery beat ile otomatik çalıştırma
- Manuel çalıştırma: python -m app.tasks.proxy_update
"""

import os
import sys
import logging
from datetime import datetime

sys.path.append('/app')

from app.database import get_db
from app.services.ProxyService import ProxyService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_proxy_list_task():
    """
    Proxy listesini tüm kaynaklardan güncelle
    
    Bu fonksiyon:
    1. Tüm kaynaklardan proxy listesi çeker
    2. Parse eder
    3. Veritabanına ekler/günceller
    4. Rapor döndürür
    """
    logger.info("🔄 Otomatik proxy güncelleme başladı")
    
    try:
        # Database session
        db = next(get_db())
        
        # Service instance
        service = ProxyService(db)
        
        # Tüm kaynaklardan güncelle
        result = service.update_proxy_list()
        
        logger.info(
            f"✅ Proxy güncelleme tamamlandı\n"
            f"   - Kaynaklar: {result['sources_count']}\n"
            f"   - Toplam fetch: {result['total_fetched']}\n"
            f"   - Yeni eklenen: {result['total_added']}\n"
            f"   - Güncellenen: {result['total_updated']}"
        )
        
        # İstatistikleri logla
        stats = service.get_statistics()
        logger.info(
            f"📊 Proxy istatistikleri:\n"
            f"   - Toplam: {stats['total']}\n"
            f"   - Aktif: {stats['active']}\n"
            f"   - Pasif: {stats['inactive']}\n"
            f"   - Ort. başarı: {stats['avg_working_percent']}%\n"
            f"   - Ort. yanıt: {stats['avg_response_time']}ms"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Proxy güncelleme hatası: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    
    finally:
        db.close()


# Celery task tanımı (eğer celery kullanılacaksa)
try:
    from app.celery_worker import celery
    
    @celery.task(name='proxy.update_list')
    def celery_update_proxy_list():
        """Celery task wrapper"""
        return update_proxy_list_task()

except ImportError:
    logger.warning("⚠️ Celery bulunamadı, sadManuel çalıştırma modu aktif")


# Manuel çalıştırma
if __name__ == '__main__':
    logger.info("🚀 Manuel proxy güncelleme başlatılıyor...")
    result = update_proxy_list_task()
    
    if result.get('success'):
        logger.info("✅ İşlem başarılı")
        sys.exit(0)
    else:
        logger.error("❌ İşlem başarısız")
        sys.exit(1)

