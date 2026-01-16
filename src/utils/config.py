import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'aqi_features')
    MODEL_DATABASE = os.getenv('MODEL_DATABASE', 'aqi_models')
    PREDICTION_DATABASE = os.getenv('PREDICTION_DATABASE', 'aqi_predictions')
    
    # API Configuration
    LATITUDE = float(os.getenv('LATITUDE', '24.8607'))
    LONGITUDE = float(os.getenv('LONGITUDE', '67.0011'))
    CITY_NAME = os.getenv('CITY_NAME', 'Karachi')
    
    # Model Configuration
    MODELS = ['random_forest', 'xgboost', 'lightgbm']
    PREDICTION_DAYS = 3
    
    # Data Collection
    HISTORICAL_MONTHS = 4  # Collect 4 months of data
    
    # Collection Names
    RAW_DATA_COLLECTION = 'raw_data'
    PROCESSED_FEATURES_COLLECTION = 'processed_features'
    MODELS_COLLECTION = 'models'
    MODEL_METRICS_COLLECTION = 'model_metrics'
    PREDICTIONS_COLLECTION = 'predictions'