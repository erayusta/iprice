"""
Proxy API Endpoints
===================
Proxy yönetimi için REST API endpoints.

Endpoints:
- GET  /proxy/get         - Akıllı proxy seçimi
- POST /proxy/report-failure - Başarısızlık raporu
- POST /proxy/report-success - Başarı raporu (opsiyonel)
- POST /proxy/update-list     - Manuel proxy güncelleme
- GET  /proxy/stats           - İstatistikler
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.database import get_db
from app.services.ProxyService import ProxyService

logger = logging.getLogger(__name__)

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class ProxyResponse(BaseModel):
    """Proxy response model"""
    id: int
    ip: str
    port: int
    country: Optional[str] = None
    protocols: List[str]
    working_percent: float
    response_time: Optional[float] = None
    is_active: bool
    url: str  # Kullanıma hazır URL (http://ip:port)


class FailureReportRequest(BaseModel):
    """Failure report request model"""
    proxy_id: int
    reason: Optional[str] = None


class SuccessReportRequest(BaseModel):
    """Success report request model"""
    proxy_id: int


class UpdateListRequest(BaseModel):
    """Update list request model"""
    sources: Optional[List[str]] = None


# ========================================
# API Endpoints
# ========================================

@router.get("/get", response_model=ProxyResponse, summary="Akıllı Proxy Seçimi")
async def get_proxy(
    protocol: str = Query(default='http', description="İstenen protokol: http, https, socks4, socks5"),
    db: Session = Depends(get_db)
):
    """
    Akıllı algoritma ile en iyi proxy'yi seç
    
    **Algoritma:**
    - Aktif olan (is_active=true)
    - İstenen protokolü destekleyen
    - Başarı oranı yüksek (working_percent > 70%)
    - Response time düşük (hızlı olanlar)
    
    **Örnek:**
    ```
    GET /api/v1/proxy/get?protocol=http
    ```
    
    **Response:**
    ```json
    {
        "id": 123,
        "ip": "192.168.1.1",
        "port": 8080,
        "country": "US",
        "protocols": ["http", "https"],
        "working_percent": 95.5,
        "response_time": 150.2,
        "is_active": true,
        "url": "http://192.168.1.1:8080"
    }
    ```
    """
    service = ProxyService(db)
    
    proxy = service.get_proxy(protocol=protocol)
    
    if not proxy:
        raise HTTPException(
            status_code=404,
            detail=f"Uygun proxy bulunamadı (protocol={protocol})"
        )
    
    return ProxyResponse(
        id=proxy.id,
        ip=proxy.ip,
        port=proxy.port,
        country=proxy.country,
        protocols=proxy.protocols or [],
        working_percent=proxy.working_percent,
        response_time=proxy.response_time,
        is_active=proxy.is_active,
        url=proxy.get_url(protocol)
    )


@router.post("/report-failure", summary="Proxy Başarısızlık Raporu")
async def report_failure(
    request: FailureReportRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Proxy başarısızlığını raporla
    
    - failure_count artırılır
    - failure_count >= 3 ise is_active = False (proxy devre dışı kalır)
    
    **Örnek:**
    ```json
    POST /api/v1/proxy/report-failure
    {
        "proxy_id": 123,
        "reason": "Connection timeout after 10 seconds"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "proxy_id": 123,
        "ip": "192.168.1.1",
        "port": 8080,
        "failure_count": 3,
        "is_active": false,
        "message": "Failure kaydedildi. Proxy devre dışı bırakıldı."
    }
    ```
    """
    service = ProxyService(db)
    
    result = service.report_failure(
        proxy_id=request.proxy_id,
        reason=request.reason
    )
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail=result.get('message')
        )
    
    return result


@router.post("/report-success", summary="Proxy Başarı Raporu (Opsiyonel)")
async def report_success(
    request: SuccessReportRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Proxy başarılı kullanımını raporla (istatistikler için)
    
    - up_time_success_count artırılır
    - working_percent güncellenir
    
    **Örnek:**
    ```json
    POST /api/v1/proxy/report-success
    {
        "proxy_id": 123
    }
    ```
    """
    service = ProxyService(db)
    
    result = service.report_success(proxy_id=request.proxy_id)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail=result.get('message')
        )
    
    return result


@router.post("/update-list", summary="Manuel Proxy Listesi Güncelleme")
async def update_proxy_list(
    request: UpdateListRequest = Body(default=UpdateListRequest()),
    db: Session = Depends(get_db)
):
    """
    Proxy listesini kaynaklardan manuel güncelle
    
    **Kaynaklar:**
    - proxyscrape_http
    - proxyscrape_socks4
    - proxyscrape_socks5
    - geonode
    - github_http
    - github_socks4
    - github_socks5
    
    **Örnek (Tüm kaynaklar):**
    ```json
    POST /api/v1/proxy/update-list
    {
        "sources": null
    }
    ```
    
    **Örnek (Belirli kaynaklar):**
    ```json
    POST /api/v1/proxy/update-list
    {
        "sources": ["geonode", "proxyscrape_http"]
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "sources_count": 7,
        "total_fetched": 3500,
        "total_added": 250,
        "total_updated": 3250,
        "timestamp": "2025-01-10T12:00:00"
    }
    ```
    """
    service = ProxyService(db)
    
    result = service.update_proxy_list(sources=request.sources)
    
    return result


@router.get("/stats", summary="Proxy İstatistikleri")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Proxy istatistiklerini getir
    
    **Response:**
    ```json
    {
        "total": 5000,
        "active": 3500,
        "inactive": 1500,
        "avg_working_percent": 85.5,
        "avg_response_time": 250.3,
        "by_protocol": {
            "http": 2000,
            "https": 1800,
            "socks4": 1200,
            "socks5": 800
        }
    }
    ```
    """
    service = ProxyService(db)
    
    stats = service.get_statistics()
    
    return stats


@router.delete("/cleanup", summary="Pasif Proxyleri Temizle")
async def cleanup_inactive_proxies(
    days: int = Query(default=30, description="Kaç günden eski proxyleri temizle"),
    db: Session = Depends(get_db)
):
    """
    Uzun süredir kullanılmayan proxyleri sil
    
    **Örnek:**
    ```
    DELETE /api/v1/proxy/cleanup?days=30
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "deleted_count": 450,
        "days": 30
    }
    ```
    """
    service = ProxyService(db)
    
    deleted_count = service.cleanup_inactive_proxies(days=days)
    
    return {
        'success': True,
        'deleted_count': deleted_count,
        'days': days
    }

