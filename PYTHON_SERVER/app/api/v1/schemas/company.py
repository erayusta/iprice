from pydantic import BaseModel
from typing import Optional

class CompanyRequest(BaseModel):
    company_id: int
    company_name: str
    job_log_id: int

class CompanyResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    
    class Config:
        from_attributes = True