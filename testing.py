from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
import pandas as pd

prediction_db = mongodb_client.get_prediction_store()
prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]

# Get latest prediction
latest = prediction_collection.find_one(sort=[("created_at", -1)])

if latest:
    print(f"Prediction created at: {latest['created_at']}")
    print(f"Prediction for timestamp: {latest['timestamp']}")
    print(f"Predicted AQI: {latest['predicted_aqi']}")