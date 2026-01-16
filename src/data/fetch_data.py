import requests
import pandas as pd
from datetime import datetime, timedelta
from src.utils.config import Config
import logging

logger = logging.getLogger(__name__)

def fetch_air_quality_data(start_date, end_date):
    """Fetch air quality data from Open-Meteo API"""
    
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': [
            'pm10', 'pm2_5', 'carbon_monoxide', 
            'nitrogen_dioxide', 'sulphur_dioxide', 
            'ozone', 'dust', 'uv_index'
        ],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        logger.info(f"Fetching air quality data from {start_date} to {end_date}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'pm10': data['hourly']['pm10'],
            'pm2_5': data['hourly']['pm2_5'],
            'co': data['hourly']['carbon_monoxide'],
            'no2': data['hourly']['nitrogen_dioxide'],
            'so2': data['hourly']['sulphur_dioxide'],
            'ozone': data['hourly']['ozone'],
            'dust': data['hourly']['dust'],
            'uv_index': data['hourly']['uv_index']
        })
        
        logger.info(f"Fetched {len(df)} air quality records")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing API data: {e}")
        raise

def fetch_weather_data(start_date, end_date):
    """Fetch weather data from Open-Meteo ARCHIVE API"""
    
    # Use ARCHIVE API for historical data
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': [
            'temperature_2m',
            'relative_humidity_2m',
            'wind_speed_10m'
        ],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        logger.info(f"Fetching weather data from {start_date} to {end_date}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'temperature': data['hourly']['temperature_2m'],
            'humidity': data['hourly']['relative_humidity_2m'],
            'wind_speed': data['hourly']['wind_speed_10m']
        })
        
        logger.info(f"Fetched {len(df)} weather records")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing weather data: {e}")
        raise

def calculate_aqi(pm2_5, pm10):
    """Calculate AQI based on PM2.5 and PM10 (US EPA standard)"""
    
    def get_aqi_pm25(pm25):
        if pd.isna(pm25):
            return 0
        if pm25 <= 12.0:
            return (50 / 12.0) * pm25
        elif pm25 <= 35.4:
            return 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
        elif pm25 <= 55.4:
            return 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
        elif pm25 <= 150.4:
            return 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
        elif pm25 <= 250.4:
            return 200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5)
        else:
            return 300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5)
    
    def get_aqi_pm10(pm10):
        if pd.isna(pm10):
            return 0
        if pm10 <= 54:
            return (50 / 54) * pm10
        elif pm10 <= 154:
            return 50 + ((100 - 50) / (154 - 55)) * (pm10 - 55)
        elif pm10 <= 254:
            return 100 + ((150 - 100) / (254 - 155)) * (pm10 - 155)
        elif pm10 <= 354:
            return 150 + ((200 - 150) / (354 - 255)) * (pm10 - 255)
        elif pm10 <= 424:
            return 200 + ((300 - 200) / (424 - 355)) * (pm10 - 355)
        else:
            return 300 + ((500 - 300) / (604 - 425)) * (pm10 - 425)
    
    aqi_pm25 = get_aqi_pm25(pm2_5)
    aqi_pm10 = get_aqi_pm10(pm10)
    
    return max(aqi_pm25, aqi_pm10)

def fetch_historical_data(months=4):
    """Fetch historical data for training"""
    
    # Calculate CORRECT dates - PAST data only!
    today = datetime.now().date()
    
    # End date is 2 weeks ago (to ensure archive data is available)
    end_date = today - timedelta(days=14)
    
    # Start date is 4 months before end date
    start_date = end_date - timedelta(days=30 * months)
    
    logger.info(f"Fetching historical data from {start_date} to {end_date}")
    
    # Fetch air quality data
    df_air = fetch_air_quality_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Fetch weather data using ARCHIVE API
    df_weather = fetch_weather_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Merge on timestamp
    df = pd.merge(df_air, df_weather, on='timestamp', how='inner')
    
    logger.info(f"Merged data: {len(df)} records")
    
    # Calculate AQI
    df['aqi'] = df.apply(
        lambda row: calculate_aqi(row['pm2_5'], row['pm10']), 
        axis=1
    )
    
    # Check for NaN values
    nan_counts = df.isnull().sum()
    if nan_counts.sum() > 0:
        logger.warning(f"NaN values found:\n{nan_counts[nan_counts > 0]}")
        # Drop rows with any NaN values
        initial_len = len(df)
        df = df.dropna()
        logger.info(f"Dropped {initial_len - len(df)} rows with NaN values")
    
    logger.info(f"Final dataset: {len(df)} records with AQI calculated")
    return df

def fetch_latest_data():
    """Fetch latest data for feature pipeline (last 48 hours)"""
    
    today = datetime.now().date()
    
    # For latest data, use data from 2-4 weeks ago (archive data)
    end_date = today - timedelta(days=14)
    start_date = end_date - timedelta(days=2)
    
    logger.info(f"Fetching latest data from {start_date} to {end_date}")
    
    # Fetch air quality data
    df_air = fetch_air_quality_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Fetch weather data using ARCHIVE API
    df_weather = fetch_weather_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Merge on timestamp
    df = pd.merge(df_air, df_weather, on='timestamp', how='inner')
    
    # Calculate AQI
    df['aqi'] = df.apply(
        lambda row: calculate_aqi(row['pm2_5'], row['pm10']), 
        axis=1
    )
    
    # Drop rows with NaN values
    df = df.dropna()
    
    logger.info(f"Latest data fetched: {len(df)} records")
    return df