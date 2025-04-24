import os
import toml
import h2o
from datetime import datetime
from h2o.estimators.random_forest import H2ORandomForestEstimator

h2o.init()

MODEL_PATH = "app/artifacts/model_rf"
META_PATH = "app/artifacts/model_metadata.toml"

def train_model(df, features, target):
    hf = h2o.H2OFrame(df)
    model = H2ORandomForestEstimator()
    model.train(x=features, y=target, training_frame=hf)
    model.save_mojo(MODEL_PATH, force=True)

    r2 = model.model_performance(hf).r2()
    metadata = {
        "name": "RFModel",
        "features": features,
        "target": target,
        "r2_score": r2,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(META_PATH, 'w') as f:
        toml.dump(metadata, f)
    return model

def load_model():
    if not os.path.exists(META_PATH):
        return None
    return h2o.import_mojo(MODEL_PATH)

def predict(model, row):
    hf = h2o.H2OFrame([row])
    return model.predict(hf).as_data_frame().iloc[0, 0]