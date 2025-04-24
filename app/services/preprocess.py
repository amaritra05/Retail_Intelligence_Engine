import pandas as pd

def clean_data(df):
    if 'amount' in df.columns:
        df = df.dropna(subset=["amount"])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    if 'qty' in df.columns:
        df = df.dropna(subset=["qty"])
        df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
        df = df[df["qty"] > 0]
    if 'status' in df.columns:
        df = df[df["status"].str.lower() != "cancelled"]
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    rename_map = {
        'amount': 'price',
        'qty': 'quantity',
    }
    df = df.rename(columns=rename_map)
    return df

def merge_datasets(amazon, international, sale):
    df = amazon.merge(international, on="sku", how="outer")
    df = df.merge(sale, on="sku", how="outer")
    return df

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df["revenue"] = df["price"] * df["quantity"]

    print("Raw date samples:", df["date"].dropna().unique()[:5])
    df["date"] = pd.to_datetime(df["date"], unit="ms")
    df = df.dropna(subset=["date"])

    grouped = df.groupby(["ship-state", "category", "sku", "date"]).agg(
        daily_revenue=("revenue", "sum"),
        avg_selling_price=("price", "mean"),
        order_count=("sku", "count"),
        sku_velocity=("quantity", "sum")
    ).reset_index()

    top_skus = (
        grouped.groupby("sku")
        .agg(total_revenue=("daily_revenue", "sum"), total_quantity=("sku_velocity", "sum"))
        .sort_values("total_revenue", ascending=False)
        .reset_index()
    )
    return grouped, top_skus