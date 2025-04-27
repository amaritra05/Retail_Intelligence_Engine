import h2o
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from datetime import datetime
import json

class RevenueModel:
    def __init__(self):
        self.model = None

    def train(self, train_data, predictors, response, model_type="glm"):
        if model_type == "glm":
            self.model = H2OGeneralizedLinearEstimator(family="gaussian")
        elif model_type == "rf":
            self.model = H2ORandomForestEstimator()
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
        
        self.model.train(x=predictors, y=response, training_frame=train_data)

    def predict(self, new_data):
        if self.model is None:
            raise ValueError("Model is not trained yet")
        
        preds = self.model.predict(new_data)
        return preds.as_data_frame().values.flatten().tolist()[0]