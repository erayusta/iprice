#!/usr/bin/env python3
"""
🎭 Playwright Worker
===================
playwright.queue'dan mesaj consume eder ve Playwright ile parse eder

Queue: playwright.queue
Callback: playwright.queue.completed / playwright.queue.error

Kullanım:
    python -m workers.playwright_worker
"""

import sys
sys.path.append('/app')

from .base_worker import BaseWorker
from app.parsers.factory import ParserFactory
from typing import Dict, Any


class PlaywrightWorker(BaseWorker):
    """Playwright parsing worker"""
    
    def get_queue_name(self) -> str:
        """Consume edilecek queue adı"""
        return 'playwright.queue'
    
    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Playwright parsing job'ını işle
        
        Args:
            job_data: RabbitMQ'dan gelen job data
            
        Returns:
            Parse result
        """
        try:
            # Job data'dan bilgileri çıkar
            url = job_data['url']
            company_id = job_data['company_id']
            application_id = job_data['application_id']
            server_id = job_data['server_id']
            job_id = job_data.get('job_id')
            product_id = job_data.get('product_id')
            npm = job_data.get('npm')
            
            print(f"🎭 Playwright Job işleniyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
            
            # Playwright parser al
            parser = ParserFactory.get_parser('playwright')
            
            # Parse et
            result = parser.parse(url, company_id, application_id, server_id, job_data=job_data)
            
            # Başarı durumuna göre queue'ye gönder
            if result.get('status') == 'success':
                # ✅ Parsing başarılı → save.queue'ye gönder (DB kayıt için)
                self._publish_to_save_queue(result)
                print(f"✅ Playwright parsing başarılı, save.queue'ye gönderildi: {url}")
            else:
                # ❌ Parsing hatası → playwright.queue.error'a gönderilecek (base_worker halleder)
                print(f"❌ Playwright parsing hatası: {result.get('error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Playwright Job işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
            # Hata sonucu oluştur
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': job_data.get('job_id'),
                'product_id': job_data.get('product_id'),
                'url': job_data.get('url'),
                'company_id': job_data.get('company_id'),
                'parser_used': 'playwright'
            }
            
            return error_result


if __name__ == "__main__":
    print("🎭 Playwright Worker başlatılıyor...")
    worker = PlaywrightWorker()
    worker.start_consuming()

