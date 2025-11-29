"""
EDA Module for Polymarket Trader Analysis

This module provides reusable plotting functions for exploratory data analysis
of Polymarket trader behavior, performance, and risk profiles.

Usage:
------
```python
import pandas as pd
from eda import performance, categories, trader_types, risk

# Load data
df = pd.read_csv('data/users_data.csv')

# Generate plots
fig, stats = performance.plot_win_rate_distribution(df)
fig.show()

# Or use convenience function
from eda import plot_all_performance
plot_all_performance(df)
```

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

# Import main modules
from . import performance
from . import categories
from . import trader_types
from . import risk

# Import key functions for convenience
from .performance import (
    plot_win_rate_distribution,
    plot_smart_score_analysis,
    get_performance_summary
)

from .categories import (
    plot_category_volumes,
    plot_category_winrates,
    plot_specialization_analysis,
    get_category_summary
)

from .trader_types import (
    plot_trader_type_prevalence,
    plot_performance_by_type,
    plot_type_cooccurrence,
    get_trader_type_summary
)

from .risk import (
    plot_betting_probability_distribution,
    plot_winrate_by_probability_range,
    get_risk_behavior_summary
)

__version__ = '1.0.0'
__author__ = 'Ąžuolas Saulius Balbieris'

__all__ = [
    # Modules
    'performance',
    'categories',
    'trader_types',
    'risk',
    
    # Performance functions
    'plot_win_rate_distribution',
    'plot_smart_score_analysis',
    'get_performance_summary',
    
    # Category functions
    'plot_category_volumes',
    'plot_category_winrates',
    'plot_specialization_analysis',
    'get_category_summary',
    
    # Trader type functions
    'plot_trader_type_prevalence',
    'plot_performance_by_type',
    'plot_type_cooccurrence',
    'get_trader_type_summary',
    
    # Risk functions
    'plot_betting_probability_distribution',
    'plot_winrate_by_probability_range',
    'get_risk_behavior_summary',
    
    # Convenience functions
    'plot_all_performance',
    'plot_all_categories',
    'plot_all_trader_types',
    'plot_all_risk',
    'generate_full_report'
]


def plot_all_performance(df, save=False, output_dir=None):
    """
    Generate all performance-related plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    save : bool
        Whether to save figures
    output_dir : str
        Directory to save figures (if save=True)
    
    Returns:
    --------
    figures : dict
        Dictionary of figure objects
    """
    figures = {}
    
    print("Generating performance plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/win_rate_distribution.png"
        path2 = f"{output_dir}/smart_score_analysis.png"
    else:
        path1 = path2 = None
    
    fig1, stats1 = plot_win_rate_distribution(df, save=save, path=path1)
    fig2, stats2 = plot_smart_score_analysis(df, save=save, path=path2)
    
    figures['win_rate'] = fig1
    figures['smart_score'] = fig2
    
    print("✓ Performance plots complete")
    return figures


def plot_all_categories(df, save=False, output_dir=None):
    """
    Generate all category-related plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    save : bool
        Whether to save figures
    output_dir : str
        Directory to save figures (if save=True)
    
    Returns:
    --------
    figures : dict
        Dictionary of figure objects
    """
    figures = {}
    
    print("Generating category plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/category_volumes.png"
        path2 = f"{output_dir}/category_winrates.png"
        path3 = f"{output_dir}/specialization_analysis.png"
    else:
        path1 = path2 = path3 = None
    
    fig1, _ = plot_category_volumes(df, save=save, path=path1)
    fig2, _ = plot_category_winrates(df, save=save, path=path2)
    fig3, _ = plot_specialization_analysis(df, save=save, path=path3)
    
    figures['volumes'] = fig1
    figures['winrates'] = fig2
    figures['specialization'] = fig3
    
    print("✓ Category plots complete")
    return figures


def plot_all_trader_types(df, save=False, output_dir=None):
    """
    Generate all trader type plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    save : bool
        Whether to save figures
    output_dir : str
        Directory to save figures (if save=True)
    
    Returns:
    --------
    figures : dict
        Dictionary of figure objects
    """
    figures = {}
    
    print("Generating trader type plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/trader_type_prevalence.png"
        path2 = f"{output_dir}/performance_by_type.png"
        path3 = f"{output_dir}/type_cooccurrence.png"
    else:
        path1 = path2 = path3 = None
    
    fig1, _ = plot_trader_type_prevalence(df, save=save, path=path1)
    fig2, _ = plot_performance_by_type(df, save=save, path=path2)
    fig3, _ = plot_type_cooccurrence(df, save=save, path=path3)
    
    figures['prevalence'] = fig1
    figures['performance'] = fig2
    figures['cooccurrence'] = fig3
    
    print("✓ Trader type plots complete")
    return figures


def plot_all_risk(df, save=False, output_dir=None):
    """
    Generate all risk behavior plots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    save : bool
        Whether to save figures
    output_dir : str
        Directory to save figures (if save=True)
    
    Returns:
    --------
    figures : dict
        Dictionary of figure objects
    """
    figures = {}
    
    print("Generating risk behavior plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/betting_probability_distribution.png"
        path2 = f"{output_dir}/winrate_by_probability_range.png"
    else:
        path1 = path2 = None
    
    fig1, _ = plot_betting_probability_distribution(df, save=save, path=path1)
    fig2, _ = plot_winrate_by_probability_range(df, save=save, path=path2)
    
    figures['distribution'] = fig1
    figures['winrate_by_range'] = fig2
    
    print("✓ Risk behavior plots complete")
    return figures


def generate_full_report(df, save=False, output_dir='eda/visualizations/report'):
    """
    Generate all EDA plots and summaries.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    save : bool
        Whether to save figures
    output_dir : str
        Directory to save figures (if save=True)
    
    Returns:
    --------
    report : dict
        Dictionary containing all figures and summaries
    """
    import os
    if save:
        os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("GENERATING FULL EDA REPORT")
    print("="*80)
    
    report = {
        'performance': plot_all_performance(df, save=save, output_dir=output_dir),
        'categories': plot_all_categories(df, save=save, output_dir=output_dir),
        'trader_types': plot_all_trader_types(df, save=save, output_dir=output_dir),
        'risk': plot_all_risk(df, save=save, output_dir=output_dir),
        'summaries': {
            'performance': get_performance_summary(df),
            'categories': get_category_summary(df),
            'trader_types': get_trader_type_summary(df),
            'risk': get_risk_behavior_summary(df)
        }
    }
    
    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE")
    print("="*80)
    
    if save:
        print(f"\nAll figures saved to: {output_dir}/")
    
    return report

