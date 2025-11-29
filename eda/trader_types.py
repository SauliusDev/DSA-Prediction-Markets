"""
Trader Type Analysis Functions

Reusable plotting functions for analyzing different trader types:
- Trader type prevalence
- Performance by trader type
- Type co-occurrence patterns

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Define trader type features
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


def plot_trader_type_prevalence(df, figsize=(16, 6), save=False, path=None):
    """
    Plot trader type distribution and types per trader.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader type columns
    figsize : tuple
        Figure size (width, height)
    save : bool
        Whether to save the figure
    path : str
        Path to save the figure (if save=True)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure object
    type_counts : dict
        Dictionary containing type counts and percentages
    """
    # Count traders of each type
    type_counts = {}
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        count = df[col].sum()
        pct = (count / len(df)) * 100
        type_counts[type_name] = {'count': count, 'percentage': pct}
    
    # Sort by count
    type_counts_sorted = dict(sorted(type_counts.items(), key=lambda x: x[1]['count'], reverse=True))
    
    # Count types per trader
    df_temp = df.copy()
    df_temp['num_types'] = df_temp[TRADER_TYPE_FEATURES].sum(axis=1)
    type_count_dist = df_temp['num_types'].value_counts().sort_index()
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Trader Type Prevalence', fontsize=16, fontweight='bold')
    
    # Bar chart of type counts
    type_names = list(type_counts_sorted.keys())
    type_values = [v['count'] for v in type_counts_sorted.values()]
    colors = plt.cm.Set3(range(len(type_names)))
    
    axes[0].barh(type_names, type_values, color=colors, edgecolor='black', alpha=0.8)
    axes[0].set_xlabel('Number of Traders', fontsize=12)
    axes[0].set_ylabel('Trader Type', fontsize=12)
    axes[0].set_title('Trader Type Distribution')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    # Distribution of number of types per trader
    axes[1].bar(type_count_dist.index, type_count_dist.values, color='steelblue', 
                edgecolor='black', alpha=0.7)
    axes[1].set_xlabel('Number of Types per Trader', fontsize=12)
    axes[1].set_ylabel('Number of Traders', fontsize=12)
    axes[1].set_title('Distribution of Types per Trader')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, type_counts_sorted


def plot_performance_by_type(df, figsize=(18, 14), save=False, path=None):
    """
    Plot performance metrics by trader type.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader type and performance columns
    figsize : tuple
        Figure size (width, height)
    save : bool
        Whether to save the figure
    path : str
        Path to save the figure (if save=True)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure object
    performance : dict
        Dictionary containing performance metrics by type
    """
    # Calculate performance metrics for each type
    type_performance = {}
    
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        type_traders = df[df[col] == 1]
        
        if len(type_traders) > 0:
            type_performance[type_name] = {
                'count': len(type_traders),
                'avg_winrate': type_traders['win_rate'].mean(),
                'median_winrate': type_traders['win_rate'].median(),
                'avg_pnl': type_traders['total_pnl'].mean(),
                'median_pnl': type_traders['total_pnl'].median(),
                'avg_smart_score': type_traders['smart_score'].mean(),
                'profitable_pct': (type_traders['total_pnl'] > 0).sum() / len(type_traders) * 100
            }
    
    # Sort by average win rate
    type_performance_sorted = dict(sorted(type_performance.items(), 
                                         key=lambda x: x[1]['avg_winrate'], 
                                         reverse=True))
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Performance by Trader Type', fontsize=16, fontweight='bold')
    
    # Win rate by type
    type_names_perf = list(type_performance_sorted.keys())
    avg_winrates = [v['avg_winrate'] for v in type_performance_sorted.values()]
    colors_perf = ['green' if wr > df['win_rate'].mean() else 'red' for wr in avg_winrates]
    
    axes[0, 0].barh(type_names_perf, avg_winrates, color=colors_perf, edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
                       label=f'Overall Avg: {df["win_rate"].mean():.2%}')
    axes[0, 0].set_xlabel('Average Win Rate', fontsize=12)
    axes[0, 0].set_ylabel('Trader Type', fontsize=12)
    axes[0, 0].set_title('Average Win Rate by Type')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='x')
    
    # PnL by type
    avg_pnls = [v['avg_pnl'] for v in type_performance_sorted.values()]
    colors_pnl = ['green' if pnl > 0 else 'red' for pnl in avg_pnls]
    
    axes[0, 1].barh(type_names_perf, avg_pnls, color=colors_pnl, edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=2)
    axes[0, 1].set_xlabel('Average PnL ($)', fontsize=12)
    axes[0, 1].set_ylabel('Trader Type', fontsize=12)
    axes[0, 1].set_title('Average PnL by Type')
    axes[0, 1].grid(True, alpha=0.3, axis='x')
    
    # Box plot comparison (top 5 most common types)
    type_counts = {TYPE_DISPLAY_NAMES[col]: df[col].sum() for col in TRADER_TYPE_FEATURES}
    top_5_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_names = [t[0] for t in top_5_types]
    
    winrate_data = []
    labels = []
    for type_name in top_5_names:
        col = [k for k, v in TYPE_DISPLAY_NAMES.items() if v == type_name][0]
        type_traders = df[df[col] == 1]
        winrate_data.append(type_traders['win_rate'].values)
        labels.append(type_name)
    
    bp = axes[1, 0].boxplot(winrate_data, labels=labels, patch_artist=True)
    for patch, color in zip(bp['boxes'], plt.cm.Set3(range(len(labels)))):
        patch.set_facecolor(color)
    axes[1, 0].set_ylabel('Win Rate', fontsize=12)
    axes[1, 0].set_title('Win Rate Distribution (Top 5 Types)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Profitable percentage by type
    profitable_pcts = [v['profitable_pct'] for v in type_performance_sorted.values()]
    axes[1, 1].barh(type_names_perf, profitable_pcts, color='lightgreen', edgecolor='black', alpha=0.7)
    axes[1, 1].axvline(50, color='red', linestyle='--', linewidth=2, label='50% threshold')
    axes[1, 1].set_xlabel('Percentage Profitable (%)', fontsize=12)
    axes[1, 1].set_ylabel('Trader Type', fontsize=12)
    axes[1, 1].set_title('Percentage of Profitable Traders by Type')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, type_performance_sorted


def plot_type_cooccurrence(df, figsize=(14, 12), save=False, path=None):
    """
    Plot co-occurrence matrix of trader types.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader type columns
    figsize : tuple
        Figure size (width, height)
    save : bool
        Whether to save the figure
    path : str
        Path to save the figure (if save=True)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The generated figure object
    cooccurrence : pd.DataFrame
        Co-occurrence matrix
    """
    # Create co-occurrence matrix
    cooccurrence = pd.DataFrame(0, index=TRADER_TYPE_FEATURES, columns=TRADER_TYPE_FEATURES)
    
    for i, type1 in enumerate(TRADER_TYPE_FEATURES):
        for j, type2 in enumerate(TRADER_TYPE_FEATURES):
            if i != j:
                both = ((df[type1] == 1) & (df[type2] == 1)).sum()
                cooccurrence.loc[type1, type2] = both
    
    # Rename for display
    cooccurrence.index = [TYPE_DISPLAY_NAMES[t] for t in cooccurrence.index]
    cooccurrence.columns = [TYPE_DISPLAY_NAMES[t] for t in cooccurrence.columns]
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cooccurrence, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Number of Traders'}, ax=ax)
    ax.set_title('Trader Type Co-occurrence Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Trader Type', fontsize=12)
    ax.set_ylabel('Trader Type', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, cooccurrence


def get_trader_type_summary(df):
    """
    Get a comprehensive summary of trader types.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader type columns
    
    Returns:
    --------
    summary : dict
        Dictionary containing trader type summary statistics
    """
    # Most common type
    type_counts = {TYPE_DISPLAY_NAMES[col]: df[col].sum() for col in TRADER_TYPE_FEATURES}
    most_common = max(type_counts.items(), key=lambda x: x[1])
    
    # Best performing type
    type_performance = {}
    for col in TRADER_TYPE_FEATURES:
        type_name = TYPE_DISPLAY_NAMES[col]
        type_traders = df[df[col] == 1]
        if len(type_traders) > 0:
            type_performance[type_name] = type_traders['win_rate'].mean()
    
    best_performing = max(type_performance.items(), key=lambda x: x[1]) if type_performance else (None, None)
    
    # Average types per trader
    df_temp = df.copy()
    df_temp['num_types'] = df_temp[TRADER_TYPE_FEATURES].sum(axis=1)
    
    summary = {
        'most_common_type': most_common[0],
        'most_common_count': most_common[1],
        'best_performing_type': best_performing[0],
        'best_performing_winrate': best_performing[1],
        'avg_types_per_trader': df_temp['num_types'].mean(),
        'median_types_per_trader': df_temp['num_types'].median()
    }
    
    return summary
