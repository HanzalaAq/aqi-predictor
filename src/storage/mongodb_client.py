from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.utils.config import Config
import logging
import certifi

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection with SSL support"""
        try:
            # Use certifi for SSL certificate verification (fixes GitHub Actions SSL issue)
            self.client = MongoClient(
                Config.MONGODB_URI,
                tlsCAFile=certifi.where()
            )
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Initialize databases
            self.feature_db = self.client[Config.MONGODB_DATABASE]
            self.model_db = self.client[Config.MODEL_DATABASE]
            self.prediction_db = self.client[Config.PREDICTION_DATABASE]
            
            # Create indexes for better performance
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes on collections for better query performance"""
        # Feature store indexes
        self.feature_db[Config.RAW_DATA_COLLECTION].create_index([("timestamp", -1)])
        self.feature_db[Config.PROCESSED_FEATURES_COLLECTION].create_index([("timestamp", -1)])
        
        # Model registry indexes
        self.model_db[Config.MODELS_COLLECTION].create_index([("model_name", 1), ("version", -1)])
        self.model_db[Config.MODEL_METRICS_COLLECTION].create_index([("model_name", 1), ("created_at", -1)])
        
        # Prediction indexes
        self.prediction_db[Config.PREDICTIONS_COLLECTION].create_index([("timestamp", -1)])
    
    def get_feature_store(self):
        """Get feature store database"""
        return self.feature_db
    
    def get_model_registry(self):
        """Get model registry database"""
        return self.model_db
    
    def get_prediction_store(self):
        """Get prediction database"""
        return self.prediction_db
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global instance
mongodb_client = MongoDBClient()