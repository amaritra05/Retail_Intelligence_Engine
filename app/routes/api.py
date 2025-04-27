from fastapi import APIRouter, Query, HTTPException
from app.models.schema import PredictRequest, PredictResponse
from app.models.predictors import RevenueModel
from app.utils.cache import FullDataCacheManager, cache_response
from app.services.preprocess import compute_metrics, merge_datasets
from app.config.config_loader import load_config
import pandas as pd
import os
import h2o

router = APIRouter()

# Global objects
full_data_cache = FullDataCacheManager()
path = os.path.join("app", "config.toml")
config = load_config(path)
model = RevenueModel()


def train_global_model():
    print("Training global revenue model...")
    data = full_data_cache.load_data(config)
    df = data

    # Preprocessing
    df['date'] = pd.to_datetime(df['date'], errors="coerce")
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['sku'] = df['sku'].str.lower()
    df['ship-state'] = df['ship-state'].str.lower()

    

    # H2OFrame
    h2o_df = h2o.H2OFrame(df)
    h2o_df['sku'] = h2o_df['sku'].asfactor()
    h2o_df['ship-state'] = h2o_df['ship-state'].asfactor()

    # Features and Target
    features = ['sku', 'ship-state', 'year', 'month', 'day']
    target = 'revenue'

    # Train Model
    model.train(h2o_df, features, target, model_type="glm")

train_global_model()
@router.post("/predict-revenue", response_model=PredictResponse)
@cache_response
def predict_revenue(req: PredictRequest):
    # Build input row
    
    input_data = {
        "sku": [req.sku.strip().lower()],
        "ship-state": [req.ship_state.strip().lower()],
        "year": [req.date.year],
        "month": [req.date.month],
        "day": [req.date.day],
    }
    input_df = pd.DataFrame(input_data)
    input_hf = h2o.H2OFrame(input_df)
    input_hf['sku'] = input_hf['sku'].asfactor()
    input_hf['ship-state'] = input_hf['ship-state'].asfactor()

    # Predict
    predicted_revenue = model.predict(input_hf)

    return PredictResponse(predicted_revenue=round(predicted_revenue, 2))


@router.get("/top-skus/{year}/{month}/{metric}/{n}")
def top_skus_by_month(year: int, month: int, metric: str, n: int):
    if metric not in ["quantity", "revenue"]:
        raise HTTPException(status_code=400, detail="Invalid metric")

    df = full_data_cache.load_data(config)
    df, _ = compute_metrics(df)

    df['date'] = pd.to_datetime(df['date'], errors="coerce")

    filtered = df[
        (df['date'].dt.year == year) & 
        (df['date'].dt.month == month)
    ]

    if filtered.empty:
        return []

    sort_col = 'sku_velocity' if metric == 'quantity' else 'daily_revenue'

    top_skus = (
        filtered.groupby('sku')
        .agg({sort_col: 'sum'})
        .sort_values(sort_col, ascending=False)
        .head(n)
        .reset_index()
    )

    return top_skus.to_dict(orient='records')


@router.get("/category-performance")
def category_performance(group_by: str = Query("category", enum=["category", "ship-state"])):
    df = full_data_cache.load_data(config)
    print(df.columns)
    df, _ = compute_metrics(df)

    if group_by not in df.columns:
        return {"error": "Invalid group_by option"}

    grouped = df.groupby(group_by)['daily_revenue'].sum().reset_index()

    return grouped.to_dict(orient='records')