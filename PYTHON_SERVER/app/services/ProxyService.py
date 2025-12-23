"""
Proxy Service
=============
Proxy yönetim servisi - API ve worker'lar için merkezi proxy yönetimi.

Özellikler:
- Akıllı proxy seçimi
- Failure tracking ve auto-disable
- Multi-source proxy fetching
- Health check ve statistics
"""

import os
import requests
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.repositories.ProxyRepository import ProxyRepository
from app.model.Proxy import Proxy

logger = logging.getLogger(__name__)


class ProxyService:
    """Merkezi Proxy Yönetim Servisi"""
    
    # Proxy kaynakları
    SOURCES = {
        'proxyscrape_http': 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'proxyscrape_socks4': 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all',
        'proxyscrape_socks5': 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all',
        'geonode': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
        'github_http': 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        'github_socks4': 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt',
        'github_socks5': 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt',
    }
    
    def __init__(self, db: Session):
        """
        Args:
            db: Database session
        """
        self.db = db
        self.repo = ProxyRepository(db)
        
        # .env'den ayarlar
        self.min_working_percent = float(os.getenv('PROXY_MIN_WORKING_PERCENT', '70'))
        self.failure_threshold = int(os.getenv('PROXY_FAILURE_THRESHOLD', '3'))
        self.default_protocol = os.getenv('PROXY_DEFAULT_PROTOCOL', 'http')
    
    def get_proxy(self, protocol: str = None, exclude_ids: List[int] = None) -> Optional[Proxy]:
        """
        Akıllı proxy seçimi - En iyi performanslı proxy'yi al
        
        Args:
            protocol: İstenen protokol (None ise default kullan)
            exclude_ids: Hariç tutulacak proxy ID'leri
            
        Returns:
            Seçilen Proxy veya None
        """
        protocol = protocol or self.default_protocol
        
        proxy = self.repo.get_smart_proxy(
            protocol=protocol,
            min_working_percent=self.min_working_percent,
            exclude_ids=exclude_ids
        )
        
        if proxy:
            # Kullanım zamanını güncelle
            self.repo.mark_as_used(proxy.id)
        
        return proxy
    
    def report_failure(self, proxy_id: int, reason: str = None) -> Dict:
        """
        Proxy başarısızlığını raporla
        
        - failure_count artırılır
        - failure_count >= 3 ise is_active = False
        
        Args:
            proxy_id: Proxy ID
            reason: Başarısızlık sebebi (opsiyonel)
            
        Returns:
            Güncellenmiş durum bilgisi
        """
        logger.warning(f"⚠️ Proxy failure raporu: ID={proxy_id}, reason={reason}")
        
        proxy = self.repo.increment_failure(proxy_id)
        
        if not proxy:
            return {
                'success': False,
                'message': f'Proxy bulunamadı: ID={proxy_id}'
            }
        
        return {
            'success': True,
            'proxy_id': proxy.id,
            'ip': proxy.ip,
            'port': proxy.port,
            'failure_count': proxy.failure_count,
            'is_active': proxy.is_active,
            'message': f"Failure kaydedildi. {'Proxy devre dışı bırakıldı.' if not proxy.is_active else f'Kalan hak: {self.failure_threshold - proxy.failure_count}'}"
        }
    
    def report_success(self, proxy_id: int) -> Dict:
        """
        Proxy başarılı kullanımını raporla (opsiyonel - statistics için)
        
        Args:
            proxy_id: Proxy ID
            
        Returns:
            Durum bilgisi
        """
        proxy = self.repo.get_by_id(proxy_id)
        
        if not proxy:
            return {
                'success': False,
                'message': f'Proxy bulunamadı: ID={proxy_id}'
            }
        
        # Success count artır (eğer varsa)
        proxy.up_time_success_count += 1
        proxy.up_time_try_count += 1
        
        # Working percent hesapla
        if proxy.up_time_try_count > 0:
            proxy.working_percent = (proxy.up_time_success_count / proxy.up_time_try_count) * 100
        
        self.db.commit()
        
        logger.info(f"✅ Proxy başarılı: {proxy.ip}:{proxy.port} (working: {proxy.working_percent:.2f}%)")
        
        return {
            'success': True,
            'proxy_id': proxy.id,
            'working_percent': proxy.working_percent
        }
    
    def fetch_proxies_from_source(self, source_name: str) -> List[Dict]:
        """
        Belirli bir kaynaktan proxy listesi çek
        
        Args:
            source_name: Kaynak adı (SOURCES dict'inden)
            
        Returns:
            Proxy dict listesi
        """
        url = self.SOURCES.get(source_name)
        
        if not url:
            logger.error(f"❌ Bilinmeyen kaynak: {source_name}")
            return []
        
        try:
            logger.info(f"🔄 Proxy listesi çekiliyor: {source_name}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Kaynak tipine göre parse et
            if 'geonode' in source_name:
                return self._parse_geonode_response(response.json())
            else:
                # Basit IP:PORT formatı (proxyscrape, github)
                return self._parse_simple_list(response.text, source_name)
        
        except Exception as e:
            logger.error(f"❌ Proxy fetch hatası ({source_name}): {e}")
            return []
    
    def _parse_simple_list(self, text: str, source_name: str) -> List[Dict]:
        """
        Basit IP:PORT formatındaki listeyi parse et
        
        Args:
            text: Response text
            source_name: Kaynak adı (protokol tespiti için)
            
        Returns:
            Proxy dict listesi
        """
        proxies = []
        
        # Protokol belirle
        if 'socks4' in source_name:
            protocols = ['socks4']
        elif 'socks5' in source_name:
            protocols = ['socks5']
        elif 'http' in source_name:
            protocols = ['http', 'https']
        else:
            protocols = ['http']
        
        for line in text.split('\n'):
            line = line.strip()
            
            if not line or ':' not in line:
                continue
            
            try:
                ip, port = line.split(':', 1)
                
                proxies.append({
                    'ip': ip.strip(),
                    'port': int(port.strip()),
                    'protocols': protocols,
                    'anonymity_level': 'unknown',
                    'is_active': True,
                    'failure_count': 0,
                    'working_percent': 100.0,
                    'last_checked': datetime.now(),
                })
            
            except ValueError:
                continue
        
        logger.info(f"✅ {len(proxies)} proxy parse edildi ({source_name})")
        
        return proxies
    
    def _parse_geonode_response(self, json_data: Dict) -> List[Dict]:
        """
        GeoNode API response'unu parse et
        
        Args:
            json_data: API response JSON
            
        Returns:
            Proxy dict listesi
        """
        proxies = []
        
        for item in json_data.get('data', []):
            try:
                protocols = item.get('protocols', ['http'])
                
                proxies.append({
                    'ip': item.get('ip'),
                    'port': item.get('port'),
                    'country': item.get('country'),
                    'city': item.get('city'),
                    'protocols': protocols,
                    'anonymity_level': item.get('anonymityLevel', 'unknown'),
                    'latency': item.get('latency'),
                    'response_time': item.get('responseTime'),
                    'up_time': item.get('upTime'),
                    'is_active': True,
                    'failure_count': 0,
                    'working_percent': item.get('upTime', 100.0),
                    'last_checked': datetime.now(),
                    'isp': item.get('isp'),
                    'organization': item.get('org'),
                })
            
            except Exception as e:
                logger.warning(f"⚠️ GeoNode proxy parse hatası: {e}")
                continue
        
        logger.info(f"✅ {len(proxies)} proxy parse edildi (GeoNode)")
        
        return proxies
    
    def update_proxy_list(self, sources: List[str] = None) -> Dict:
        """
        Proxy listesini kaynaklardan güncelle
        
        Args:
            sources: Kullanılacak kaynak listesi (None ise tümü)
            
        Returns:
            Güncelleme raporu
        """
        sources = sources or list(self.SOURCES.keys())
        
        total_fetched = 0
        total_added = 0
        
        logger.info(f"🔄 Proxy güncelleme başladı - {len(sources)} kaynak")
        
        for source_name in sources:
            proxy_list = self.fetch_proxies_from_source(source_name)
            
            if proxy_list:
                added = self.repo.bulk_insert(proxy_list)
                total_fetched += len(proxy_list)
                total_added += added
        
        logger.info(
            f"✅ Proxy güncelleme tamamlandı: "
            f"{total_fetched} fetch, {total_added} yeni eklendi"
        )
        
        return {
            'success': True,
            'sources_count': len(sources),
            'total_fetched': total_fetched,
            'total_added': total_added,
            'total_updated': total_fetched - total_added,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict:
        """
        Proxy istatistikleri
        
        Returns:
            İstatistik dictionary
        """
        stats = self.repo.get_stats()
        
        # Protokol bazlı istatistikler
        http_count = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.protocols.op('@>')('["http"]')
        ).count()
        
        https_count = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.protocols.op('@>')('["https"]')
        ).count()
        
        socks4_count = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.protocols.op('@>')('["socks4"]')
        ).count()
        
        socks5_count = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.protocols.op('@>')('["socks5"]')
        ).count()
        
        stats['by_protocol'] = {
            'http': http_count,
            'https': https_count,
            'socks4': socks4_count,
            'socks5': socks5_count,
        }
        
        return stats
    
    def cleanup_inactive_proxies(self, days: int = 30) -> int:
        """
        Uzun süredir kullanılmayan proxyleri temizle
        
        Args:
            days: Gün sayısı
            
        Returns:
            Silinen proxy sayısı
        """
        inactive_proxies = self.repo.get_inactive_proxies(days=days)
        
        count = 0
        for proxy in inactive_proxies:
            self.db.delete(proxy)
            count += 1
        
        self.db.commit()
        
        logger.info(f"🗑️ {count} pasif proxy temizlendi ({days} günden eski)")
        
        return count

