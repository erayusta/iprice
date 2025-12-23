import logging
from typing import Optional, Dict
from app.services.base.CrawlerServiceInterface import CrawlerServiceInterface

# Kullanılacak TÜM servis sınıflarını en üste import edelim
from app.services.marketplace.HepsiburadaSeleniumService import HepsiburadaSeleniumService

logger = logging.getLogger(__name__)


class CrawlerServiceFactory:
    """
    Company name'e göre uygun crawler service nesnesini oluşturur ve yönetir.
    """

    def __init__(self, product_repository, image_repository, screenshot_repository, product_service):
        self.product_repository = product_repository
        self.image_repository = image_repository
        self.screenshot_repository = screenshot_repository
        self.product_service = product_service
        self.services: Dict[str, CrawlerServiceInterface] = {}
        self._register_services()

    def _register_services(self):
        logger.info("🔄 Servisler kaydediliyor...")

        # --- GEÇİCİ OLARAK TRY-EXCEPT'İ DEVRE DIŞI BIRAKTIK ---
        # try:
        company_name_to_register = 'Hepsiburada'
        logger.info(f"🔍 '{company_name_to_register}' şirketi veritabanında aranıyor...")

        # Bu satırlardan birinde hata varsa, program artık burada çökecek ve bize hatayı gösterecek
        from app.services.marketplace.HepsiburadaSeleniumService import HepsiburadaSeleniumService

        hepsiburada_company = self.product_service.get_company_by_name(company_name_to_register)

        if not hepsiburada_company:
            logger.error(f"❌ KAYIT BAŞARISIZ: Veritabanında '{company_name_to_register}' adında bir şirket bulunamadı.")
            return

        logger.info(
            f"✅ '{company_name_to_register}' şirketi bulundu. ID: {hepsiburada_company.id}. Servis oluşturuluyor...")

        hepsiburada_service = HepsiburadaSeleniumService(
            product_repository=self.product_repository,
            image_repository=self.image_repository,
            screenshot_repository=self.screenshot_repository,
            db_session=self.product_repository.db_session,
            hepsiburada_company_id=hepsiburada_company.id
        )
        self.services[company_name_to_register] = hepsiburada_service
        logger.info(f"🎉 {company_name_to_register} servisi başarıyla kaydedildi!")

        # except Exception as e:
        #    logger.error(f"💥 KAYIT BAŞARISIZ: Hata: {e}", exc_info=True)

        if not self.services:
            logger.warning("⚠️ Hiçbir özel servis kaydedilemedi!")
        else:
            logger.info(f"🎯 Kayıtlı özel servisler: {list(self.services.keys())}")

    def get_service(self, company_name: str) -> Optional[CrawlerServiceInterface]:
        service = self.services.get(company_name)
        if not service:
            logger.debug(f"ℹ️ {company_name} için özel bir servis kayıtlı değil, normal Scrapy kullanılacak.")
        return service

    def cleanup_all(self):
        logger.info("🧹 Tüm servisler cleanup ediliyor...")
        for company_name, service in self.services.items():
            try:
                service.cleanup()
            except Exception as e:
                logger.error(f"⚠️ {company_name} cleanup hatası: {e}")
        logger.info("✅ Tüm servis cleanup tamamlandı")

    def get_registered_companies(self) -> list:
        return list(self.services.keys())