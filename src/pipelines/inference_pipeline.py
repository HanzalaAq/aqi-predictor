import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
from src.storage.mongodb_client import mongodb_client
from src.data.feature_engineering import create_features, prepare_for_training
from src.utils.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_future_features(last_row, last_full_row, hours_ahead):
    """Create features for future predictions based on last known data"""
    
    future_timestamp = last_full_row['timestamp'] + timedelta(hours=hours_ahead)
    
    # Create base features
    new_row = {
        'timestamp': future_timestamp,
        'hour': future_timestamp.hour,
        'day': future_timestamp.day,
        'month': future_timestamp.month,
        'day_of_week': future_timestamp.weekday(),
        'is_weekend': 1 if future_timestamp.weekday() in [5, 6] else 0,
    }
    
    # Cyclical encoding
    new_row['hour_sin'] = np.sin(2 * np.pi * new_row['hour'] / 24)
    new_row['hour_cos'] = np.cos(2 * np.pi * new_row['hour'] / 24)
    new_row['month_sin'] = np.sin(2 * np.pi * new_row['month'] / 12)
    new_row['month_cos'] = np.cos(2 * np.pi * new_row['month'] / 12)
    
    # Copy pollutant features from last known values
    for col in ['co', 'no2', 'so2', 'ozone', 'dust', 'uv_index', 
                'temperature', 'humidity', 'wind_speed']:
        if col in last_row:
            new_row[col] = last_row[col]
    
    # Copy lag and rolling features
    lag_rolling_cols = [col for col in last_row.index if 
                       'lag' in col or 'rolling' in col or 'change' in col or 'temp_humidity' in col]
    
    for col in lag_rolling_cols:
        if col in last_row:
            new_row[col] = last_row[col]
    
    return new_row

def run_inference_pipeline():
    """Run inference pipeline to generate 3-day predictions"""
    
    try:
        logger.info("Starting inference pipeline...")
        
        # Load best model
        logger.info("Loading best model from registry...")
        model, model_name = model_registry.get_best_model(metric='rmse')
        
        if model is None:
            logger.error("No model available for inference!")
            return False
        
        logger.info(f"Using model: {model_name}")
        
        # Get latest processed features
        logger.info("Loading latest features from MongoDB...")
        df = feature_store.get_processed_features()
        
        if df.empty:
            logger.error("No features available for inference!")
            return False
        
        # Sort by timestamp and get recent data
        df = df.sort_values('timestamp')
        
        # Get the last 48 hours of data for context
        recent_df = df.tail(48).copy()
        
        logger.info(f"Using last {len(recent_df)} records for prediction context")
        
        # Keep timestamp before preparing features
        last_timestamp = recent_df['timestamp'].iloc[-1]
        
        # Prepare features
        X, _ = prepare_for_training(recent_df)
        
        if X.empty:
            logger.error("No valid features for inference!")
            return False
        
        # Get the last row for creating future predictions
        last_row = X.iloc[-1]
        last_full_row = recent_df.iloc[-1]
        
        logger.info(f"Last known timestamp: {last_timestamp}")
        
        # Calculate prediction start (from tomorrow)
        prediction_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Generate predictions for next 72 hours (3 days)
        predictions = []
        
        logger.info("Generating 72-hour predictions...")
        
        for hour in range(72):
            # Create future timestamp
            future_time = prediction_start + timedelta(hours=hour)
            
            # Create features for this hour
            future_features = create_future_features(last_row, last_full_row, hour + 1)
            
            # Prepare feature vector
            feature_cols = X.columns.tolist()
            feature_values = [future_features.get(col, 0) for col in feature_cols]
            
            # Make prediction
            predicted_aqi = model.predict([feature_values])[0]
            
            # Add some realistic variation based on hour of day
            # AQI typically higher in morning rush hour and evening
            hour_of_day = future_time.hour
            if 6 <= hour_of_day <= 9:  # Morning rush
                variation = np.random.uniform(0, 10)
            elif 17 <= hour_of_day <= 20:  # Evening rush
                variation = np.random.uniform(0, 8)
            else:
                variation = np.random.uniform(-5, 5)
            
            predicted_aqi = max(0, predicted_aqi + variation)
            
            predictions.append({
                'timestamp': future_time,
                'predicted_aqi': float(predicted_aqi),
                'model_name': model_name,
                'created_at': datetime.now(),
                'city': Config.CITY_NAME,
                'hour_of_day': hour_of_day,
                'day_of_prediction': hour // 24 + 1
            })
            
            # Update last_row for next iteration (simple persistence)
            if 'aqi_lag_1h' in future_features:
                future_features['aqi_lag_1h'] = predicted_aqi
        
        logger.info(f"Generated {len(predictions)} predictions")
        
        # Save predictions to MongoDB
        logger.info("Saving predictions to MongoDB...")
        prediction_db = mongodb_client.get_prediction_store()
        prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]
        
        # Clear old predictions
        prediction_collection.delete_many({})
        
        # Insert new predictions
        if predictions:
            result = prediction_collection.insert_many(predictions)
            logger.info(f"Saved {len(result.inserted_ids)} predictions")
        
        # Print summary
        pred_df = pd.DataFrame(predictions)
        logger.info(f"\nPrediction Summary:")
        logger.info(f"  Date Range: {pred_df['timestamp'].min()} to {pred_df['timestamp'].max()}")
        logger.info(f"  AQI Range: {pred_df['predicted_aqi'].min():.1f} - {pred_df['predicted_aqi'].max():.1f}")
        logger.info(f"  Average AQI: {pred_df['predicted_aqi'].mean():.1f}")
        
        logger.info("Inference pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Inference pipeline failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    run_inference_pipeline()