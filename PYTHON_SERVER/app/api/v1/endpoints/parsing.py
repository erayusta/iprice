from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

# Queue producer import et
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from app.messaging.producer import JobProducer

router = APIRouter()


# Schemas
class AttributeSchema(BaseModel):
    company_id: int
    attributes_id: int
    attributes_name: str
    attributes_type: str
    attributes_value: str


class ParseUrlRequest(BaseModel):
    job_id: int
    company_id: int
    product_id: int
    application_id: int
    server_id: int
    server_name: str
    screenshot: bool = False
    marketplace: bool = False
    url: str
    npm: str  # MPN (Manufacturer Part Number)
    attributes: list[AttributeSchema]
    parser_type: str = "scrapy"  # Opsiyonel - scrapy, selenium, playwright
    use_proxy: bool = True  # Proxy kullanılsın mı? (varsayılan: True)
    proxy_type: str = "brightdata"  # Proxy tipi (varsayılan: brightdata)


class ParseUrlResponse(BaseModel):
    status: str
    message: str
    job_id: int  # Original job_id from payload
    queue: str


# Parse URL endpoint
@router.post("/parse-url", response_model=ParseUrlResponse)
async def parse_url(request: ParseUrlRequest) -> Any:
    try:
        producer = JobProducer()

        print(f"🔍 Request alındı: {request.dict()}")

        # Request'i dict'e çevir
        job_data = request.dict()
        
        result = producer.send_parsing_job(job_data=job_data)

        print(f"🔍 Producer result: {result}")

        if result['success']:
            response_data = {
                "status": "success",
                "message": "Parsing job queue'ya gönderildi",
                "job_id": result['job_id'],
                "queue": result['queue']
            }

            print(f"🔍 API Response: {response_data}")

            return ParseUrlResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Parse URL hatası: {str(e)}"
        )


# Queue status endpoint (bonus)
@router.get("/queue-status/{queue_name}")
async def get_queue_status(queue_name: str) -> Any:
    """Queue durumunu kontrol et"""
    try:
        producer = JobProducer()
        size = producer.get_queue_size(queue_name)

        return {
            "queue_name": queue_name,
            "message_count": size,
            "status": "active" if size >= 0 else "error"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Queue status hatası: {str(e)}"
        )