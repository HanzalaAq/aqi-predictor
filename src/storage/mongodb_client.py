import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.utils.config import Config
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection with SSL fix"""
        if self._initialized:
            return
            
        try:
            logger.info("Attempting to connect to MongoDB...")
            
            # SSL FIX: Critical parameters for MongoDB Atlas M0 compatibility
            self.client = MongoClient(
                Config.MONGODB_URI,
                tlsCAFile=certifi.where(),              # Use certifi's CA bundle
                tlsAllowInvalidCertificates=True,       # For GitHub Actions/Windows compatibility
                serverSelectionTimeoutMS=30000,         # 30 second timeout
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,                       # Enable retry writes
                w='majority'                            # Write concern
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB!")
            
            # Initialize databases
            self.feature_db = self.client[Config.MONGODB_DATABASE]
            self.model_db = self.client[Config.MODEL_DATABASE]
            self.prediction_db = self.client[Config.PREDICTION_DATABASE]
            
            # Create indexes for better performance
            self._create_indexes()
            
            self._initialized = True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            logger.error("Please check:")
            logger.error("1. MongoDB URI is correct")
            logger.error("2. Network access is configured (0.0.0.0/0)")
            logger.error("3. Database user has correct permissions")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
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
            
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes: {e}")
    
    def get_feature_store(self):
        """Get feature store database"""
        if not self._initialized:
            self._initialize()
        return self.feature_db
    
    def get_model_registry(self):
        """Get model registry database"""
        if not self._initialized:
            self._initialize()
        return self.model_db
    
    def get_prediction_store(self):
        """Get prediction database"""
        if not self._initialized:
            self._initialize()
        return self.prediction_db
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global instance (lazy initialization)
mongodb_client = MongoDBClient()