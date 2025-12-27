import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_prepare_data(csv_path='data/users_data.csv', target='win_rate', test_size=0.2, random_state=42):
    df = pd.read_csv(csv_path)
    
    df = df.dropna(subset=[target])
    
    feature_cols = [
        'smart_score', 'total_positions', 'num_markets', 'total_pnl',
        'trader_type_bagholder', 'trader_type_contrarian', 'trader_type_lottery_ticket',
        'trader_type_trend_follower', 'trader_type_senior', 'trader_type_novice',
        'trader_bets_0_0', 'trader_bets_0_1', 'trader_bets_0_2', 'trader_bets_0_3',
        'trader_bets_0_4', 'trader_bets_0_5', 'trader_bets_0_6', 'trader_bets_0_7',
        'trader_bets_0_8', 'trader_bets_0_9',
        'most_traded_categories_politics', 'most_traded_categories_sport',
        'most_traded_categories_crypto', 'most_traded_categories_culture'
    ]
    
    available_features = [col for col in feature_cols if col in df.columns]
    
    X = df[available_features].copy()
    y = df[target].copy()
    
    X = X.fillna(0)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    return X_train, X_test, y_train, y_test, available_features

