import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.preprocessing import load_and_prepare_data
from ml.models import train_xgboost, get_feature_importance
from ml.evaluation import evaluate_model

def test_ml_pipeline():
    print("="*60)
    print("Testing ML Pipeline")
    print("="*60)
    
    print("\n1. Loading data...")
    X_train, X_test, y_train, y_test, feature_names = load_and_prepare_data()
    print(f"   ✓ Training samples: {X_train.shape[0]}")
    print(f"   ✓ Testing samples: {X_test.shape[0]}")
    print(f"   ✓ Features: {len(feature_names)}")
    
    print("\n2. Training XGBoost...")
    xgb_model = train_xgboost(X_train, y_train)
    xgb_results = evaluate_model(xgb_model, X_test, y_test, model_name='XGBoost')
    print(f"   ✓ RMSE: {xgb_results['rmse']:.4f}")
    print(f"   ✓ MAE: {xgb_results['mae']:.4f}")
    print(f"   ✓ R² Score: {xgb_results['r2']:.4f}")
    
    print("\n3. Feature importance...")
    xgb_importance = get_feature_importance(xgb_model, feature_names)
    print(xgb_importance.head(5).to_string(index=False))
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)

if __name__ == "__main__":
    test_ml_pipeline()
