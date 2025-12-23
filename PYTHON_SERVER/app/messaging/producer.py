import json
import uuid
import pika
from datetime import datetime
from typing import Dict, Any
from .connection import RabbitMQConnection


class JobProducer:
    def __init__(self):
        self.rabbitmq = RabbitMQConnection()
        self.setup_queues()

    def setup_queues(self):
        """Queue'ları oluştur"""
        connection = self.rabbitmq.get_connection()
        channel = connection.channel()

        # Parser input queue'ları
        channel.queue_declare(queue='scrapy.queue', durable=True)
        channel.queue_declare(queue='selenium.queue', durable=True)
        channel.queue_declare(queue='playwright.queue', durable=True)
        
        # Parser error queue'ları (parsing hatalarını saklar)
        channel.queue_declare(queue='scrapy.queue.error', durable=True)
        channel.queue_declare(queue='selenium.queue.error', durable=True)
        channel.queue_declare(queue='playwright.queue.error', durable=True)
        
        # ✅ YENİ: Timeout queue'ları
        channel.queue_declare(queue='timeout.queue', durable=True)
        channel.queue_declare(queue='timeout.queue.error', durable=True)
        
        # ✅ YENİ: Save queue'ları (DB kayıt işlemleri)
        channel.queue_declare(queue='save.queue', durable=True)
        channel.queue_declare(queue='save.queue.completed', durable=True)
        channel.queue_declare(queue='save.queue.error', durable=True)
        
        # ❌ KALDIRILDI: Parser completed queue'leri
        # Artık başarılı parse sonuçları save.queue'ye gidiyor
        # channel.queue_declare(queue='scrapy.queue.completed', durable=True)
        # channel.queue_declare(queue='selenium.queue.completed', durable=True)
        # channel.queue_declare(queue='playwright.queue.completed', durable=True)

        connection.close()
        print("✅ Queue'lar oluşturuldu: Parser (3), Error (3), Timeout (2), Save (3) = 11 queue")

    def send_parsing_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsing job'ını uygun queue'ya gönder"""

        # Parser type'ı al (varsayılan: scrapy)
        parser_type = job_data.get('parser_type', 'scrapy')
        
        # Unique queue job ID oluştur
        queue_job_id = str(uuid.uuid4())
        
        # Job datasına ek alanlar ekle
        job_data['queue_job_id'] = queue_job_id
        job_data['created_at'] = datetime.now().isoformat()
        job_data['status'] = 'queued'

        # Queue adını belirle
        queue_name = f"{parser_type}.queue"

        try:
            connection = self.rabbitmq.get_connection()
            channel = connection.channel()

            # Job'ı queue'ya gönder
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(job_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    message_id=queue_job_id,
                    timestamp=int(datetime.now().timestamp())
                )
            )

            connection.close()

            print(f"✅ Job gönderildi: Job ID: {job_data.get('job_id')} | Queue Job ID: {queue_job_id} -> {queue_name}")

            return {
                'success': True,
                'job_id': job_data.get('job_id'),  # Original job_id
                'queue_job_id': queue_job_id,  # Queue tracking ID
                'queue': queue_name,
                'message': f'Job sent to {queue_name}'
            }

        except Exception as e:
            print(f"❌ Job gönderme hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_queue_size(self, queue_name: str) -> int:
        """Queue'daki mesaj sayısını döndür"""
        try:
            connection = self.rabbitmq.get_connection()
            channel = connection.channel()

            method = channel.queue_declare(queue=queue_name, durable=True, passive=True)
            message_count = method.method.message_count

            connection.close()
            return message_count

        except Exception as e:
            print(f" Queue size hatası: {e}")
            return -1