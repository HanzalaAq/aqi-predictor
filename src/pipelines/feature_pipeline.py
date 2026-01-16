import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.fetch_data import fetch_latest_data, fetch_historical_data
from src.data.feature_engineering import create_features
from src.storage.feature_store import feature_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_feature_pipeline(historical=False):
    """Run feature pipeline to fetch and process data"""
    
    try:
        logger.info("Starting feature pipeline...")
        
        # Fetch data
        if historical:
            logger.info("Fetching historical data...")
            df = fetch_historical_data(months=4)
        else:
            logger.info("Fetching latest data...")
            df = fetch_latest_data()
        
        # Save raw data
        logger.info("Saving raw data to MongoDB...")
        feature_store.save_raw_data(df)
        
        # Create features
        logger.info("Creating features...")
        df_features = create_features(df)
        
        # Save processed features
        logger.info("Saving processed features to MongoDB...")
        feature_store.save_processed_features(df_features)
        
        logger.info("Feature pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Feature pipeline failed: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--historical', action='store_true', 
                       help='Run historical data backfill')
    args = parser.parse_args()
    
    run_feature_pipeline(historical=args.historical)