from fastapi import FastAPI
from loguru import logger
from app.routes.api import router as api_router

app = FastAPI(title="Retail Forecasting API")

logger.add("logs/app.log", rotation="1 MB")

@app.get("/health")
def health():
    return {"status": "OK"}

app.include_router(api_router)