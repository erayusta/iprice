# workers/base_worker.py
import pika
import os
import json
import sys
import requests
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

sys.path.append('/app')
from app.messaging.connection import RabbitMQConnection


class BaseWorker(ABC):
    def __init__(self):
        self.rabbitmq = RabbitMQConnection()
        self.connection = self.rabbitmq.get_connection()
        self.channel = self.connection.channel()
        self.setup_queues()
        
        # ✅ Proxy Management
        self.current_proxy = None
        self.proxy_enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        self.proxy_timeout = int(os.getenv('PROXY_TIMEOUT_SECONDS', '10'))
        self.api_url = os.getenv('API_URL', 'http://localhost:8000')
        
        # Worker başlangıcında proxy al
        if self.proxy_enabled:
            self._fetch_initial_proxy()

    def setup_queues(self):
        # Ana queue
        self.channel.queue_declare(queue=self.get_queue_name(), durable=True)
        
        # Error ve Completed queue'ları da declare et
        queue_base = self.get_queue_name()
        self.channel.queue_declare(queue=f'{queue_base}.error', durable=True)
        self.channel.queue_declare(queue=f'{queue_base}.completed', durable=True)
        
        self.channel.basic_qos(prefetch_count=1)

    @abstractmethod
    def get_queue_name(self) -> str:
        pass

    @abstractmethod
    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def start_consuming(self):
        self.channel.basic_consume(
            queue=self.get_queue_name(),
            on_message_callback=self._callback
        )

        print(f"🚀 {self.__class__.__name__} başlatıldı. Queue: {self.get_queue_name()}")
        self.channel.start_consuming()

    def _callback(self, ch, method, properties, body):
        try:
            import random
            import time
            
            # Random delay (1-3 saniye) - Rate limiting için
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            job_data = json.loads(body)
            print(f"📥 İş alındı: {job_data.get('url', 'Unknown')}")

            result = self.process_job(job_data)

            # Parser worker için: başarı/hata yönetimi
            # Save worker için: bu metod override edilecek
            if result.get('status') == 'success':
                print(f"✅ İş tamamlandı: {job_data.get('url')}")
                
                # Başarılı sonucu kendi completed queue'sine de gönder
                self._publish_result(result, 'completed')
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f"❌ İş başarısız: {result.get('error')}")
                # Hatalı sonucu error queue'ya gönder
                self._publish_result(result, 'error')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            print(f"❌ Worker hatası: {e}")
            # Hata durumunda error queue'ya gönder
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_data': job_data
            }
            self._publish_result(error_result, 'error')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    # ========================================
    # Proxy Management Methods
    # ========================================
    
    def _fetch_initial_proxy(self):
        """Worker başlangıcında API'den proxy al"""
        try:
            print("🔍 Proxy alınıyor...")
            
            response = requests.get(
                f"{self.api_url}/api/v1/proxy/get?protocol=http",
                timeout=5
            )
            
            if response.status_code == 200:
                self.current_proxy = response.json()
                print(
                    f"✅ Proxy alındı: {self.current_proxy['ip']}:{self.current_proxy['port']} "
                    f"(working: {self.current_proxy['working_percent']}%)"
                )
            else:
                print(f"⚠️ Proxy alınamadı: {response.status_code}")
                self.proxy_enabled = False
        
        except Exception as e:
            print(f"❌ Proxy fetch hatası: {e}")
            self.proxy_enabled = False
    
    def _report_proxy_failure(self, reason: str = None):
        """Mevcut proxy'yi başarısız olarak raporla ve yeni proxy al"""
        if not self.current_proxy:
            return
        
        try:
            # Eski proxy'yi raporla
            print(f"⚠️ Proxy failure raporu: {self.current_proxy['ip']}:{self.current_proxy['port']}")
            
            requests.post(
                f"{self.api_url}/api/v1/proxy/report-failure",
                json={
                    'proxy_id': self.current_proxy['id'],
                    'reason': reason or f'Timeout after {self.proxy_timeout} seconds'
                },
                timeout=5
            )
            
            # Yeni proxy al
            print("🔄 Yeni proxy alınıyor...")
            response = requests.get(
                f"{self.api_url}/api/v1/proxy/get?protocol=http",
                timeout=5
            )
            
            if response.status_code == 200:
                self.current_proxy = response.json()
                print(
                    f"✅ Yeni proxy alındı: {self.current_proxy['ip']}:{self.current_proxy['port']} "
                    f"(working: {self.current_proxy['working_percent']}%)"
                )
            else:
                print(f"⚠️ Yeni proxy alınamadı: {response.status_code}")
                self.current_proxy = None
        
        except Exception as e:
            print(f"❌ Proxy değiştirme hatası: {e}")
            self.current_proxy = None
    
    def _report_proxy_success(self):
        """Mevcut proxy'yi başarılı olarak raporla (opsiyonel)"""
        if not self.current_proxy:
            return
        
        try:
            requests.post(
                f"{self.api_url}/api/v1/proxy/report-success",
                json={'proxy_id': self.current_proxy['id']},
                timeout=2
            )
        
        except Exception:
            pass  # Silent fail - not critical
    
    def get_proxy_url(self) -> Optional[str]:
        """Kullanılacak proxy URL'ini döndür (veya None)"""
        if self.proxy_enabled and self.current_proxy:
            return self.current_proxy['url']
        return None
    
    # ========================================
    # Queue Management Methods
    # ========================================
    
    def _publish_result(self, result: Dict[str, Any], result_type: str):
        """Sonucu ilgili result queue'ya gönder (completed veya error)"""
        try:
            queue_base = self.get_queue_name()
            result_queue = f"{queue_base}.{result_type}"
            
            self.channel.basic_publish(
                exchange='',
                routing_key=result_queue,
                body=json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json'
                )
            )
            print(f"📤 Sonuç gönderildi: {result_queue}")
        except Exception as e:
            print(f"⚠️ Sonuç gönderilemedi: {e}")
    
    def _publish_to_save_queue(self, result: Dict[str, Any]):
        """Parse sonucunu save.queue'ye gönder (DB kayıt için)"""
        try:
            import uuid
            from datetime import datetime
            
            save_payload = {
                **result,  # Tüm parse sonuçlarını dahil et
                'queue_job_id': str(uuid.uuid4()),
                'save_timestamp': datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='save.queue',
                body=json.dumps(save_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            print(f"💾 save.queue'ye gönderildi: {result.get('url')}")
        except Exception as e:
            print(f"⚠️ save.queue'ye gönderilemedi: {e}")
    
    def _publish_to_timeout_queue(self, job_data: Dict[str, Any]):
        """Timeout'a düşen job'ı timeout.queue'ya gönder"""
        try:
            import uuid
            from datetime import datetime
            
            timeout_payload = {
                **job_data,  # Tüm job verilerini dahil et
                'queue_job_id': str(uuid.uuid4()),
                'timeout_timestamp': datetime.now().isoformat(),
                'retry_count': job_data.get('retry_count', 0) + 1
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='timeout.queue',
                body=json.dumps(timeout_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            print(f"⏰ timeout.queue'ya gönderildi: {job_data.get('url')}")
        except Exception as e:
            print(f"⚠️ timeout.queue'ya gönderilemedi: {e}")