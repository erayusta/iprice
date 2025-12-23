#!/usr/bin/env python3
"""
💾 Save Worker
==============
save.queue'dan mesaj consume eder ve veritabanına kaydeder

Queue: save.queue
Success: save.queue.completed
Error: save.queue.error

Kullanım:
    python -m workers.save_worker
"""

import sys
sys.path.append('/app')

from .base_worker import BaseWorker
from app.services import CallbackService
from typing import Dict, Any
from datetime import datetime
import traceback
import re
from bs4 import BeautifulSoup
from app.helper.llm_price_parser import parse_price_with_llm, get_llm_price_parser


class SaveWorker(BaseWorker):
    """Database save worker - Parse sonuçlarını DB'ye kaydeder"""
    
    def __init__(self):
        super().__init__()
        # Repository'ler lazy load edilecek (import döngüsü önlemek için)
        self._repositories_initialized = False
    
    def _clean_price_value(self, value: str, attr_name: str) -> str:
        """
        Price attribute'ları için değer temizleme
        - TL/₺ işaretlerini kaldır
        - Boşlukları temizle
        - Decimal formatını düzenle: 33.999 -> 33999, 33.999,70 -> 33999.70
        - LLM ile karmaşık formatları parse et
        """
        if not value or not isinstance(value, str):
            return value
        
        # Price attribute'ları kontrol et
        price_attrs = ['price', 'sale_price', 'multi_price', 'sub_price']
        if attr_name.lower() not in price_attrs:
            return value
        
        # 🤖 Önce LLM ile parse et (eğer çalışıyorsa)
        try:
            llm_parser = get_llm_price_parser()
            if llm_parser.is_ollama_running():
                llm_result = parse_price_with_llm(value)
                if llm_result is not None:
                    print(f"🤖 LLM Price Parse: '{value}' → {llm_result}")
                    return str(llm_result)
        except Exception as e:
            print(f"⚠️ LLM parse hatası, normal parsing'e geçiliyor: {e}")
        
        # Normal parsing (fallback)
        
        # TL ve ₺ işaretlerini kaldır
        cleaned = value.replace('TL', '').replace('₺', '').strip()
        
        # Boşlukları temizle
        cleaned = re.sub(r'\s+', '', cleaned)
        
        # Türkçe format: 39.999,00 TL -> 39999.00
        # Önce nokta ile binlik ayıracı, virgül ile decimal ayıracı olan formatı düzelt
        if ',' in cleaned and '.' in cleaned:
            # Format: 39.999,00 -> 39999.00
            parts = cleaned.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')  # Noktaları kaldır (binlik ayıracı)
                decimal_part = parts[1]
                
                # Decimal part boşsa (.00 ekle)
                if not decimal_part:
                    decimal_part = '00'
                # Decimal part'ı 2 haneli yap
                elif len(decimal_part) > 2:
                    decimal_part = decimal_part[:2]
                elif len(decimal_part) == 1:
                    decimal_part = decimal_part + '0'
                
                return f"{integer_part}.{decimal_part}"
        
        # HTML tag'ları temizle (BeautifulSoup ile)
        from bs4 import BeautifulSoup
        cleaned = BeautifulSoup(cleaned, 'html.parser').get_text().strip()
        
        # Virgülsüz formatlar için özel kontrol (64.950 TL -> 64950.00)
        if '.' in cleaned and ',' not in cleaned:
            # Sayısal kısımları ayıkla
            match = re.match(r'(\d+)\.(\d+)', cleaned)
            if match:
                integer_part = match.group(1)
                decimal_part = match.group(2)
                
                # Eğer decimal part 3 karakter ise (950), binlik ayıracı olabilir
                if len(decimal_part) == 3:
                    # 64.950 -> 64950.00 (binlik ayıracı)
                    return f"{integer_part}{decimal_part}.00"
                elif len(decimal_part) == 2:
                    # 64.95 -> 64.95 (decimal)
                    return f"{integer_part}.{decimal_part}"
                elif len(decimal_part) == 1:
                    # 64.9 -> 64.90
                    return f"{integer_part}.{decimal_part}0"
        
        # Virgülü noktaya çevir (decimal format için)
        cleaned = cleaned.replace(',', '.')
        
        # Sayısal kısımları ayıkla
        # Format: 33.999 -> 33999, 33.999.70 -> 33999.70
        match = re.match(r'(\d+)\.(\d+)', cleaned)
        if match:
            integer_part = match.group(1)
            decimal_part = match.group(2)
            
            # Eğer decimal part 2'den fazla karakter ise, 2'ye kısalt
            if len(decimal_part) > 2:
                decimal_part = decimal_part[:2]
            
            return f"{integer_part}.{decimal_part}"
        
        # Sadece integer varsa
        match = re.match(r'(\d+)', cleaned)
        if match:
            return match.group(1)
        
        return cleaned
    
    def _clean_html_css_value(self, value: str) -> str:
        """
        HTML ve CSS kodlarını temizle, sadece metin değerini döndür
        """
        if not value or not isinstance(value, str):
            return value
        
        try:
            # BeautifulSoup ile HTML tag'lerini temizle
            soup = BeautifulSoup(value, 'html.parser')
            cleaned = soup.get_text()
            
            # CSS class'ları ve style attribute'larını temizle
            # Örnek: <span class="price">50.000 TL</span> -> 50.000 TL
            cleaned = re.sub(r'<[^>]*>', '', cleaned)
            
            # Fazla boşlukları temizle
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            # HTML entity'leri decode et
            cleaned = cleaned.replace('&amp;', '&')
            cleaned = cleaned.replace('&lt;', '<')
            cleaned = cleaned.replace('&gt;', '>')
            cleaned = cleaned.replace('&quot;', '"')
            cleaned = cleaned.replace('&#39;', "'")
            cleaned = cleaned.replace('&nbsp;', ' ')
            
            return cleaned
            
        except Exception as e:
            print(f"⚠️ HTML/CSS temizleme hatası: {e}")
            # Hata durumunda orijinal değeri döndür
            return value
    
    def _upsert_to_summary_table(self, job_id: int, product_id: int, company_id: int, 
                                attribute_id: int, mpn: str, value: str, attr_name: str):
        """
        ProductAttributeValueSummary tablosuna UPSERT işlemi
        - Aynı kayıt varsa UPDATE (company_id, attribute_id, product_id, mpn)
        - Yoksa INSERT
        """
        try:
            # Mevcut kaydı kontrol et
            existing_record = self.db.query(self.ProductAttributeValueSummary).filter(
                self.ProductAttributeValueSummary.company_id == company_id,
                self.ProductAttributeValueSummary.attribute_id == attribute_id,
                self.ProductAttributeValueSummary.product_id == product_id,
                self.ProductAttributeValueSummary.mpn == mpn
            ).first()
            
            if existing_record:
                # Eğer job_id aynı ve mevcut value yeni value'den küçükse güncelleme yapma
                if existing_record.job_id == job_id and existing_record.value and value:
                    # Value'ları sayısal olarak karşılaştırmayı dene
                    try:
                        existing_value_num = float(str(existing_record.value).replace(',', '.').replace(' ', ''))
                        new_value_num = float(str(value).replace(',', '.').replace(' ', ''))
                        if existing_value_num < new_value_num:
                            print(f"  ⏭️  ProductAttributeValueSummary: {attr_name} = {value} (SKIP - job_id aynı ve mevcut value daha küçük: {existing_record.value} < {value})")
                            return
                    except (ValueError, AttributeError):
                        # Sayıya çevrilemezse string karşılaştırması yap
                        if str(existing_record.value) < str(value):
                            print(f"  ⏭️  ProductAttributeValueSummary: {attr_name} = {value} (SKIP - job_id aynı ve mevcut value daha küçük: {existing_record.value} < {value})")
                            return
                
                # UPDATE: value ve job_id güncelle
                existing_record.value = value
                existing_record.job_id = job_id
                existing_record.updated_at = datetime.now()
                
                self.db.commit()
                print(f"  🔄 ProductAttributeValueSummary: {attr_name} = {value} (UPDATE)")
            else:
                # INSERT: Yeni kayıt ekle
                summary_record = self.ProductAttributeValueSummary(
                    job_id=job_id,
                    product_id=product_id,
                    company_id=company_id,
                    attribute_id=attribute_id,
                    mpn=mpn,
                    value=value,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.db.add(summary_record)
                self.db.commit()
                print(f"  ➕ ProductAttributeValueSummary: {attr_name} = {value} (INSERT)")
                
        except Exception as e:
            print(f"  ⚠️ ProductAttributeValueSummary hatası ({attr_name}): {e}")
            self.db.rollback()
    
    def _initialize_repositories(self):
        """Repository'leri lazy load et"""
        if not self._repositories_initialized:
            try:
                # Database session
                from app.database import SessionLocal
                self.db = SessionLocal()
                
                # Models
                from app.model.ProductAttributeValue import ProductAttributeValue
                from app.model.ProductAttributeValueSummary import ProductAttributeValueSummary
                from app.model.ProductHistory import ProductHistory
                from app.model.JobLog import JobLog
                
                self.ProductAttributeValue = ProductAttributeValue
                self.ProductAttributeValueSummary = ProductAttributeValueSummary
                self.ProductHistory = ProductHistory
                self.JobLog = JobLog
                
                self._repositories_initialized = True
                print("✅ SaveWorker: Repository'ler yüklendi")
            except Exception as e:
                print(f"❌ SaveWorker: Repository yükleme hatası: {e}")
                raise
    
    def get_queue_name(self) -> str:
        """Consume edilecek queue adı"""
        return 'save.queue'
    
    def process_job(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse sonucunu veritabanına kaydet
        
        Args:
            save_data: Parser worker'dan gelen veri (parse sonucu + job data)
            
        Returns:
            Save result
        """
        try:
            # Repository'leri initialize et
            self._initialize_repositories()
            
            job_id = save_data.get('job_id')
            product_id = save_data.get('product_id')
            url = save_data.get('url')
            
            print(f"💾 DB kayıt başlıyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
            
            # 1. Veritabanı kayıtları
            self._save_to_database(save_data)
            
            # 2. Laravel API'ye callback gönder
            self._send_callback(save_data)
            
            print(f"✅ DB kayıt başarılı - Job ID: {job_id}")
            
            return {
                'status': 'success',
                'job_id': job_id,
                'product_id': product_id,
                'url': url,
                'message': 'Veritabanına başarıyla kaydedildi'
            }
            
        except Exception as e:
            print(f"❌ DB kayıt hatası: {e}")
            traceback.print_exc()
            
            # 🔥 HATAYI LOGS TABLOSUNA KAYDET
            self._log_save_error_to_db(save_data, str(e))
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': save_data.get('job_id'),
                'product_id': save_data.get('product_id'),
                'url': save_data.get('url'),
                'db_error_timestamp': datetime.now().isoformat()
            }
            
            return error_result
    
    def _save_to_database(self, save_data: Dict[str, Any]):
        """
        Veritabanına kayıt işlemleri
        
        1. product_attribute_value tablosuna attribute değerleri
        2. products_history tablosuna tarihçe
        3. crawler_logs tablosuna log
        4. job_logs tablosuna job durumu
        """
        try:
            # Job bilgileri
            job_id = save_data.get('job_id')
            product_id = save_data.get('product_id')
            company_id = save_data.get('company_id')
            application_id = save_data.get('application_id')
            server_id = save_data.get('server_id')
            url = save_data.get('url')
            npm = save_data.get('npm')
            parser_used = save_data.get('parser_used', 'unknown')
            
            # Parse sonuçları
            results = save_data.get('results', {})
            attributes = save_data.get('attributes', [])
            
            print(f"📊 Kayıt edilecek sonuçlar: {results}")
            print(f"📊 Kayıt edilecek attributes: {len(attributes)} adet")
            
            # 1. ProductAttributeValue - Her bir attribute için
            for attr in attributes:
                attr_name = attr.get('attributes_name')
                attr_id = attr.get('attributes_id')
                attr_value = results.get(attr_name)
                
                if attr_value:
                    try:
                        # 🔥 HTML/CSS temizleme (önce)
                        html_cleaned_value = self._clean_html_css_value(str(attr_value))
                        
                        # 🔥 Price temizleme (sonra)
                        final_cleaned_value = self._clean_price_value(html_cleaned_value, attr_name)
                        
                        product_attr_value = self.ProductAttributeValue(
                            job_id=job_id,  # 🔥 Job ID eklendi
                            product_id=product_id,  # 🔥 Product ID eklendi
                            mpn=npm,
                            company_id=company_id,
                            attribute_id=attr_id,
                            value=final_cleaned_value,  # 🔥 HTML/CSS ve Price temizlenmiş değer
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        self.db.add(product_attr_value)
                        print(f"  ✅ ProductAttributeValue: {attr_name} = {final_cleaned_value} (orijinal: {attr_value})")
                        
                        # 🔥 ProductAttributeValueSummary tablosuna UPSERT
                        self._upsert_to_summary_table(
                            job_id=job_id,
                            product_id=product_id,
                            company_id=company_id,
                            attribute_id=attr_id,
                            mpn=npm,
                            value=final_cleaned_value,
                            attr_name=attr_name
                        )
                        
                    except Exception as e:
                        print(f"  ⚠️ ProductAttributeValue hatası ({attr_name}): {e}")
            
            # 2. ProductHistory - Ürün tarihçesi
            try:
                # Price'ı al - önce 'price', yoksa 'unit_sale_price' (Gürgençler için)
                price = results.get('price') or results.get('unit_sale_price')
                stock = results.get('is_stock')
                
                # 🔍 DEBUG: Results içeriğini logla
                print(f"🔍 DEBUG ProductHistory - results keys: {list(results.keys())}")
                print(f"🔍 DEBUG ProductHistory - price from results: {price}")
                print(f"🔍 DEBUG ProductHistory - product_id: {product_id}")
                
                product_history = self.ProductHistory(
                    process_id=product_id,  # product_id yerine process_id kullan
                    price=price,
                    link=url,  # url yerine link kullan
                    mpn=npm,  # npm yerine mpn kullan
                    availability=stock,  # stock yerine availability kullan
                    created_at=datetime.now()
                )
                self.db.add(product_history)
                print(f"  ✅ ProductHistory: price={price}, stock={stock}")
            except Exception as e:
                print(f"  ⚠️ ProductHistory hatası: {e}")
            
            # 3. JobLog - Job durumu
            try:
                job_log = self.JobLog(
                    user_id=1,  # Default user_id
                    company_id=company_id,
                    status='success',  # String değer (enum değil)
                    total_urls='[1]',  # JSON format (integer değil)
                    message=f"Parse completed by {parser_used}",
                    started_at=datetime.now(),
                    finished_at=datetime.now()
                )
                self.db.add(job_log)
                print(f"  ✅ JobLog: company_id={company_id}, status=success")
            except Exception as e:
                print(f"  ⚠️ JobLog hatası: {e}")
            
            # Commit
            self.db.commit()
            print(f"💾 Tüm kayıtlar DB'ye commit edildi")
            
        except Exception as e:
            print(f"❌ DB kayıt hatası: {e}")
            self.db.rollback()
            raise
    
    def _send_callback(self, save_data: Dict[str, Any]):
        """
        Laravel API'ye callback gönder
        
        Args:
            save_data: Save data
        """
        try:
            print(f"📤 Laravel callback hazırlanıyor...")
            
            callback_service = CallbackService.CallbackService()
            
            # Results'tan veriyi çıkar
            results = save_data.get('results', {})
            
            # Callback payload hazırla
            callback_payload = {
                'job_id': save_data.get('job_id'),
                'status': save_data.get('status', 'success'),
                'error': save_data.get('error'),
                'parser_used': save_data.get('parser_used', 'unknown'),
                'http_status_code': save_data.get('http_status_code', 200),
                'url': save_data.get('url'),
                'price': results.get('price'),
                'stock': results.get('is_stock'),
                'timestamp': save_data.get('timestamp')
            }
            
            # Callback gönder
            success = callback_service.send_parsing_result(callback_payload)
            
            if success:
                print(f"✅ Laravel callback başarılı: {save_data.get('url')}")
            else:
                print(f"⚠️ Laravel callback başarısız: {save_data.get('url')}")
                
        except Exception as e:
            print(f"❌ Callback hatası: {e}")
            traceback.print_exc()
            # Callback hatası DB kayıt işlemini etkilememelidir, devam et
    
    def _callback(self, ch, method, properties, body):
        """
        Override base_worker callback
        Save worker için özel callback mantığı
        """
        import json
        
        try:
            save_data = json.loads(body)
            print(f"📥 Save job alındı: {save_data.get('url', 'Unknown')}")
            
            result = self.process_job(save_data)
            
            if result.get('status') == 'success':
                print(f"✅ Save işlemi tamamlandı: {save_data.get('url')}")
                # Başarılı sonucu save.queue.completed'e gönder (orijinal save_data ile)
                completed_payload = {
                    **save_data,  # Orijinal parse sonuçları
                    'save_status': 'completed',
                    'save_timestamp': datetime.now().isoformat(),
                    'save_result': result
                }
                self._publish_result(completed_payload, 'completed')
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f"❌ Save işlemi başarısız: {result.get('error')}")
                # Hatalı sonucu save.queue.error'a gönder (orijinal save_data ile)
                error_payload = {
                    **save_data,  # Orijinal parse sonuçları
                    'save_status': 'error',
                    'save_timestamp': datetime.now().isoformat(),
                    'save_error': result.get('error')
                }
                self._publish_result(error_payload, 'error')
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            print(f"❌ Save worker hatası: {e}")
            traceback.print_exc()
            
            # Hata durumunda error queue'ya gönder (orijinal save_data ile)
            if 'save_data' in locals():
                error_payload = {
                    **save_data,  # Orijinal parse sonuçları
                    'save_status': 'error',
                    'save_timestamp': datetime.now().isoformat(),
                    'save_error': str(e),
                    'error_type': 'worker_exception'
                }
            else:
                # save_data yoksa minimal error payload
                error_payload = {
                    'status': 'error',
                    'error': str(e),
                    'save_status': 'error',
                    'save_timestamp': datetime.now().isoformat(),
                    'error_type': 'worker_exception'
                }
            
            self._publish_result(error_payload, 'error')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def _log_save_error_to_db(self, save_data: Dict[str, Any], error: str):
        """Save worker hatalarını logs tablosuna kaydet"""
        try:
            # Database session
            from app.database import SessionLocal
            db = SessionLocal()
            
            # Job bilgileri
            job_id = save_data.get('job_id', 0)
            product_id = save_data.get('product_id', 0)
            company_id = save_data.get('company_id', 0)
            url = save_data.get('url', 'unknown')
            npm = save_data.get('npm', 'unknown')
            
            # Hata tipini belirle
            if 'connection' in error.lower():
                error_type = 3  # Bağlantı hatası
            elif 'constraint' in error.lower() or 'foreign key' in error.lower():
                error_type = 5  # DB constraint hatası
            else:
                error_type = 4  # Genel hata
            
            # Log mesajını hazırla
            log_message = f"[SAVE_WORKER] {error} | Job: {job_id} | URL: {url}"
            
            # Raw SQL ile logs tablosuna kaydet
            query = """
                INSERT INTO logs (process_id, company_id, mpn, status, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            import psycopg2
            connection = psycopg2.connect(
                host='10.20.50.16',
                database='ipricetest',
                user='ipricetestuser',
                password='YeniSifre123!',
                port='5432'
            )
            
            cursor = connection.cursor()
            cursor.execute(query, (product_id, company_id, npm, error_type, log_message))
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"📝 Save Worker hatası logs tablosuna kaydedildi: {error_type} - {log_message[:100]}")
            
        except Exception as e:
            print(f"❌ Save Worker log kayıt hatası: {e}")


if __name__ == "__main__":
    print("💾 Save Worker başlatılıyor...")
    worker = SaveWorker()
    worker.start_consuming()

