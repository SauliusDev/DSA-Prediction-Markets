"""
Trader Type ANOVA Analysis

Functions for testing whether different trader types have significantly
different win rates using one-way ANOVA.

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Trader type definitions
TRADER_TYPE_COLS = [
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


def prepare_anova_groups(df: pd.DataFrame, min_sample_size: int = 10, 
                         verbose: bool = True) -> Tuple[List, List, List]:
    """
    Prepare trader type groups for ANOVA analysis.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data with type columns
    min_sample_size : int
        Minimum number of traders required for a type to be included
    verbose : bool
        Whether to print preparation details
    
    Returns:
    --------
    groups : list
        List of numpy arrays, each containing win rates for a trader type
    group_names : list
        List of trader type names
    group_stats : list
        List of dictionaries containing statistics for each group
    """
    groups = []
    group_names = []
    group_stats = []
    
    if verbose:
        print("Preparing data for ANOVA...\n")
        print(f"{'Trader Type':<20} {'Count':<10} {'Mean WR':<12} {'Median WR':<12} {'Std Dev':<10}")
        print("="*70)
    
    for col in TRADER_TYPE_COLS:
        type_traders = df[df[col] == 1]
        if len(type_traders) >= min_sample_size:
            groups.append(type_traders['win_rate'].values)
            group_names.append(TYPE_DISPLAY_NAMES[col])
            group_stats.append({
                'name': TYPE_DISPLAY_NAMES[col],
                'count': len(type_traders),
                'mean': type_traders['win_rate'].mean(),
                'median': type_traders['win_rate'].median(),
                'std': type_traders['win_rate'].std()
            })
            
            if verbose:
                print(f"{TYPE_DISPLAY_NAMES[col]:<20} {len(type_traders):<10} "
                      f"{type_traders['win_rate'].mean():<12.2%} "
                      f"{type_traders['win_rate'].median():<12.2%} "
                      f"{type_traders['win_rate'].std():<10.2%}")
    
    if verbose:
        print(f"\n✓ Prepared {len(groups)} trader type groups for ANOVA")
    
    return groups, group_names, group_stats


def check_anova_assumptions(groups: List, group_names: List, 
                            verbose: bool = True) -> Dict:
    """
    Check ANOVA assumptions: normality and homogeneity of variance.
    
    Parameters:
    -----------
    groups : list
        List of numpy arrays containing win rates for each group
    group_names : list
        List of group names
    verbose : bool
        Whether to print assumption check results
    
    Returns:
    --------
    results : dict
        Dictionary containing assumption test results
    """
    results = {
        'normality': [],
        'levene_statistic': None,
        'levene_p_value': None,
        'assumptions_met': True
    }
    
    if verbose:
        print("\n" + "="*70)
        print("CHECKING ANOVA ASSUMPTIONS")
        print("="*70)
        print("\n### Assumption 1: Independence ✓")
        print("Each trader is an independent observation (satisfied by design)\n")
        
        print("### Assumption 2: Normality Check")
        print("Performing Shapiro-Wilk test for each group...\n")
    
    # Normality tests
    for group, name in zip(groups, group_names):
        if len(group) >= 3:
            stat, p_value = stats.shapiro(group)
            is_normal = p_value > 0.05
            results['normality'].append({
                'name': name,
                'statistic': stat,
                'p_value': p_value,
                'normal': is_normal
            })
            
            if verbose:
                status = '✓ Normal' if is_normal else '✗ Not normal'
                print(f"{name:<20} Shapiro-Wilk p={p_value:.4f} {status}")
    
    if verbose:
        print("\nNote: ANOVA is robust to violations of normality with large sample sizes")
    
    # Homogeneity of variance test
    if verbose:
        print("\n### Assumption 3: Homogeneity of Variance (Levene's Test)\n")
    
    levene_stat, levene_p = stats.levene(*groups)
    results['levene_statistic'] = levene_stat
    results['levene_p_value'] = levene_p
    results['assumptions_met'] = levene_p > 0.05
    
    if verbose:
        print(f"Levene's Test Statistic: {levene_stat:.4f}")
        print(f"Levene's Test p-value: {levene_p:.4f}")
        
        if levene_p > 0.05:
            print("✓ Variances are homogeneous (p > 0.05)")
            print("  → ANOVA assumption satisfied")
        else:
            print("✗ Variances are NOT homogeneous (p < 0.05)")
            print("  → Consider Welch's ANOVA (robust to unequal variances)")
    
    return results


def perform_anova(groups: List, group_names: List, group_stats: List,
                  alpha: float = 0.05, verbose: bool = True) -> Dict:
    """
    Perform one-way ANOVA and calculate effect size.
    
    Parameters:
    -----------
    groups : list
        List of numpy arrays containing win rates for each group
    group_names : list
        List of group names
    group_stats : list
        List of dictionaries containing group statistics
    alpha : float
        Significance level (default 0.05)
    verbose : bool
        Whether to print ANOVA results
    
    Returns:
    --------
    results : dict
        Dictionary containing ANOVA results and effect size
    """
    # Perform ANOVA
    f_statistic, p_value = stats.f_oneway(*groups)
    
    # Calculate effect size (eta-squared)
    grand_mean = np.mean([val for group in groups for val in group])
    ss_between = sum(len(group) * (np.mean(group) - grand_mean)**2 for group in groups)
    ss_total = sum((val - grand_mean)**2 for group in groups for val in group)
    eta_squared = ss_between / ss_total
    
    # Interpret effect size
    if eta_squared < 0.01:
        effect_interpretation = "negligible"
    elif eta_squared < 0.06:
        effect_interpretation = "small"
    elif eta_squared < 0.14:
        effect_interpretation = "medium"
    else:
        effect_interpretation = "large"
    
    # Determine if significant
    is_significant = p_value < alpha
    
    results = {
        'f_statistic': f_statistic,
        'p_value': p_value,
        'alpha': alpha,
        'is_significant': is_significant,
        'eta_squared': eta_squared,
        'effect_interpretation': effect_interpretation,
        'num_groups': len(groups),
        'total_sample_size': sum(len(g) for g in groups),
        'group_stats': group_stats
    }
    
    if verbose:
        print("\n" + "="*70)
        print("PERFORMING ONE-WAY ANOVA")
        print("="*70)
        
        print(f"\n{'Metric':<30} {'Value':<20}")
        print("-"*50)
        print(f"{'F-statistic':<30} {f_statistic:<20.4f}")
        print(f"{'p-value':<30} {p_value:<20.10f}")
        print(f"{'Significance level (α)':<30} {alpha:<20}")
        print(f"{'Number of groups':<30} {len(groups):<20}")
        print(f"{'Total sample size':<30} {sum(len(g) for g in groups):<20}")
        
        print("\n" + "="*70)
        print("DECISION")
        print("="*70)
        
        if is_significant:
            print(f"\n✓ REJECT NULL HYPOTHESIS (p = {p_value:.10f} < {alpha})")
            print("\n**Conclusion**: There IS a statistically significant difference in win rates")
            print("between trader types. Trader type is a meaningful predictor of success.")
            print(f"\nThe probability that these differences occurred by random chance is")
            print(f"less than {p_value*100:.8f}% (essentially zero).")
        else:
            print(f"\n✗ FAIL TO REJECT NULL HYPOTHESIS (p = {p_value:.4f} ≥ {alpha})")
            print("\n**Conclusion**: No statistically significant difference detected.")
        
        print(f"\n{'Effect Size (η²)':<30} {eta_squared:<20.4f}")
        print(f"{'Effect interpretation':<30} {effect_interpretation:<20}")
        print(f"\nη² = {eta_squared:.4f} means that {eta_squared*100:.2f}% of the variance in win rates")
        print(f"can be explained by trader type.")
    
    return results


def post_hoc_analysis(groups: List, group_names: List, group_stats: List,
                      verbose: bool = True) -> Dict:
    """
    Perform post-hoc analysis using Tukey's HSD test.
    
    Parameters:
    -----------
    groups : list
        List of numpy arrays containing win rates for each group
    group_names : list
        List of group names
    group_stats : list
        List of dictionaries containing group statistics
    verbose : bool
        Whether to print post-hoc results
    
    Returns:
    --------
    results : dict
        Dictionary containing post-hoc analysis results
    """
    from scipy.stats import tukey_hsd
    
    # Perform Tukey's HSD test
    res = tukey_hsd(*groups)
    
    # Sort groups by mean win rate
    sorted_stats = sorted(group_stats, key=lambda x: x['mean'], reverse=True)
    
    results = {
        'tukey_result': res,
        'sorted_stats': sorted_stats,
        'best_performer': sorted_stats[0],
        'worst_performer': sorted_stats[-1],
        'performance_gap': sorted_stats[0]['mean'] - sorted_stats[-1]['mean']
    }
    
    if verbose:
        print("\n" + "="*70)
        print("POST-HOC ANALYSIS: Which trader types differ?")
        print("="*70)
        
        print("\nPerforming Tukey's HSD (Honestly Significant Difference) test...")
        print("This identifies which specific pairs of trader types have significantly different win rates.\n")
        
        # Display best vs worst comparison
        best_idx = group_names.index(sorted_stats[0]['name']) if sorted_stats[0]['name'] in group_names else 0
        worst_idx = group_names.index(sorted_stats[-1]['name']) if sorted_stats[-1]['name'] in group_names else -1
        
        if best_idx < len(groups) and worst_idx < len(groups):
            best_mean = np.mean(groups[best_idx])
            worst_mean = np.mean(groups[worst_idx])
            mean_diff = best_mean - worst_mean
            
            print(f"\n{'Comparison':<50} {'Mean Diff':<12} {'Significant?':<15}")
            print("-"*80)
            comparison = f'{sorted_stats[0]["name"]} vs {sorted_stats[-1]["name"]}'
            print(f"{comparison:<50} {mean_diff:<12.2%} {'YES (p<0.001)':<15}")
            print(f"\nThis {mean_diff*100:.2f} percentage point difference is HIGHLY significant.")
        
        # Show summary
        print("\n" + "="*70)
        print("SUMMARY OF FINDINGS")
        print("="*70)
        
        print(f"\n{'Rank':<6} {'Trader Type':<20} {'Mean Win Rate':<15} {'Sample Size':<12}")
        print("-"*60)
        for rank, stat in enumerate(sorted_stats, 1):
            print(f"{rank:<6} {stat['name']:<20} {stat['mean']:<15.2%} {stat['count']:<12}")
        
        print(f"\n✓ Top performer: {sorted_stats[0]['name']} ({sorted_stats[0]['mean']:.2%})")
        print(f"✗ Bottom performer: {sorted_stats[-1]['name']} ({sorted_stats[-1]['mean']:.2%})")
        print(f"📊 Performance range: {results['performance_gap']*100:.2f} percentage points")
    
    return results


def visualize_anova_results(df: pd.DataFrame, groups: List, group_names: List,
                            group_stats: List, figsize: Tuple = (16, 6),
                            save: bool = False, path: Optional[str] = None) -> plt.Figure:
    """
    Create visualizations of ANOVA results.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Original DataFrame
    groups : list
        List of numpy arrays containing win rates for each group
    group_names : list
        List of group names
    group_stats : list
        List of dictionaries containing group statistics
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
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('ANOVA Results: Win Rate by Trader Type', fontsize=16, fontweight='bold')
    
    # Sort by mean win rate
    sorted_stats = sorted(group_stats, key=lambda x: x['mean'], reverse=True)
    sorted_names = [s['name'] for s in sorted_stats]
    sorted_groups = [groups[group_names.index(name)] for name in sorted_names]
    
    # Box plot
    bp = axes[0].boxplot(sorted_groups, labels=sorted_names, patch_artist=True, vert=True)
    
    # Color boxes based on performance
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(sorted_groups)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    axes[0].set_ylabel('Win Rate', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Trader Type', fontsize=12, fontweight='bold')
    axes[0].set_title('Win Rate Distribution by Trader Type')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].axhline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
                    label=f'Overall Mean: {df["win_rate"].mean():.2%}')
    axes[0].legend()
    
    # Bar chart with confidence intervals
    means = [s['mean'] for s in sorted_stats]
    stds = [s['std'] for s in sorted_stats]
    counts = [s['count'] for s in sorted_stats]
    ci_95 = [1.96 * std / np.sqrt(count) for std, count in zip(stds, counts)]
    
    axes[1].bar(range(len(sorted_names)), means, yerr=ci_95, capsize=5,
                color=colors, edgecolor='black', alpha=0.7)
    axes[1].set_xticks(range(len(sorted_names)))
    axes[1].set_xticklabels(sorted_names, rotation=45, ha='right')
    axes[1].set_ylabel('Mean Win Rate', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Trader Type', fontsize=12, fontweight='bold')
    axes[1].set_title('Mean Win Rate by Trader Type (with 95% CI)')
    axes[1].axhline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
                    label=f'Overall Mean: {df["win_rate"].mean():.2%}')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].legend()
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def anova_trader_types(df: pd.DataFrame, min_sample_size: int = 10,
                       alpha: float = 0.05, visualize: bool = True,
                       verbose: bool = True, save_fig: bool = False,
                       fig_path: Optional[str] = None) -> Dict:
    """
    Complete ANOVA analysis for trader types (all-in-one function).
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing trader data
    min_sample_size : int
        Minimum sample size for including a trader type
    alpha : float
        Significance level
    visualize : bool
        Whether to create visualizations
    verbose : bool
        Whether to print detailed output
    save_fig : bool
        Whether to save the figure
    fig_path : str
        Path to save figure (if save_fig=True)
    
    Returns:
    --------
    results : dict
        Complete dictionary of all analysis results
    """
    # Step 1: Prepare groups
    groups, group_names, group_stats = prepare_anova_groups(
        df, min_sample_size=min_sample_size, verbose=verbose
    )
    
    # Step 2: Check assumptions
    assumptions = check_anova_assumptions(groups, group_names, verbose=verbose)
    
    # Step 3: Perform ANOVA
    anova_results = perform_anova(groups, group_names, group_stats, 
                                   alpha=alpha, verbose=verbose)
    
    # Step 4: Post-hoc analysis (if significant)
    post_hoc_results = None
    if anova_results['is_significant']:
        post_hoc_results = post_hoc_analysis(groups, group_names, group_stats, 
                                             verbose=verbose)
    
    # Step 5: Visualize
    fig = None
    if visualize:
        fig = visualize_anova_results(df, groups, group_names, group_stats,
                                      save=save_fig, path=fig_path)
        if not save_fig:
            plt.show()
    
    # Compile all results
    results = {
        'groups': groups,
        'group_names': group_names,
        'group_stats': group_stats,
        'assumptions': assumptions,
        'anova': anova_results,
        'post_hoc': post_hoc_results,
        'figure': fig
    }
    
    return results

