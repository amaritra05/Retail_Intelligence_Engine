# Retail Forecasting API

This project is a modular Python backend built with **FastAPI** 
which loads, processes, and forecasts retail sales data using **H2O.ai** for modeling, **Pydantic** for config and data validation. The system can predict revenue, identify top-performing SKUs, and provide category-level performance analytics.

---

## Features

- **Data Loading**: Load sales data, profit & loss statements, and sales reports from a TOML config file.
- **Preprocessing**: Cleans, normalizes datasets. 
- **Feature Engineering**: Computes metrics like daily revenue, ASP, order count, SKU velocity.
- **Prediction**: Predicts revenue for a given SKU, date, and ship-state.
- **Analytics Endpoints**: Retrieve top SKUs and category performance.
- **Design**: Separated concerns across `config`, `data`, `models`, `routes`, `services`, `utils`.

### 1. Set up a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

## Example Requests

See `api_examples.md`for example request/response payloads.

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic
- H2O.ai
- Pandas
- Loguru
- TOML config

---

## Project Structure

```
app/
│
├── config/           # TOML config loader
├── data/             # Data ingestion
├── models/           # Schema + Predictors
├── routes/           # FastAPI routes
├── services/         # Preprocessing and metrics
├── utils/            # Caching, helpers
├── tests/            # Unit tests
└── main.py           # App entry point
```

---
