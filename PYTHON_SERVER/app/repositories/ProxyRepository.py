"""
Proxy Repository
================
Proxy veritabanı işlemleri için repository pattern implementasyonu.

Özellikler:
- CRUD operasyonları
- Akıllı proxy seçimi (working_percent ve response_time bazlı)
- Failure tracking
- Bulk insert/update
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import logging

from app.model.Proxy import Proxy

logger = logging.getLogger(__name__)


class ProxyRepository:
    """Proxy Database Repository"""
    
    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_smart_proxy(
        self, 
        protocol: str = 'http',
        min_working_percent: float = 70.0,
        exclude_ids: List[int] = None
    ) -> Optional[Proxy]:
        """
        Akıllı proxy seçimi - En iyi performanslı proxy'yi seç
        
        Algoritma:
        1. Aktif olan (is_active=true)
        2. İstenen protokolü destekleyen
        3. Başarı oranı yüksek (working_percent > 70%)
        4. Response time düşük (hızlı olanlar)
        
        Args:
            protocol: İstenen protokol (http, https, socks4, socks5)
            min_working_percent: Minimum başarı yüzdesi (default: 70%)
            exclude_ids: Hariç tutulacak proxy ID'leri
            
        Returns:
            En uygun Proxy veya None
        """
        query = self.db.query(Proxy).filter(
            Proxy.is_active == True,
            Proxy.protocols.op('@>')(f'["{protocol}"]'),  # JSON contains check
            Proxy.working_percent >= min_working_percent
        )
        
        # Belirli ID'leri hariç tut (önceki başarısız olanlar)
        if exclude_ids:
            query = query.filter(~Proxy.id.in_(exclude_ids))
        
        # Sıralama: Başarı oranı yüksek, hız hızlı
        proxy = query.order_by(
            desc(Proxy.working_percent),
            asc(Proxy.response_time)
        ).first()
        
        if proxy:
            logger.info(
                f"🎯 Proxy seçildi: {proxy.ip}:{proxy.port} "
                f"(working: {proxy.working_percent}%, response: {proxy.response_time}ms)"
            )
        else:
            logger.warning(f"⚠️ Uygun proxy bulunamadı (protocol={protocol}, min_percent={min_working_percent})")
        
        return proxy
    
    def get_by_id(self, proxy_id: int) -> Optional[Proxy]:
        """ID'ye göre proxy getir"""
        return self.db.query(Proxy).filter(Proxy.id == proxy_id).first()
    
    def get_by_proxy_id(self, proxy_id: str) -> Optional[Proxy]:
        """External proxy_id'ye göre getir"""
        return self.db.query(Proxy).filter(Proxy.proxy_id == proxy_id).first()
    
    def get_by_ip_port(self, ip: str, port: int) -> Optional[Proxy]:
        """IP ve Port'a göre proxy getir"""
        return self.db.query(Proxy).filter(
            Proxy.ip == ip,
            Proxy.port == port
        ).first()
    
    def increment_failure(self, proxy_id: int) -> Proxy:
        """
        Proxy'nin başarısızlık sayacını artır
        
        Eğer failure_count >= 3 olursa is_active = False yap
        
        Args:
            proxy_id: Proxy ID
            
        Returns:
            Güncellenmiş Proxy
        """
        proxy = self.get_by_id(proxy_id)
        
        if not proxy:
            logger.error(f"❌ Proxy bulunamadı: ID={proxy_id}")
            return None
        
        # Failure count artır
        proxy.failure_count += 1
        
        # 3 veya daha fazla hata olursa devre dışı bırak
        if proxy.failure_count >= 3:
            proxy.is_active = False
            logger.warning(
                f"🔴 Proxy devre dışı bırakıldı: {proxy.ip}:{proxy.port} "
                f"(failure_count={proxy.failure_count})"
            )
        else:
            logger.info(
                f"⚠️ Proxy failure kaydedildi: {proxy.ip}:{proxy.port} "
                f"(failure_count={proxy.failure_count})"
            )
        
        self.db.commit()
        self.db.refresh(proxy)
        
        return proxy
    
    def mark_as_used(self, proxy_id: int) -> Proxy:
        """
        Proxy'yi kullanıldı olarak işaretle (last_used_at güncelle)
        
        Args:
            proxy_id: Proxy ID
            
        Returns:
            Güncellenmiş Proxy
        """
        proxy = self.get_by_id(proxy_id)
        
        if not proxy:
            return None
        
        proxy.last_used_at = datetime.now()
        self.db.commit()
        self.db.refresh(proxy)
        
        return proxy
    
    def reactivate(self, proxy_id: int) -> Proxy:
        """
        Proxy'yi tekrar aktif et (failure_count sıfırla)
        
        Args:
            proxy_id: Proxy ID
            
        Returns:
            Güncellenmiş Proxy
        """
        proxy = self.get_by_id(proxy_id)
        
        if not proxy:
            return None
        
        proxy.is_active = True
        proxy.failure_count = 0
        
        logger.info(f"✅ Proxy yeniden aktif edildi: {proxy.ip}:{proxy.port}")
        
        self.db.commit()
        self.db.refresh(proxy)
        
        return proxy
    
    def create(self, proxy_data: Dict) -> Proxy:
        """
        Yeni proxy oluştur
        
        Args:
            proxy_data: Proxy bilgileri (dict)
            
        Returns:
            Oluşturulan Proxy
        """
        proxy = Proxy(**proxy_data)
        self.db.add(proxy)
        self.db.commit()
        self.db.refresh(proxy)
        
        logger.info(f"➕ Yeni proxy eklendi: {proxy.ip}:{proxy.port}")
        
        return proxy
    
    def bulk_insert(self, proxy_list: List[Dict]) -> int:
        """
        Toplu proxy ekleme (duplicate kontrolü ile)
        
        Args:
            proxy_list: Proxy bilgileri listesi
            
        Returns:
            Eklenen proxy sayısı
        """
        added_count = 0
        
        for proxy_data in proxy_list:
            # Duplicate kontrolü (ip:port unique)
            existing = self.get_by_ip_port(
                proxy_data.get('ip'), 
                proxy_data.get('port')
            )
            
            if not existing:
                self.create(proxy_data)
                added_count += 1
            else:
                # Mevcut proxy'yi güncelle (working_percent, response_time, vb.)
                for key, value in proxy_data.items():
                    if hasattr(existing, key) and key not in ['id', 'created_at']:
                        setattr(existing, key, value)
                
                existing.last_checked = datetime.now()
                self.db.commit()
        
        logger.info(f"📊 Bulk insert tamamlandı: {added_count} yeni, {len(proxy_list) - added_count} güncellendi")
        
        return added_count
    
    def get_inactive_proxies(self, days: int = 7) -> List[Proxy]:
        """
        Belirli gün sayısından uzun süredir kullanılmayan proxyleri getir
        
        Args:
            days: Gün sayısı
            
        Returns:
            Pasif proxy listesi
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return self.db.query(Proxy).filter(
            or_(
                Proxy.last_used_at == None,
                Proxy.last_used_at < cutoff_date
            )
        ).all()
    
    def get_all_active(self, protocol: str = None) -> List[Proxy]:
        """
        Tüm aktif proxyleri getir
        
        Args:
            protocol: Filtrelemek için protokol (opsiyonel)
            
        Returns:
            Aktif proxy listesi
        """
        query = self.db.query(Proxy).filter(Proxy.is_active == True)
        
        if protocol:
            query = query.filter(Proxy.protocols.op('@>')(f'["{protocol}"]'))
        
        return query.all()
    
    def get_stats(self) -> Dict:
        """
        Proxy istatistikleri
        
        Returns:
            İstatistik dictionary
        """
        total = self.db.query(Proxy).count()
        active = self.db.query(Proxy).filter(Proxy.is_active == True).count()
        inactive = total - active
        
        avg_working_percent = self.db.query(
            func.avg(Proxy.working_percent)
        ).filter(Proxy.is_active == True).scalar() or 0
        
        avg_response_time = self.db.query(
            func.avg(Proxy.response_time)
        ).filter(Proxy.is_active == True).scalar() or 0
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'avg_working_percent': round(avg_working_percent, 2),
            'avg_response_time': round(avg_response_time, 2),
        }

