# workers/selenium_worker.py
from typing import Dict, Any
import sys

sys.path.append('/app')
from .base_worker import BaseWorker
from app.parsers.factory import ParserFactory


class SeleniumWorker(BaseWorker):
    def get_queue_name(self) -> str:
        return 'selenium.queue'

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Selenium job'ını işle"""
        try:
            # Job verilerini al
            url = job_data['url']
            company_id = job_data['company_id']
            application_id = job_data['application_id']
            server_id = job_data['server_id']
            job_id = job_data.get('job_id')
            product_id = job_data.get('product_id')
            npm = job_data.get('npm')
            
            print(f"📦 Selenium Job işleniyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
            
            # 🔍 URL'de "gurgencler" kelimesi varsa, Gurgencler worker'ı kullan
            if 'gurgencler' in url.lower():
                print(f"🔥 URL'de 'gurgencler' tespit edildi, HTTP parsing kullanılacak")
                from .gurgencler_worker import GurgenclerWorker
                gurgencler_worker = GurgenclerWorker()
                result = gurgencler_worker.process_job(job_data)
                return result
            
            # Normal Selenium parsing
            # Parser'ı al
            parser = ParserFactory.get_parser('selenium')
            # Parse işlemi - job_data'yı da gönder
            result = parser.parse(url, company_id, application_id, server_id, job_data=job_data)

            # Başarı durumuna göre queue'ye gönder
            if result.get('status') == 'success':
                # ✅ Parsing başarılı → save.queue'ye gönder (DB kayıt için)
                self._publish_to_save_queue(result)
                print(f"✅ Selenium parsing başarılı, save.queue'ye gönderildi: {url}")
            else:
                # Timeout hatası kontrolü
                error_msg = result.get('error', '').lower()
                http_status = result.get('http_status_code', 0)
                
                # Timeout hatası tespit edilirse timeout.queue'ya gönder
                if 'timeout' in error_msg or http_status == 408:
                    print(f"⏰ Timeout hatası tespit edildi, timeout.queue'ya gönderiliyor: {url}")
                    self._publish_to_timeout_queue(job_data)
                else:
                    # ❌ Diğer parsing hataları → selenium.queue.error'a gönderilecek (base_worker halleder)
                    print(f"❌ Selenium parsing hatası: {result.get('error')}")
            
            return result

        except Exception as e:
            print(f"❌ Selenium Job işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': job_data.get('job_id'),
                'product_id': job_data.get('product_id'),
                'url': job_data.get('url'),
                'company_id': job_data.get('company_id'),
                'parser_used': 'selenium'
            }
            
            return error_result


if __name__ == "__main__":
    worker = SeleniumWorker()
    worker.start_consuming()
