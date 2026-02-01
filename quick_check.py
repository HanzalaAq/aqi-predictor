# diagnosis.py
from src.storage.feature_store import feature_store
from src.data.fetch_data import fetch_latest_data
import pandas as pd

print("="*60)
print("DIAGNOSIS: Why is prediction 72 when actual is 101?")
print("="*60)

# 1. Check current actual AQI
current = fetch_latest_data()
print(f"\n1. CURRENT ACTUAL AQI (from API right now):")
print(f"   Now: {current['aqi'].iloc[-1]:.1f}")
print(f"   Today's avg: {current['aqi'].mean():.1f}")
print(f"   Today's max: {current['aqi'].max():.1f}")

# 2. Check features in MongoDB
df = feature_store.get_processed_features()
print(f"\n2. FEATURES IN MONGODB:")
print(f"   Latest timestamp: {df['timestamp'].max()}")
print(f"   Latest AQI: {df['aqi'].iloc[-1]:.1f}")
print(f"   Latest 24h avg: {df['aqi'].tail(24).mean():.1f}")

# 3. Check lag features (what model sees)
latest = df.tail(1)
print(f"\n3. LAG FEATURES (what model uses for prediction):")
print(f"   aqi_lag_1h: {latest['aqi_lag_1h'].iloc[0]:.1f}")
print(f"   aqi_lag_24h: {latest['aqi_lag_24h'].iloc[0]:.1f}")
print(f"   aqi_rolling_24h: {latest['aqi_rolling_24h'].iloc[0]:.1f}")

# 4. Compare
print(f"\n4. COMPARISON:")
print(f"   Current ACTUAL AQI: {current['aqi'].iloc[-1]:.1f}")
print(f"   Features show AQI: {df['aqi'].iloc[-1]:.1f}")
print(f"   Rolling 24h: {latest['aqi_rolling_24h'].iloc[0]:.1f}")

gap = current['aqi'].iloc[-1] - latest['aqi_rolling_24h'].iloc[0]
print(f"\n   Gap: {gap:.1f} points")

if gap > 20:
    print(f"\n⚠️ FOUND THE ISSUE!")
    print(f"   Model is using 24h average (~{latest['aqi_rolling_24h'].iloc[0]:.0f})")
    print(f"   But current AQI spiked to {current['aqi'].iloc[-1]:.0f}")
    print(f"   Model hasn't 'seen' the spike in its features yet")
    print(f"\n   SOLUTION: Run feature pipeline to update with current high values")
else:
    print(f"\n✅ Features are current - Model genuinely predicts improvement")

print("="*60)