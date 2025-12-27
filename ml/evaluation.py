import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_model(model, X_test, y_test, model_name='Model'):
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results = {
        'model_name': model_name,
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred
    }
    
    return results

def compare_models(results_dict):
    comparison = pd.DataFrame({
        name: {
            'RMSE': res['rmse'],
            'MAE': res['mae'],
            'R² Score': res['r2']
        }
        for name, res in results_dict.items()
    }).T
    
    return comparison

def plot_predictions(y_test, y_pred, model_name='Model', save_path=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.scatter(y_test, y_pred, alpha=0.5, edgecolors='k', linewidths=0.5)
    
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    ax.set_xlabel('Actual Win Rate', fontsize=12)
    ax.set_ylabel('Predicted Win Rate', fontsize=12)
    ax.set_title(f'{model_name}: Predicted vs Actual', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def plot_residuals(y_test, y_pred, model_name='Model', save_path=None):
    residuals = y_test - y_pred
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].scatter(y_pred, residuals, alpha=0.5, edgecolors='k', linewidths=0.5)
    axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[0].set_xlabel('Predicted Win Rate', fontsize=12)
    axes[0].set_ylabel('Residuals', fontsize=12)
    axes[0].set_title(f'{model_name}: Residual Plot', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
    axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Residuals', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title(f'{model_name}: Residual Distribution', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def plot_feature_importance(importance_df, model_name='Model', top_n=15, save_path=None):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    plot_data = importance_df.head(top_n)
    
    if 'coefficient' in plot_data.columns:
        y_col = 'coefficient'
        x_label = 'Coefficient Value'
    else:
        y_col = 'importance'
        x_label = 'Importance Score'
    
    colors = ['green' if x > 0 else 'red' for x in plot_data[y_col]]
    
    ax.barh(plot_data['feature'], plot_data[y_col], color=colors, edgecolor='black')
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel('Feature', fontsize=12)
    ax.set_title(f'{model_name}: Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

