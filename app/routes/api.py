from fastapi import APIRouter, Query, Path, HTTPException
from datetime import datetime
from models.schema import PredictRequest, PredictResponse, TopSKUsRequest, CategoryPerformanceResponse
from models.predictors import RevenueModel
from utils.cache import cache_response
from typing import List
import pandas as pd
import h2o
from config.config_loader import load_config
from data.loader import load_all_data
from services.preprocess import compute_metrics
from models.engine import RevenueModelEngine


config = load_config("config.toml")
data = load_all_data(config)
router = APIRouter()
model = RevenueModel()
model_engine = RevenueModelEngine()


@router.post("/predict-revenue", response_model=PredictResponse)
@cache_response
def predict_revenue(req: PredictRequest):
    sku = req.sku.strip().lower()
    state = req.ship_state.strip().lower()

    amazon_df = data["amazon"]
    amazon_df["sku"] = amazon_df["sku"].str.strip().str.lower()
    amazon_df["ship-state"] = amazon_df["ship-state"].str.strip().str.lower()

    filtered = amazon_df[(amazon_df["sku"] == sku) & (amazon_df["ship-state"] == state)]

    if filtered.empty:
        return PredictResponse(predicted_revenue=0.0)

    if "revenue" not in filtered.columns:
        filtered["revenue"] = filtered["price"] * filtered["quantity"]

    predictors = ["price"]
    response = "revenue"

    h2o_train = h2o.H2OFrame(filtered[predictors + [response]])
    model.train(h2o_train, predictors, response, model_type="glm")

    avg_price = filtered["price"].mean()
    h2o_input = h2o.H2OFrame({"price": [avg_price]})
    prediction = model.predict(h2o_input)

    return PredictResponse(predicted_revenue=round(prediction, 2))


@router.get("/top-skus/{year}/{month}/{metric}/{n}")
def top_skus_by_month(year: int, month: int, metric: str, n: int):
    if metric not in ["quantity", "revenue"]:
        raise HTTPException(status_code=400, detail="Invalid metric")

    df, _ = compute_metrics(data["amazon"])

    # print("Metrics DataFrame shape:", df.shape)
    # print("Sample data:\n", df.head())

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # print("Unique years in data:", df["date"].dt.year.unique())
    # print("Unique months in data:", df["date"].dt.month.unique())

    filtered = df[
        (df["date"].dt.year == year) &
        (df["date"].dt.month == month)
    ]

    # print("Filtered shape:", filtered.shape)
    # print("Filtered sample:\n", filtered.head())

    if filtered.empty:
        return []

    sort_col = "sku_velocity" if metric == "quantity" else "daily_revenue"

    top_skus = (
        filtered.groupby("sku")
        .agg({sort_col: "sum"})
        .sort_values(sort_col, ascending=False)
        .head(n)
        .reset_index()
    )

    # print("Top SKUs:\n", top_skus)

    return top_skus.to_dict(orient="records")


@router.get("/category-performance")
def category_performance(group_by: str = Query("category", enum=["category", "ship-state"])):
    df, _ = compute_metrics(data["amazon"])

    if group_by not in df.columns:
        return {"error": "Invalid group_by option"}

    grouped = df.groupby(group_by)["daily_revenue"].sum().reset_index()
    return grouped.to_dict(orient="records")