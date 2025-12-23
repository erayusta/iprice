import uvicorn
from fastapi import FastAPI
from app.api.v1.endpoints import company, parsing, proxy

app = FastAPI(title="Price Analysis API")

app.include_router(company.router, prefix="/api/v1/company", tags=["company"])
app.include_router(parsing.router, prefix="/api/v1", tags=["parsing"])
app.include_router(proxy.router, prefix="/api/v1/proxy", tags=["proxy"])


if __name__ == "__main__":
    uvicorn.run("app.api_main:app", host="0.0.0.0", port=8000)