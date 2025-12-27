import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from ml.preprocessing import load_and_prepare_data
from ml.models import train_xgboost, get_feature_importance
from ml.evaluation import evaluate_model, plot_predictions, plot_residuals, plot_feature_importance

def generate_all_visualizations():
    print("Generating ML visualizations...")
    
    os.makedirs('ml/visualizations', exist_ok=True)
    
    X_train, X_test, y_train, y_test, feature_names = load_and_prepare_data()
    
    print("\nTraining XGBoost...")
    xgb_model = train_xgboost(X_train, y_train)
    xgb_results = evaluate_model(xgb_model, X_test, y_test, model_name='XGBoost')
    xgb_importance = get_feature_importance(xgb_model, feature_names)
    
    print("Generating XGBoost plots...")
    plot_predictions(y_test, xgb_results['predictions'],
                    model_name='XGBoost',
                    save_path='ml/visualizations/xgb_predictions.png')
    plt.close()
    
    plot_residuals(y_test, xgb_results['predictions'],
                  model_name='XGBoost',
                  save_path='ml/visualizations/xgb_residuals.png')
    plt.close()
    
    plot_feature_importance(xgb_importance,
                           model_name='XGBoost',
                           save_path='ml/visualizations/xgb_feature_importance.png')
    plt.close()
    
    print("\n✓ All visualizations saved to ml/visualizations/")
    print(f"\n  XGBoost - R²: {xgb_results['r2']:.4f}")

if __name__ == "__main__":
    generate_all_visualizations()
