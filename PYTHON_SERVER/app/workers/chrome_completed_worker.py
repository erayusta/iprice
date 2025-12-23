#!/usr/bin/env python3
"""
🔌 Chrome Completed Queue Worker
================================
chrome.queue.completed queue'sundan mesaj consume eder ve veritabanına kaydeder

Queue: chrome.queue.completed
Success: chrome.db.queue.success
Error: chrome.db.queue.error

Kullanım:
    python -m workers.chrome_completed_worker
"""

import sys
import os
import json
import traceback
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

sys.path.append('/app')

import pika
import pytz
from pika.exceptions import AMQPConnectionError, AMQPChannelError, ConnectionClosed
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Türkiye saati (UTC+3)
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

from app.database import SessionLocal
from app.model.ProductAttributeValue import ProductAttributeValue
from app.model.ProductAttributeValueSummary import ProductAttributeValueSummary
from app.model.Attribute import Attribute
from app.model.ScraperData import ScraperData


class ChromeCompletedQueueWorker:
    """Chrome extension'dan gelen completed mesajlarını işleyen worker"""
    
    def __init__(self):
        # SERVER değişkenine göre RabbitMQ ayarlarını belirle
        server_type = os.getenv('SERVER', 'SERVER_AZURE')
        
        if server_type == 'SERVER_AZURE':
            self.rabbitmq_host = os.getenv('RABBITMQ_HOST_AZURE', '68.219.209.108')
            self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT_AZURE', 5672))
            self.rabbitmq_user = os.getenv('RABBITMQ_USER_AZURE', 'admin')
            self.rabbitmq_pass = os.getenv('RABBITMQ_PASS_AZURE', '41jqJ526lOxP')
            self.vhost = os.getenv('RABBITMQ_VHOST_AZURE', 'chrome')  # Chrome extension için vhost
        else:  # SERVER_LOCAL
            self.rabbitmq_host = os.getenv('RABBITMQ_HOST_LOCAL', '10.20.50.16')
            self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT_LOCAL', 5672))
            self.rabbitmq_user = os.getenv('RABBITMQ_USER_LOCAL', 'admin')
            self.rabbitmq_pass = os.getenv('RABBITMQ_PASS_LOCAL', 'admin123')
            self.vhost = os.getenv('RABBITMQ_VHOST_LOCAL', 'chrome')
        
        self.queue_name = 'chrome.queue.completed'
        self.error_queue_name = 'chrome.db.queue.error'
        self.success_queue_name = 'chrome.db.queue.success'
        
        # Retry ayarları
        self.max_retries = 5
        self.retry_delay = 5  # seconds
        
        # Connection ve channel (lazy init)
        self.connection = None
        self.channel = None
        
        # Database session (her mesaj için yeni session)
        self.db: Optional[Session] = None
        
        print(f"🔌 RabbitMQ Bağlantı: {server_type} -> {self.rabbitmq_host}:{self.rabbitmq_port}/{self.vhost}")
    
    def _get_connection_params(self):
        """RabbitMQ connection parametrelerini oluştur"""
        return pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            virtual_host=self.vhost,
            credentials=pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass),
            connection_attempts=3,
            retry_delay=3.0,
            socket_timeout=3.0,
            heartbeat=60
        )
    
    def _connect(self):
        """RabbitMQ'ya bağlan"""
        try:
            params = self._get_connection_params()
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # Queue'ları declare et
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.queue_declare(queue=self.error_queue_name, durable=True)
            self.channel.queue_declare(queue=self.success_queue_name, durable=True)
            
            # QoS ayarla (her seferinde 1 mesaj işle)
            self.channel.basic_qos(prefetch_count=1)
            
            print(f"✅ RabbitMQ bağlantısı başarılı: {self.queue_name}")
            return True
        except Exception as e:
            print(f"❌ RabbitMQ bağlantı hatası: {e}")
            return False
    
    def _close_connection(self):
        """RabbitMQ bağlantısını kapat"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception:
            pass
        
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass
    
    def _get_db_session(self) -> Session:
        """Yeni database session oluştur"""
        return SessionLocal()
    
    def _close_db_session(self, session: Session):
        """Database session'ı kapat"""
        try:
            session.close()
        except Exception:
            pass
    
    def consume(self):
        """Mesajları consume et ve işle"""
        while True:
            try:
                # Bağlantı kur
                if not self._connect():
                    print(f"⏳ {self.retry_delay} saniye sonra tekrar denenecek...")
                    time.sleep(self.retry_delay)
                    continue
                
                print(f"🚀 Chrome Completed Queue Consumer başlatıldı: {self.queue_name}")
                
                # Consumer callback'i tanımla
                def callback(ch, method, properties, body):
                    try:
                        # Mesajı parse et
                        try:
                            message_data = json.loads(body.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            print(f"❌ Geçersiz JSON mesajı: {e}")
                            print(f"   Body: {body[:200]}")
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return
                        
                        job_id = message_data.get('job_id')
                        url = message_data.get('url')
                        print(f"📥 Mesaj alındı - Job ID: {job_id}, URL: {url}")
                        
                        # Mesajı işle
                        try:
                            self.process_message(message_data)
                            
                            # Başarılı işlem sonrası success queue'suna gönder
                            try:
                                self.send_to_success_queue(message_data)
                            except Exception as success_queue_exception:
                                print(f"⚠️ Success queue'ya gönderme hatası: {success_queue_exception}")
                                # Success queue hatası ana işlemi etkilemesin
                            
                            # Mesajı acknowledge et
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            print(f"✅ Mesaj başarıyla işlendi - Job ID: {job_id}")
                            
                            # DB yükünü azaltmak için mesajlar arasında kısa bir bekleme
                            time.sleep(0.3)  # 300ms bekleme
                            
                        except Exception as e:
                            error_message = str(e)
                            error_trace = traceback.format_exc()
                            
                            print(f"❌ Mesaj işleme hatası: {error_message}")
                            print(f"   Trace: {error_trace}")
                            
                            # Hata durumunda mesajı error queue'suna gönder
                            try:
                                self.send_to_error_queue(message_data, error_message, error_trace)
                            except Exception as error_queue_exception:
                                print(f"⚠️ Error queue'ya gönderme hatası: {error_queue_exception}")
                            
                            # Hata durumunda mesajı reject et (requeue yapma)
                            try:
                                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                            except Exception as nack_exception:
                                print(f"⚠️ NACK hatası: {nack_exception}")
                    
                    except Exception as e:
                        print(f"❌ Callback hatası: {e}")
                        traceback.print_exc()
                        try:
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        except Exception:
                            pass
                
                # Consumer'ı başlat
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=callback,
                    auto_ack=False
                )
                
                print(f"👂 Mesaj dinleme başladı: {self.queue_name}")
                
                # Mesajları dinlemeye devam et
                try:
                    self.channel.start_consuming()
                except KeyboardInterrupt:
                    print("🛑 Consumer durduruldu (KeyboardInterrupt)")
                    self.channel.stop_consuming()
                    break
                except Exception as e:
                    print(f"⚠️ Channel consuming hatası: {e}")
                    self._close_connection()
                    time.sleep(self.retry_delay)
                    continue
            
            except (AMQPConnectionError, ConnectionClosed) as e:
                print(f"⚠️ RabbitMQ bağlantısı kapandı, yeniden bağlanılıyor...: {e}")
                self._close_connection()
                time.sleep(self.retry_delay)
                continue
            
            except Exception as e:
                print(f"❌ Chrome Completed Queue Consumer hatası: {e}")
                traceback.print_exc()
                self._close_connection()
                time.sleep(self.retry_delay)
                continue
    
    def process_message(self, message_data: Dict[str, Any]):
        """
        Mesajı işle (transaction ile)
        
        Args:
            message_data: RabbitMQ'dan gelen mesaj verisi
        """
        db = self._get_db_session()
        try:
            # Transaction başlat
            db.begin()
            
            # Mesajı işle
            self.process_message_without_transaction(message_data, db)
            
            # Commit
            db.commit()
            
            # Başarılı mesajı scraper_data tablosuna kaydet (ayrı session ile)
            try:
                scraper_db = self._get_db_session()
                try:
                    self.save_to_scraper_data(message_data, scraper_db)
                finally:
                    self._close_db_session(scraper_db)
            except Exception as scraper_data_exception:
                print(f"⚠️ ScraperData kayıt hatası (ana işlemi etkilemez): {scraper_data_exception}")
                # ScraperData hatası ana işlemi etkilemesin
            
        except Exception as e:
            # Rollback
            db.rollback()
            raise
        finally:
            self._close_db_session(db)
    
    def process_message_without_transaction(self, message_data: Dict[str, Any], db: Session):
        """
        Transaction olmadan mesajı işle
        
        Args:
            message_data: RabbitMQ'dan gelen mesaj verisi
            db: Database session
        """
        try:
            job_id = message_data.get('job_id')
            product_id = message_data.get('product_id')
            company_id = message_data.get('company_id')
            url = message_data.get('url')
            mpn = message_data.get('npm') or message_data.get('mpn')
            
            # Scraped data (kazınan veriler)
            scraped_data_raw = message_data.get('scraped_data', {})
            
            # scraped_data'nın tipini kontrol et - eğer list ise dict'e çevir veya boş dict kullan
            if isinstance(scraped_data_raw, list):
                print(f"⚠️ scraped_data list olarak geldi")
                scraped_data = {}
            elif isinstance(scraped_data_raw, dict):
                scraped_data = scraped_data_raw
            else:
                scraped_data = {}
            
            # scraped_data boş mu kontrol et - eğer boşsa hata fırlat
            is_scraped_data_empty = (
                scraped_data is None or
                (isinstance(scraped_data, dict) and len(scraped_data) == 0) or
                (isinstance(scraped_data, list) and len(scraped_data) == 0)
            )
            
            if is_scraped_data_empty:
                error_msg = f"scraped_data boş veya null - Job ID: {job_id}, Product ID: {product_id}, URL: {url}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            # Attributes (attribute bilgileri - eğer varsa)
            attributes = message_data.get('attributes', [])
            
            if not job_id or not product_id or not company_id:
                raise Exception("Eksik bilgi: job_id, product_id veya company_id bulunamadı")
            
            print(f"💾 Veri kaydı başlıyor - Job ID: {job_id}, Product ID: {product_id}, Company ID: {company_id}, URL: {url}")
            
            # Eğer attributes array'i varsa, onu kullan
            # Yoksa scraped_data'dan attribute'ları çıkar
            if not attributes and scraped_data and isinstance(scraped_data, dict):
                # scraped_data'dan attribute'ları oluştur
                attributes = []
                for attr_name, attr_value in scraped_data.items():
                    # Attribute'ı bul veya oluştur
                    attribute = db.query(Attribute).filter(Attribute.name == attr_name).first()
                    if not attribute:
                        attribute = Attribute(
                            name=attr_name,
                            description=None,
                            created_at=datetime.now(TURKEY_TZ),
                            updated_at=datetime.now(TURKEY_TZ)
                        )
                        db.add(attribute)
                        db.flush()  # ID'yi almak için flush
                    
                    attributes.append({
                        'attributes_id': attribute.id,
                        'attributes_name': attr_name
                    })
            
            # Her attribute için kayıt yap
            inserted_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for attr in attributes:
                attr_id = attr.get('attributes_id')
                attr_name = attr.get('attributes_name')
                
                if not attr_id or not attr_name:
                    print(f"⚠️ Attribute bilgisi eksik: {attr}")
                    skipped_count += 1
                    continue
                
                # Scraped data'dan değeri al (scraped_data dict olmalı)
                if isinstance(scraped_data, dict):
                    attr_value = scraped_data.get(attr_name)
                else:
                    attr_value = None
                
                # Null, boş string veya boş array kontrolü - bunlar kaydedilmesin
                if attr_value is None or attr_value == '' or (isinstance(attr_value, list) and len(attr_value) == 0):
                    print(f"⏭️  Attribute atlandı (null/boş) - {attr_name}: {attr_value}")
                    skipped_count += 1
                    continue
                
                try:
                    # ProductAttributeValue'ye INSERT (veriyi olduğu gibi kaydet)
                    product_attr_value = ProductAttributeValue(
                        job_id=job_id,
                        product_id=product_id,
                        mpn=mpn,
                        company_id=company_id,
                        attribute_id=attr_id,
                        value=str(attr_value),
                        created_at=datetime.now(TURKEY_TZ),
                        updated_at=datetime.now(TURKEY_TZ)
                    )
                    db.add(product_attr_value)
                    # Flush yerine commit'te yapılacak - DB yükünü azaltmak için
                    
                    inserted_count += 1
                    print(f"✅ ProductAttributeValue hazırlandı - {attr_name}: {attr_value}")
                    
                    # ProductAttributeValueSummary'ye UPSERT
                    summary_result = self.upsert_to_summary_table(
                        db=db,
                        job_id=job_id,
                        product_id=product_id,
                        company_id=company_id,
                        attr_id=attr_id,
                        mpn=mpn,
                        value=str(attr_value),
                        attr_name=attr_name
                    )
                    
                    if summary_result == 'updated':
                        updated_count += 1
                    elif summary_result == 'inserted':
                        inserted_count += 1
                
                except Exception as e:
                    error_count += 1
                    print(f"❌ Attribute kayıt hatası ({attr_name}): {e}")
                    traceback.print_exc()
                    # Bir attribute hatası diğerlerini etkilemesin, devam et
            
            # Eğer hiçbir kayıt yapılamadıysa hata fırlat
            if inserted_count == 0 and updated_count == 0 and error_count > 0:
                raise Exception(f"Hiçbir attribute kaydedilemedi. Toplam hata: {error_count}, Atlanan: {skipped_count}")
            
            print(f"📊 Kayıt özeti - Job ID: {job_id}, Product ID: {product_id}")
            print(f"   Inserted: {inserted_count}, Updated: {updated_count}, Skipped: {skipped_count}, Errors: {error_count}")
            print(f"✅ Veri kaydı başarılı - Job ID: {job_id}, Product ID: {product_id}")
        
        except Exception as e:
            error_message = str(e)
            error_trace = traceback.format_exc()
            
            print(f"❌ Veri kayıt hatası: {error_message}")
            print(f"   Trace: {error_trace}")
            
            # Hata durumunda mesajı error queue'suna gönder
            try:
                self.send_to_error_queue(message_data, error_message, error_trace)
            except Exception as error_queue_exception:
                print(f"⚠️ Error queue'ya gönderme hatası: {error_queue_exception}")
            
            raise
    
    def upsert_to_summary_table(self, db: Session, job_id: int, product_id: int, company_id: int,
                                attr_id: int, mpn: str, value: str, attr_name: str) -> str:
        """
        ProductAttributeValueSummary tablosuna UPSERT işlemi
        
        Args:
            db: Database session
            job_id: Job ID
            product_id: Product ID
            company_id: Company ID
            attr_id: Attribute ID
            mpn: MPN
            value: Attribute value
            attr_name: Attribute name (logging için)
        
        Returns:
            'inserted', 'updated', or 'skipped'
        """
        try:
            # Null veya boş değer kontrolü - güncelleme/insert yapma
            if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
                print(f"⏭️  ProductAttributeValueSummary: SKIP - value null/boş ({attr_name})")
                return 'skipped'
            
            # Mevcut kaydı kontrol et
            existing_record = db.query(ProductAttributeValueSummary).filter(
                ProductAttributeValueSummary.company_id == company_id,
                ProductAttributeValueSummary.attribute_id == attr_id,
                ProductAttributeValueSummary.product_id == product_id,
                ProductAttributeValueSummary.mpn == mpn
            ).first()
            
            if existing_record:
                # Eğer job_id aynı ve mevcut value yeni value'den küçükse güncelleme yapma
                if existing_record.job_id == job_id and existing_record.value and value:
                    try:
                        existing_value_num = float(str(existing_record.value).replace(',', '.').replace(' ', ''))
                        new_value_num = float(str(value).replace(',', '.').replace(' ', ''))
                        
                        if existing_value_num < new_value_num:
                            print(f"⏭️  ProductAttributeValueSummary: SKIP - job_id aynı ve mevcut value daha küçük")
                            print(f"   {attr_name}: {existing_record.value} < {value}")
                            return 'skipped'
                    except (ValueError, AttributeError):
                        # Sayıya çevrilemezse string karşılaştırması yap
                        if str(existing_record.value) < str(value):
                            print(f"⏭️  ProductAttributeValueSummary: SKIP - job_id aynı ve mevcut value daha küçük (string)")
                            print(f"   {attr_name}: {existing_record.value} < {value}")
                            return 'skipped'
                
                # UPDATE: value ve job_id güncelle
                existing_record.value = value
                existing_record.job_id = job_id
                existing_record.updated_at = datetime.now(TURKEY_TZ)
                
                # Flush yerine commit'te yapılacak - DB yükünü azaltmak için
                print(f"🔄 ProductAttributeValueSummary: UPDATE hazırlandı - ID: {existing_record.id}, {attr_name}: {value}")
                return 'updated'
            
            else:
                # INSERT: Yeni kayıt ekle
                new_record = ProductAttributeValueSummary(
                    job_id=job_id,
                    product_id=product_id,
                    company_id=company_id,
                    attribute_id=attr_id,
                    mpn=mpn,
                    value=value,
                    created_at=datetime.now(TURKEY_TZ),
                    updated_at=datetime.now(TURKEY_TZ)
                )
                db.add(new_record)
                # Flush yerine commit'te yapılacak - DB yükünü azaltmak için
                
                print(f"➕ ProductAttributeValueSummary: INSERT hazırlandı - {attr_name}: {value}")
                return 'inserted'
        
        except Exception as e:
            print(f"❌ ProductAttributeValueSummary hatası ({attr_name}): {e}")
            traceback.print_exc()
            raise
    
    def send_to_error_queue(self, message_data: Dict[str, Any], error_message: str, error_trace: Optional[str] = None):
        """
        Error mesajını chrome.db.queue.error queue'suna gönder
        
        Args:
            message_data: Orijinal mesaj verisi
            error_message: Hata mesajı
            error_trace: Hata trace (opsiyonel)
        """
        try:
            # Yeni bağlantı oluştur
            params = self._get_connection_params()
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            # Error queue'yu declare et
            channel.queue_declare(queue=self.error_queue_name, durable=True)
            
            # Scraped data'yı null olmayan değerlerle filtrele
            scraped_data_raw = message_data.get('scraped_data', {})
            # Eğer list ise boş dict kullan
            if isinstance(scraped_data_raw, list):
                scraped_data_raw = {}
            scraped_data = self.filter_non_null_data(scraped_data_raw)
            
            # Error mesajını hazırla - tüm önemli verileri ekle
            error_data = {
                'original_message': message_data,
                'scraped_data': scraped_data,
                'job_id': message_data.get('job_id'),
                'product_id': message_data.get('product_id'),
                'company_id': message_data.get('company_id'),
                'url': message_data.get('url'),
                'mpn': message_data.get('npm') or message_data.get('mpn'),
                'attributes': message_data.get('attributes', []),
                'error_message': error_message,
                'error_trace': error_trace,
                'error_timestamp': datetime.now(TURKEY_TZ).isoformat(),
                'queue_name': self.queue_name
            }
            
            # Mesajı gönder
            channel.basic_publish(
                exchange='',
                routing_key=self.error_queue_name,
                body=json.dumps(error_data, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json'
                )
            )
            
            channel.close()
            connection.close()
            
            print(f"📤 Hata mesajı error queue'suna gönderildi - Queue: {self.error_queue_name}, Job ID: {message_data.get('job_id')}")
            return True
        
        except Exception as e:
            print(f"❌ Error queue'ya gönderme hatası: {e}")
            traceback.print_exc()
            return False
    
    def send_to_success_queue(self, message_data: Dict[str, Any]):
        """
        Success mesajını chrome.db.queue.success queue'suna gönder
        
        Args:
            message_data: Orijinal mesaj verisi
        """
        try:
            # Yeni bağlantı oluştur
            params = self._get_connection_params()
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            # Success queue'yu declare et
            channel.queue_declare(queue=self.success_queue_name, durable=True)
            
            # Scraped data'yı null olmayan değerlerle filtrele
            scraped_data_raw = message_data.get('scraped_data', {})
            # Eğer list ise boş dict kullan
            if isinstance(scraped_data_raw, list):
                scraped_data_raw = {}
            scraped_data = self.filter_non_null_data(scraped_data_raw)
            
            # Success mesajını hazırla - tüm önemli verileri ekle
            success_data = {
                'original_message': message_data,
                'scraped_data': scraped_data,
                'job_id': message_data.get('job_id'),
                'product_id': message_data.get('product_id'),
                'company_id': message_data.get('company_id'),
                'url': message_data.get('url'),
                'mpn': message_data.get('npm') or message_data.get('mpn'),
                'attributes': message_data.get('attributes', []),
                'success_timestamp': datetime.now(TURKEY_TZ).isoformat(),
                'queue_name': self.queue_name
            }
            
            # Mesajı gönder
            channel.basic_publish(
                exchange='',
                routing_key=self.success_queue_name,
                body=json.dumps(success_data, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json'
                )
            )
            
            channel.close()
            connection.close()
            
            print(f"📤 Başarılı mesaj success queue'suna gönderildi - Queue: {self.success_queue_name}, Job ID: {message_data.get('job_id')}")
            return True
        
        except Exception as e:
            print(f"❌ Success queue'ya gönderme hatası: {e}")
            traceback.print_exc()
            return False
    
    def save_to_scraper_data(self, message_data: Dict[str, Any], db: Session):
        """
        Başarılı mesajı scraper_data tablosuna kaydet
        
        Args:
            message_data: RabbitMQ'dan gelen mesaj verisi
            db: Database session
        """
        try:
            # data_id'yi process_id olarak al
            process_id = message_data.get('data_id')
            job_id = message_data.get('job_id')
            
            # Eğer data_id yoksa, original_message içinde olabilir
            if not process_id:
                original_message = message_data.get('original_message', {})
                process_id = original_message.get('data_id')
                if not job_id:
                    job_id = original_message.get('job_id')
            
            # Eğer hala yoksa, kaydetme
            if not process_id:
                print(f"⚠️ ScraperData: process_id (data_id) bulunamadı, kayıt atlandı")
                return
            
            # scraped_data kontrolü - eğer boşsa kaydetme
            scraped_data_raw = message_data.get('scraped_data', {})
            original_message = message_data.get('original_message', {})
            scraped_data = scraped_data_raw if scraped_data_raw else original_message.get('scraped_data', {})
            
            # scraped_data boş mu kontrol et
            is_scraped_data_empty = (
                scraped_data is None or
                (isinstance(scraped_data, dict) and len(scraped_data) == 0) or
                (isinstance(scraped_data, list) and len(scraped_data) == 0)
            )
            
            if is_scraped_data_empty:
                print(f"⚠️ ScraperData: scraped_data boş, kayıt atlandı - Process ID: {process_id}")
                return
            
            # Mesajın tamamını JSON olarak kaydet
            data_json = json.dumps(message_data, ensure_ascii=False)
            
            # ScraperData kaydı oluştur
            scraper_data = ScraperData(
                process_id=process_id,
                job_id=job_id,
                data=data_json,
                created_at=datetime.now(TURKEY_TZ)
            )
            
            db.add(scraper_data)
            db.commit()
            
            print(f"💾 ScraperData kaydedildi - Process ID: {process_id}, Job ID: {job_id}")
            
        except Exception as e:
            print(f"❌ ScraperData kayıt hatası: {e}")
            traceback.print_exc()
            # Hata durumunda rollback yap ama ana işlemi etkileme
            try:
                db.rollback()
            except Exception:
                pass
            raise
    
    def filter_non_null_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Null değerleri filtrele (recursive)
        Null, empty string, ve empty array değerleri kaldırılır
        
        Args:
            data: Filtrelenecek veri (dict veya list olabilir)
        
        Returns:
            Filtrelenmiş veri (dict)
        """
        # Eğer data list ise, boş dict döndür
        if isinstance(data, list):
            return {}
        
        # Eğer data dict değilse, boş dict döndür
        if not isinstance(data, dict):
            return {}
        
        filtered = {}
        
        for key, value in data.items():
            # Null kontrolü
            if value is None:
                continue
            
            # Boş string kontrolü
            if value == '':
                continue
            
            # Boş array kontrolü
            if isinstance(value, list) and len(value) == 0:
                continue
            
            # Eğer nested dict ise, recursive olarak filtrele
            if isinstance(value, dict) and len(value) > 0:
                filtered_value = self.filter_non_null_data(value)
                # Eğer filtreleme sonrası boş kaldıysa ekleme
                if len(filtered_value) > 0:
                    filtered[key] = filtered_value
            else:
                # Normal değer, ekle
                filtered[key] = value
        
        return filtered
    
    def purge_queue(self):
        """
        chrome.queue.completed queue'sunu temizle (tüm mesajları sil)
        
        Returns:
            Purge edilen mesaj sayısı
        """
        try:
            # Bağlantı kur
            params = self._get_connection_params()
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            # Queue'yu declare et
            channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Queue'yu purge et
            result = channel.queue_purge(queue=self.queue_name)
            purged_count = result.method.message_count
            
            channel.close()
            connection.close()
            
            print(f"🧹 Chrome Completed Queue purged - Queue: {self.queue_name}, Purged: {purged_count}")
            return purged_count
        
        except Exception as e:
            print(f"❌ Queue purge hatası: {e}")
            traceback.print_exc()
            raise


if __name__ == "__main__":
    print("🔌 Chrome Completed Queue Worker başlatılıyor...")
    worker = ChromeCompletedQueueWorker()
    worker.consume()

