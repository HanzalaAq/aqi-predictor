from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
from src.data.feature_engineering import prepare_for_training

# Get model
model, model_name = model_registry.get_best_model(metric='rmse')

# Get high AQI examples from training data
df = feature_store.get_processed_features()
high_aqi_samples = df[df['aqi'] > 100]

if len(high_aqi_samples) > 0:
    print(f"Found {len(high_aqi_samples)} high AQI samples in training data")
    
    # Test model on these
    X, y = prepare_for_training(high_aqi_samples)
    
    if len(X) > 0:
        predictions = model.predict(X)
        actual = y.values
        
        print(f"\nModel performance on HIGH AQI samples:")
        print(f"Actual AQI range: {actual.min():.1f} - {actual.max():.1f}")
        print(f"Predicted AQI range: {predictions.min():.1f} - {predictions.max():.1f}")
        print(f"Average actual: {actual.mean():.1f}")
        print(f"Average predicted: {predictions.mean():.1f}")
        
        underestimation = actual.mean() - predictions.mean()
        print(f"\n⚠️ Model underestimates high AQI by: {underestimation:.1f} points")
else:
    print("⚠️ No high AQI samples in training data!")
    print("Model has never seen AQI >100, so it can't predict it well")