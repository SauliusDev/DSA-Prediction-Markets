"""
Performance Distribution Analysis Functions

Reusable plotting functions for analyzing trader performance metrics:
- Win rate distributions
- Smart score analysis
- Correlations between metrics

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_win_rate_distribution(df, figsize=(18, 5), save=False, path=None):
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle('Win Rate Distribution Analysis', fontsize=16, fontweight='bold')
    
    # Histogram
    axes[0].hist(df['win_rate'], bins=40, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].axvline(df['win_rate'].mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {df["win_rate"].mean():.2%}')
    axes[0].axvline(df['win_rate'].median(), color='green', linestyle='--', linewidth=2, 
                    label=f'Median: {df["win_rate"].median():.2%}')
    axes[0].set_xlabel('Win Rate', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('Win Rate Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Box plot
    box = axes[1].boxplot(df['win_rate'], vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('lightblue')
    axes[1].set_ylabel('Win Rate', fontsize=12)
    axes[1].set_title('Win Rate Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    # Density plot
    df['win_rate'].plot(kind='density', ax=axes[2], color='darkblue', linewidth=2)
    axes[2].axvline(df['win_rate'].mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {df["win_rate"].mean():.2%}')
    axes[2].set_xlabel('Win Rate', fontsize=12)
    axes[2].set_ylabel('Density', fontsize=12)
    axes[2].set_title('Win Rate Density Plot')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    # Calculate statistics
    stats = {
        'mean': df['win_rate'].mean(),
        'median': df['win_rate'].median(),
        'std': df['win_rate'].std(),
        'min': df['win_rate'].min(),
        'max': df['win_rate'].max(),
        'q1': df['win_rate'].quantile(0.25),
        'q3': df['win_rate'].quantile(0.75)
    }
    
    return fig, stats


def plot_smart_score_analysis(df, figsize=(16, 12), save=False, path=None):
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Smart Score Analysis', fontsize=16, fontweight='bold')
    
    # Use 10th percentile as minimum and 100 as max for display
    score_min = df['smart_score'].quantile(0.10)
    score_max = 100
    
    # Distribution
    axes[0, 0].hist(df['smart_score'], bins=30, edgecolor='black', alpha=0.7, color='purple')
    axes[0, 0].axvline(df['smart_score'].mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {df["smart_score"].mean():.1f}')
    axes[0, 0].set_xlabel('Smart Score', fontsize=12)
    axes[0, 0].set_ylabel('Number of Traders', fontsize=12)
    axes[0, 0].set_title('Smart Score Distribution')
    axes[0, 0].set_xlim(score_min - 2, score_max + 2)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Smart Score vs Win Rate
    corr_score_winrate = df['smart_score'].corr(df['win_rate'])
    axes[0, 1].scatter(df['smart_score'], df['win_rate'], alpha=0.5, s=30)
    z = np.polyfit(df['smart_score'], df['win_rate'], 1)
    p = np.poly1d(z)
    axes[0, 1].plot(df['smart_score'].sort_values(), p(df['smart_score'].sort_values()), 
                    "r--", linewidth=2, label=f'Correlation: {corr_score_winrate:.3f}')
    axes[0, 1].set_xlabel('Smart Score', fontsize=12)
    axes[0, 1].set_ylabel('Win Rate', fontsize=12)
    axes[0, 1].set_title('Smart Score vs Win Rate')
    axes[0, 1].set_xlim(score_min - 2, score_max + 2)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Smart Score vs PnL (remove extreme outliers)
    pnl_threshold = df['total_pnl'].quantile(0.995)
    df_pnl_filtered = df[df['total_pnl'] <= pnl_threshold]
    corr_score_pnl = df['smart_score'].corr(df['total_pnl'])
    
    axes[1, 0].scatter(df_pnl_filtered['smart_score'], df_pnl_filtered['total_pnl'], 
                       alpha=0.5, s=30, color='green')
    z = np.polyfit(df_pnl_filtered['smart_score'], df_pnl_filtered['total_pnl'], 1)
    p = np.poly1d(z)
    axes[1, 0].plot(df_pnl_filtered['smart_score'].sort_values(), 
                    p(df_pnl_filtered['smart_score'].sort_values()), 
                    "r--", linewidth=2, label=f'Correlation: {corr_score_pnl:.3f}')
    axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=1)
    axes[1, 0].set_xlabel('Smart Score', fontsize=12)
    axes[1, 0].set_ylabel('Total PnL ($)', fontsize=12)
    axes[1, 0].set_title('Smart Score vs Total PnL (top 0.5% excluded)')
    axes[1, 0].set_xlim(score_min - 2, score_max + 2)
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Performance by Smart Score Quartile
    df_temp = df.copy()
    df_temp['score_quartile'] = pd.qcut(df_temp['smart_score'], q=4, 
                                         labels=['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'])
    quartile_winrates = df_temp.groupby('score_quartile')['win_rate'].mean()
    axes[1, 1].bar(quartile_winrates.index, quartile_winrates.values, 
                   color=['red', 'orange', 'lightgreen', 'darkgreen'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 1].set_xlabel('Smart Score Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Average Win Rate', fontsize=12)
    axes[1, 1].set_title('Win Rate by Smart Score Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    # Calculate correlations with statistical significance
    r_winrate, p_winrate = pearsonr(df['smart_score'], df['win_rate'])
    r_pnl, p_pnl = pearsonr(df['smart_score'], df['total_pnl'])
    
    correlations = {
        'smart_score_vs_winrate': {
            'correlation': r_winrate,
            'p_value': p_winrate,
            'significant': p_winrate < 0.05
        },
        'smart_score_vs_pnl': {
            'correlation': r_pnl,
            'p_value': p_pnl,
            'significant': p_pnl < 0.05
        }
    }
    
    return fig, correlations


def get_performance_summary(df):
    summary = {
        'win_rate': {
            'mean': df['win_rate'].mean(),
            'median': df['win_rate'].median(),
            'std': df['win_rate'].std(),
            'min': df['win_rate'].min(),
            'max': df['win_rate'].max()
        },
        'smart_score': {
            'mean': df['smart_score'].mean(),
            'median': df['smart_score'].median(),
            'std': df['smart_score'].std(),
            'min': df['smart_score'].min(),
            'max': df['smart_score'].max()
        },
        'total_traders': len(df),
        'profitable_traders': (df['total_pnl'] > 0).sum(),
        'profitable_percentage': (df['total_pnl'] > 0).sum() / len(df) * 100
    }
    
    return summary

