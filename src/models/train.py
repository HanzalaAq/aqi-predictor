import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import logging

logger = logging.getLogger(__name__)

def train_random_forest(X_train, y_train):
    """Train Random Forest model"""
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train, y_train):
    """Train XGBoost model"""
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

def train_lightgbm(X_train, y_train):
    """Train LightGBM model"""
    model = lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    y_pred = model.predict(X_test)
    
    metrics = {
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'r2': float(r2_score(y_test, y_pred))
    }
    
    return metrics

def train_all_models(X, y):
    """Train and compare all models"""
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    models = {
        'random_forest': train_random_forest(X_train, y_train),
        'xgboost': train_xgboost(X_train, y_train),
        'lightgbm': train_lightgbm(X_train, y_train)
    }
    
    results = {}
    
    for name, model in models.items():
        metrics = evaluate_model(model, X_test, y_test)
        results[name] = metrics
        logger.info(f"\n{name.upper()} Results:")
        logger.info(f"  RMSE: {metrics['rmse']:.2f}")
        logger.info(f"  MAE: {metrics['mae']:.2f}")
        logger.info(f"  R²: {metrics['r2']:.4f}")
    
    # Select best model based on RMSE
    best_model_name = min(results, key=lambda k: results[k]['rmse'])
    best_model = models[best_model_name]
    
    logger.info(f"\nBest Model: {best_model_name.upper()}")
    
    return best_model, best_model_name, results