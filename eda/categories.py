"""
Category Performance Analysis Functions

Reusable plotting functions for analyzing trading performance across categories:
- Category trading volumes
- Category-specific win rates
- Specialization analysis

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Define category features
CATEGORY_VOLUME_COLS = [
    'most_traded_categories_politics', 'most_traded_categories_sport',
    'most_traded_categories_music', 'most_traded_categories_crypto',
    'most_traded_categories_mentions', 'most_traded_categories_weather',
    'most_traded_categories_culture', 'most_traded_categories_other'
]

CATEGORY_WINRATE_COLS = [
    'win_rate_categories_politics', 'win_rate_categories_sport',
    'win_rate_categories_music', 'win_rate_categories_crypto'
]


def plot_category_volumes(df, figsize=(16, 6), save=False, path=None):
    """
    Plot trading volume distribution across categories.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing category volume columns
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
    volumes : pd.Series
        Series containing category volumes
    """
    # Calculate total volume per category
    category_volumes = df[CATEGORY_VOLUME_COLS].sum()
    category_volumes.index = [col.replace('most_traded_categories_', '').title() 
                               for col in category_volumes.index]
    category_volumes = category_volumes.sort_values(ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('Category Trading Volume Analysis', fontsize=16, fontweight='bold')
    
    # Bar chart
    colors = plt.cm.Set3(range(len(category_volumes)))
    axes[0].bar(category_volumes.index, category_volumes.values, color=colors, 
                edgecolor='black', alpha=0.8)
    axes[0].set_xlabel('Category', fontsize=12)
    axes[0].set_ylabel('Total Trading Volume', fontsize=12)
    axes[0].set_title('Trading Volume by Category')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Pie chart
    axes[1].pie(category_volumes.values, labels=category_volumes.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
    axes[1].set_title('Market Share by Category')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, category_volumes


def plot_category_winrates(df, figsize=(16, 12), save=False, path=None):
    """
    Plot win rate distributions for each category.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing category win rate columns
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
    stats : dict
        Dictionary containing win rate statistics by category
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Win Rate Distribution by Category', fontsize=16, fontweight='bold')
    
    colors = plt.cm.Set3(range(4))
    stats = {}
    
    for idx, col in enumerate(CATEGORY_WINRATE_COLS):
        ax = axes[idx // 2, idx % 2]
        cat_name = col.replace('win_rate_categories_', '').title()
        valid_data = df[col][(df[col] > 0) & (df[col].notna())]
        
        if len(valid_data) > 0:
            ax.hist(valid_data, bins=30, edgecolor='black', alpha=0.7, color=colors[idx])
            ax.axvline(valid_data.mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {valid_data.mean():.2%}')
            ax.set_xlabel('Win Rate', fontsize=11)
            ax.set_ylabel('Number of Traders', fontsize=11)
            ax.set_title(f'{cat_name} Win Rate Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            stats[cat_name] = {
                'mean': valid_data.mean(),
                'median': valid_data.median(),
                'std': valid_data.std(),
                'count': len(valid_data)
            }
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, stats


def plot_specialization_analysis(df, figsize=(12, 7), save=False, path=None):
    """
    Plot category diversification distribution.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing category volume columns
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
    specialization_stats : dict
        Dictionary containing specialization statistics
    """
    # Count number of categories each trader participates in
    df_temp = df.copy()
    df_temp['num_categories'] = (df_temp[CATEGORY_VOLUME_COLS] > 0).sum(axis=1)
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Category Specialization Analysis', fontsize=16, fontweight='bold')
    
    # Number of categories distribution
    ax.hist(df_temp['num_categories'], bins=range(1, df_temp['num_categories'].max()+2), 
            edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel('Number of Categories Traded', fontsize=12)
    ax.set_ylabel('Number of Traders', fontsize=12)
    ax.set_title('Distribution of Category Diversification')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    # Calculate specialization statistics
    specialists = df_temp[df_temp['num_categories'] <= 2]
    generalists = df_temp[df_temp['num_categories'] >= 5]
    moderate = df_temp[(df_temp['num_categories'] > 2) & (df_temp['num_categories'] < 5)]
    
    specialization_stats = {
        'avg_categories': df_temp['num_categories'].mean(),
        'median_categories': df_temp['num_categories'].median(),
        'specialists_count': len(specialists),
        'specialists_pct': len(specialists) / len(df_temp) * 100,
        'moderate_count': len(moderate),
        'moderate_pct': len(moderate) / len(df_temp) * 100,
        'generalists_count': len(generalists),
        'generalists_pct': len(generalists) / len(df_temp) * 100,
        'specialists_avg_winrate': specialists['win_rate'].mean() if len(specialists) > 0 else None,
        'generalists_avg_winrate': generalists['win_rate'].mean() if len(generalists) > 0 else None
    }
    
    return fig, specialization_stats


def get_category_summary(df):
    """
    Get a comprehensive summary of category performance.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing category columns
    
    Returns:
    --------
    summary : dict
        Dictionary containing category summary statistics
    """
    # Most popular category
    category_volumes = df[CATEGORY_VOLUME_COLS].sum()
    category_volumes.index = [col.replace('most_traded_categories_', '').title() 
                               for col in category_volumes.index]
    most_popular = category_volumes.idxmax()
    
    # Category win rates
    category_winrates = {}
    for col in CATEGORY_WINRATE_COLS:
        cat_name = col.replace('win_rate_categories_', '').title()
        valid_data = df[col][(df[col] > 0) & (df[col].notna())]
        if len(valid_data) > 0:
            category_winrates[cat_name] = valid_data.mean()
    
    best_category = max(category_winrates.items(), key=lambda x: x[1]) if category_winrates else (None, None)
    
    summary = {
        'most_popular_category': most_popular,
        'most_popular_volume': category_volumes[most_popular],
        'best_performing_category': best_category[0],
        'best_category_winrate': best_category[1],
        'total_volume': category_volumes.sum(),
        'avg_categories_per_trader': (df[CATEGORY_VOLUME_COLS] > 0).sum(axis=1).mean()
    }
    
    return summary

