from xgboost import XGBRegressor
import pandas as pd

def train_xgboost(X_train, y_train, params=None):
    default_params = {
        'n_estimators': 100,
        'max_depth': 5,
        'learning_rate': 0.1,
        'random_state': 42
    }
    
    if params:
        default_params.update(params)
    
    model = XGBRegressor(**default_params)
    model.fit(X_train, y_train)
    return model

def get_feature_importance(model, feature_names):
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance

