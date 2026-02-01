from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
import pandas as pd

print("Checking Model Input Data...")
print("="*50)

# Get latest processed features
df = feature_store.get_processed_features()

if len(df) > 0:
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    print(f"\n📊 Training Data Info:")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Check recent AQI values
    print(f"\n🔍 Recent AQI Values in Training Data:")
    recent = df.tail(24)
    print(f"Last 24 hours average AQI: {recent['aqi'].mean():.2f}")
    print(f"Min: {recent['aqi'].min():.2f}")
    print(f"Max: {recent['aqi'].max():.2f}")
    
    # Check January data specifically
    df['month'] = pd.to_datetime(df['timestamp']).dt.month
    jan_data = df[df['month'] == 1]
    
    if len(jan_data) > 0:
        print(f"\n❄️ January Data Statistics:")
        print(f"January records: {len(jan_data)}")
        print(f"Average AQI in January: {jan_data['aqi'].mean():.2f}")
        print(f"Min: {jan_data['aqi'].min():.2f}")
        print(f"Max: {jan_data['aqi'].max():.2f}")
    
    # Check what the model "sees" as most recent
    print(f"\n⏰ Data Freshness:")
    from datetime import datetime
    latest_timestamp = df['timestamp'].max()
    current_time = datetime.now()
    gap = current_time - latest_timestamp
    
    print(f"Latest data in MongoDB: {latest_timestamp}")
    print(f"Current time: {current_time}")
    print(f"Data gap: {gap.days} days, {gap.seconds//3600} hours")
    
    if gap.days > 3:
        print(f"\n⚠️ WARNING: Data is {gap.days} days old!")
        print("Model is predicting based on old patterns.")
        print("Solution: Run feature pipeline to get current data")