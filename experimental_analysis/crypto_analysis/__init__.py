import pandas as pd
import os

from . import performance
from . import risk
from . import trader_types

from .performance import (
    plot_crypto_win_rate_distribution,
    plot_crypto_smart_score_analysis,
    plot_crypto_vs_overall_performance,
    get_crypto_performance_summary
)

from .risk import (
    plot_crypto_betting_probability_distribution,
    plot_crypto_winrate_by_probability_range,
    get_crypto_risk_behavior_summary
)

from .trader_types import (
    plot_crypto_trader_type_prevalence,
    plot_crypto_performance_by_type,
    plot_crypto_type_cooccurrence,
    get_crypto_trader_type_summary
)

__version__ = '1.0.0'
__author__ = 'Ąžuolas Saulius Balbieris'

__all__ = [
    'performance',
    'risk',
    'trader_types',
    'plot_crypto_win_rate_distribution',
    'plot_crypto_smart_score_analysis',
    'plot_crypto_vs_overall_performance',
    'get_crypto_performance_summary',
    'plot_crypto_betting_probability_distribution',
    'plot_crypto_winrate_by_probability_range',
    'get_crypto_risk_behavior_summary',
    'plot_crypto_trader_type_prevalence',
    'plot_crypto_performance_by_type',
    'plot_crypto_type_cooccurrence',
    'get_crypto_trader_type_summary',
    'plot_all_crypto_performance',
    'plot_all_crypto_risk',
    'plot_all_crypto_trader_types',
    'generate_crypto_report',
    'filter_crypto_traders'
]


def filter_crypto_traders(df, min_crypto_volume=0, min_crypto_winrate_data=False):
    df_crypto = df[df['most_traded_categories_crypto'] > min_crypto_volume].copy()
    
    if min_crypto_winrate_data:
        df_crypto = df_crypto[df_crypto['win_rate_categories_crypto'].notna() & 
                              (df_crypto['win_rate_categories_crypto'] > 0)]
    
    return df_crypto


def plot_all_crypto_performance(df, save=False, output_dir=None):
    figures = {}
    
    print("Generating crypto performance plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/crypto_win_rate_distribution.png"
        path2 = f"{output_dir}/crypto_smart_score_analysis.png"
        path3 = f"{output_dir}/crypto_vs_overall_performance.png"
    else:
        path1 = path2 = path3 = None
    
    fig1, stats1 = plot_crypto_win_rate_distribution(df, save=save, path=path1)
    fig2, stats2 = plot_crypto_smart_score_analysis(df, save=save, path=path2)
    fig3, stats3 = plot_crypto_vs_overall_performance(df, save=save, path=path3)
    
    figures['win_rate'] = fig1
    figures['smart_score'] = fig2
    figures['vs_overall'] = fig3
    
    print("Crypto performance plots complete")
    return figures


def plot_all_crypto_risk(df, save=False, output_dir=None):
    figures = {}
    
    print("Generating crypto risk behavior plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/crypto_betting_probability_distribution.png"
        path2 = f"{output_dir}/crypto_winrate_by_probability_range.png"
    else:
        path1 = path2 = None
    
    fig1, _ = plot_crypto_betting_probability_distribution(df, save=save, path=path1)
    fig2, _ = plot_crypto_winrate_by_probability_range(df, save=save, path=path2)
    
    figures['distribution'] = fig1
    figures['winrate_by_range'] = fig2
    
    print("Crypto risk behavior plots complete")
    return figures


def plot_all_crypto_trader_types(df, save=False, output_dir=None):
    figures = {}
    
    print("Generating crypto trader type plots...")
    
    if save and output_dir:
        path1 = f"{output_dir}/crypto_trader_type_prevalence.png"
        path2 = f"{output_dir}/crypto_performance_by_type.png"
        path3 = f"{output_dir}/crypto_type_cooccurrence.png"
    else:
        path1 = path2 = path3 = None
    
    fig1, _ = plot_crypto_trader_type_prevalence(df, save=save, path=path1)
    fig2, _ = plot_crypto_performance_by_type(df, save=save, path=path2)
    fig3, _ = plot_crypto_type_cooccurrence(df, save=save, path=path3)
    
    figures['prevalence'] = fig1
    figures['performance'] = fig2
    figures['cooccurrence'] = fig3
    
    print("Crypto trader type plots complete")
    return figures


def generate_crypto_report(df, save=False, output_dir='crypto_analysis/data'):
    if save:
        os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("GENERATING CRYPTO TRADER ANALYSIS REPORT")
    print("="*80)
    
    df_crypto = filter_crypto_traders(df, min_crypto_volume=0)
    print(f"Analyzing {len(df_crypto)} crypto traders")
    
    report = {
        'performance': plot_all_crypto_performance(df_crypto, save=save, output_dir=output_dir),
        'risk': plot_all_crypto_risk(df_crypto, save=save, output_dir=output_dir),
        'trader_types': plot_all_crypto_trader_types(df_crypto, save=save, output_dir=output_dir),
        'summaries': {
            'performance': get_crypto_performance_summary(df_crypto),
            'risk': get_crypto_risk_behavior_summary(df_crypto),
            'trader_types': get_crypto_trader_type_summary(df_crypto)
        }
    }
    
    print("\n" + "="*80)
    print("CRYPTO REPORT GENERATION COMPLETE")
    print("="*80)
    
    if save:
        print(f"\nAll figures saved to: {output_dir}/")
    
    return report

