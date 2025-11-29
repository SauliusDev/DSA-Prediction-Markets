"""
Risk Behavior Analysis Functions

Reusable plotting functions for analyzing trader risk behavior:
- Betting probability distributions
- Risk profiles
- Win rate by betting probability range

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

# Define betting pattern features
BETTING_PATTERN_FEATURES = [
    'trader_bets_0_0', 'trader_bets_0_1', 'trader_bets_0_2',
    'trader_bets_0_3', 'trader_bets_0_4', 'trader_bets_0_5',
    'trader_bets_0_6', 'trader_bets_0_7', 'trader_bets_0_8',
    'trader_bets_0_9'
]

PROB_LABELS = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
               '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']


def plot_betting_probability_distribution(df, figsize=(16, 12), save=False, path=None):
    """
    Plot overall betting probability distribution.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing betting pattern columns
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
    distribution : dict
        Dictionary containing betting distribution statistics
    """
    # Calculate total bets in each probability range
    total_bets_by_range = df[BETTING_PATTERN_FEATURES].sum()
    total_bets = total_bets_by_range.sum()
    
    # Categorize betting behavior
    def categorize_risk_profile(row):
        """Categorize trader based on betting patterns"""
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
    
    df_temp = df.copy()
    df_temp['risk_profile'] = df_temp.apply(categorize_risk_profile, axis=1)
    risk_profile_counts = df_temp['risk_profile'].value_counts()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Betting Probability Distribution Analysis', fontsize=16, fontweight='bold')
    
    # Bar chart of total bets by range
    colors = plt.cm.RdYlGn(np.linspace(0, 1, len(PROB_LABELS)))
    axes[0, 0].bar(PROB_LABELS, total_bets_by_range.values, color=colors, edgecolor='black', alpha=0.8)
    axes[0, 0].set_xlabel('Probability Range', fontsize=12)
    axes[0, 0].set_ylabel('Total Number of Bets', fontsize=12)
    axes[0, 0].set_title('Distribution of Bets Across Probability Ranges')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Pie chart
    axes[0, 1].pie(total_bets_by_range.values, labels=PROB_LABELS, autopct='%1.1f%%',
                   colors=colors, startangle=90)
    axes[0, 1].set_title('Bet Distribution by Probability Range')
    
    # Risk profile distribution
    profile_colors = {'Longshot Hunter': 'red', 'Balanced': 'orange', 'Safe Player': 'green', 'Unknown': 'gray'}
    profile_color_list = [profile_colors.get(p, 'gray') for p in risk_profile_counts.index]
    axes[1, 0].bar(risk_profile_counts.index, risk_profile_counts.values, 
                   color=profile_color_list, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Risk Profile', fontsize=12)
    axes[1, 0].set_ylabel('Number of Traders', fontsize=12)
    axes[1, 0].set_title('Trader Risk Profile Distribution')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Average betting pattern per trader
    avg_bets_per_trader = df[BETTING_PATTERN_FEATURES].mean()
    axes[1, 1].plot(PROB_LABELS, avg_bets_per_trader.values, marker='o', linewidth=2, 
                    markersize=8, color='steelblue')
    axes[1, 1].set_xlabel('Probability Range', fontsize=12)
    axes[1, 1].set_ylabel('Average Bets per Trader', fontsize=12)
    axes[1, 1].set_title('Average Betting Pattern')
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


def plot_winrate_by_probability_range(df, figsize=(14, 8), save=False, path=None):
    """
    Plot win rate distribution by betting probability range using box plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing betting pattern and win rate columns
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
    correlations : dict
        Dictionary containing correlation statistics
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Win Rate by Betting Probability Range', fontsize=16, fontweight='bold')
    
    # For each probability range, get win rates of traders who bet in that range
    winrate_by_prob_range = []
    prob_range_labels = []
    
    for idx, col in enumerate(BETTING_PATTERN_FEATURES):
        # Only include traders who placed bets in this range
        traders_in_range = df[df[col] > 0]
        if len(traders_in_range) >= 5:  # Minimum sample size
            winrate_by_prob_range.append(traders_in_range['win_rate'].values)
            prob_range_labels.append(PROB_LABELS[idx])
    
    # Create box plots
    bp = ax.boxplot(winrate_by_prob_range, 
                    labels=prob_range_labels,
                    patch_artist=True,
                    showmeans=True,
                    meanline=True,
                    widths=0.6)
    
    # Color the boxes with a gradient (red to green)
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(prob_range_labels)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Customize the plot
    ax.set_xlabel('Betting Probability Range', fontsize=14, fontweight='bold')
    ax.set_ylabel('Win Rate', fontsize=14, fontweight='bold')
    ax.set_title('Win Rate Distribution by Betting Probability Range', fontsize=14, pad=15)
    ax.tick_params(axis='x', rotation=45, labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add a horizontal line for overall average
    ax.axhline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
               alpha=0.7, label=f'Overall Avg: {df["win_rate"].mean():.2%}')
    ax.legend(loc='upper right', fontsize=11)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    # Calculate correlations
    correlations = {}
    for idx, col in enumerate(BETTING_PATTERN_FEATURES):
        traders_in_range = df[df[col] > 0]
        if len(traders_in_range) > 10:
            corr = traders_in_range[col].corr(traders_in_range['win_rate'])
            correlations[PROB_LABELS[idx]] = corr
    
    return fig, correlations


def get_risk_behavior_summary(df):
    """
    Get a comprehensive summary of risk behavior.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing betting pattern columns
    
    Returns:
    --------
    summary : dict
        Dictionary containing risk behavior summary statistics
    """
    # Calculate total bets
    total_bets_by_range = df[BETTING_PATTERN_FEATURES].sum()
    most_popular_idx = total_bets_by_range.argmax()
    
    # Categorize traders
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
    
    df_temp = df.copy()
    df_temp['risk_profile'] = df_temp.apply(categorize_risk_profile, axis=1)
    
    # Longshot specialists
    df_temp['longshot_pct'] = (df_temp['trader_bets_0_0'] + df_temp['trader_bets_0_1']) / df_temp[BETTING_PATTERN_FEATURES].sum(axis=1)
    longshot_specialists = df_temp[df_temp['longshot_pct'] > 0.8]
    
    # Safe bet specialists
    df_temp['safe_pct'] = (df_temp['trader_bets_0_8'] + df_temp['trader_bets_0_9']) / df_temp[BETTING_PATTERN_FEATURES].sum(axis=1)
    safe_specialists = df_temp[df_temp['safe_pct'] > 0.8]
    
    summary = {
        'most_popular_range': PROB_LABELS[most_popular_idx],
        'most_popular_bets': total_bets_by_range.iloc[most_popular_idx],
        'total_bets': total_bets_by_range.sum(),
        'longshot_hunters': (df_temp['risk_profile'] == 'Longshot Hunter').sum(),
        'safe_players': (df_temp['risk_profile'] == 'Safe Player').sum(),
        'balanced_traders': (df_temp['risk_profile'] == 'Balanced').sum(),
        'longshot_specialists_count': len(longshot_specialists),
        'longshot_specialists_avg_winrate': longshot_specialists['win_rate'].mean() if len(longshot_specialists) > 0 else None,
        'safe_specialists_count': len(safe_specialists),
        'safe_specialists_avg_winrate': safe_specialists['win_rate'].mean() if len(safe_specialists) > 0 else None
    }
    
    return summary

