import shap
import pandas as pd
from src.storage.feature_store import feature_store
from src.storage.model_registry import model_registry
from src.data.feature_engineering import prepare_for_training
import matplotlib.pyplot as plt

print("Analyzing Feature Importance with SHAP...")

model, model_name = model_registry.get_best_model(metric='rmse')
df = feature_store.get_processed_features()
X, y = prepare_for_training(df)

X_sample = X.sample(min(500, len(X)), random_state=42)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample)

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': abs(shap_values).mean(axis=0)
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10))

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
print("Saved to feature_importance.png")