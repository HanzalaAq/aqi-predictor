from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.utils.config import Config
import logging
import certifi

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None
    _client = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection with lazy loading"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing MongoDB connection...")
            
            # Connection parameters that work best with GitHub Actions
            connection_params = {
                'tlsCAFile': certifi.where(),
                'tlsAllowInvalidCertificates': True,  # Allows connection in GitHub Actions
                'serverSelectionTimeoutMS': 10000,
                'connectTimeoutMS': 20000,
                'socketTimeoutMS': 20000,
                'retryWrites': True,
                'w': 'majority'
            }
            
            self._client = MongoClient(Config.MONGODB_URI, **connection_params)
            
            # Test connection
            self._client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB!")
            
            # Initialize databases
            self.feature_db = self._client[Config.MONGODB_DATABASE]
            self.model_db = self._client[Config.MODEL_DATABASE]
            self.prediction_db = self._client[Config.PREDICTION_DATABASE]
            
            # Create indexes
            self._create_indexes()
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes on collections for better query performance"""
        try:
            # Feature store indexes
            self.feature_db[Config.RAW_DATA_COLLECTION].create_index([("timestamp", -1)])
            self.feature_db[Config.PROCESSED_FEATURES_COLLECTION].create_index([("timestamp", -1)])
            
            # Model registry indexes
            self.model_db[Config.MODELS_COLLECTION].create_index([("model_name", 1), ("version", -1)])
            self.model_db[Config.MODEL_METRICS_COLLECTION].create_index([("model_name", 1), ("created_at", -1)])
            
            # Prediction indexes
            self.prediction_db[Config.PREDICTIONS_COLLECTION].create_index([("timestamp", -1)])
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    def get_feature_store(self):
        """Get feature store database - lazy initialize if needed"""
        if not self._initialized:
            self._initialize()
        return self.feature_db
    
    def get_model_registry(self):
        """Get model registry database - lazy initialize if needed"""
        if not self._initialized:
            self._initialize()
        return self.model_db
    
    def get_prediction_store(self):
        """Get prediction database - lazy initialize if needed"""
        if not self._initialized:
            self._initialize()
        return self.prediction_db
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._initialized = False
            logger.info("MongoDB connection closed")

# Global instance (connection happens lazily when first used)
mongodb_client = MongoDBClient()