from src.storage.feature_store import feature_store
import pandas as pd
import matplotlib.pyplot as plt

df = feature_store.get_processed_features()

print("AQI Distribution in Training Data:")
print(df['aqi'].describe())

# Check how often AQI was >100
high_aqi = df[df['aqi'] > 100]
print(f"\nRecords with AQI >100: {len(high_aqi)} / {len(df)} ({len(high_aqi)/len(df)*100:.1f}%)")

# Recent trend
df_recent = df.tail(168)  # Last week
print(f"\nLast week average AQI: {df_recent['aqi'].mean():.1f}")
print(f"Last week max AQI: {df_recent['aqi'].max():.1f}")

# Plot distribution
plt.figure(figsize=(10, 6))
plt.hist(df['aqi'], bins=50, edgecolor='black')
plt.axvline(df['aqi'].mean(), color='red', linestyle='--', label=f'Mean: {df["aqi"].mean():.1f}')
plt.axvline(101, color='orange', linestyle='--', label='Today: 101')
plt.xlabel('AQI')
plt.ylabel('Frequency')
plt.title('AQI Distribution in Training Data')
plt.legend()
plt.savefig('aqi_distribution.png')
print("\n✅ Saved plot to aqi_distribution.png")