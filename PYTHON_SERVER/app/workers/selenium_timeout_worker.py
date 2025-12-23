# workers/selenium_timeout_worker.py
from typing import Dict, Any
import sys
import json
import pika

sys.path.append('/app')
from .base_worker import BaseWorker
from app.parsers.factory import ParserFactory


class SeleniumTimeoutWorker(BaseWorker):
    def get_queue_name(self) -> str:
        return 'timeout.queue'

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Timeout job'ını işle - İlk deneme, timeout olursa proxy ile tekrar dene"""
        try:
            # Job verilerini al
            url = job_data['url']
            company_id = job_data['company_id']
            application_id = job_data['application_id']
            server_id = job_data['server_id']
            job_id = job_data.get('job_id')
            product_id = job_data.get('product_id')
            npm = job_data.get('npm')
            
            print(f"⏰ Timeout Job işleniyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
            
            # 🔍 URL'de "gurgencler" kelimesi varsa, Gurgencler worker'ı kullan
            if 'gurgencler' in url.lower():
                print(f"🔥 URL'de 'gurgencler' tespit edildi, HTTP parsing kullanılacak")
                from .gurgencler_worker import GurgenclerWorker
                gurgencler_worker = GurgenclerWorker()
                result = gurgencler_worker.process_job(job_data)
                return result
            
            # İLK DENEME: Normal parsing (proxy olmadan veya mevcut proxy ile)
            print(f"🔄 İlk deneme başlatılıyor (proxy: {'var' if job_data.get('use_proxy') else 'yok'})...")
            parser = ParserFactory.get_parser('selenium')
            result = parser.parse(url, company_id, application_id, server_id, job_data=job_data)
            
            # İlk deneme başarılı mı?
            if result.get('status') == 'success':
                # ✅ Başarılı → save.queue'ye gönder
                self._publish_to_save_queue(result)
                print(f"✅ İlk deneme başarılı, save.queue'ye gönderildi: {url}")
                return result
            
            # İlk deneme timeout hatası mı?
            error_msg = result.get('error', '').lower()
            http_status = result.get('http_status_code', 0)
            is_timeout = 'timeout' in error_msg or http_status == 408
            
            if is_timeout:
                print(f"⏰ İlk deneme timeout'a düştü, proxy ile tekrar deneniyor...")
                
                # PROXY İLE TEKRAR DENEME
                # Job data'yı proxy kullanacak şekilde güncelle
                retry_job_data = job_data.copy()
                retry_job_data['use_proxy'] = True
                retry_job_data['proxy_type'] = retry_job_data.get('proxy_type', 'brightdata')  # Varsayılan proxy tipi
                retry_job_data['retry_count'] = retry_job_data.get('retry_count', 0) + 1
                
                print(f"🔒 Proxy ile tekrar deneme başlatılıyor (proxy_type: {retry_job_data.get('proxy_type')})...")
                retry_result = parser.parse(url, company_id, application_id, server_id, job_data=retry_job_data)
                
                # Proxy ile deneme başarılı mı?
                if retry_result.get('status') == 'success':
                    # ✅ Başarılı → save.queue'ye gönder
                    self._publish_to_save_queue(retry_result)
                    print(f"✅ Proxy ile deneme başarılı, save.queue'ye gönderildi: {url}")
                    return retry_result
                else:
                    # ❌ Tekrar timeout → timeout.queue.error'a gönder
                    retry_error_msg = retry_result.get('error', '').lower()
                    retry_http_status = retry_result.get('http_status_code', 0)
                    retry_is_timeout = 'timeout' in retry_error_msg or retry_http_status == 408
                    
                    if retry_is_timeout:
                        print(f"❌ Proxy ile deneme de timeout'a düştü, timeout.queue.error'a gönderiliyor: {url}")
                        self._publish_to_timeout_error_queue(retry_result)
                        return retry_result
                    else:
                        # Proxy ile deneme başka bir hata verdi → normal error queue'ya gönder
                        print(f"❌ Proxy ile deneme başka bir hata verdi: {retry_result.get('error')}")
                        return retry_result
            else:
                # İlk deneme timeout değil, başka bir hata → normal error queue'ya gönder
                print(f"❌ İlk deneme timeout değil, başka bir hata: {result.get('error')}")
                return result
            
        except Exception as e:
            print(f"❌ Timeout Job işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': job_data.get('job_id'),
                'product_id': job_data.get('product_id'),
                'url': job_data.get('url'),
                'company_id': job_data.get('company_id'),
                'parser_used': 'selenium_timeout'
            }
            
            return error_result
    
    def _publish_to_timeout_error_queue(self, result: Dict[str, Any]):
        """Timeout hatası sonucunu timeout.queue.error'a gönder"""
        try:
            import uuid
            from datetime import datetime
            
            error_payload = {
                **result,  # Tüm hata sonuçlarını dahil et
                'queue_job_id': str(uuid.uuid4()),
                'error_timestamp': datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='timeout.queue.error',
                body=json.dumps(error_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            print(f"❌ timeout.queue.error'a gönderildi: {result.get('url')}")
        except Exception as e:
            print(f"⚠️ timeout.queue.error'a gönderilemedi: {e}")


if __name__ == "__main__":
    worker = SeleniumTimeoutWorker()
    worker.start_consuming()

