"""
🔒 Proxy Manager Service
========================
Merkezi proxy yönetim sistemi - Tüm proxy işlemlerini buradan yönetin!

Özellikler:
- .env'den tamamen kontrol edilebilir
- Free/Ücretli proxy desteği
- Health check sistemi
- Kolay açma/kapama
- Scrapy & Selenium entegrasyonu

Kullanım:
    proxy_manager = ProxyManager()
    proxy = proxy_manager.get_proxy()
"""

import os
import random
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProxyManager:
    """Merkezi Proxy Yönetim Sistemi"""
    
    # Proxy tipi enum
    PROXY_NONE = 'none'
    PROXY_FREE = 'free'
    PROXY_SMARTPROXY = 'smartproxy'
    PROXY_BRIGHTDATA = 'brightdata'
    PROXY_CUSTOM = 'custom'
    
    def __init__(self):
        """Proxy Manager başlat"""
        # .env'den ayarları çek
        self.enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        self.proxy_type = os.getenv('PROXY_TYPE', 'none').lower()
        
        # Free proxy ayarları
        self.free_proxy_file = os.getenv('FREE_PROXY_FILE', '/app/app/proxies')
        self.free_proxy_test_enabled = os.getenv('FREE_PROXY_TEST', 'false').lower() == 'true'
        
        # Smartproxy ayarları
        self.smartproxy_user = os.getenv('SMARTPROXY_USER', '')
        self.smartproxy_pass = os.getenv('SMARTPROXY_PASS', '')
        self.smartproxy_endpoint = os.getenv('SMARTPROXY_ENDPOINT', 'gate.smartproxy.com:7000')
        self.smartproxy_country = os.getenv('SMARTPROXY_COUNTRY', '')  # Örn: 'tr' Türkiye için
        self.smartproxy_session_type = os.getenv('SMARTPROXY_SESSION_TYPE', 'rotating')  # rotating veya sticky
        
        # Bright Data ayarları
        self.brightdata_username = os.getenv('BRIGHTDATA_USERNAME', '')
        self.brightdata_password = os.getenv('BRIGHTDATA_PASSWORD', '')
        self.brightdata_endpoint = os.getenv('BRIGHTDATA_ENDPOINT', 'brd.superproxy.io:33335')
        self.brightdata_country = os.getenv('BRIGHTDATA_COUNTRY', 'TR')
        self.brightdata_token = os.getenv('BRIGHTDATA_TOKEN', '')
        
        # Custom proxy ayarları
        self.custom_proxy_url = os.getenv('CUSTOM_PROXY_URL', '')
        self.custom_proxy_user = os.getenv('CUSTOM_PROXY_USER', '')
        self.custom_proxy_pass = os.getenv('CUSTOM_PROXY_PASS', '')
        
        # Performans ayarları
        self.max_retry = int(os.getenv('PROXY_MAX_RETRY', '3'))
        self.timeout = int(os.getenv('PROXY_TIMEOUT', '10'))
        
        # Cache
        self._free_proxy_list: List[str] = []
        self._tested_proxies: Dict[str, Tuple[bool, datetime]] = {}
        self._last_load_time: Optional[datetime] = None
        
        logger.info(f"🔒 Proxy Manager başlatıldı")
        logger.info(f"   - Enabled: {self.enabled}")
        logger.info(f"   - Type: {self.proxy_type}")
        
    def get_proxy(self, force_type: Optional[str] = None, job_data: Optional[Dict] = None) -> Optional[str]:
        """
        Proxy al - Queue'dan gelen ayarlara göre
        
        Args:
            force_type: Belirli bir proxy tipi zorla (None, free, smartproxy, brightdata, custom)
            job_data: Queue'dan gelen job data (use_proxy, proxy_type içerir)
            
        Returns:
            Proxy URL veya None
        """
        # Queue'dan gelen ayarları kontrol et
        if job_data:
            use_proxy = job_data.get('use_proxy', False)
            proxy_type_from_queue = job_data.get('proxy_type', None)
            
            # Queue'da use_proxy=false ise proxy kullanma
            if not use_proxy:
                logger.debug("📴 Queue'da use_proxy=false - No proxy used")
                return None
            
            # Queue'da proxy_type varsa onu kullan
            if proxy_type_from_queue:
                proxy_type = proxy_type_from_queue.lower()
                logger.info(f"🔒 Queue'dan proxy tipi: {proxy_type}")
            else:
                # Queue'da proxy_type yoksa .env'den al
                proxy_type = force_type if force_type else self.proxy_type
        else:
            # Job data yoksa .env ayarlarına göre
            if not self.enabled:
                logger.debug("📴 Proxy disabled - No proxy used")
                return None
            
            proxy_type = force_type if force_type else self.proxy_type
        
        if proxy_type == self.PROXY_NONE:
            logger.debug("📴 Proxy type: NONE")
            return None
            
        elif proxy_type == self.PROXY_FREE:
            return self._get_free_proxy()
            
        elif proxy_type == self.PROXY_SMARTPROXY:
            return self._get_smartproxy()
            
        elif proxy_type == self.PROXY_BRIGHTDATA:
            return self._get_brightdata()
            
        elif proxy_type == self.PROXY_CUSTOM:
            return self._get_custom_proxy()
            
        else:
            logger.warning(f"⚠️ Bilinmeyen proxy tipi: {proxy_type}")
            return None
    
    def _get_free_proxy(self) -> Optional[str]:
        """Free proxy listesinden proxy al"""
        try:
            # Listeyi yükle (cache'den veya dosyadan)
            if not self._free_proxy_list or self._should_reload_proxies():
                self._load_free_proxies()
            
            if not self._free_proxy_list:
                logger.warning("⚠️ Free proxy listesi boş!")
                return None
            
            # Test etme kapalıysa rastgele seç
            if not self.free_proxy_test_enabled:
                proxy = random.choice(self._free_proxy_list)
                logger.debug(f"🔄 Free proxy (test edilmeden): {proxy}")
                return f"http://{proxy}"
            
            # Test et ve çalışan birini bul
            max_attempts = min(10, len(self._free_proxy_list))
            for _ in range(max_attempts):
                proxy = random.choice(self._free_proxy_list)
                
                # Önce cache'e bak
                if proxy in self._tested_proxies:
                    is_working, test_time = self._tested_proxies[proxy]
                    # 5 dakikadan yeniyse kullan
                    if datetime.now() - test_time < timedelta(minutes=5):
                        if is_working:
                            logger.debug(f"✅ Free proxy (cache'den): {proxy}")
                            return f"http://{proxy}"
                        else:
                            continue
                
                # Test et
                if self._test_proxy(proxy):
                    self._tested_proxies[proxy] = (True, datetime.now())
                    logger.debug(f"✅ Free proxy (test edildi): {proxy}")
                    return f"http://{proxy}"
                else:
                    self._tested_proxies[proxy] = (False, datetime.now())
            
            # Çalışan bulunamadıysa yine de rastgele birini dön
            proxy = random.choice(self._free_proxy_list)
            logger.warning(f"⚠️ Çalışan free proxy bulunamadı, rastgele deneniyor: {proxy}")
            return f"http://{proxy}"
            
        except Exception as e:
            logger.error(f"❌ Free proxy alma hatası: {e}")
            return None
    
    def _get_smartproxy(self) -> Optional[str]:
        """Smartproxy URL oluştur"""
        try:
            if not self.smartproxy_user or not self.smartproxy_pass:
                logger.error("❌ Smartproxy credentials eksik! .env'i kontrol edin.")
                return None
            
            # Session type'a göre URL oluştur
            if self.smartproxy_session_type == 'sticky':
                # Sticky session - aynı IP 10 dakika boyunca
                session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M')}"
                username = f"{self.smartproxy_user}-session-{session_id}"
            else:
                # Rotating - her request farklı IP
                username = self.smartproxy_user
            
            # Ülke belirtildiyse ekle
            if self.smartproxy_country:
                username = f"{username}-country-{self.smartproxy_country}"
            
            proxy_url = f"http://{username}:{self.smartproxy_pass}@{self.smartproxy_endpoint}"
            logger.debug(f"💎 Smartproxy: {username}@{self.smartproxy_endpoint}")
            return proxy_url
            
        except Exception as e:
            logger.error(f"❌ Smartproxy oluşturma hatası: {e}")
            return None
    
    def _get_custom_proxy(self) -> Optional[str]:
        """Custom proxy URL oluştur"""
        try:
            if not self.custom_proxy_url:
                logger.error("❌ Custom proxy URL eksik! .env'i kontrol edin.")
                return None
            
            # Kullanıcı adı/şifre varsa ekle
            if self.custom_proxy_user and self.custom_proxy_pass:
                # URL'den protocol'ü ayır
                if '://' in self.custom_proxy_url:
                    protocol, rest = self.custom_proxy_url.split('://', 1)
                    proxy_url = f"{protocol}://{self.custom_proxy_user}:{self.custom_proxy_pass}@{rest}"
                else:
                    proxy_url = f"http://{self.custom_proxy_user}:{self.custom_proxy_pass}@{self.custom_proxy_url}"
            else:
                proxy_url = self.custom_proxy_url if '://' in self.custom_proxy_url else f"http://{self.custom_proxy_url}"
            
            logger.debug(f"🔧 Custom proxy: {proxy_url}")
            return proxy_url
            
        except Exception as e:
            logger.error(f"❌ Custom proxy oluşturma hatası: {e}")
            return None
    
    def _load_free_proxies(self):
        """Free proxy listesini dosyadan yükle"""
        try:
            if not os.path.exists(self.free_proxy_file):
                logger.warning(f"⚠️ Proxy dosyası bulunamadı: {self.free_proxy_file}")
                return
            
            with open(self.free_proxy_file, 'r') as f:
                self._free_proxy_list = [line.strip() for line in f if line.strip()]
            
            self._last_load_time = datetime.now()
            logger.info(f"📋 {len(self._free_proxy_list)} free proxy yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Proxy dosyası okuma hatası: {e}")
    
    def _should_reload_proxies(self) -> bool:
        """Proxy listesi yeniden yüklenmeli mi?"""
        if not self._last_load_time:
            return True
        # 1 saatte bir yeniden yükle
        return datetime.now() - self._last_load_time > timedelta(hours=1)
    
    def _test_proxy(self, proxy: str) -> bool:
        """Proxy'i test et"""
        try:
            test_url = os.getenv('PROXY_TEST_URL', 'http://httpbin.org/ip')
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"Proxy test failed for {proxy}: {e}")
            return False
    
    def get_proxy_dict(self, force_type: Optional[str] = None, job_data: Optional[Dict] = None) -> Optional[Dict[str, str]]:
        """
        Requests kütüphanesi için proxy dict döndür
        
        Returns:
            {'http': 'http://...', 'https': 'http://...'} veya None
        """
        proxy_url = self.get_proxy(force_type, job_data)
        
        if not proxy_url:
            return None
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_scrapy_settings(self, force_type: Optional[str] = None, job_data: Optional[Dict] = None) -> Dict:
        """
        Scrapy için proxy ayarları döndür
        
        Returns:
            Scrapy custom_settings dict
        """
        proxy_url = self.get_proxy(force_type, job_data)
        
        if not proxy_url:
            return {}
        
        # Scrapy için meta proxy ayarı
        return {
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            },
            'HTTPPROXY_ENABLED': True,
        }
    
    def get_selenium_proxy(self, force_type: Optional[str] = None, job_data: Optional[Dict] = None) -> Optional[str]:
        """
        Selenium için proxy string döndür
        
        Returns:
            'user:pass@host:port' veya 'host:port' formatında proxy veya None
        """
        proxy_url = self.get_proxy(force_type, job_data)
        
        if not proxy_url:
            return None
        
        # URL'den protocol'ü çıkar (http:// veya https://)
        # Selenium için: user:pass@host:port veya host:port formatı gerekli
        try:
            # http://user:pass@host:port -> user:pass@host:port
            # http://host:port -> host:port
            proxy_without_protocol = proxy_url.replace('http://', '').replace('https://', '')
            
            logger.debug(f"🔒 Selenium proxy (auth dahil): {proxy_without_protocol}")
            return proxy_without_protocol
            
        except Exception as e:
            logger.error(f"❌ Selenium proxy parse hatası: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Proxy istatistikleri döndür"""
        stats = {
            'enabled': self.enabled,
            'type': self.proxy_type,
            'free_proxy_count': len(self._free_proxy_list),
            'tested_proxy_count': len(self._tested_proxies),
            'working_proxies': sum(1 for working, _ in self._tested_proxies.values() if working),
            'failed_proxies': sum(1 for working, _ in self._tested_proxies.values() if not working),
        }
        return stats
    
    def _get_brightdata(self) -> Optional[str]:
        """Bright Data proxy al"""
        try:
            if not self.brightdata_username or not self.brightdata_password:
                logger.warning("⚠️ Bright Data credentials eksik!")
                return None
            
            # Username'i kontrol et - country zaten eklenmişse tekrar ekleme
            username = self.brightdata_username
            
            # Eğer username'de zaten -country-XX yoksa ekle
            if '-country-' not in username.lower() and self.brightdata_country:
                username = f"{username}-country-{self.brightdata_country.lower()}"
                logger.info(f"🔒 Bright Data proxy (country eklendi): {username}@{self.brightdata_endpoint}")
            else:
                logger.info(f"🔒 Bright Data proxy (username zaten country içeriyor): {username}@{self.brightdata_endpoint}")
            
            proxy_url = f"http://{username}:{self.brightdata_password}@{self.brightdata_endpoint}"
            
            return proxy_url
            
        except Exception as e:
            logger.error(f"❌ Bright Data proxy hatası: {e}")
            return None
    
    def clear_cache(self):
        """Proxy cache'i temizle"""
        self._tested_proxies.clear()
        logger.info("🧹 Proxy cache temizlendi")


# Global instance (singleton pattern)
_proxy_manager_instance = None


def get_proxy_manager() -> ProxyManager:
    """Global ProxyManager instance'ı döndür"""
    global _proxy_manager_instance
    if _proxy_manager_instance is None:
        _proxy_manager_instance = ProxyManager()
    return _proxy_manager_instance

