from src.data.fetch_data import fetch_latest_data
from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
from datetime import datetime
import pandas as pd

print("Fetching ACTUAL current AQI...")

# Get today's actual data
df_actual = fetch_latest_data()

print(f"\n📊 Today's ACTUAL AQI (from Open-Meteo):")
print(f"Date: {df_actual['timestamp'].max().date()}")
print(f"Current hour AQI: {df_actual['aqi'].iloc[-1]:.2f}")
print(f"Today's average: {df_actual['aqi'].mean():.2f}")
print(f"Range: {df_actual['aqi'].min():.2f} - {df_actual['aqi'].max():.2f}")

# Get predictions for TODAY from MongoDB
prediction_db = mongodb_client.get_prediction_store()
prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]

# Current date
today = datetime.now().date()

# Get predictions that were made BEFORE today, FOR today
predictions_for_today = list(prediction_collection.find({
    'timestamp': {
        '$gte': pd.Timestamp(today).to_pydatetime(),
        '$lt': pd.Timestamp(today + pd.Timedelta(days=1)).to_pydatetime()
    }
}).sort('timestamp', 1))

if len(predictions_for_today) > 0:
    df_pred = pd.DataFrame(predictions_for_today)
    
    print(f"\n🤖 MODEL PREDICTIONS FOR TODAY:")
    print(f"Number of hourly predictions: {len(df_pred)}")
    print(f"Average predicted AQI: {df_pred['predicted_aqi'].mean():.2f}")
    print(f"Range: {df_pred['predicted_aqi'].min():.2f} - {df_pred['predicted_aqi'].max():.2f}")
    print(f"Prediction created at: {df_pred['created_at'].iloc[0]}")
    
    # Compare averages
    actual_avg = df_actual['aqi'].mean()
    predicted_avg = df_pred['predicted_aqi'].mean()
    difference = abs(actual_avg - predicted_avg)
    percentage_error = (difference / actual_avg) * 100
    
    print(f"\n📊 COMPARISON:")
    print(f"Actual average AQI: {actual_avg:.2f}")
    print(f"Predicted average AQI: {predicted_avg:.2f}")
    print(f"Difference: {difference:.2f} AQI points")
    print(f"Percentage error: {percentage_error:.1f}%")
    
    if percentage_error <= 10:
        print("✅ EXCELLENT accuracy (<10% error)")
    elif percentage_error <= 20:
        print("✅ GOOD accuracy (<20% error)")
    elif percentage_error <= 30:
        print("⚠️ ACCEPTABLE accuracy (<30% error)")
    else:
        print("❌ HIGH error (>30%)")
        
    # Hour-by-hour comparison (if we have matching hours)
    print(f"\n🕐 HOURLY COMPARISON:")
    for idx, pred_row in df_pred.head(5).iterrows():
        pred_time = pred_row['timestamp']
        pred_aqi = pred_row['predicted_aqi']
        
        # Find matching actual hour
        actual_matches = df_actual[df_actual['timestamp'] == pred_time]
        if len(actual_matches) > 0:
            actual_aqi = actual_matches['aqi'].iloc[0]
            error = abs(pred_aqi - actual_aqi)
            print(f"  {pred_time.strftime('%H:%M')}: Predicted {pred_aqi:.1f}, Actual {actual_aqi:.1f}, Error {error:.1f}")
        
else:
    print("\n⚠️ No predictions found for today!")
    print("Your predictions are for future dates (Feb 3).")
    print("\nThis is expected behavior - the model predicts 3 days AHEAD.")
    print("\n💡 To validate:")
    print("1. Wait until Feb 3")
    print("2. Run this script on Feb 3 to compare predicted vs actual")
    print("3. Or compare older predictions with historical actual data")