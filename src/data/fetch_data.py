# import requests
# import pandas as pd
# from datetime import datetime, timedelta
# from src.utils.config import Config
# import logging

# logger = logging.getLogger(__name__)

# def fetch_air_quality_current():
#     """Fetch ONLY current day air quality data (no forecast)"""
#     url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
#     # Get only TODAY's data
#     today = datetime.now().date()
    
#     params = {
#         'latitude': Config.LATITUDE,
#         'longitude': Config.LONGITUDE,
#         'start_date': today.strftime('%Y-%m-%d'),
#         'end_date': today.strftime('%Y-%m-%d'),  # Same as start = today only!
#         'hourly': [
#             'pm10', 'pm2_5', 'carbon_monoxide',
#             'nitrogen_dioxide', 'sulphur_dioxide',
#             'ozone', 'dust', 'uv_index'
#         ],
#         'timezone': 'Asia/Karachi'
#         # NO 'forecast_days' parameter - this is key!
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         df = pd.DataFrame({
#             'timestamp': pd.to_datetime(data['hourly']['time']),
#             'pm10': data['hourly']['pm10'],
#             'pm2_5': data['hourly']['pm2_5'],
#             'co': data['hourly']['carbon_monoxide'],
#             'no2': data['hourly']['nitrogen_dioxide'],
#             'so2': data['hourly']['sulphur_dioxide'],
#             'ozone': data['hourly']['ozone'],
#             'dust': data['hourly']['dust'],
#             'uv_index': data['hourly']['uv_index']
#         })
        
#         logger.info(f"Fetched {len(df)} current air quality records for {today}")
#         return df
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"API request failed: {e}")
#         raise


# def fetch_weather_current():
#     """Fetch ONLY current day weather data (no forecast)"""
#     url = "https://api.open-meteo.com/v1/forecast"
    
#     today = datetime.now().date()
    
#     params = {
#         'latitude': Config.LATITUDE,
#         'longitude': Config.LONGITUDE,
#         'start_date': today.strftime('%Y-%m-%d'),
#         'end_date': today.strftime('%Y-%m-%d'),  # Same day!
#         'hourly': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m'],
#         'timezone': 'Asia/Karachi'
#         # NO 'forecast_days' parameter!
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         df = pd.DataFrame({
#             'timestamp': pd.to_datetime(data['hourly']['time']),
#             'temperature': data['hourly']['temperature_2m'],
#             'humidity': data['hourly']['relative_humidity_2m'],
#             'wind_speed': data['hourly']['wind_speed_10m']
#         })
        
#         logger.info(f"Fetched {len(df)} current weather records for {today}")
#         return df
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Weather API request failed: {e}")
#         raise


# def calculate_aqi(pm2_5, pm10):
#     """Calculate AQI based on PM2.5 and PM10 (US EPA standard)"""
#     def get_aqi_pm25(pm25):
#         if pd.isna(pm25):
#             return 0
#         if pm25 <= 12.0:
#             return (50 / 12.0) * pm25
#         elif pm25 <= 35.4:
#             return 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
#         elif pm25 <= 55.4:
#             return 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
#         elif pm25 <= 150.4:
#             return 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
#         elif pm25 <= 250.4:
#             return 200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5)
#         else:
#             return 300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5)
    
#     def get_aqi_pm10(pm10):
#         if pd.isna(pm10):
#             return 0
#         if pm10 <= 54:
#             return (50 / 54) * pm10
#         elif pm10 <= 154:
#             return 50 + ((100 - 50) / (154 - 55)) * (pm10 - 55)
#         elif pm10 <= 254:
#             return 100 + ((150 - 100) / (254 - 155)) * (pm10 - 155)
#         elif pm10 <= 354:
#             return 150 + ((200 - 150) / (354 - 255)) * (pm10 - 255)
#         elif pm10 <= 424:
#             return 200 + ((300 - 200) / (424 - 355)) * (pm10 - 355)
#         else:
#             return 300 + ((500 - 300) / (604 - 425)) * (pm10 - 425)
    
#     aqi_pm25 = get_aqi_pm25(pm2_5)
#     aqi_pm10 = get_aqi_pm10(pm10)
#     return max(aqi_pm25, aqi_pm10)


# def fetch_historical_data(months=4):
#     """Fetch historical data for training (uses ARCHIVE API)"""
#     # Archive API has 2-week delay for finalized data
#     end_date = datetime.now().date() - timedelta(days=14)
#     start_date = end_date - timedelta(days=30 * months)
    
#     logger.info(f"Fetching historical data from {start_date} to {end_date}")
    
#     # Fetch air quality from archive
#     df_aqi = fetch_air_quality_data_archive(start_date, end_date)
    
#     # Fetch weather from archive
#     df_weather = fetch_weather_data_archive(start_date, end_date)
    
#     # Merge dataframes
#     df = pd.merge(df_aqi, df_weather, on='timestamp', how='inner')
    
#     # Calculate AQI
#     df['aqi'] = df.apply(
#         lambda row: calculate_aqi(row['pm2_5'], row['pm10']),
#         axis=1
#     )
    
#     logger.info(f"Calculated AQI for {len(df)} historical records")
#     return df


# def fetch_air_quality_data_archive(start_date, end_date):
#     """Fetch air quality from ARCHIVE API (for historical training only)"""
#     url = "https://archive-api.open-meteo.com/v1/archive"
    
#     params = {
#         'latitude': Config.LATITUDE,
#         'longitude': Config.LONGITUDE,
#         'start_date': start_date.strftime('%Y-%m-%d'),
#         'end_date': end_date.strftime('%Y-%m-%d'),
#         'hourly': [
#             'pm10', 'pm2_5', 'carbon_monoxide',
#             'nitrogen_dioxide', 'sulphur_dioxide',
#             'ozone', 'dust'
#         ],
#         'timezone': 'Asia/Karachi'
#     }
    
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     data = response.json()
    
#     df = pd.DataFrame({
#         'timestamp': pd.to_datetime(data['hourly']['time']),
#         'pm10': data['hourly']['pm10'],
#         'pm2_5': data['hourly']['pm2_5'],
#         'co': data['hourly']['carbon_monoxide'],
#         'no2': data['hourly']['nitrogen_dioxide'],
#         'so2': data['hourly']['sulphur_dioxide'],
#         'ozone': data['hourly']['ozone'],
#         'dust': data['hourly']['dust']
#     })
    
#     logger.info(f"Fetched {len(df)} archive air quality records")
#     return df


# def fetch_weather_data_archive(start_date, end_date):
#     """Fetch weather from ARCHIVE API (for historical training only)"""
#     url = "https://archive-api.open-meteo.com/v1/archive"
    
#     params = {
#         'latitude': Config.LATITUDE,
#         'longitude': Config.LONGITUDE,
#         'start_date': start_date.strftime('%Y-%m-%d'),
#         'end_date': end_date.strftime('%Y-%m-%d'),
#         'hourly': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'uv_index'],
#         'timezone': 'Asia/Karachi'
#     }
    
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     data = response.json()
    
#     df = pd.DataFrame({
#         'timestamp': pd.to_datetime(data['hourly']['time']),
#         'temperature': data['hourly']['temperature_2m'],
#         'humidity': data['hourly']['relative_humidity_2m'],
#         'wind_speed': data['hourly']['wind_speed_10m'],
#         'uv_index': data['hourly']['uv_index']
#     })
    
#     logger.info(f"Fetched {len(df)} archive weather records")
#     return df


# def fetch_latest_data():
#     """
#     Fetch latest data for feature pipeline (CURRENT DAY ONLY - no forecast!)
#     """
#     logger.info("Fetching CURRENT day data (today only - no forecast)")
    
#     # Fetch current air quality (today only)
#     df_aqi = fetch_air_quality_current()
    
#     # Fetch current weather (today only)
#     df_weather = fetch_weather_current()
    
#     # Merge dataframes
#     df = pd.merge(df_aqi, df_weather, on='timestamp', how='inner')
    
#     # Calculate AQI
#     df['aqi'] = df.apply(
#         lambda row: calculate_aqi(row['pm2_5'], row['pm10']),
#         axis=1
#     )
    
#     logger.info(f"Calculated AQI for {len(df)} current records")
#     logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
#     return df



import requests
import pandas as pd
from datetime import datetime, timedelta
from src.utils.config import Config
import logging

logger = logging.getLogger(__name__)


def fetch_air_quality_current():
    """Fetch ONLY current day air quality data (no forecast)"""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    today = datetime.now().date()
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': today.strftime('%Y-%m-%d'),  # Same day = current only!
        'hourly': [
            'pm10', 'pm2_5', 'carbon_monoxide',
            'nitrogen_dioxide', 'sulphur_dioxide',
            'ozone', 'dust', 'uv_index'
        ],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
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


def fetch_weather_current():
    """Fetch ONLY current day weather data (no forecast)"""
    url = "https://api.open-meteo.com/v1/forecast"
    
    today = datetime.now().date()
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': today.strftime('%Y-%m-%d'),  # Same day!
        'hourly': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m'],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
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


def fetch_air_quality_data(start_date, end_date):
    """Fetch air quality data from Archive API (for historical training only)"""
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    logger.info(f"Fetching air quality data from {start_date} to {end_date}")
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': [
            'pm10', 'pm2_5', 'carbon_monoxide',
            'nitrogen_dioxide', 'sulphur_dioxide',
            'ozone', 'dust'
        ],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'pm10': data['hourly']['pm10'],
            'pm2_5': data['hourly']['pm2_5'],
            'co': data['hourly']['carbon_monoxide'],
            'no2': data['hourly']['nitrogen_dioxide'],
            'so2': data['hourly']['sulphur_dioxide'],
            'ozone': data['hourly']['ozone'],
            'dust': data['hourly']['dust']
        })
        
        logger.info(f"Fetched {len(df)} air quality records")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing API data: {e}")
        raise


def fetch_weather_data(start_date, end_date, use_archive=True):
    """Fetch weather data from Archive API (for historical training only)"""
    if use_archive:
        url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        url = "https://api.open-meteo.com/v1/forecast"
    
    logger.info(f"Fetching weather data from {start_date} to {end_date}")
    
    params = {
        'latitude': Config.LATITUDE,
        'longitude': Config.LONGITUDE,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'uv_index'],
        'timezone': 'Asia/Karachi'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'temperature': data['hourly']['temperature_2m'],
            'humidity': data['hourly']['relative_humidity_2m'],
            'wind_speed': data['hourly']['wind_speed_10m'],
            'uv_index': data['hourly']['uv_index']
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
    """Fetch historical data for training (uses ARCHIVE API with 2-week delay)"""
    # Archive API has 2-week delay for finalized data
    end_date = datetime.now().date() - timedelta(days=14)
    start_date = end_date - timedelta(days=30 * months)
    
    logger.info(f"Fetching historical data from {start_date} to {end_date}")
    
    # Fetch air quality from archive
    df_aqi = fetch_air_quality_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Fetch weather from archive
    df_weather = fetch_weather_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        use_archive=True
    )
    
    # Merge dataframes
    df = pd.merge(df_aqi, df_weather, on='timestamp', how='inner')
    
    # Calculate AQI
    df['aqi'] = df.apply(
        lambda row: calculate_aqi(row['pm2_5'], row['pm10']),
        axis=1
    )
    
    logger.info(f"Calculated AQI for {len(df)} historical records")
    return df


def fetch_latest_data():
    """
    Fetch latest data for feature pipeline (CURRENT DAY ONLY - no forecast!)
    
    This fetches TODAY's data using the forecast API with same start/end date.
    This approach gets current data without the 2-week Archive API delay.
    """
    today = datetime.now().date()
    
    logger.info(f"Fetching latest data from {today} to {today}")
    
    # Fetch current air quality (today only)
    df_aqi = fetch_air_quality_current()
    
    # Fetch current weather (today only)
    df_weather = fetch_weather_current()
    
    # Merge dataframes
    df = pd.merge(df_aqi, df_weather, on='timestamp', how='inner')
    
    # Calculate AQI
    df['aqi'] = df.apply(
        lambda row: calculate_aqi(row['pm2_5'], row['pm10']),
        axis=1
    )
    
    logger.info(f"Latest data fetched: {len(df)} records")
    logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    return df