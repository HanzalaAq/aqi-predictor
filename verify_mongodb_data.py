from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
from datetime import datetime

print("Verifying MongoDB Data...")
print("="*50)

# Get latest raw data
print("\n📊 RAW DATA:")
print("-"*50)
df_raw = feature_store.get_latest_raw_data(limit=10)
print(f"Sample records fetched: {len(df_raw)}")

if len(df_raw) > 0:
    print(f"Latest timestamp: {df_raw['timestamp'].max()}")
    print(f"Oldest timestamp (in sample): {df_raw['timestamp'].min()}")
    print(f"\nColumns: {list(df_raw.columns)}")
    
# Get total count of raw data
try:
    raw_collection = mongodb_client.get_feature_store()[Config.RAW_DATA_COLLECTION]
    total_raw = raw_collection.count_documents({})
    print(f"\nTotal raw data records in MongoDB: {total_raw}")
except Exception as e:
    print(f"⚠️ Could not count raw data: {e}")

# Get all processed features
print("\n🔧 PROCESSED FEATURES:")
print("-"*50)
df_features = feature_store.get_processed_features()
print(f"Total feature records: {len(df_features)}")

if len(df_features) > 0:
    print(f"Date range: {df_features['timestamp'].min()} to {df_features['timestamp'].max()}")
    print(f"Total columns/features: {len(df_features.columns)}")
    print(f"\nFeature columns: {list(df_features.columns)}")
    
    # Check for training readiness
    time_diff = datetime.now() - df_features['timestamp'].max()
    hours_old = time_diff.total_seconds() / 3600
    print(f"\n⏰ Data freshness: {time_diff}")
    print(f"   Hours since last data: {hours_old:.1f}h")
    
    if len(df_features) >= 1000:
        print(f"✅ Sufficient data for training ({len(df_features)} samples)")
    else:
        print(f"⚠️ Limited data ({len(df_features)} samples). Recommend 1000+ for good training")
    
    # Show data quality
    print(f"\n📈 DATA QUALITY:")
    print("-"*50)
    null_counts = df_features.isnull().sum()
    if null_counts.sum() > 0:
        print("⚠️ Columns with null values:")
        print(null_counts[null_counts > 0])
    else:
        print("✅ No null values in processed features")
else:
    print("⚠️ No processed features found in MongoDB")
    print("   Run: python backfill_to_mongodb.py")

# Check models
print("\n🤖 MODELS:")
print("-"*50)
models = model_registry.list_models()
print(f"Total models in registry: {len(models)}")

if len(models) > 0:
    for model in models:
        print(f"\n  Model: {model['_id']}")
        print(f"  Latest version: {model['latest_version']}")
        print(f"  Created: {model['created_at']}")
        
        # Get metrics for this model
        metrics = model_registry.get_model_metrics(model['_id'])
        if metrics:
            latest_metric = metrics[0]
            print(f"  Latest metrics:")
            for metric_name, value in latest_metric['metrics'].items():
                print(f"    {metric_name}: {value:.4f}")
else:
    print("⚠️ No models found in registry")
    print("   Run: python src/pipelines/training_pipeline.py")

# Check predictions
print("\n🔮 PREDICTIONS:")
print("-"*50)
try:
    prediction_db = mongodb_client.get_prediction_store()
    prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]
    
    total_predictions = prediction_collection.count_documents({})
    print(f"Total predictions in database: {total_predictions}")
    
    if total_predictions > 0:
        # Get latest predictions
        latest_predictions = list(prediction_collection.find().sort("created_at", -1).limit(5))
        
        print(f"\nLatest prediction batch:")
        if latest_predictions:
            first_pred = latest_predictions[0]
            print(f"  Model used: {first_pred.get('model_name', 'Unknown')}")
            print(f"  Created at: {first_pred.get('created_at', 'Unknown')}")
            print(f"  Prediction timestamp: {first_pred.get('timestamp', 'Unknown')}")
            print(f"  Predicted AQI: {first_pred.get('predicted_aqi', 'Unknown'):.2f}")
            
        # Get prediction date range
        oldest_pred = prediction_collection.find_one(sort=[("timestamp", 1)])
        newest_pred = prediction_collection.find_one(sort=[("timestamp", -1)])
        
        if oldest_pred and newest_pred:
            print(f"\nPrediction date range:")
            print(f"  From: {oldest_pred['timestamp']}")
            print(f"  To: {newest_pred['timestamp']}")
    else:
        print("⚠️ No predictions found")
        print("   Run: python src/pipelines/inference_pipeline.py")
        
except Exception as e:
    print(f"⚠️ Could not check predictions: {e}")

# Summary
print("\n" + "="*50)
print("📋 SUMMARY:")
print("="*50)

status = []
if len(df_raw) > 0 or total_raw > 0:
    status.append("✅ Raw data present")
else:
    status.append("❌ No raw data")
    
if len(df_features) >= 1000:
    status.append(f"✅ Sufficient training data ({len(df_features)} samples)")
elif len(df_features) > 0:
    status.append(f"⚠️ Limited training data ({len(df_features)} samples)")
else:
    status.append("❌ No processed features")
    
if len(models) > 0:
    status.append(f"✅ {len(models)} trained model(s)")
else:
    status.append("❌ No trained models")
    
if total_predictions > 0:
    status.append(f"✅ {total_predictions} prediction(s)")
else:
    status.append("❌ No predictions")

for s in status:
    print(s)

print("\n" + "="*50)

# Action items
if len(df_features) == 0:
    print("\n🔄 NEXT STEPS:")
    print("1. Run: python backfill_to_mongodb.py")
elif len(models) == 0:
    print("\n🔄 NEXT STEPS:")
    print("1. Run: python src/pipelines/training_pipeline.py")
elif total_predictions == 0:
    print("\n🔄 NEXT STEPS:")
    print("1. Run: python src/pipelines/inference_pipeline.py")
else:
    print("\n🎉 ALL SYSTEMS READY!")
    print("Run: streamlit run app/streamlit_app.py")