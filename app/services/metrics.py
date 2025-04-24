def compute_metrics(df):
    df["revenue"] = df["price"] * df["quantity"]
    grouped = df.groupby(["ship_state", "category", "date"]).agg({
        "revenue": "sum",
        "SKU": "count",
        "quantity": "sum"
    }).rename(columns={"SKU": "order_count"})
    grouped["ASP"] = grouped["revenue"] / grouped["quantity"]
    return grouped.reset_index()