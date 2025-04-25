import h2o
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from datetime import datetime
import json

class RevenueModel:
    def __init__(self):
        self.models = {}
        self.dummy = H2OGeneralizedLinearEstimator()

    def train(self, data, predictors, response, model_type="glm"):
        if model_type == "glm":
            model = H2OGeneralizedLinearEstimator()
        elif model_type == "rf":
            model = H2ORandomForestEstimator()
        model.train(x=predictors, y=response, training_frame=data)
        self.models[model_type] = model
        self._log_metadata(model_type, predictors, model.r2())

    def predict(self, data, model_type="glm"):
        if model_type in self.models:
            pred = self.models[model_type].predict(data)
            return pred.as_data_frame().iloc[0, 0]
        return 0.0

    def _log_metadata(self, model_name, features, r2_score):
        meta = {
            "model": model_name,
            "features": features,
            "r2_score": r2_score,
            "timestamp": str(datetime.now())
        }
        with open(f"logs/{model_name}_metadata.json", "w") as f:
            json.dump(meta, f)