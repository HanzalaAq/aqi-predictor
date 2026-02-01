import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_features(df):
    """Create time-based and derived features"""
    df = df.copy()
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    logger.info(f"Starting feature engineering with {len(df)} records")
    
    # Convert None to NaN for numerical operations
    numeric_cols = ['pm10', 'pm2_5', 'co', 'no2', 'so2', 'ozone', 'dust', 
                    'uv_index', 'temperature', 'humidity', 'wind_speed', 'aqi']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Cyclical encoding for hour
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Cyclical encoding for month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    logger.info("Creating lag features...")
    # Lag features (previous hour values)
    for col in ['pm2_5', 'pm10', 'aqi', 'temperature', 'humidity']:
        if col in df.columns:
            df[f'{col}_lag_1h'] = df[col].shift(1)
            df[f'{col}_lag_24h'] = df[col].shift(24)
    
    logger.info("Creating rolling averages...")
    # Rolling averages
    for col in ['pm2_5', 'pm10', 'aqi']:
        if col in df.columns:
            df[f'{col}_rolling_3h'] = df[col].rolling(window=3, min_periods=1).mean()
            df[f'{col}_rolling_24h'] = df[col].rolling(window=24, min_periods=1).mean()
    
    logger.info("Creating rate of change features...")
    # Rate of change (handle NaN/None values)
    if 'aqi' in df.columns:
        df['aqi_change_rate'] = df['aqi'].diff().fillna(0)
    
    if 'pm2_5' in df.columns:
        df['pm2_5_change_rate'] = df['pm2_5'].diff().fillna(0)
    
    # Interaction features
    if 'temperature' in df.columns and 'humidity' in df.columns:
        df['temp_humidity'] = df['temperature'] * df['humidity']
    
    logger.info("Filling missing values...")
    # Fill missing values (forward then backward fill)
    for col in df.columns:
        if col != 'timestamp' and df[col].dtype in ['float64', 'int64']:
            # Use bfill() and ffill() instead of deprecated fillna(method=)
            df[col] = df[col].bfill()
            df[col] = df[col].ffill()
            # Fill any remaining NaN with 0
            df[col] = df[col].fillna(0)
    
    logger.info(f"Feature engineering complete! Created features for {len(df)} records")
    
    return df


def prepare_for_training(df, target_col='aqi'):
    """Prepare data for model training"""
    # Exclude non-feature columns
    exclude_cols = ['timestamp', 'aqi', 'pm2_5', 'pm10', 'created_at', 'city', '_id']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df[target_col] if target_col in df.columns else None
    
    logger.info(f"Prepared {len(X)} samples with {len(feature_cols)} features for training")
    
    return X, y