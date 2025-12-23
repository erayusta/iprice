#!/usr/bin/env python3
"""
🔄 Chrome Error Queue Retry Script
==================================
chrome.db.queue.error queue'sundaki mesajları alır, 
chrome.db.queue.error.try queue'suna taşır ve tekrar işlemeye çalışır.

Kullanım:
    python -m app.scripts.chrome_error_retry
    veya
    cd /app/app && python3 scripts/chrome_error_retry.py
"""

import sys
import os
import json
import traceback
import time
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.append('/app')

import pika
import pytz
from pika.exceptions import AMQPConnectionError, ConnectionClosed

from app.workers.chrome_completed_worker import ChromeCompletedQueueWorker

# Türkiye saati (UTC+3)
TURKEY_TZ = pytz.timezone('Europe/Istanbul')


class ChromeErrorRetry:
    """Error queue'daki mesajları retry eden sınıf"""
    
    def __init__(self):
        # Worker'ı initialize et (RabbitMQ ve DB bağlantıları için)
        self.worker = ChromeCompletedQueueWorker()
        
        # Queue isimleri
        self.error_queue_name = 'chrome.db.queue.error'
        self.try_queue_name = 'chrome.db.queue.error.try'
        self.success_queue_name = 'chrome.db.queue.success'
        self.failed_queue_name = 'chrome.db.queue.error.failed'
    
    def _get_connection(self):
        """RabbitMQ bağlantısı oluştur"""
        params = self.worker._get_connection_params()
        return pika.BlockingConnection(params)
    
    def retry_error_messages(self, limit: Optional[int] = None):
        """
        Error queue'daki mesajları retry et
        
        Args:
            limit: İşlenecek maksimum mesaj sayısı (None = tümü)
        """
        connection = None
        channel = None
        
        try:
            # Bağlantı kur
            connection = self._get_connection()
            channel = connection.channel()
            
            # Queue'ları declare et
            channel.queue_declare(queue=self.error_queue_name, durable=True)
            channel.queue_declare(queue=self.try_queue_name, durable=True)
            channel.queue_declare(queue=self.success_queue_name, durable=True)
            channel.queue_declare(queue=self.failed_queue_name, durable=True)
            
            print(f"🔄 Error queue retry işlemi başlatılıyor...")
            print(f"   Error Queue: {self.error_queue_name}")
            print(f"   Try Queue: {self.try_queue_name}")
            print(f"   Failed Queue: {self.failed_queue_name}")
            print()
            
            processed_count = 0
            success_count = 0
            failed_count = 0
            
            while True:
                # Limit kontrolü
                if limit and processed_count >= limit:
                    print(f"⏸️  Limit ({limit}) ulaşıldı, durduruluyor...")
                    break
                
                # Error queue'dan mesaj al (non-blocking)
                method_frame, header_frame, body = channel.basic_get(
                    queue=self.error_queue_name,
                    auto_ack=False
                )
                
                if method_frame is None:
                    # Queue boş
                    if processed_count == 0:
                        print("ℹ️  Error queue boş, işlenecek mesaj yok")
                    else:
                        print(f"\n✅ Tüm mesajlar işlendi!")
                        print(f"   Toplam: {processed_count}, Başarılı: {success_count}, Başarısız: {failed_count}")
                    break
                
                try:
                    # Mesajı parse et
                    try:
                        message_data = json.loads(body.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"❌ Geçersiz JSON mesajı: {e}")
                        # Mesajı acknowledge et ve atla
                        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                        processed_count += 1
                        failed_count += 1
                        continue
                    
                    job_id = message_data.get('job_id')
                    product_id = message_data.get('product_id')
                    url = message_data.get('url')
                    
                    print(f"📥 Mesaj alındı - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
                    
                    # Orijinal mesajı al (eğer original_message varsa onu kullan)
                    original_message = message_data.get('original_message', message_data)
                    
                    # Try queue'ya taşı (acknowledge etmeden önce)
                    try:
                        channel.basic_publish(
                            exchange='',
                            routing_key=self.try_queue_name,
                            body=json.dumps(original_message, ensure_ascii=False),
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # Persistent
                                content_type='application/json'
                            )
                        )
                        print(f"   ➡️  Mesaj {self.try_queue_name} queue'suna taşındı")
                    except Exception as e:
                        print(f"   ❌ Try queue'ya taşıma hatası: {e}")
                        # Hata durumunda mesajı error queue'da bırak (nack ile requeue)
                        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
                        processed_count += 1
                        failed_count += 1
                        continue
                    
                    # Error queue'dan mesajı sil (acknowledge)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    
                    # Mesajı tekrar işlemeye çalış
                    try:
                        print(f"   🔄 Mesaj tekrar işleniyor...")
                        
                        # Worker'ın process_message metodunu kullan
                        # (process_message içinde zaten scraper_data'ya kayıt yapılıyor)
                        self.worker.process_message(original_message)
                        
                        # Başarılı - success queue'ya gönder
                        try:
                            self.worker.send_to_success_queue(original_message)
                            print(f"   ✅ Mesaj başarıyla işlendi ve success queue'ya gönderildi")
                            success_count += 1
                        except Exception as success_exception:
                            print(f"   ⚠️  Mesaj işlendi ama success queue'ya gönderilemedi: {success_exception}")
                            success_count += 1  # DB işlemi başarılı olduğu için say
                        
                    except Exception as process_exception:
                        error_message = str(process_exception)
                        error_trace = traceback.format_exc()
                        
                        print(f"   ❌ Mesaj işleme hatası: {error_message}")
                        
                        # Başarısız - failed queue'ya gönder (retry_count yok, sadece 1 kere denendi)
                        try:
                            # Hata bilgilerini hazırla
                            failed_data = {
                                'original_message': original_message,
                                'scraped_data': self.worker.filter_non_null_data(original_message.get('scraped_data', {})),
                                'job_id': original_message.get('job_id'),
                                'product_id': original_message.get('product_id'),
                                'company_id': original_message.get('company_id'),
                                'url': original_message.get('url'),
                                'mpn': original_message.get('npm') or original_message.get('mpn'),
                                'attributes': original_message.get('attributes', []),
                                'error_message': error_message,
                                'error_trace': error_trace,
                                'error_timestamp': datetime.now(TURKEY_TZ).isoformat(),
                                'failed_timestamp': datetime.now(TURKEY_TZ).isoformat(),
                                'queue_name': self.worker.queue_name,
                                'retry_attempted': True
                            }
                            
                            # Failed queue'ya gönder
                            channel.basic_publish(
                                exchange='',
                                routing_key=self.failed_queue_name,
                                body=json.dumps(failed_data, ensure_ascii=False),
                                properties=pika.BasicProperties(
                                    delivery_mode=2,  # Persistent message
                                    content_type='application/json'
                                )
                            )
                            print(f"   ⬅️  Mesaj failed queue'ya gönderildi: {self.failed_queue_name}")
                            failed_count += 1
                        except Exception as failed_queue_exception:
                            print(f"   ❌ Failed queue'ya gönderme hatası: {failed_queue_exception}")
                            failed_count += 1
                    
                    processed_count += 1
                    print()  # Boş satır
                    
                    # DB yükünü azaltmak için mesajlar arasında kısa bir bekleme
                    time.sleep(0.5)  # 500ms bekleme
                    
                except Exception as e:
                    print(f"❌ Mesaj işleme genel hatası: {e}")
                    traceback.print_exc()
                    
                    # Mesajı acknowledge et (hata durumunda kaybolmasın)
                    try:
                        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    except Exception:
                        pass
                    
                    processed_count += 1
                    failed_count += 1
                    print()
            
            print(f"\n📊 Retry işlemi tamamlandı!")
            print(f"   Toplam işlenen: {processed_count}")
            print(f"   Başarılı: {success_count}")
            print(f"   Başarısız: {failed_count}")
            
        except Exception as e:
            print(f"❌ Retry işlemi hatası: {e}")
            traceback.print_exc()
        finally:
            # Bağlantıları kapat
            try:
                if channel and channel.is_open:
                    channel.close()
            except Exception:
                pass
            
            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass
    
    def get_error_queue_count(self) -> int:
        """
        Error queue'daki mesaj sayısını döndür
        
        Returns:
            Mesaj sayısı
        """
        try:
            connection = self._get_connection()
            channel = connection.channel()
            
            # Queue'yu declare et
            result = channel.queue_declare(queue=self.error_queue_name, durable=True, passive=True)
            message_count = result.method.message_count
            
            channel.close()
            connection.close()
            
            return message_count
        except Exception as e:
            print(f"⚠️  Queue sayısı alınamadı: {e}")
            return 0


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chrome Error Queue Retry Script')
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='İşlenecek maksimum mesaj sayısı (varsayılan: tümü)'
    )
    parser.add_argument(
        '--count',
        action='store_true',
        help='Sadece error queue\'daki mesaj sayısını göster'
    )
    
    args = parser.parse_args()
    
    retry = ChromeErrorRetry()
    
    if args.count:
        # Sadece sayıyı göster
        count = retry.get_error_queue_count()
        print(f"📊 Error queue'daki mesaj sayısı: {count}")
        return
    
    # Retry işlemini başlat
    print("=" * 60)
    print("🔄 Chrome Error Queue Retry Script")
    print("=" * 60)
    print()
    
    # Önce queue'daki mesaj sayısını göster
    count = retry.get_error_queue_count()
    print(f"📊 Error queue'daki mesaj sayısı: {count}")
    print()
    
    if count == 0:
        print("ℹ️  İşlenecek mesaj yok, çıkılıyor...")
        return
    
    # Retry işlemini başlat
    retry.retry_error_messages(limit=args.limit)


if __name__ == "__main__":
    main()

