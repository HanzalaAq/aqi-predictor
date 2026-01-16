import joblib
import pickle
from datetime import datetime
from bson.binary import Binary
from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
import logging
import io

logger = logging.getLogger(__name__)

class ModelRegistry:
    
    def __init__(self):
        self.db = mongodb_client.get_model_registry()
        self.models_collection = self.db[Config.MODELS_COLLECTION]
        self.metrics_collection = self.db[Config.MODEL_METRICS_COLLECTION]
    
    def save_model(self, model, model_name, metrics, metadata=None):
        """Save trained model to MongoDB"""
        try:
            # Serialize model to binary
            buffer = io.BytesIO()
            joblib.dump(model, buffer)
            buffer.seek(0)
            model_binary = Binary(buffer.read())
            
            # Get next version number
            latest = self.models_collection.find_one(
                {'model_name': model_name},
                sort=[('version', -1)]
            )
            version = (latest['version'] + 1) if latest else 1
            
            # Prepare model document
            model_doc = {
                'model_name': model_name,
                'version': version,
                'model_binary': model_binary,
                'created_at': datetime.now(),
                'city': Config.CITY_NAME,
                'metadata': metadata or {}
            }
            
            # Save model
            result = self.models_collection.insert_one(model_doc)
            logger.info(f"Saved {model_name} v{version} to model registry")
            
            # Save metrics
            metrics_doc = {
                'model_name': model_name,
                'version': version,
                'model_id': result.inserted_id,
                'metrics': metrics,
                'created_at': datetime.now()
            }
            
            self.metrics_collection.insert_one(metrics_doc)
            logger.info(f"Saved metrics for {model_name} v{version}")
            
            return version
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return None
    
    def load_model(self, model_name, version=None):
        """Load model from MongoDB"""
        try:
            query = {'model_name': model_name}
            
            if version:
                query['version'] = version
            
            # Get latest version if not specified
            model_doc = self.models_collection.find_one(
                query,
                sort=[('version', -1)]
            )
            
            if not model_doc:
                logger.error(f"Model {model_name} not found")
                return None
            
            # Deserialize model
            buffer = io.BytesIO(model_doc['model_binary'])
            model = joblib.load(buffer)
            
            logger.info(f"Loaded {model_name} v{model_doc['version']} from registry")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def get_best_model(self, metric='rmse'):
        """Get the best performing model based on metric"""
        try:
            # Get all latest metrics
            pipeline = [
                {'$sort': {'created_at': -1}},
                {'$group': {
                    '_id': '$model_name',
                    'latest_metrics': {'$first': '$metrics'},
                    'version': {'$first': '$version'}
                }}
            ]
            
            results = list(self.metrics_collection.aggregate(pipeline))
            
            if not results:
                logger.error("No models found in registry")
                return None, None
            
            # Find best model (lowest RMSE)
            best_model_name = min(results, 
                                 key=lambda x: x['latest_metrics'].get(metric, float('inf')))
            
            model = self.load_model(best_model_name['_id'], best_model_name['version'])
            
            logger.info(f"Best model: {best_model_name['_id']} "
                       f"with {metric}={best_model_name['latest_metrics'][metric]:.2f}")
            
            return model, best_model_name['_id']
            
        except Exception as e:
            logger.error(f"Error getting best model: {e}")
            return None, None
    
    def get_model_metrics(self, model_name):
        """Get all metrics for a model"""
        try:
            metrics = list(self.metrics_collection.find(
                {'model_name': model_name}
            ).sort('created_at', -1))
            
            return metrics
        except Exception as e:
            logger.error(f"Error retrieving model metrics: {e}")
            return []
    
    def list_models(self):
        """List all available models"""
        try:
            pipeline = [
                {'$group': {
                    '_id': '$model_name',
                    'latest_version': {'$max': '$version'},
                    'created_at': {'$max': '$created_at'}
                }},
                {'$sort': {'created_at': -1}}
            ]
            
            models = list(self.models_collection.aggregate(pipeline))
            return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

# Global instance
model_registry = ModelRegistry()