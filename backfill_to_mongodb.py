import logging
logging.basicConfig(level=logging.INFO)

from src.data.fetch_data import fetch_historical_data
from src.data.feature_engineering import create_features
from src.storage.feature_store import feature_store

print("Backfilling Historical Data to MongoDB...")
print("="*50)

# Fetch 4 months of historical data
print("\nFetching 4 months of historical data...")
df_historical = fetch_historical_data(months=4)

print(f"✅ Fetched {len(df_historical)} historical records")
print(f"Date range: {df_historical['timestamp'].min()} to {df_historical['timestamp'].max()}")

# Save raw historical data
print("\nSaving raw historical data to MongoDB...")
success = feature_store.save_raw_data(df_historical)

if success:
    print("✅ Raw historical data saved")
else:
    print("❌ Failed to save raw data")

# Create features
print("\nCreating features from historical data...")
df_features = create_features(df_historical)

print(f"✅ Created {len(df_features)} feature records")

# Save processed features
print("\nSaving processed features to MongoDB...")
success = feature_store.save_processed_features(df_features)

if success:
    print("✅ Processed features saved")
    print(f"\n🎉 Backfill complete! {len(df_features)} training samples ready in MongoDB")
else:
    print("❌ Failed to save processed features")