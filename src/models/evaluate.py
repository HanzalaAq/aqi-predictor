import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

def evaluate_model(model, X_test, y_test, model_name="Model"):
    """
    Evaluate a trained model on test data
    
    Parameters:
    -----------
    model : trained model object
        The model to evaluate
    X_test : array-like
        Test features
    y_test : array-like
        True target values
    model_name : str
        Name of the model for reporting
        
    Returns:
    --------
    dict : Dictionary containing evaluation metrics
    """
    
    predictions = model.predict(X_test)
    
    metrics = {
        'model_name': model_name,
        'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
        'mae': mean_absolute_error(y_test, predictions),
        'r2': r2_score(y_test, predictions),
        'predictions': predictions,
        'actuals': y_test
    }
    
    logger.info(f"{model_name} Evaluation Metrics:")
    logger.info(f"  RMSE: {metrics['rmse']:.4f}")
    logger.info(f"  MAE: {metrics['mae']:.4f}")
    logger.info(f"  R² Score: {metrics['r2']:.4f}")
    
    return metrics

def compare_models(results_dict):
    """
    Compare multiple models and return summary
    
    Parameters:
    -----------
    results_dict : dict
        Dictionary with model names as keys and metrics dicts as values
        
    Returns:
    --------
    pd.DataFrame : Comparison table of all models
    """
    
    comparison_data = []
    
    for model_name, metrics in results_dict.items():
        comparison_data.append({
            'Model': model_name,
            'RMSE': metrics['rmse'],
            'MAE': metrics['mae'],
            'R² Score': metrics['r2']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('RMSE')
    
    logger.info("\nModel Comparison:")
    logger.info(comparison_df.to_string(index=False))
    
    return comparison_df

def plot_predictions_vs_actual(y_true, y_pred, model_name="Model", save_path=None):
    """
    Plot predicted vs actual values
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
    model_name : str
        Name of the model
    save_path : str, optional
        Path to save the plot
    """
    
    plt.figure(figsize=(10, 6))
    
    plt.scatter(y_true, y_pred, alpha=0.5, s=20)
    
    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    
    plt.xlabel('Actual AQI', fontsize=12)
    plt.ylabel('Predicted AQI', fontsize=12)
    plt.title(f'{model_name}: Predicted vs Actual AQI', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Plot saved to {save_path}")
    
    plt.show()

def plot_residuals(y_true, y_pred, model_name="Model", save_path=None):
    """
    Plot residuals distribution
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
    model_name : str
        Name of the model
    save_path : str, optional
        Path to save the plot
    """
    
    residuals = y_true - y_pred
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residual plot
    axes[0].scatter(y_pred, residuals, alpha=0.5, s=20)
    axes[0].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Predicted AQI', fontsize=12)
    axes[0].set_ylabel('Residuals', fontsize=12)
    axes[0].set_title(f'{model_name}: Residual Plot', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Residual distribution
    axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
    axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Residuals', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title(f'{model_name}: Residual Distribution', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Plot saved to {save_path}")
    
    plt.show()

def calculate_mape(y_true, y_pred):
    """
    Calculate Mean Absolute Percentage Error
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
        
    Returns:
    --------
    float : MAPE value
    """
    
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    
    # Avoid division by zero
    mask = y_true != 0
    
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    return mape

def generate_evaluation_report(model, X_test, y_test, model_name="Model"):
    """
    Generate comprehensive evaluation report
    
    Parameters:
    -----------
    model : trained model
        Model to evaluate
    X_test : array-like
        Test features
    y_test : array-like
        True values
    model_name : str
        Name of the model
        
    Returns:
    --------
    dict : Complete evaluation metrics
    """
    
    predictions = model.predict(X_test)
    
    metrics = {
        'model_name': model_name,
        'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
        'mae': mean_absolute_error(y_test, predictions),
        'r2': r2_score(y_test, predictions),
        'mape': calculate_mape(y_test, predictions),
        'n_samples': len(y_test)
    }
    
    print("=" * 80)
    print(f"{model_name} - EVALUATION REPORT")
    print("=" * 80)
    print(f"Number of test samples: {metrics['n_samples']}")
    print(f"\nPerformance Metrics:")
    print(f"  Root Mean Squared Error (RMSE): {metrics['rmse']:.4f}")
    print(f"  Mean Absolute Error (MAE): {metrics['mae']:.4f}")
    print(f"  R² Score: {metrics['r2']:.4f}")
    print(f"  Mean Absolute Percentage Error (MAPE): {metrics['mape']:.2f}%")
    print("=" * 80)
    
    return metrics