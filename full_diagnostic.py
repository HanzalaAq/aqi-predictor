# full_diagnostic.py
from src.storage.mongodb_client import mongodb_client
from src.storage.feature_store import feature_store
from src.utils.config import Config
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

print("="*60)
print("FULL SYSTEM DIAGNOSTIC")
print("="*60)

# 1. MongoDB Connection
print("\n1. MONGODB CONNECTION:")
load_dotenv()
uri = os.getenv('MONGODB_URI')
print(f"   URI (first 50 chars): {uri[:50]}...")

# 2. Collections Check
print("\n2. MONGODB COLLECTIONS:")
fs = mongodb_client.get_feature_store()
collections = fs.list_collection_names()

for coll in [Config.RAW_DATA_COLLECTION, Config.PROCESSED_FEATURES_COLLECTION]:
    count = fs[coll].count_documents({})
    if count > 0:
        latest = fs[coll].find_one(sort=[('timestamp', -1)])
        oldest = fs[coll].find_one(sort=[('timestamp', 1)])
        
        print(f"\n   {coll}:")
        print(f"     Total docs: {count}")
        print(f"     Oldest: {oldest['timestamp']}")
        print(f"     Latest: {latest['timestamp']}")
        print(f"     Created at: {latest.get('created_at', 'N/A')}")
        
        # Check if fresh
        if 'timestamp' in latest:
            age = datetime.now() - latest['timestamp']
            print(f"     Age: {age.days} days, {age.seconds//3600} hours")
            
            if age.days > 1:
                print(f"     ⚠️ WARNING: Data is {age.days} days old!")
            else:
                print(f"     ✅ Data is fresh")

# 3. Predictions Check
print("\n3. PREDICTIONS:")
pred_db = mongodb_client.get_prediction_store()
pred_coll = pred_db[Config.PREDICTIONS_COLLECTION]

pred_count = pred_coll.count_documents({})
if pred_count > 0:
    latest_pred = pred_coll.find_one(sort=[('created_at', -1)])
    print(f"   Total predictions: {pred_count}")
    print(f"   Latest created: {latest_pred['created_at']}")
    print(f"   Prediction for: {latest_pred['timestamp']}")
    print(f"   Predicted AQI: {latest_pred['predicted_aqi']:.1f}")
    
    pred_age = datetime.now() - latest_pred['created_at']
    print(f"   Age: {pred_age.days} days, {pred_age.seconds//3600} hours")
    
    if pred_age.total_seconds() > 7200:  # More than 2 hours
        print(f"   ⚠️ WARNING: Predictions are {pred_age.seconds//3600} hours old!")
    else:
        print(f"   ✅ Predictions are fresh")

# 4. GitHub Actions Check
print("\n4. GITHUB ACTIONS STATUS:")
print("   Go to: https://github.com/HanzalaAq/aqi-predictor/actions")
print("   Check:")
print("     - When did Feature Pipeline last run?")
print("     - When did Inference Pipeline last run?")
print("     - Are there any red X (failures)?")

print("\n" + "="*60)
print("END DIAGNOSTIC")
print("="*60)