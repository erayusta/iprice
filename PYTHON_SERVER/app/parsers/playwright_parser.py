"""
🎭 Playwright Parser
==================
Modern ve hızlı web scraping için Playwright tabanlı parser

Özellikler:
- Scrapy ve Selenium'dan daha hızlı
- Otomatik bekleme mekanizması
- Multiple browser desteği (Chromium, Firefox, WebKit)
- Network interception
- Proxy desteği
- Headless ve headful mod

Kullanım:
    parser = PlaywrightParser()
    result = parser.parse(url, company_id, application_id, server_id, job_data)
"""

import time
import os
from typing import Dict, Any, Optional
from .base import ParserInterface
from app.helper.get_random_agents import get_random_user_agent
from app.services.ProxyManager import get_proxy_manager


class PlaywrightParser(ParserInterface):
    """
    Playwright-based web scraping parser
    """
    
    def __init__(self):
        """Initialize Playwright parser"""
        super().__init__()
        self._load_playwright()
    
    def _load_playwright(self):
        """Playwright modüllerini yükle"""
        try:
            from playwright.sync_api import sync_playwright
            self.sync_playwright = sync_playwright
            print("✅ Playwright modülleri yüklendi")
        except ImportError as e:
            print(f"❌ Playwright import hatası: {e}")
            print("💡 Playwright kurulumu için: pip install playwright && playwright install chromium")
            raise
    
    def get_parser_name(self) -> str:
        return 'playwright'
    
    def parse(self, url: str, company_id: int, application_id: int, server_id: int, job_data: dict = None) -> Dict[str, Any]:
        # Job data'yı instance'a kaydet (proxy için)
        self.job_data = job_data
        """
        Playwright ile URL'i parse et
        
        Args:
            url: Parse edilecek URL
            company_id: Şirket ID
            application_id: Uygulama ID
            server_id: Server ID
            job_data: Job metadata (attributes, npm, vb.)
            
        Returns:
            Parse sonucu dictionary
        """
        playwright = None
        browser = None
        
        try:
            print(f"🎭 Playwright parsing başladı: Company: {company_id}, URL: {url}")
            
            # Attribute'ları job_data'dan al
            if not job_data or 'attributes' not in job_data:
                return self._error_result(
                    url, company_id, application_id, server_id,
                    "Job data'da attributes bulunamadı", 
                    job_data=job_data
                )
            
            raw_attributes = job_data.get('attributes', [])
            attributes = self._transform_attributes(raw_attributes)
            
            print(f"📋 {len(attributes)} attribute parse edilecek")
            
            # Playwright başlat
            playwright = self.sync_playwright().start()
            
            # Browser başlat (proxy ile)
            browser = self._create_browser(playwright)
            
            # Context oluştur (stealth ayarları ile)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=get_random_user_agent(),
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                # Gerçek cihaz özelliklerini taklit et
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                # Ek headers
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            # Sayfa oluştur
            page = context.new_page()
            
            # Anti-detection JavaScript inject et
            self._inject_stealth_scripts(page)
            
            # URL'e git
            print(f"🔗 URL'e gidiliyor: {url}")
            # networkidle yerine domcontentloaded kullan (daha hızlı)
            # timeout'u 60 saniyeye çıkar (proxy kullanımı için)
            response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            if not response:
                return self._error_result(
                    url, company_id, application_id, server_id,
                    "Sayfa yüklenemedi", 
                    500, 
                    job_data
                )
            
            http_status = response.status
            print(f"📡 HTTP Status: {http_status}")
            
            # Hata durumları
            if http_status in [403, 401, 429, 503]:
                return self._error_result(
                    url, company_id, application_id, server_id,
                    f"HTTP {http_status} - Access denied",
                    http_status,
                    job_data
                )
            
            if not (200 <= http_status < 300):
                return self._error_result(
                    url, company_id, application_id, server_id,
                    f"HTTP Error: {http_status}",
                    http_status,
                    job_data
                )
            
            # Attribute'ları parse et
            results = {}  # Initialize results variable
            try:
                results = self._extract_attributes(page, attributes)
                print(f"📊 Parse sonuçları: {results}")
                
                # Başarılı sonuç döndür
                return self._success_result(
                    url, company_id, application_id, server_id,
                    results, http_status, job_data
                )
                
            except Exception as attr_error:
                # Attribute parsing hatası - HTTP 500 değil, detaylı hata mesajı
                print(f"❌ Attribute parsing hatası: {attr_error}")
                
                # Tüm attribute'ları başarısız olarak işaretle
                failed_attributes = list(attributes.keys())
                error_message = f"Attribute'lar parse edilemedi: {', '.join(failed_attributes)} ({len(failed_attributes)}/{len(attributes)})"
                
                return self._error_result(
                    url, company_id, application_id, server_id,
                    error_message, http_status, job_data  # HTTP status - site erişilebilir
                )
            
        except Exception as e:
            print(f"❌ Playwright hatası: {e}")
            import traceback
            traceback.print_exc()
            return self._error_result(
                url, company_id, application_id, server_id,
                str(e), 500, job_data
            )
            
        finally:
            # Cleanup
            if browser:
                try:
                    browser.close()
                    print(f"🔚 Browser kapatıldı")
                except:
                    pass
            
            if playwright:
                try:
                    playwright.stop()
                    print(f"🛑 Playwright durduruldu")
                except:
                    pass
    
    def _create_browser(self, playwright):
        """
        Playwright browser oluştur (Stealth mode + Anti-detection)
        
        Args:
            playwright: Playwright instance
            
        Returns:
            Browser instance
        """
        try:
            # Proxy manager'dan proxy al - job_data'dan dinamik proxy
            proxy_manager = get_proxy_manager()
            proxy_url = proxy_manager.get_proxy(job_data=self.job_data)
            
            # Browser launch options (Anti-detection için optimize edilmiş)
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    # Anti-bot detection ayarları
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    # Ek stealth ayarları
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certifcate-errors-spki-list',
                    '--disable-software-rasterizer',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-ipc-flooding-protection',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    '--force-color-profile=srgb',
                    '--disable-hang-monitor',
                    '--disable-prompt-on-repost',
                    '--disable-domain-reliability',
                    '--disable-component-extensions-with-background-pages',
                ]
            }
            
            # Proxy varsa ekle
            if proxy_url:
                # Playwright proxy formatı: {'server': 'http://...'}
                # Eğer authentication varsa: {'server': '...', 'username': '...', 'password': '...'}
                
                if '@' in proxy_url:
                    # Credential'lı proxy: http://user:pass@host:port
                    import re
                    match = re.match(r'http://([^:]+):([^@]+)@(.+)', proxy_url)
                    if match:
                        username, password, server = match.groups()
                        launch_options['proxy'] = {
                            'server': f'http://{server}',
                            'username': username,
                            'password': password
                        }
                        print(f"🔒 Playwright proxy (auth): {server}")
                    else:
                        launch_options['proxy'] = {'server': proxy_url}
                        print(f"🔒 Playwright proxy: {proxy_url}")
                else:
                    # Credential'sız proxy
                    launch_options['proxy'] = {'server': proxy_url}
                    print(f"🔒 Playwright proxy: {proxy_url}")
            
            # Chromium browser başlat
            print(f"🛡️ Playwright Stealth Mode aktif...")
            browser = playwright.chromium.launch(**launch_options)
            
            return browser
            
        except Exception as e:
            print(f"❌ Browser oluşturma hatası: {e}")
            raise
    
    def _inject_stealth_scripts(self, page):
        """
        Anti-detection JavaScript kodlarını sayfaya inject et
        
        Bu scriptler bot detection sistemlerinin kontrol ettiği
        JavaScript API'lerini ve özellikleri manipüle eder.
        
        Args:
            page: Playwright page instance
        """
        try:
            # WebDriver özelliğini gizle
            page.add_init_script("""
                // Navigator.webdriver özelliğini kaldır
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Chrome runtime özelliklerini ekle
            page.add_init_script("""
                // Chrome runtime özelliklerini ekle (Headless Chrome tespitini engelle)
                window.chrome = {
                    runtime: {}
                };
            """)
            
            # Permissions API'yi override et
            page.add_init_script("""
                // Permissions API override (bot tespitini engelle)
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Plugin array'ini doldur
            page.add_init_script("""
                // Plugin array'ini gerçekçi hale getir
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Languages array'ini doldur
            page.add_init_script("""
                // Languages özelliğini gerçekçi hale getir
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['tr-TR', 'tr', 'en-US', 'en']
                });
            """)
            
            # Canvas fingerprinting'i engelle
            page.add_init_script("""
                // Canvas fingerprinting'i kısmen engelle
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    if (type === 'image/png' && this.width === 0 && this.height === 0) {
                        return 'data:image/png;base64,iVBORw0KGg=';
                    }
                    return originalToDataURL.apply(this, arguments);
                };
            """)
            
            # WebGL vendor info'yu override et
            page.add_init_script("""
                // WebGL vendor bilgisini gerçekçi hale getir
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
            """)
            
            # User Agent override (ek kontrol)
            page.add_init_script(f"""
                // Navigator.userAgent override
                Object.defineProperty(navigator, 'userAgent', {{
                    get: () => '{get_random_user_agent()}'
                }});
            """)
            
            # Automation kontrollerini engelle
            page.add_init_script("""
                // Automation kontrollerini engelle
                delete navigator.__proto__.webdriver;
                
                // Document.documentElement içindeki automation flag'i kaldır
                const originalGetAttribute = document.documentElement.getAttribute;
                document.documentElement.getAttribute = function(name) {
                    if (name === 'webdriver') {
                        return null;
                    }
                    return originalGetAttribute.apply(this, arguments);
                };
            """)
            
            print(f"🛡️ Stealth scriptleri inject edildi")
            
        except Exception as e:
            print(f"⚠️ Stealth script injection hatası: {e}")
            # Hata olsa bile devam et
    
    def _transform_attributes(self, raw_attributes: list) -> Dict[str, Any]:
        """
        Yeni attribute yapısını parser'ın beklediği formata çevir
        
        Args:
            raw_attributes: API'den gelen attribute listesi
            
        Returns:
            Transformed attributes dictionary
        """
        attributes = {}
        
        for attr in raw_attributes:
            attr_name = attr.get('attributes_name')
            attr_type = attr.get('attributes_type')
            attr_value = attr.get('attributes_value')
            
            if not attr_name or not attr_value:
                continue
            
            # Attribute type'a göre selector type'ı belirle
            if attr_type == 'xpath':
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'xpath'
                }
            elif attr_type == 'id':
                attributes[attr_name] = {
                    'selector': f'#{attr_value}',  # Playwright için CSS selector
                    'selector_type': 'css'
                }
            else:  # class, css
                attributes[attr_name] = {
                    'selector': attr_value,
                    'selector_type': 'css'
                }
        
        return attributes
    
    def _extract_attributes(self, page, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Playwright page'den attribute'ları çıkar
        
        Args:
            page: Playwright page instance
            attributes: Parse edilecek attribute'lar
            
        Returns:
            Extracted attributes dictionary
        """
        results = {}
        error_count = 0
        
        for attr_name, attr_data in attributes.items():
            selector = attr_data.get('selector', '')
            selector_type = attr_data.get('selector_type', 'css')
            meta_value = attr_data.get('meta_value', '')
            
            # 🆕 Meta/JSON tipindeyse özel işlem
            if selector_type == 'meta' and meta_value:
                print(f"  🔍 Meta/JSON değeri alınıyor: {meta_value}")
                try:
                    meta_result = page.evaluate(f"""() => {{
                        // 1. Meta tag
                        var metaByProperty = document.querySelector('meta[property="{meta_value}"]');
                        if (metaByProperty) return metaByProperty.getAttribute('content');
                        
                        var metaByName = document.querySelector('meta[name="{meta_value}"]');
                        if (metaByName) return metaByName.getAttribute('content');
                        
                        // 2. window.insider_object
                        if (window.insider_object?.product?.['{meta_value}']) {{
                            return window.insider_object.product['{meta_value}'];
                        }}
                        
                        // 3. dataLayer
                        if (window.dataLayer) {{
                            for (var i = 0; i < window.dataLayer.length; i++) {{
                                if (window.dataLayer[i].product?.['{meta_value}']) {{
                                    return window.dataLayer[i].product['{meta_value}'];
                                }}
                            }}
                        }}
                        
                        // 4. Regex arama
                        var pageSource = document.documentElement.innerHTML;
                        var regex = new RegExp('"{meta_value}"\\\\s*:\\\\s*([0-9.]+)', 'i');
                        var match = pageSource.match(regex);
                        if (match?.[1]) return match[1];
                        
                        return null;
                    }}""")
                    
                    if meta_result:
                        print(f"  ✅ Meta/JSON değeri bulundu: {meta_result}")
                        results[attr_name] = str(meta_result)
                    else:
                        print(f"  ⚠️ Meta/JSON değeri bulunamadı: {meta_value}")
                        results[attr_name] = None
                        error_count += 1
                except Exception as e:
                    print(f"  ⚠️ Meta/JSON hatası: {str(e)[:100]}")
                    results[attr_name] = None
                    error_count += 1
                
                continue
            
            try:
                # Artık veritabanından ::text ve /text() suffix'leri gelmiyor, direkt kullan
                # Playwright'in güçlü locator sistemi
                if selector_type == 'xpath':
                    locator = page.locator(f'xpath={selector}')
                else:  # css
                    locator = page.locator(selector)
                
                # Element'i bekle (max 3 saniye - hızlı fail için)
                try:
                    locator.wait_for(timeout=3000, state='visible')
                except Exception as wait_error:
                    # Timeout veya element bulunamadı
                    print(f"   ❌ {attr_name} hatası: Element bulunamadı veya timeout ({str(wait_error)[:50]})")
                    results[attr_name] = None
                    error_count += 1
                    continue
                
                # Text içeriğini al - CSS strict mode için .first kullan
                try:
                    value = locator.first.text_content()
                except Exception as text_error:
                    # Strict mode violation veya başka bir hata
                    print(f"   ❌ {attr_name} hatası: Text alınamadı ({str(text_error)[:50]})")
                    results[attr_name] = None
                    error_count += 1
                    continue
                
                if value:
                    value = value.strip()
                    results[attr_name] = value
                    print(f"   ✅ {attr_name}: {value}")
                else:
                    results[attr_name] = None
                    print(f"   ⚠️ {attr_name}: Boş değer")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ {attr_name} hatası: {e}")
                results[attr_name] = None
                error_count += 1
        
        # Eğer tüm attribute'lar başarısız olduysa, raise et
        if error_count == len(attributes) and error_count > 0:
            raise Exception(f"Tüm attribute'lar parse edilemedi ({error_count}/{len(attributes)})")
        
        return results
    
    def supports_javascript(self) -> bool:
        """Playwright JavaScript'i destekler"""
        return True
    
    def supports_cookies(self) -> bool:
        """Playwright cookie'leri destekler"""
        return True
    
    def get_browser_type(self) -> str:
        """Kullanılan browser tipi"""
        return 'chromium'

