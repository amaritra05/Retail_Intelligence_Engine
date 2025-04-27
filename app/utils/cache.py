from functools import lru_cache, wraps
from app.models.schema import PredictRequest
from app.services.preprocess import clean_data, normalize_columns, merge_datasets
from app.config.config_loader import AppConfig

from typing import Optional
import pandas as pd
import h2o

def cache_response(func):
    cached_func = lru_cache(maxsize=128)(lambda sku, state, date: func(PredictRequest(sku=sku, ship_state=state, date=date)))

    @wraps(func)
    def wrapper(req: PredictRequest):
        return cached_func(req.sku, req.ship_state, str(req.date))
    
    return wrapper

class FullDataCacheManager:
    def __init__(self):
        self.last_config_hash: Optional[int] = None
        self._config: Optional[AppConfig] = None
        if not h2o.connection():
                h2o.init()

    def load_data(self, config: AppConfig) -> pd.DataFrame:
        config_hash = self._hash_config(config)

        if self.last_config_hash == config_hash:
            return self._get_cached_data(config_hash)
        else:
            self._clear_cache()
            self.last_config_hash = config_hash
            self._config = config
            return self._get_cached_data(config_hash)

    @lru_cache(maxsize=1)
    def _get_cached_data(self, config_hash: int) -> pd.DataFrame:
        """Load and cache data."""
        print(f"Loading fresh data from disk")
        return self._load_all_data(self._config)

    def _clear_cache(self):
        self._get_cached_data.cache_clear()

    def _hash_config(self, config: AppConfig) -> int:
        """Create a hash based on all file paths."""
        all_paths = [
            config.amazon_sales,
            config.international_sales,
            config.sale_report,
            *config.pl_files
        ]
        return hash(tuple(all_paths))

    def _load_all_data(self, config: AppConfig) -> pd.DataFrame:
        """loading and preprocessing."""
        data = {
            "amazon": clean_data(h2o.import_file(config.amazon_sales).as_data_frame()),
            "international": clean_data(h2o.import_file(config.international_sales).as_data_frame()),
            "sale": clean_data(h2o.import_file(config.sale_report).as_data_frame()),
            "pl": [clean_data(h2o.import_file(f).as_data_frame()) for f in config.pl_files]
        }

        # Normalize columns
        for key in data:
            if isinstance(data[key], list):
                data[key] = [normalize_columns(df) for df in data[key]]
            else:
                data[key] = normalize_columns(data[key])

        # Post-processing
        data['sale']['sku'] = data['sale']['sku_code']
        data['merged'] = merge_datasets(data['amazon'], data['international'], data['sale'])
        df = data["merged"]

        df['date'] = pd.to_datetime(df['date_x'], unit='ms')  

        # Extract year, month, day
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['category'] = df['category_x']

        # Calculate revenue if not present
        if "revenue" not in df.columns:
            df["revenue"] = df["price"] * df["quantity"]

        return df
