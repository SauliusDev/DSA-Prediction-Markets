import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

TRADER_TYPE_FEATURES = [
    'trader_type_bagholder', 'trader_type_contrarian',
    'trader_type_lottery_ticket', 'trader_type_new',
    'trader_type_novice', 'trader_type_reverse_cramer',
    'trader_type_senior', 'trader_type_trend_follower',
    'trader_type_veteran', 'trader_type_waiting_for_the_money',
    'trader_type_whale_splash'
]

TYPE_DISPLAY_NAMES = {
    'trader_type_bagholder': 'Bagholder',
    'trader_type_contrarian': 'Contrarian',
    'trader_type_lottery_ticket': 'Lottery Ticket',
    'trader_type_new': 'New',
    'trader_type_novice': 'Novice',
    'trader_type_reverse_cramer': 'Reverse Cramer',
    'trader_type_senior': 'Senior',
    'trader_type_trend_follower': 'Trend Follower',
    'trader_type_veteran': 'Veteran',
    'trader_type_waiting_for_the_money': 'Waiting for Money',
    'trader_type_whale_splash': 'Whale Splash'
}


def filter_crypto_traders(df, min_volume=0):
    return df[df['most_traded_categories_crypto'] > min_volume].copy()


def plot_crypto_trader_type_prevalence(df, figsize=(16, 6), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    type_counts = {}
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        count = df_crypto[col].sum()
        pct = (count / len(df_crypto)) * 100
        type_counts[type_name] = {'count': count, 'percentage': pct}
    
    type_counts_sorted = dict(sorted(type_counts.items(), key=lambda x: x[1]['count'], reverse=True))
    
    df_temp = df_crypto.copy()
    df_temp['num_types'] = df_temp[TRADER_TYPE_FEATURES].sum(axis=1)
    type_count_dist = df_temp['num_types'].value_counts().sort_index()
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Crypto Trader Type Prevalence', fontsize=16, fontweight='bold')
    
    type_names = list(type_counts_sorted.keys())
    type_values = [v['count'] for v in type_counts_sorted.values()]
    colors = plt.cm.Set3(range(len(type_names)))
    
    axes[0].barh(type_names, type_values, color=colors, edgecolor='black', alpha=0.8)
    axes[0].set_xlabel('Number of Crypto Traders', fontsize=12)
    axes[0].set_ylabel('Trader Type', fontsize=12)
    axes[0].set_title('Crypto Trader Type Distribution')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    axes[1].bar(type_count_dist.index, type_count_dist.values, color='#F7931A', 
                edgecolor='black', alpha=0.7)
    axes[1].set_xlabel('Number of Types per Trader', fontsize=12)
    axes[1].set_ylabel('Number of Crypto Traders', fontsize=12)
    axes[1].set_title('Distribution of Types per Crypto Trader')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, type_counts_sorted


def plot_crypto_performance_by_type(df, figsize=(18, 14), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    type_performance = {}
    
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        type_traders = df_crypto[df_crypto[col] == 1]
        
        if len(type_traders) > 0:
            crypto_wr = type_traders['win_rate_categories_crypto']
            crypto_wr_valid = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
            
            type_performance[type_name] = {
                'count': len(type_traders),
                'avg_crypto_winrate': crypto_wr_valid.mean() if len(crypto_wr_valid) > 0 else None,
                'median_crypto_winrate': crypto_wr_valid.median() if len(crypto_wr_valid) > 0 else None,
                'avg_overall_winrate': type_traders['win_rate'].mean(),
                'avg_pnl': type_traders['total_pnl'].mean(),
                'avg_smart_score': type_traders['smart_score'].mean(),
                'profitable_pct': (type_traders['total_pnl'] > 0).sum() / len(type_traders) * 100
            }
    
    type_performance_sorted = dict(sorted(
        [(k, v) for k, v in type_performance.items() if v['avg_crypto_winrate'] is not None],
        key=lambda x: x[1]['avg_crypto_winrate'] if x[1]['avg_crypto_winrate'] else 0, 
        reverse=True
    ))
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Crypto Performance by Trader Type', fontsize=16, fontweight='bold')
    
    type_names_perf = list(type_performance_sorted.keys())
    avg_crypto_winrates = [v['avg_crypto_winrate'] for v in type_performance_sorted.values()]
    
    crypto_wr_all = df_crypto['win_rate_categories_crypto']
    crypto_wr_all_valid = crypto_wr_all[(crypto_wr_all > 0) & (crypto_wr_all.notna())]
    overall_crypto_avg = crypto_wr_all_valid.mean() if len(crypto_wr_all_valid) > 0 else 0
    
    colors_perf = ['green' if wr and wr > overall_crypto_avg else 'red' for wr in avg_crypto_winrates]
    
    axes[0, 0].barh(type_names_perf, avg_crypto_winrates, color=colors_perf, edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(overall_crypto_avg, color='#F7931A', linestyle='--', linewidth=2, 
                       label=f'Crypto Avg: {overall_crypto_avg:.2%}')
    axes[0, 0].set_xlabel('Average Crypto Win Rate', fontsize=12)
    axes[0, 0].set_ylabel('Trader Type', fontsize=12)
    axes[0, 0].set_title('Average Crypto Win Rate by Type')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='x')
    
    avg_overall_winrates = [v['avg_overall_winrate'] for v in type_performance_sorted.values()]
    x = np.arange(len(type_names_perf))
    width = 0.35
    
    bars1 = axes[0, 1].barh(x - width/2, avg_crypto_winrates, width, label='Crypto WR', 
                            color='#F7931A', edgecolor='black', alpha=0.7)
    bars2 = axes[0, 1].barh(x + width/2, avg_overall_winrates, width, label='Overall WR', 
                            color='steelblue', edgecolor='black', alpha=0.7)
    axes[0, 1].set_yticks(x)
    axes[0, 1].set_yticklabels(type_names_perf)
    axes[0, 1].set_xlabel('Win Rate', fontsize=12)
    axes[0, 1].set_ylabel('Trader Type', fontsize=12)
    axes[0, 1].set_title('Crypto vs Overall Win Rate by Type')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='x')
    
    type_counts = {TYPE_DISPLAY_NAMES[col]: df_crypto[col].sum() for col in TRADER_TYPE_FEATURES}
    top_5_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_names = [t[0] for t in top_5_types]
    
    winrate_data = []
    labels = []
    for type_name in top_5_names:
        col = [k for k, v in TYPE_DISPLAY_NAMES.items() if v == type_name][0]
        type_traders = df_crypto[df_crypto[col] == 1]
        crypto_wr = type_traders['win_rate_categories_crypto']
        crypto_wr_valid = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
        if len(crypto_wr_valid) > 0:
            winrate_data.append(crypto_wr_valid.values)
            labels.append(type_name)
    
    if len(winrate_data) > 0:
        bp = axes[1, 0].boxplot(winrate_data, labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], plt.cm.Set3(range(len(labels)))):
            patch.set_facecolor(color)
        axes[1, 0].set_ylabel('Crypto Win Rate', fontsize=12)
        axes[1, 0].set_title('Crypto Win Rate Distribution (Top 5 Types)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    profitable_pcts = [v['profitable_pct'] for v in type_performance_sorted.values()]
    axes[1, 1].barh(type_names_perf, profitable_pcts, color='lightgreen', edgecolor='black', alpha=0.7)
    axes[1, 1].axvline(50, color='red', linestyle='--', linewidth=2, label='50% threshold')
    axes[1, 1].set_xlabel('Percentage Profitable (%)', fontsize=12)
    axes[1, 1].set_ylabel('Trader Type', fontsize=12)
    axes[1, 1].set_title('Percentage of Profitable Crypto Traders by Type')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, type_performance_sorted


def plot_crypto_type_cooccurrence(df, figsize=(14, 12), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    cooccurrence = pd.DataFrame(0, index=TRADER_TYPE_FEATURES, columns=TRADER_TYPE_FEATURES)
    
    for i, type1 in enumerate(TRADER_TYPE_FEATURES):
        for j, type2 in enumerate(TRADER_TYPE_FEATURES):
            if i != j:
                both = ((df_crypto[type1] == 1) & (df_crypto[type2] == 1)).sum()
                cooccurrence.loc[type1, type2] = both
    
    cooccurrence.index = [TYPE_DISPLAY_NAMES[t] for t in cooccurrence.index]
    cooccurrence.columns = [TYPE_DISPLAY_NAMES[t] for t in cooccurrence.columns]
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cooccurrence, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Number of Crypto Traders'}, ax=ax)
    ax.set_title('Crypto Trader Type Co-occurrence Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Trader Type', fontsize=12)
    ax.set_ylabel('Trader Type', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, cooccurrence


def get_crypto_trader_type_summary(df):
    df_crypto = filter_crypto_traders(df)
    
    type_counts = {TYPE_DISPLAY_NAMES[col]: df_crypto[col].sum() for col in TRADER_TYPE_FEATURES}
    most_common = max(type_counts.items(), key=lambda x: x[1])
    
    type_performance = {}
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        type_traders = df_crypto[df_crypto[col] == 1]
        if len(type_traders) > 0:
            crypto_wr = type_traders['win_rate_categories_crypto']
            crypto_wr_valid = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
            if len(crypto_wr_valid) > 0:
                type_performance[type_name] = crypto_wr_valid.mean()
    
    best_performing = max(type_performance.items(), key=lambda x: x[1]) if type_performance else (None, None)
    
    df_temp = df_crypto.copy()
    df_temp['num_types'] = df_temp[TRADER_TYPE_FEATURES].sum(axis=1)
    
    summary = {
        'total_crypto_traders': len(df_crypto),
        'most_common_type': most_common[0],
        'most_common_count': most_common[1],
        'best_performing_type': best_performing[0],
        'best_performing_crypto_winrate': best_performing[1],
        'avg_types_per_trader': df_temp['num_types'].mean(),
        'median_types_per_trader': df_temp['num_types'].median()
    }
    
    return summary

