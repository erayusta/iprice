import logging
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class CrawlerServiceInterface(ABC):
    # Service tipi - selenium gerektiren service'ler True yapacak
    use_selenium = False

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract_product_data(self, url: str, mpn: str, company: str) -> Dict[str, any]:
        pass

    def validate_url(self, url: str) -> bool:
        return url and url.startswith(('http://', 'https://'))

    def cleanup(self):
        pass

    def get_service_name(self) -> str:
        return self.__class__.__name__

    def is_selenium_service(self) -> bool:
        return self.use_selenium

    def _log_extraction_start(self, url: str, mpn: str, company: str):
        self.logger.info(f"🎯 {company} extraction başlıyor - MPN: {mpn}")
        self.logger.debug(f"   URL: {url}")

    def _log_extraction_success(self, extracted_data: Dict, mpn: str):
        data_keys = list(extracted_data.keys()) if extracted_data else []
        self.logger.info(f"✅ Extraction başarılı - MPN: {mpn}, Fields: {data_keys}")

    def _log_extraction_error(self, error: Exception, url: str, mpn: str):
        self.logger.error(f"💥 Extraction hatası - MPN: {mpn}, Error: {str(error)}")
        self.logger.debug(f"   URL: {url}")