import h2o
import pandas as pd
from config.config_loader import AppConfig
from services.preprocess import clean_data, normalize_columns

h2o.init()

def load_all_data(config: AppConfig):
    data = {
        "amazon": clean_data(h2o.import_file(config.amazon_sales).as_data_frame()),
        "international": clean_data(h2o.import_file(config.international_sales).as_data_frame()),
        "sale": clean_data(h2o.import_file(config.sale_report).as_data_frame()),
        "pl": [clean_data(h2o.import_file(f).as_data_frame()) for f in config.pl_files]
    }
    # Normalize column names
    for key in data:
        if isinstance(data[key], list):
            data[key] = [normalize_columns(df) for df in data[key]]
        else:
            data[key] = normalize_columns(data[key])
    return data