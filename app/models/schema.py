from pydantic import BaseModel
from datetime import date

class PredictRequest(BaseModel):
    sku: str
    ship_state: str
    date: date

class PredictResponse(BaseModel):
    predicted_revenue: float

class TopSKUsRequest(BaseModel):
    month: str
    top_n: int = 10
    metric: str = "revenue"

class CategoryPerformanceResponse(BaseModel):
    category: str
    region: str
    revenue: float