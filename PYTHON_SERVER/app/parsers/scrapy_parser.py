import json
import subprocess
import tempfile
import os
import time
import cloudscraper
from .base import ParserInterface
from typing import Dict, Any
from app.services.ProxyManager import get_proxy_manager
from app.helper.get_random_agents import get_random_user_agent


class ScrapyParser(ParserInterface):
    def get_parser_name(self) -> str:
        return 'scrapy'

    def parse(self, url: str, company_id: int, application_id: int, server_id: int, job_data: dict = None) -> Dict[
        str, Any]:
        try:
            print(f"🕷️  Scrapy parsing başladı: Company: {company_id}, URL: {url}")

            # Attribute'ları job_data'dan al
            if not job_data or 'attributes' not in job_data:
                return self._error_result(url, company_id, application_id, server_id,
                                          "Job data'da attributes bulunamadı")
            
            raw_attributes = job_data.get('attributes', [])
            
            if not raw_attributes:
                return self._error_result(url, company_id, application_id, server_id,
                                          "Attributes listesi boş")
            
            # Attribute'ları dönüştür (yeni yapı -> parser formatı)
            attributes = self._transform_attributes(raw_attributes)
            
            print(f"📋 Attributes dönüştürüldü: {len(attributes)} attribute")

            # ÖNCELİKLE Spider'ı çalıştır (normal Scrapy)
            result = self._run_spider_subprocess(url, attributes, job_data)

            # Eğer Cloudflare/bot koruması tespit edilirse cloudscraper ile tekrar dene
            if not result.get('success') and result.get('http_status_code') in [403, 503]:
                print(f"⚠️ Anti-bot koruması tespit edildi (HTTP {result.get('http_status_code')})")
                print(f"🛡️ Cloudscraper ile tekrar deneniyor...")
                result = self._run_cloudscraper(url, attributes, job_data)

            # Job ID'yi ekle
            result['job_id'] = job_data.get('job_id')
            result['product_id'] = job_data.get('product_id')
            result['npm'] = job_data.get('npm')

            if result.get('success'):
                return self._success_result(url, company_id, application_id, server_id,
                                            result.get('results', {}),
                                            result.get('http_status_code'),
                                            job_data)
            else:
                return self._error_result(url, company_id, application_id, server_id,
                                          result.get('error'), 
                                          result.get('http_status_code'),
                                          job_data)

        except Exception as e:
            print(f"❌ Parser exception: {e}")
            import traceback
            traceback.print_exc()
            return self._error_result(url, company_id, application_id, server_id, str(e), job_data=job_data)
    
    def _transform_attributes(self, raw_attributes: list) -> Dict[str, Any]:
        """
        Yeni attribute yapısını parser'ın beklediği formata çevir
        
        Input: [
            {
                "attributes_id": 1,
                "attributes_name": "price",
                "attributes_type": "class",
                "attributes_value": ".p-price span"
            }
        ]
        
        Output: {
            "price": {
                "xpath": ".p-price span" veya "selector": ".p-price span",
                "selector_type": "css" veya "xpath"
            }
        }
        """
        attributes = {}
        
        for attr in raw_attributes:
            attr_name = attr.get('attributes_name')
            attr_type = attr.get('attributes_type')  # "class", "xpath", "id", vb.
            attr_value = attr.get('attributes_value')
            
            if not attr_name or not attr_value:
                continue
            
            # Attribute type'a göre selector type'ı belirle
            if attr_type == 'xpath':
                attributes[attr_name] = {
                    'xpath': attr_value,
                    'selector_type': 'xpath'
                }
            else:  # class, id, css gibi
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'css'
                }
        
        return attributes

    def _run_cloudscraper(self, url: str, attributes: Dict[str, Any], job_data: dict = None) -> Dict[str, Any]:
        """
        Cloudscraper ile Cloudflare bypass yaparak scrape et
        
        Args:
            url: Scrape edilecek URL
            attributes: Parse edilecek attribute'lar
            job_data: Job metadata
            
        Returns:
            Parse result
        """
        try:
            # Cloudscraper session oluştur
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
            
            # Proxy ayarları - job_data'dan dinamik proxy
            proxy_manager = get_proxy_manager()
            proxy_url = proxy_manager.get_proxy(job_data=job_data)
            
            proxies = None
            if proxy_url:
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                print(f"🔒 Cloudscraper proxy kullanılıyor: {proxy_url}")
            
            # Headers
            headers = {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Request gönder
            print(f"🛡️ Cloudscraper ile istek gönderiliyor: {url}")
            response = scraper.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=30,
                allow_redirects=True
            )
            
            http_status = response.status_code
            print(f"📡 Cloudscraper HTTP Status: {http_status}")
            
            # Hata kontrolü
            if http_status in [403, 401, 429, 503]:
                return {
                    'success': False,
                    'error': f'HTTP {http_status} - Access denied (cloudscraper)',
                    'http_status_code': http_status
                }
            
            if not (200 <= http_status < 300):
                return {
                    'success': False,
                    'error': f'HTTP Error: {http_status}',
                    'http_status_code': http_status
                }
            
            # BeautifulSoup ile parse
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Attribute'ları çıkar
            results = {}
            error_count = 0
            
            for attr_name, attr_data in attributes.items():
                selector = attr_data.get('xpath') or attr_data.get('selector', '')
                selector_type = attr_data.get('selector_type', 'xpath')
                meta_value = attr_data.get('meta_value', '')
                
                # 🆕 Meta/JSON tipindeyse özel işlem
                if selector_type == 'meta' and meta_value:
                    print(f"  🔍 Meta/JSON değeri alınıyor (Scrapy): {meta_value}")
                    try:
                        # HTML'den meta tag ara
                        meta_property = soup.find('meta', {'property': meta_value})
                        meta_name = soup.find('meta', {'name': meta_value})
                        
                        if meta_property:
                            meta_result = meta_property.get('content')
                            print(f"  ✅ Meta tag (property) bulundu: {meta_result}")
                            results[attr_name] = str(meta_result)
                            continue
                        elif meta_name:
                            meta_result = meta_name.get('content')
                            print(f"  ✅ Meta tag (name) bulundu: {meta_result}")
                            results[attr_name] = str(meta_result)
                            continue
                        else:
                            # Regex ile JSON ara
                            import re
                            pattern = f'"{meta_value}"\\s*:\\s*([0-9.]+)'
                            match = re.search(pattern, response.text, re.IGNORECASE)
                            if match:
                                meta_result = match.group(1)
                                print(f"  ✅ JSON'dan bulundu: {meta_result}")
                                results[attr_name] = str(meta_result)
                                continue
                        
                        print(f"  ⚠️ Meta/JSON değeri bulunamadı: {meta_value}")
                        results[attr_name] = None
                        error_count += 1
                    except Exception as e:
                        print(f"  ⚠️ Meta/JSON hatası: {str(e)[:100]}")
                        results[attr_name] = None
                        error_count += 1
                    
                    continue
                
                if not selector:
                    results[attr_name] = None
                    error_count += 1
                    continue
                
                try:
                    # XPath için lxml gerekir, CSS selector kullanabiliriz
                    if selector_type == 'css' or selector_type != 'xpath':
                        # CSS selector - artık ::text suffix'i yok, direkt kullan
                        element = soup.select_one(selector)
                        if element:
                            value = element.get_text(strip=True)
                            results[attr_name] = value
                            print(f"  ✓ {attr_name}: {value}")
                        else:
                            results[attr_name] = None
                            error_count += 1
                            print(f"  ✗ {attr_name}: Element bulunamadı")
                    else:
                        # XPath desteği için lxml kullan - artık /text() suffix'i yok, direkt kullan
                        from lxml import html
                        tree = html.fromstring(response.text)
                        elements = tree.xpath(selector)
                        
                        if elements:
                            if isinstance(elements[0], str):
                                results[attr_name] = elements[0].strip()
                            else:
                                results[attr_name] = elements[0].text_content().strip()
                            print(f"  ✓ {attr_name}: {results[attr_name]}")
                        else:
                            results[attr_name] = None
                            error_count += 1
                            print(f"  ✗ {attr_name}: XPath sonuç vermedi")
                            
                except Exception as e:
                    error_msg = str(e)
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    print(f"  ⚠️ {attr_name} parse hatası: {error_msg}")
                    results[attr_name] = None
                    error_count += 1
            
            # Eğer tüm attribute'lar başarısız olduysa hata döndür
            if error_count == len(attributes) and error_count > 0:
                # Hangi attribute'ların bulunamadığını belirle
                failed_attrs = [attr_name for attr_name, value in results.items() if not value]
                return {
                    'success': False,
                    'error': f'Cloudscraper: Attribute\'lar parse edilemedi: {", ".join(failed_attrs)} ({error_count}/{len(attributes)})',
                    'http_status_code': http_status  # Site erişilebilir, sadece attribute'lar bulunamadı
                }
            
            print(f"✅ Cloudscraper başarılı: {results}")
            return {
                'success': True,
                'results': results,
                'http_status_code': http_status
            }
            
        except Exception as e:
            print(f"❌ Cloudscraper hatası: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Cloudscraper error: {str(e)}',
                'http_status_code': 500
            }

    def _run_spider_subprocess(self, url: str, attributes: Dict[str, Any], job_data: dict = None) -> Dict[str, Any]:
        """Subprocess'te scrapy çalıştır - Reactor problemi yok"""
        result_file = None  # Initialize to prevent UnboundLocalError in finally
        try:
            # Proxy manager'dan proxy al
            proxy_manager = get_proxy_manager()
            print(f"🔍 Debug - job_data: {job_data}")
            proxy_url = proxy_manager.get_proxy(job_data=job_data)
            print(f"🔍 Debug - proxy_url: {proxy_url}")
            
            # Temp file'lar oluştur
            result_file = f"/tmp/scrapy_result_{int(time.time())}.json"

            # Proxy ayarlarını hazırla
            proxy_meta = ""
            if proxy_url:
                proxy_meta = f", 'proxy': '{proxy_url}'"
                print(f"🔒 Scrapy proxy kullanılıyor: {proxy_url}")

            # Attribute sayısını hesapla (template'de kullanmak için)
            attr_count = len(attributes)
            
            # Scrapy script'i oluştur
            spider_script = f'''
import scrapy
import json
import sys
from scrapy.crawler import CrawlerProcess

class TempSpider(scrapy.Spider):
    name = 'temp_spider'
    start_urls = ["{url}"]

    custom_settings = {{
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 3,
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'CRITICAL',
        'LOG_ENABLED': False,
        'TELNETCONSOLE_ENABLED': False,
        'RETRY_ENABLED': False,
        'RETRY_TIMES': 0,
        'DOWNLOAD_TIMEOUT': 10,
        'DNSCACHE_ENABLED': False,
        'REDIRECT_ENABLED': True,
        'HTTPPROXY_ENABLED': True
    }}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.errback,
                dont_filter=True,
                meta={{'download_timeout': 10, 'dont_retry': True{proxy_meta}}}
            )

    def parse(self, response):
        try:
            http_status = response.status
            print(f"🌐 Parse çalıştı - HTTP Status: {{http_status}} - URL: {{response.url}}")

            if http_status in [403, 401, 429, 503]:
                result = {{
                    'success': False,
                    'error': f'HTTP {{http_status}} - Access denied',
                    'http_status_code': http_status
                }}
                self._save_result(result)
                return

            if not (200 <= http_status < 300):
                result = {{
                    'success': False,
                    'error': f'HTTP Error: {{http_status}}',
                    'http_status_code': http_status
                }}
                self._save_result(result)
                return

            # Veri çıkarma
            attributes = {json.dumps(attributes)}
            results = {{}}
            error_count = 0

            for attr_name, attr_data in attributes.items():
                selector = attr_data.get('xpath') or attr_data.get('selector', '')
                selector_type = attr_data.get('selector_type', 'xpath')

                if not selector:
                    results[attr_name] = None
                    error_count += 1
                    continue

                if selector_type == 'xpath':
                    value = response.xpath(selector).get()
                else:
                    value = response.css(selector).get()

                results[attr_name] = value.strip() if value else None
                
                if not value:
                    error_count += 1

            # Eğer tüm attribute'lar başarısız olduysa hata döndür
            total_attrs = {attr_count}
            if error_count == total_attrs and error_count > 0:
                # Hangi attribute'ların bulunamadığını belirle
                failed_attrs = [attr_name for attr_name, value in results.items() if not value]
                error_msg = f'Scrapy: Attribute\\'lar parse edilemedi: {", ".join(failed_attrs)} ({{error_count}}/{{total_attrs}})'
                result = {{
                    'success': False,
                    'error': error_msg,
                    'http_status_code': http_status  # Site erişilebilir, sadece attribute'lar bulunamadı
                }}
                self._save_result(result)
                return

            result = {{
                'success': True,
                'results': results,
                'http_status_code': http_status
            }}
            self._save_result(result)

        except Exception as e:
            result = {{
                'success': False,
                'error': str(e),
                'http_status_code': getattr(response, 'status', 500)
            }}
            self._save_result(result)

    def errback(self, failure):
        try:
            if hasattr(failure.value, 'response') and failure.value.response:
                status_code = failure.value.response.status
                error_msg = f'HTTP {{status_code}} - Access denied (from errback)'
            else:
                status_code = 0
                error_msg = f'Network error: {{str(failure.value)}}'

            result = {{
                'success': False,
                'error': error_msg,
                'http_status_code': status_code
            }}
            self._save_result(result)
        except Exception as e:
            result = {{
                'success': False,
                'error': f'Error callback failed: {{str(e)}}',
                'http_status_code': 0
            }}
            self._save_result(result)

    def _save_result(self, result):
        with open("{result_file}", "w") as f:
            json.dump(result, f)

# Process başlat
try:
    process = CrawlerProcess()
    process.crawl(TempSpider)
    process.start()
except Exception as e:
    # Hata durumunda sonuç kaydet
    with open("{result_file}", "w") as f:
        json.dump({{"success": False, "error": str(e), "http_status_code": 500}}, f)
'''

            # Script'i çalıştır
            print(f"🚀 Subprocess scrapy başlatılıyor...")

            result = subprocess.run([
                'python3', '-c', spider_script
            ],
                capture_output=True,
                text=True,
                timeout=30,  # 30 saniye timeout
                cwd='/app'  # Working directory
            )

            # Sonucu oku
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    spider_result = json.load(f)

                # Temp file'ı temizle
                os.remove(result_file)

                print(f"✅ Subprocess tamamlandı: {spider_result}")
                return spider_result
            else:
                print(f"❌ Result file bulunamadı")
                return {
                    'success': False,
                    'error': 'No result file found',
                    'http_status_code': 500
                }

        except subprocess.TimeoutExpired:
            print(f"⏰ Subprocess timeout")
            return {
                'success': False,
                'error': 'Subprocess timeout',
                'http_status_code': 408
            }
        except Exception as e:
            print(f"💥 Subprocess hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'http_status_code': 500
            }
        finally:
            # Cleanup
            if os.path.exists(result_file):
                try:
                    os.remove(result_file)
                except:
                    pass