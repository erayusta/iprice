# workers/scrapy_worker.py
from typing import Dict, Any
import sys

sys.path.append('/app')
from .base_worker import BaseWorker
from app.parsers.factory import ParserFactory



class ScrapyWorker(BaseWorker):
    def get_queue_name(self) -> str:
        return 'scrapy.queue'

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrapy job'ını işle"""
        try:
            # Job verilerini al
            url = job_data['url']
            company_id = job_data['company_id']
            application_id = job_data['application_id']
            server_id = job_data['server_id']
            job_id = job_data.get('job_id')
            product_id = job_data.get('product_id')
            npm = job_data.get('npm')
            
            print(f"📦 Scrapy Job işleniyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")

            # Parser'ı al
            parser = ParserFactory.get_parser('scrapy')

            # Parse işlemi - job_data'yı da gönder
            result = parser.parse(url, company_id, application_id, server_id, job_data=job_data)

            # Başarı durumuna göre queue'ye gönder
            if result.get('status') == 'success':
                # ✅ Parsing başarılı → save.queue'ye gönder (DB kayıt için)
                self._publish_to_save_queue(result)
                print(f"✅ Scrapy parsing başarılı, save.queue'ye gönderildi: {url}")
            else:
                # ❌ Parsing hatası → scrapy.queue.error'a gönderilecek (base_worker halleder)
                print(f"❌ Scrapy parsing hatası: {result.get('error')}")
            
            return result

        except Exception as e:
            print(f"❌ Scrapy Job işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': job_data.get('job_id'),
                'product_id': job_data.get('product_id'),
                'url': job_data.get('url'),
                'company_id': job_data.get('company_id'),
                'parser_used': 'scrapy'
            }
            
            return error_result


if __name__ == "__main__":
    worker = ScrapyWorker()
    worker.start_consuming()