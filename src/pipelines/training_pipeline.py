import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
from src.data.feature_engineering import prepare_for_training
from src.models.train import train_all_models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_training_pipeline():
    """Run training pipeline to train and save models"""
    
    try:
        logger.info("Starting training pipeline...")
        
        # Load training data from feature store
        logger.info("Loading training data from MongoDB...")
        df = feature_store.get_training_data()
        
        if df.empty:
            logger.error("No training data available!")
            return False
        
        logger.info(f"Loaded {len(df)} training samples")
        
        # Prepare data
        X, y = prepare_for_training(df)
        
        # Train models
        logger.info("Training models...")
        best_model, best_model_name, all_results = train_all_models(X, y)
        
        # Save all models to registry
        logger.info("Saving models to MongoDB...")
        for model_name, metrics in all_results.items():
            # Get the actual model
            from src.models.train import train_random_forest, train_xgboost, train_lightgbm
            from sklearn.model_selection import train_test_split
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            if model_name == 'random_forest':
                model = train_random_forest(X_train, y_train)
            elif model_name == 'xgboost':
                model = train_xgboost(X_train, y_train)
            else:
                model = train_lightgbm(X_train, y_train)
            
            # Save to registry
            version = model_registry.save_model(
                model=model,
                model_name=model_name,
                metrics=metrics,
                metadata={
                    'training_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features': list(X.columns),
                    'is_best': (model_name == best_model_name)
                }
            )
            
            logger.info(f"Saved {model_name} v{version} with RMSE: {metrics['rmse']:.2f}")
        
        logger.info(f"Training pipeline completed! Best model: {best_model_name}")
        return True
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_training_pipeline()