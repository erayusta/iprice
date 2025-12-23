import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any

from app.api.v1.schemas.company import CompanyRequest, CompanyResponse
from app.database import get_db
from app.services.CompanyParser import CompanyParser
from app.repositories.ProductRepository import ProductRepository
from app.repositories.ScreenshotRepository import ScreenshotRepository
from app.services.ProductService import ProductService
from app.services.ScreenshotService import ScreenshotService
from app.repositories.ProductHistoryRepository import ProductHistoryRepository
from app.repositories.ImageRepository import ImageRepository
from app.repositories.JobLogRepository import JobLogRepository

router = APIRouter()


def get_job_log_repository(db: Session = Depends(get_db)):
    return JobLogRepository(db)


def get_screenshot_repository(db: Session = Depends(get_db)):
    return ScreenshotRepository(db)


def get_product_repository(db: Session = Depends(get_db)):
    return ProductRepository(db)


def get_screenshot_service(screenshot_repo: ScreenshotRepository = Depends(get_screenshot_repository)):
    return ScreenshotService(screenshot_repo)


def get_product_history_repository(db: Session = Depends(get_db)):
    return ProductHistoryRepository(db)


def get_image_repository(db: Session = Depends(get_db)):
    return ImageRepository(db)


def get_product_service(
        product_repo: ProductRepository = Depends(get_product_repository),
        product_history_repo: ProductHistoryRepository = Depends(get_product_history_repository),
        image_repo: ImageRepository = Depends(get_image_repository)
):
    return ProductService(product_repo, product_history_repo, image_repo)


def run_company_processing_in_background(
        job_log_id: int,
        company_id: int,
        company_name: str,
        product_service: ProductService,
        screenshot_service: ScreenshotService,
        job_log_repo: JobLogRepository
):
    print(f"Arka plan işlemi başlıyor: {company_name} (Job ID: {job_log_id})")

    # Yeni bir veritabanı bağlantısı al
    from app.database import get_db
    db = next(get_db())
    job_log_repo_bg = JobLogRepository(db)

    try:
        # İşlem başlarken durumu 'running' yap
        job_log_repo_bg.update_status(job_log_id, 'running')

        service = CompanyParser(
            product_service=product_service,
            screenshot_service=screenshot_service
        )

        result = asyncio.run(service.process_company_data(
            company_id=company_id,
            company_name=company_name,
        ))

        # Sonucu JSON formatında hazırla
        result_data = {
            "company_id": company_id,
            "company_name": company_name,
            "status": "completed",
            "total_products": result.get("total_products", 0),
            "processed_products": result.get("processed_products", 0),
            "successful": result.get("successful", 0),
            "failed": result.get("failed", 0),
            "duration": result.get("duration", 0)
        }

        # Başarılı olduğunda durumu güncelle
        job_log_repo_bg.update_on_finish(job_log_id, 'success', result_data, "İşlem başarıyla tamamlandı.")
        print(f"Arka plan işlemi başarıyla tamamlandı: {company_name}")

    except Exception as e:
        print(f"Background processing error for {company_name}: {str(e)}")
        try:
            # Hata durumunda yeni bir session ile güncelleme yap
            db.rollback()
            job_log_repo_bg.update_on_finish(job_log_id, 'failed', {"error": True}, str(e))
        except Exception as update_error:
            print(f"Failed to update job log status: {str(update_error)}")
    finally:
        db.close()


@router.post("/process", response_model=CompanyResponse)
async def process_company(
        request: CompanyRequest,
        background_tasks: BackgroundTasks,
        product_service: ProductService = Depends(get_product_service),
        screenshot_service: ScreenshotService = Depends(get_screenshot_service),
        job_log_repo: JobLogRepository = Depends(get_job_log_repository)
) -> Any:
    background_tasks.add_task(
        run_company_processing_in_background,
        request.job_log_id,
        request.company_id,
        request.company_name,
        product_service,
        screenshot_service,
        job_log_repo
    )

    return CompanyResponse(
        status="success",
        message=f"Processing for '{request.company_name}' has been started in the background.",
        data={"status": "processing_started"}
    )