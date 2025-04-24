from functools import lru_cache, wraps
from models.schema import PredictRequest

def cache_response(func):
    cached_func = lru_cache(maxsize=128)(lambda sku, state, date: func(PredictRequest(sku=sku, ship_state=state, date=date)))

    @wraps(func)
    def wrapper(req: PredictRequest):
        return cached_func(req.sku, req.ship_state, str(req.date))
    
    return wrapper
