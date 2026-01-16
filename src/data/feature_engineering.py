import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_features(df):
    """Create time-based and derived features"""
    
    if df.empty:
        logger.warning("Input dataframe is empty!")
        return df
    
    df = df.copy()
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    logger.info(f"Starting feature engineering with {len(df)} records")
    
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
    
    # Lag features (previous hour values)
    logger.info("Creating lag features...")
    for col in ['pm2_5', 'pm10', 'aqi', 'temperature', 'humidity']:
        if col in df.columns:
            df[f'{col}_lag_1h'] = df[col].shift(1)
            df[f'{col}_lag_24h'] = df[col].shift(24)
    
    # Rolling averages
    logger.info("Creating rolling averages...")
    for col in ['pm2_5', 'pm10', 'aqi']:
        if col in df.columns:
            df[f'{col}_rolling_3h'] = df[col].rolling(window=3, min_periods=1).mean()
            df[f'{col}_rolling_24h'] = df[col].rolling(window=24, min_periods=1).mean()
    
    # Rate of change
    logger.info("Creating rate of change features...")
    if 'aqi' in df.columns:
        df['aqi_change_rate'] = df['aqi'].diff()
    if 'pm2_5' in df.columns:
        df['pm2_5_change_rate'] = df['pm2_5'].diff()
    
    # Interaction features
    if 'temperature' in df.columns and 'humidity' in df.columns:
        df['temp_humidity'] = df['temperature'] * df['humidity']
    
    # Fill NaN values for lag features with forward fill then backward fill
    logger.info("Filling missing values...")
    
    # For lag features, fill with the previous valid value
    lag_cols = [col for col in df.columns if 'lag' in col or 'rolling' in col or 'change' in col]
    
    for col in lag_cols:
        # Fill first few NaN values with the first valid value (backward fill)
        df[col] = df[col].fillna(method='bfill')
        # Then forward fill any remaining
        df[col] = df[col].fillna(method='ffill')
        # If still NaN (shouldn't happen), fill with 0
        df[col] = df[col].fillna(0)
    
    # Drop any remaining NaN rows (should be very few if any)
    initial_len = len(df)
    df = df.dropna()
    dropped = initial_len - len(df)
    
    if dropped > 0:
        logger.info(f"Dropped {dropped} rows with NaN values")
    
    logger.info(f"Feature engineering complete! Created features for {len(df)} records")
    
    return df

def prepare_for_training(df, target_col='aqi'):
    """Prepare data for model training"""
    
    if df.empty:
        logger.warning("Input dataframe is empty!")
        return pd.DataFrame(), pd.Series(dtype=float)
    
    # Exclude non-feature columns
    exclude_cols = ['timestamp', 'aqi', 'pm2_5', 'pm10', 'created_at', 'city', '_id']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    logger.info(f"Feature columns: {feature_cols}")
    
    X = df[feature_cols]
    y = df[target_col] if target_col in df.columns else None
    
    logger.info(f"Prepared {len(X)} samples with {len(feature_cols)} features for training")
    
    return X, y