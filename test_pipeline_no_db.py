from src.data.fetch_data import fetch_latest_data
from src.data.feature_engineering import create_features
import pandas as pd
import os

print("Testing pipeline without MongoDB...")
print("="*50)

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Fetch data
df = fetch_latest_data()
print(f"\n✅ Fetched {len(df)} records")

# Create features
df_features = create_features(df)
print(f"✅ Created {len(df_features)} feature records")

# Save locally as backup
df_features.to_csv('data/processed_features_latest.csv', index=False)
print(f"\n✅ Saved features to data/processed_features_latest.csv")

print("\n📊 Feature columns:")
print(df_features.columns.tolist())

print("\n🔍 Sample features:")
print(df_features.head())

print("\n📈 Feature statistics:")
print(f"Total features: {len(df_features.columns)}")
print(f"Records: {len(df_features)}")
print(f"Date range: {df_features['timestamp'].min()} to {df_features['timestamp'].max()}")