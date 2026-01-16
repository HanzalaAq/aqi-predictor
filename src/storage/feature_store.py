import pandas as pd
from datetime import datetime
from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
import logging

logger = logging.getLogger(__name__)

class FeatureStore:
    
    def __init__(self):
        self.db = mongodb_client.get_feature_store()
        self.raw_collection = self.db[Config.RAW_DATA_COLLECTION]
        self.processed_collection = self.db[Config.PROCESSED_FEATURES_COLLECTION]
    
    def save_raw_data(self, df):
        """Save raw data to MongoDB"""
        try:
            records = df.to_dict('records')
            
            # Add metadata
            for record in records:
                record['created_at'] = datetime.now()
                record['city'] = Config.CITY_NAME
            
            # Insert data
            if records:
                result = self.raw_collection.insert_many(records)
                logger.info(f"Saved {len(result.inserted_ids)} raw records to MongoDB")
            
            return True
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
            return False
    
    def save_processed_features(self, df):
        """Save processed features to MongoDB"""
        try:
            records = df.to_dict('records')
            
            # Add metadata
            for record in records:
                record['created_at'] = datetime.now()
                record['city'] = Config.CITY_NAME
            
            # Insert data
            if records:
                result = self.processed_collection.insert_many(records)
                logger.info(f"Saved {len(result.inserted_ids)} processed features to MongoDB")
            
            return True
        except Exception as e:
            logger.error(f"Error saving processed features: {e}")
            return False
    
    def get_latest_raw_data(self, limit=1000):
        """Get latest raw data from MongoDB"""
        try:
            cursor = self.raw_collection.find().sort("timestamp", -1).limit(limit)
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Retrieved {len(df)} raw records from MongoDB")
            return df
        except Exception as e:
            logger.error(f"Error retrieving raw data: {e}")
            return pd.DataFrame()
    
    def get_processed_features(self, start_date=None, end_date=None):
        """Get processed features from MongoDB"""
        try:
            query = {}
            
            if start_date and end_date:
                query['timestamp'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }
            
            cursor = self.processed_collection.find(query).sort("timestamp", 1)
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Retrieved {len(df)} processed feature records from MongoDB")
            return df
        except Exception as e:
            logger.error(f"Error retrieving processed features: {e}")
            return pd.DataFrame()
    
    def get_training_data(self):
        """Get all processed features for training"""
        return self.get_processed_features()
    
    def delete_old_data(self, days=90):
        """Delete data older than specified days"""
        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            
            result_raw = self.raw_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            result_processed = self.processed_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            logger.info(f"Deleted {result_raw.deleted_count} raw records and "
                       f"{result_processed.deleted_count} processed records older than {days} days")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting old data: {e}")
            return False

# Global instance
feature_store = FeatureStore()