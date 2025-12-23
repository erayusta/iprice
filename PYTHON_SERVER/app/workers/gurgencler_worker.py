# workers/gurgencler_worker.py
"""
🔥 Gurgencler Worker
====================
Gurgencler.com.tr için özel HTTP tabanlı worker

Queue: gurgencler.queue
Success: save.queue (DB kayıt için)
Error: gurgencler.queue.error

Özellikler:
- HTTP request kullanır (Selenium değil)
- HTML parsing (BeautifulSoup)
- unit_sale_price = 0 kontrolü (stok yok)
- BrightData proxy desteği
"""

from typing import Dict, Any
import sys
import requests
import os
from urllib.parse import urlparse

sys.path.append('/app')
from .base_worker import BaseWorker
from app.services.ProxyManager import get_proxy_manager

# HTTP session (connection pooling için) - class dışında tanımla
_http_session = None

def get_http_session():
    """HTTP session singleton - connection pooling için"""
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        # Connection pool ayarları
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=2
        )
        _http_session.mount('http://', adapter)
        _http_session.mount('https://', adapter)
    return _http_session


class GurgenclerWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self._db_initialized = False
        self.db = None
    
    def _initialize_db(self):
        """Database bağlantısını lazy load et"""
        if not self._db_initialized:
            try:
                from app.database import SessionLocal
                from app.model.Attribute import Attribute
                from app.model.AttributeValue import AttributeValue
                
                self.db = SessionLocal()
                self.Attribute = Attribute
                self.AttributeValue = AttributeValue
                self._db_initialized = True
                print("✅ GurgenclerWorker: Database bağlantısı kuruldu")
            except Exception as e:
                print(f"❌ GurgenclerWorker: Database bağlantı hatası: {e}")
                raise
    
    def _get_attributes_from_db(self, company_id: int) -> list:
        """Company ID'ye göre attributes'ları veritabanından çek"""
        try:
            self._initialize_db()
            
            # AttributeValue tablosundan company_id'ye göre attributes'ları çek
            from sqlalchemy import text
            
            query = text("""
                SELECT 
                    av.company_id,
                    av.attributes_id,
                    a.attributes_name,
                    a.attributes_type,
                    av.attributes_value
                FROM attribute_value av
                JOIN attributes a ON av.attributes_id = a.attributes_id
                WHERE av.company_id = :company_id
                ORDER BY av.attributes_id
            """)
            
            result = self.db.execute(query, {"company_id": company_id})
            rows = result.fetchall()
            
            attributes = []
            for row in rows:
                attributes.append({
                    'company_id': row[0],
                    'attributes_id': row[1],
                    'attributes_name': row[2],
                    'attributes_type': row[3],
                    'attributes_value': row[4]
                })
            
            print(f"✅ DB'den {len(attributes)} adet attribute çekildi (company_id: {company_id})")
            return attributes
            
        except Exception as e:
            print(f"❌ Attribute DB hatası: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_queue_name(self) -> str:
        return 'gurgencler.queue'

    def process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gurgencler job'ını işle"""
        try:
            # Job verilerini al
            url = job_data['url']
            company_id = job_data['company_id']
            application_id = job_data['application_id']
            server_id = job_data['server_id']
            job_id = job_data.get('job_id')
            product_id = job_data.get('product_id')
            npm = job_data.get('npm')
            
            print(f"🔥 Gurgencler Job işleniyor - Job ID: {job_id}, Product ID: {product_id}, URL: {url}")
            
            # 🔍 Attributes kontrolü - yoksa DB'den çek
            if 'attributes' not in job_data or not job_data['attributes']:
                print(f"⚠️ Job data içinde attributes YOK, DB'den çekiliyor (company_id: {company_id})")
                attributes = self._get_attributes_from_db(company_id)
                job_data['attributes'] = attributes
            else:
                print(f"✅ Job data içinde {len(job_data['attributes'])} adet attributes var")

            # HTTP isteği ile parse et
            result = self._process_with_http_request(url, company_id, application_id, server_id, job_data)

            # Başarı durumuna göre queue'ye gönder
            if result.get('status') == 'success':
                # ✅ Parsing başarılı → save.queue'ye gönder (DB kayıt için)
                self._publish_to_save_queue(result)
                print(f"✅ Gurgencler parsing başarılı, save.queue'ye gönderildi: {url}")
            else:
                # ❌ Parsing hatası → gurgencler.queue.error'a gönderilecek (base_worker halleder)
                print(f"❌ Gurgencler parsing hatası: {result.get('error')}")
            
            return result

        except Exception as e:
            print(f"❌ Gurgencler Job işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
            error_result = {
                'status': 'error',
                'error': str(e),
                'job_id': job_data.get('job_id'),
                'product_id': job_data.get('product_id'),
                'url': job_data.get('url'),
                'company_id': job_data.get('company_id'),
                'parser_used': 'gurgencler_http'
            }
            
            return error_result

    def _process_with_http_request(self, url: str, company_id: int, application_id: int, 
                                   server_id: int, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        HTTP isteği ile sayfa içeriğini al ve parse et (Gurgencler.com.tr için)
        """
        try:
            print(f"🌐 HTTP isteği başladı: {url}")
            
            # Headers - gerçek tarayıcı gibi görün
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Proxy ayarları - BrightData kullan
            proxy_manager = get_proxy_manager()
            proxy_url = proxy_manager.get_proxy(job_data=job_data)
            
            proxies = None
            if proxy_url:
                # Proxy URL formatı: user:pass@host:port -> http://user:pass@host:port
                if not proxy_url.startswith('http'):
                    proxy_url = f"http://{proxy_url}"
                
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                print(f"🔒 Proxy kullanılıyor: {proxy_url}")
            else:
                print(f"📴 Proxy kullanılmıyor")
            
            # HTTP isteği at - Session kullan (connection pooling)
            session = get_http_session()
            response = session.get(url, headers=headers, proxies=proxies, timeout=10, verify=False)
            response.raise_for_status()
            
            # Encoding kontrolü - apparent_encoding YAVAŞ, direkt utf-8 kullan
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            print(f"✅ HTTP isteği başarılı - Status: {response.status_code}, Encoding: {response.encoding}")
            print(f"📄 Content Length: {len(response.text)} karakter")
            
            # HTML'i parse et
            html_content = response.text
            
            # Attributes'ları al (process_job'da zaten kontrol edildi ve DB'den çekildi)
            raw_attributes = job_data.get('attributes', [])
            
            if not raw_attributes:
                return self._create_error_result(url, company_id, application_id, server_id,
                                                "Attributes listesi boş (DB'de de yok)", job_data)
            
            # Parse HTML ve attribute'ları çıkar
            results = self._parse_html_attributes(html_content, raw_attributes)
            
            print(f"📊 HTTP Parse sonuçları: {results}")
            
            # 🔍 Gürgençler için özel kontrol: unit_sale_price = 0 -> Stok yok
            unit_sale_price = results.get('unit_sale_price')
            if unit_sale_price is not None:
                try:
                    price_value = float(unit_sale_price)
                    if price_value == 0:
                        print(f"⚠️ Gürgençler: unit_sale_price = 0 tespit edildi -> Stok yok")
                        return self._create_error_result(url, company_id, application_id, server_id,
                                                        "Stok yok", response.status_code, job_data)
                    
                    # ✅ Stok varsa (price > 0), results'a 'price' key'ini de ekle (ProductHistory için)
                    results['price'] = unit_sale_price
                    print(f"💰 Gürgençler: unit_sale_price ({unit_sale_price}) 'price' olarak eklendi")
                    
                except (ValueError, TypeError):
                    pass  # Parse edilemeyen değerleri skip et
            
            # Başarılı result oluştur
            return self._create_success_result(url, company_id, application_id, server_id,
                                              results, response.status_code, job_data)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP isteği hatası: {e}")
            return self._create_error_result(url, company_id, application_id, server_id,
                                           f"HTTP isteği hatası: {str(e)}", 500, job_data)
        except Exception as e:
            print(f"❌ HTTP processing hatası: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(url, company_id, application_id, server_id,
                                           f"HTTP processing hatası: {str(e)}", 500, job_data)

    def _parse_html_attributes(self, html_content: str, raw_attributes: list) -> Dict[str, Any]:
        """
        HTML içeriğinden attribute'ları parse et
        """
        try:
            from bs4 import BeautifulSoup
            import re
            
            # BeautifulSoup'u sadece meta type olmayanlar için oluştur
            soup = None
            needs_soup = any(
                str(attr.get('attributes_type', '')).lower() != 'meta' 
                for attr in raw_attributes 
                if attr.get('attributes_name') and attr.get('attributes_value')
            )
            
            if needs_soup:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            results = {}
            
            for attr in raw_attributes:
                attr_name = attr.get('attributes_name')
                attr_type = attr.get('attributes_type')
                attr_value = attr.get('attributes_value')
                
                if not attr_name or not attr_value:
                    continue
                
                print(f"🔍 Parsing: {attr_name} (type: {attr_type}, value: {attr_value})")
                
                # Meta/JSON tipi - HTML'den çıkar (soup gerekmez, regex kullanılır)
                if str(attr_type).lower() == 'meta':
                    meta_result = self._extract_meta_from_html(html_content, soup, attr_value)
                    results[attr_name] = meta_result
                    print(f"  {'✅' if meta_result else '❌'} {attr_name}: {meta_result}")
                    continue
                
                # Soup yoksa (sadece meta varsa), diğerlerini skip et
                if not soup:
                    results[attr_name] = None
                    continue
                    
                # CSS Selector
                if attr_value.startswith('.') or attr_value.startswith('#'):
                    element = soup.select_one(attr_value)
                    results[attr_name] = element.get_text(strip=True) if element else None
                    print(f"  {'✅' if element else '❌'} {attr_name}: {results[attr_name] if element else 'Element bulunamadı'}")
                
                # XPath (BeautifulSoup XPath desteklemiyor, CSS'e çevir veya skip)
                elif attr_value.startswith('//') or attr_value.startswith('/'):
                    css_selector = self._xpath_to_css(attr_value)
                    if css_selector:
                        element = soup.select_one(css_selector)
                        results[attr_name] = element.get_text(strip=True) if element else None
                        print(f"  {'✅' if element else '❌'} {attr_name}: {results[attr_name] if element else 'Element bulunamadı (XPath->CSS)'}")
                    else:
                        results[attr_name] = None
                        print(f"  ⚠️ {attr_name}: XPath CSS'e çevrilemedi")
                
                else:
                    # Diğer selector'lar (class, id vb.)
                    element = soup.select_one(attr_value)
                    results[attr_name] = element.get_text(strip=True) if element else None
                    print(f"  {'✅' if element else '❌'} {attr_name}: {results[attr_name] if element else 'Element bulunamadı'}")
            
            return results
            
        except Exception as e:
            print(f"❌ HTML parsing hatası: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _extract_meta_from_html(self, html_content: str, soup, meta_key: str) -> Any:
        """
        HTML'den meta/JSON değer çıkar (Gurgencler için)
        """
        try:
            import re
            import json
            
            # 1. Meta tag'den dene
            if soup:
                meta_tag = soup.find('meta', property=meta_key)
                if meta_tag and meta_tag.get('content'):
                    value = meta_tag.get('content')
                    print(f"    📍 Meta tag'den bulundu: {value}")
                    return value
            
            # 2. window.insider_object.product JSON objesinden çıkar
            # Pattern: window.insider_object.product = {...};
            # İlk önce quick check - meta_key var mı?
            if meta_key in html_content:
                pattern = r'window\.insider_object\.product\s*=\s*(\{[^;]+\});'
                match = re.search(pattern, html_content, re.IGNORECASE)
                
                if match:
                    json_str = match.group(1)
                    print(f"    📍 insider_object.product bulundu, JSON parse ediliyor...")
                    
                    try:
                        # JSON parse et
                        product_data = json.loads(json_str)
                        
                        # İstenen key'i al
                        if meta_key in product_data:
                            value = product_data[meta_key]
                            print(f"    ✅ {meta_key} JSON'dan bulundu: {value}")
                            return str(value)
                    except json.JSONDecodeError:
                        pass  # Regex fallback'e geç
            else:
                print(f"    ⚠️ {meta_key} HTML'de bulunamadı, skip ediliyor")
                return None
            
            # 3. Regex fallback - Sadece en çok kullanılan pattern'leri dene
            # Pattern önceliği: en yaygın olanlar önce (hızlı çıkış için)
            patterns = [
                # 1. Direkt JSON key-value (en yaygın)
                rf'"{re.escape(meta_key)}"\s*:\s*([\"\']?)([0-9.]+)\1',
                # 2. insider_object.product (Gurgencler için)
                rf'insider_object\.product\s*=\s*\{{[^}}]*?"{re.escape(meta_key)}"\s*:\s*([\"\']?)([0-9.]+)\1',
            ]
            
            for pattern_idx, pattern in enumerate(patterns):
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    # Group 2'de değer var (group 1 quote işareti)
                    found_value = match.group(2) if len(match.groups()) > 1 else match.group(1)
                    
                    # Değeri doğrula
                    try:
                        num_value = float(found_value)
                        if 10 <= num_value <= 10000000:  # Makul fiyat aralığı
                            print(f"    ✅ Regex pattern #{pattern_idx} ile bulundu: {found_value}")
                            return str(int(num_value))
                    except:
                        pass
            
            print(f"    ❌ Meta değer bulunamadı: {meta_key}")
            return None
            
        except Exception as e:
            print(f"    ⚠️ Meta extraction hatası: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            return None

    def _xpath_to_css(self, xpath: str) -> str:
        """
        Basit XPath'i CSS selector'a çevir (sadece basit durumlar için)
        """
        # Çok basit dönüşümler
        if xpath.startswith('//'):
            xpath = xpath[2:]
        
        # //div[@class="price"] -> div.price
        import re
        match = re.match(r'(\w+)\[@class=["\']([^"\']+)["\']\]', xpath)
        if match:
            tag, class_name = match.groups()
            return f"{tag}.{class_name.replace(' ', '.')}"
        
        # //div[@id="price"] -> div#price
        match = re.match(r'(\w+)\[@id=["\']([^"\']+)["\']\]', xpath)
        if match:
            tag, id_name = match.groups()
            return f"{tag}#{id_name}"
        
        # Basit tag selector: //div -> div
        if '/' not in xpath and '[' not in xpath:
            return xpath
        
        return None  # Dönüştürülemedi

    def _create_success_result(self, url: str, company_id: int, application_id: int,
                               server_id: int, results: Dict[str, Any], 
                               status_code: int, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Başarılı result oluştur"""
        return {
            'status': 'success',
            'url': url,
            'company_id': company_id,
            'application_id': application_id,
            'server_id': server_id,
            'job_id': job_data.get('job_id'),
            'product_id': job_data.get('product_id'),
            'npm': job_data.get('npm'),
            'http_status': status_code,
            'parser_used': 'gurgencler_http',
            'results': results,
            'attributes': job_data.get('attributes', [])  # Attributes'ları ekle (save_worker için)
        }

    def _create_error_result(self, url: str, company_id: int, application_id: int,
                            server_id: int, error_message: str, 
                            status_code: int = 500, job_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Hata result'u oluştur"""
        return {
            'status': 'error',
            'error': error_message,
            'url': url,
            'company_id': company_id,
            'application_id': application_id,
            'server_id': server_id,
            'job_id': job_data.get('job_id') if job_data else None,
            'product_id': job_data.get('product_id') if job_data else None,
            'npm': job_data.get('npm') if job_data else None,
            'http_status': status_code,
            'parser_used': 'gurgencler_http'
        }


if __name__ == "__main__":
    worker = GurgenclerWorker()
    worker.start_consuming()

