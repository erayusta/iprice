# parsers/base.py
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from abc import ABC, abstractmethod
from typing import Dict, Any


class ParserInterface(ABC):
    def __init__(self):
        self.db_connection = self._get_db_connection()

    def _get_db_connection(self):
        """Ortak database bağlantısı"""
        try:
            connection = psycopg2.connect(
                host=os.getenv('SHARED_DB_HOST', '10.20.50.16'),
                database=os.getenv('SHARED_DB_NAME', 'ipricetest'),
                user=os.getenv('SHARED_DB_USER', 'ipricetestuser'),
                password=os.getenv('SHARED_DB_PASS', 'YeniSifre123!'),
                port=os.getenv('SHARED_DB_PORT', '5432')
            )
            return connection
        except Exception as e:
            print(f" DB bağlantı hatası: {e}")
            return None

    def _get_company_attributes(self, company_id: int) -> Dict[str, Any]:
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    a.name, 
                    ca.value as xpath,
                    ca.type as selector_type
                FROM company_attributes ca
                INNER JOIN attributes a ON ca.attribute_id = a.id
                WHERE ca.company_id = %s
            """

            cursor.execute(query, (company_id,))
            results = cursor.fetchall()  # fetchone değil fetchall
            cursor.close()

            if results:
                attributes = {}
                for row in results:
                    attributes[row['name']] = {
                        'xpath': row['xpath'],
                        'selector_type': row['selector_type']
                    }
                return attributes
            else:
                return None

        except Exception as e:
            print(f" DB hatası: {e}")
            return None

    def _error_result(self, url: str, company_id: int, application_id: int, server_id: int,
                      error: str, http_status_code: int = 500, job_data: dict = None) -> Dict[str, Any]:
        """Ortak hata sonucu"""
        result = {
            'url': url,
            'company_id': company_id,
            'application_id': application_id,
            'server_id': server_id,
            'status': 'error',
            'parser_used': self.get_parser_name(),
            'error': error,
            'http_status_code': http_status_code,
            'timestamp': time.time()
        }
        
        # Job data'dan ek alanları ekle
        if job_data:
            result['job_id'] = job_data.get('job_id')
            result['product_id'] = job_data.get('product_id')
            result['npm'] = job_data.get('npm')
            result['server_name'] = job_data.get('server_name')
            result['screenshot'] = job_data.get('screenshot', False)
            result['marketplace'] = job_data.get('marketplace', False)
        
        # 🔥 HATAYI LOGS TABLOSUNA KAYDET
        print(f"🔥 Hata loglama başlıyor: {error[:50]}...")
        self._log_error_to_db(url, company_id, error, job_data)
        
        return result
    
    def _log_error_to_db(self, url: str, company_id: int, error: str, job_data: dict = None):
        """Hatayı logs tablosuna kaydet"""
        try:
            if not self.db_connection:
                print(f"⚠️ DB bağlantısı yok, log kaydedilemedi: {error}")
                return
            
            cursor = self.db_connection.cursor()
            
            # Job data'dan bilgileri al
            process_id = job_data.get('product_id', 0) if job_data else 0
            mpn = job_data.get('npm', 'unknown') if job_data else 'unknown'
            
            # Hata tipini belirle
            if 'selector' in error.lower() or 'element bulunamadı' in error.lower():
                error_type = 1  # Selector hatası
            elif 'timeout' in error.lower():
                error_type = 2  # Timeout hatası  
            elif 'connection' in error.lower():
                error_type = 3  # Bağlantı hatası
            else:
                error_type = 4  # Genel hata
            
            # Log mesajını hazırla
            log_message = f"[{self.get_parser_name()}] {error} | URL: {url}"
            
            # Logs tablosuna kaydet
            query = """
                INSERT INTO logs (process_id, company_id, mpn, status, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            cursor.execute(query, (process_id, company_id, mpn, error_type, log_message))
            self.db_connection.commit()
            cursor.close()
            
            print(f"📝 Hata logs tablosuna kaydedildi: {error_type} - {log_message[:100]}")
            
        except Exception as e:
            print(f"❌ Log kayıt hatası: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def _success_result(self, url: str, company_id: int, application_id: int, server_id: int, 
                        results: Dict[str, Any], http_status_code: int = 200, 
                        job_data: dict = None) -> Dict[str, Any]:
        """Ortak başarı sonucu - results artık tüm attribute'ları içeriyor"""
        result = {
            'url': url,
            'company_id': company_id,
            'application_id': application_id,
            'server_id': server_id,
            'status': 'success',
            'parser_used': self.get_parser_name(),
            'results': results,  # Tüm attribute sonuçları
            'http_status_code': http_status_code,
            'timestamp': time.time()
        }
        
        # Job data'dan ek alanları ekle
        if job_data:
            result['job_id'] = job_data.get('job_id')
            result['product_id'] = job_data.get('product_id')
            result['npm'] = job_data.get('npm')
            result['server_name'] = job_data.get('server_name')
            result['screenshot'] = job_data.get('screenshot', False)
            result['marketplace'] = job_data.get('marketplace', False)
            # 🔥 ÖNEMLİ: Attributes bilgisini de ekle (DB kayıt için gerekli)
            result['attributes'] = job_data.get('attributes', [])
        
        return result

    @abstractmethod
    def parse(self, url: str, company_id: int, application_id: int, server_id: int) -> Dict[str, Any]:
        """Ana parsing metodu - her parser implement etmeli"""
        pass

    @abstractmethod
    def get_parser_name(self) -> str:
        """Parser adını döndür"""
        pass