import pandas as pd
import toml

from pydantic import BaseModel

class Config(BaseModel):
    amazon_sales: str
    international_sales: str
    sale_report: str
    pnl_march_2021: str
    pnl_may_2022: str

def load_config():
    config = toml.load("app/config.toml")
    return Config(**config['paths'])

def load_data():
    cfg = load_config()
    df_amazon = pd.read_csv(cfg.amazon_sales)
    df_international = pd.read_csv(cfg.international_sales)
    df_stock = pd.read_csv(cfg.sale_report)
    df_pnl1 = pd.read_csv(cfg.pnl_march_2021)
    df_pnl2 = pd.read_csv(cfg.pnl_may_2022)

    return df_amazon, df_international, df_stock, df_pnl1, df_pnl2