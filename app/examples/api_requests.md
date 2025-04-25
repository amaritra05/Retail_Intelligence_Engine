### POST /predict-revenue
```
curl -X POST http://localhost:8000/predict-revenue \
  -H "Content-Type: application/json" \
  -d '{"sku": "SKU123", "ship_state": "NY", "date": "2023-04-21"}'
```

# 📘 API Example Requests & Responses

## GET /health

### Request:
```http
GET /health
```

### Response:
```json
{
  "status": "OK"
}
```

---

## POST /predict-revenue

### Request:
```http
POST /predict-revenue
Content-Type: application/json

{
  "sku": "JNE3371-KR-XL",
  "ship_state": "MAHARASHTRA",
  "date": "2025-05-01"
}
```

### Response:
```json
{
  "predicted_revenue": 1325.50
}
```

---

## GET /top-skus/{year}/{month}/{metric}/{top_n}

### Request:
```http
GET /top-skus/2022/4/revenue/5
```

### Response:
```json
[
  {
    "sku": "JNE3371-KR-XL",
    "total_revenue": 13500
  }
]
```

---

## GET /category-performance

### Request:
```http
GET /category-performance
```

### Response:
```json
[
  {
    "category": "Set",
    "daily_revenue": 258000
  },
  {
    "category": "Top",
    "daily_revenue": 132000
  }
]
```

