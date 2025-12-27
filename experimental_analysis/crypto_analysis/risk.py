import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

BETTING_PATTERN_FEATURES = [
    'trader_bets_0_0', 'trader_bets_0_1', 'trader_bets_0_2',
    'trader_bets_0_3', 'trader_bets_0_4', 'trader_bets_0_5',
    'trader_bets_0_6', 'trader_bets_0_7', 'trader_bets_0_8',
    'trader_bets_0_9'
]

PROB_LABELS = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
               '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']


def filter_crypto_traders(df, min_volume=0):
    return df[df['most_traded_categories_crypto'] > min_volume].copy()


def plot_crypto_betting_probability_distribution(df, figsize=(16, 12), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    total_bets_by_range = df_crypto[BETTING_PATTERN_FEATURES].sum()
    total_bets = total_bets_by_range.sum()
    
    def categorize_risk_profile(row):
        total = row[BETTING_PATTERN_FEATURES].sum()
        if total == 0:
            return 'Unknown'
        
        longshot_bets = row['trader_bets_0_0'] + row['trader_bets_0_1']
        safe_bets = row['trader_bets_0_8'] + row['trader_bets_0_9']
        
        longshot_pct = longshot_bets / total
        safe_pct = safe_bets / total
        
        if longshot_pct > 0.5:
            return 'Longshot Hunter'
        elif safe_pct > 0.5:
            return 'Safe Player'
        else:
            return 'Balanced'
    
    df_temp = df_crypto.copy()
    df_temp['risk_profile'] = df_temp.apply(categorize_risk_profile, axis=1)
    risk_profile_counts = df_temp['risk_profile'].value_counts()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Crypto Trader Betting Probability Distribution', fontsize=16, fontweight='bold')
    
    colors = plt.cm.RdYlGn(np.linspace(0, 1, len(PROB_LABELS)))
    axes[0, 0].bar(PROB_LABELS, total_bets_by_range.values, color=colors, edgecolor='black', alpha=0.8)
    axes[0, 0].set_xlabel('Probability Range', fontsize=12)
    axes[0, 0].set_ylabel('Total Number of Bets', fontsize=12)
    axes[0, 0].set_title('Crypto Traders: Bets by Probability Range')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    axes[0, 1].pie(total_bets_by_range.values, labels=PROB_LABELS, autopct='%1.1f%%',
                   colors=colors, startangle=90)
    axes[0, 1].set_title('Crypto Traders: Bet Distribution')
    
    profile_colors = {'Longshot Hunter': '#8B0000', 'Balanced': '#F7931A', 'Safe Player': '#006400', 'Unknown': 'gray'}
    profile_color_list = [profile_colors.get(p, 'gray') for p in risk_profile_counts.index]
    axes[1, 0].bar(risk_profile_counts.index, risk_profile_counts.values, 
                   color=profile_color_list, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Risk Profile', fontsize=12)
    axes[1, 0].set_ylabel('Number of Crypto Traders', fontsize=12)
    axes[1, 0].set_title('Crypto Trader Risk Profile Distribution')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    avg_bets_per_trader = df_crypto[BETTING_PATTERN_FEATURES].mean()
    axes[1, 1].plot(PROB_LABELS, avg_bets_per_trader.values, marker='o', linewidth=2, 
                    markersize=8, color='#F7931A')
    axes[1, 1].set_xlabel('Probability Range', fontsize=12)
    axes[1, 1].set_ylabel('Average Bets per Trader', fontsize=12)
    axes[1, 1].set_title('Crypto Traders: Average Betting Pattern')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    distribution = {
        'total_bets': total_bets,
        'bets_by_range': {PROB_LABELS[i]: total_bets_by_range.iloc[i] for i in range(len(PROB_LABELS))},
        'risk_profiles': risk_profile_counts.to_dict(),
        'most_popular_range': PROB_LABELS[total_bets_by_range.argmax()]
    }
    
    return fig, distribution


def plot_crypto_winrate_by_probability_range(df, figsize=(14, 8), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    crypto_wr = df_crypto['win_rate_categories_crypto']
    valid_crypto_mask = (crypto_wr > 0) & (crypto_wr.notna())
    df_crypto_valid = df_crypto[valid_crypto_mask]
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Crypto Win Rate by Betting Probability Range', fontsize=16, fontweight='bold')
    
    winrate_by_prob_range = []
    prob_range_labels = []
    
    for idx, col in enumerate(BETTING_PATTERN_FEATURES):
        traders_in_range = df_crypto_valid[df_crypto_valid[col] > 0]
        if len(traders_in_range) >= 5:
            winrate_by_prob_range.append(traders_in_range['win_rate_categories_crypto'].values)
            prob_range_labels.append(PROB_LABELS[idx])
    
    if len(winrate_by_prob_range) > 0:
        bp = ax.boxplot(winrate_by_prob_range, 
                        labels=prob_range_labels,
                        patch_artist=True,
                        showmeans=True,
                        meanline=True,
                        widths=0.6)
        
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(prob_range_labels)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Betting Probability Range', fontsize=14, fontweight='bold')
        ax.set_ylabel('Crypto Win Rate', fontsize=14, fontweight='bold')
        ax.set_title('Crypto Win Rate Distribution by Betting Probability Range', fontsize=14, pad=15)
        ax.tick_params(axis='x', rotation=45, labelsize=11)
        ax.tick_params(axis='y', labelsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        overall_avg = df_crypto_valid['win_rate_categories_crypto'].mean()
        ax.axhline(overall_avg, color='#F7931A', linestyle='--', linewidth=2, 
                   alpha=0.7, label=f'Crypto Avg: {overall_avg:.2%}')
        ax.legend(loc='upper right', fontsize=11)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    correlations = {}
    for idx, col in enumerate(BETTING_PATTERN_FEATURES):
        traders_in_range = df_crypto_valid[df_crypto_valid[col] > 0]
        if len(traders_in_range) > 10:
            corr = traders_in_range[col].corr(traders_in_range['win_rate_categories_crypto'])
            correlations[PROB_LABELS[idx]] = corr
    
    return fig, correlations


def get_crypto_risk_behavior_summary(df):
    df_crypto = filter_crypto_traders(df)
    
    total_bets_by_range = df_crypto[BETTING_PATTERN_FEATURES].sum()
    most_popular_idx = total_bets_by_range.argmax()
    
    def categorize_risk_profile(row):
        total = row[BETTING_PATTERN_FEATURES].sum()
        if total == 0:
            return 'Unknown'
        longshot_bets = row['trader_bets_0_0'] + row['trader_bets_0_1']
        safe_bets = row['trader_bets_0_8'] + row['trader_bets_0_9']
        longshot_pct = longshot_bets / total
        safe_pct = safe_bets / total
        if longshot_pct > 0.5:
            return 'Longshot Hunter'
        elif safe_pct > 0.5:
            return 'Safe Player'
        else:
            return 'Balanced'
    
    df_temp = df_crypto.copy()
    df_temp['risk_profile'] = df_temp.apply(categorize_risk_profile, axis=1)
    
    df_temp['longshot_pct'] = (df_temp['trader_bets_0_0'] + df_temp['trader_bets_0_1']) / df_temp[BETTING_PATTERN_FEATURES].sum(axis=1)
    longshot_specialists = df_temp[df_temp['longshot_pct'] > 0.8]
    
    df_temp['safe_pct'] = (df_temp['trader_bets_0_8'] + df_temp['trader_bets_0_9']) / df_temp[BETTING_PATTERN_FEATURES].sum(axis=1)
    safe_specialists = df_temp[df_temp['safe_pct'] > 0.8]
    
    crypto_wr = df_temp['win_rate_categories_crypto']
    crypto_wr_valid = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
    
    summary = {
        'most_popular_range': PROB_LABELS[most_popular_idx],
        'most_popular_bets': total_bets_by_range.iloc[most_popular_idx],
        'total_bets': total_bets_by_range.sum(),
        'longshot_hunters': (df_temp['risk_profile'] == 'Longshot Hunter').sum(),
        'safe_players': (df_temp['risk_profile'] == 'Safe Player').sum(),
        'balanced_traders': (df_temp['risk_profile'] == 'Balanced').sum(),
        'longshot_specialists_count': len(longshot_specialists),
        'longshot_specialists_avg_crypto_winrate': longshot_specialists.loc[
            longshot_specialists['win_rate_categories_crypto'].notna() & 
            (longshot_specialists['win_rate_categories_crypto'] > 0), 
            'win_rate_categories_crypto'
        ].mean() if len(longshot_specialists) > 0 else None,
        'safe_specialists_count': len(safe_specialists),
        'safe_specialists_avg_crypto_winrate': safe_specialists.loc[
            safe_specialists['win_rate_categories_crypto'].notna() & 
            (safe_specialists['win_rate_categories_crypto'] > 0), 
            'win_rate_categories_crypto'
        ].mean() if len(safe_specialists) > 0 else None
    }
    
    return summary

