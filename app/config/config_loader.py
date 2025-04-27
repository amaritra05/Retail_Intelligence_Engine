import toml
from pydantic import BaseModel
from typing import List

class AppConfig(BaseModel):
    amazon_sales: str
    international_sales: str
    sale_report: str
    pl_files: List[str]

def load_config(path: str) -> AppConfig:
    data = toml.load(path)
    return AppConfig(**data['paths'])
