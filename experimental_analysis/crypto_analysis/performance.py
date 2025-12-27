import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, ttest_ind
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def filter_crypto_traders(df, min_volume=0):
    return df[df['most_traded_categories_crypto'] > min_volume].copy()


def plot_crypto_win_rate_distribution(df, figsize=(18, 5), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    crypto_winrates = df_crypto['win_rate_categories_crypto']
    crypto_winrates = crypto_winrates[(crypto_winrates > 0) & (crypto_winrates.notna())]
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle('Crypto Trader Win Rate Distribution', fontsize=16, fontweight='bold')
    
    axes[0].hist(crypto_winrates, bins=40, edgecolor='black', alpha=0.7, color='#F7931A')
    axes[0].axvline(crypto_winrates.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {crypto_winrates.mean():.2%}')
    axes[0].axvline(crypto_winrates.median(), color='green', linestyle='--', linewidth=2, 
                    label=f'Median: {crypto_winrates.median():.2%}')
    axes[0].set_xlabel('Win Rate', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('Crypto Win Rate Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    box = axes[1].boxplot(crypto_winrates.dropna(), vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#F7931A')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Win Rate', fontsize=12)
    axes[1].set_title('Crypto Win Rate Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    crypto_winrates.plot(kind='density', ax=axes[2], color='#F7931A', linewidth=2)
    axes[2].axvline(crypto_winrates.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {crypto_winrates.mean():.2%}')
    axes[2].set_xlabel('Win Rate', fontsize=12)
    axes[2].set_ylabel('Density', fontsize=12)
    axes[2].set_title('Crypto Win Rate Density Plot')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    stats = {
        'mean': crypto_winrates.mean(),
        'median': crypto_winrates.median(),
        'std': crypto_winrates.std(),
        'min': crypto_winrates.min(),
        'max': crypto_winrates.max(),
        'q1': crypto_winrates.quantile(0.25),
        'q3': crypto_winrates.quantile(0.75),
        'count': len(crypto_winrates)
    }
    
    return fig, stats


def plot_crypto_smart_score_analysis(df, figsize=(16, 12), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Crypto Trader Smart Score Analysis', fontsize=16, fontweight='bold')
    
    crypto_scores = df_crypto['smart_score_categories_crypto']
    crypto_scores_valid = crypto_scores[crypto_scores.notna()]
    
    axes[0, 0].hist(crypto_scores_valid, bins=30, edgecolor='black', alpha=0.7, color='#F7931A')
    axes[0, 0].axvline(crypto_scores_valid.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {crypto_scores_valid.mean():.1f}')
    axes[0, 0].set_xlabel('Crypto Smart Score', fontsize=12)
    axes[0, 0].set_ylabel('Number of Traders', fontsize=12)
    axes[0, 0].set_title('Crypto Smart Score Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    crypto_winrates = df_crypto['win_rate_categories_crypto']
    valid_mask = (crypto_scores.notna()) & (crypto_winrates.notna()) & (crypto_winrates > 0)
    
    if valid_mask.sum() > 10:
        corr = crypto_scores[valid_mask].corr(crypto_winrates[valid_mask])
        axes[0, 1].scatter(crypto_scores[valid_mask], crypto_winrates[valid_mask], 
                          alpha=0.5, s=30, color='#F7931A')
        z = np.polyfit(crypto_scores[valid_mask], crypto_winrates[valid_mask], 1)
        p = np.poly1d(z)
        x_sorted = crypto_scores[valid_mask].sort_values()
        axes[0, 1].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                       label=f'Correlation: {corr:.3f}')
        axes[0, 1].set_xlabel('Crypto Smart Score', fontsize=12)
        axes[0, 1].set_ylabel('Crypto Win Rate', fontsize=12)
        axes[0, 1].set_title('Crypto Smart Score vs Win Rate')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    overall_scores = df_crypto['smart_score']
    valid_mask2 = (crypto_scores.notna()) & (overall_scores.notna())
    
    if valid_mask2.sum() > 10:
        corr2 = crypto_scores[valid_mask2].corr(overall_scores[valid_mask2])
        axes[1, 0].scatter(overall_scores[valid_mask2], crypto_scores[valid_mask2], 
                          alpha=0.5, s=30, color='green')
        axes[1, 0].plot([overall_scores.min(), overall_scores.max()], 
                       [overall_scores.min(), overall_scores.max()], 
                       'k--', linewidth=1, alpha=0.5, label='y=x line')
        axes[1, 0].set_xlabel('Overall Smart Score', fontsize=12)
        axes[1, 0].set_ylabel('Crypto Smart Score', fontsize=12)
        axes[1, 0].set_title(f'Overall vs Crypto Smart Score (r={corr2:.3f})')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    df_temp = df_crypto.copy()
    df_temp['crypto_score_valid'] = df_temp['smart_score_categories_crypto'].notna()
    df_temp = df_temp[df_temp['crypto_score_valid']]
    
    if len(df_temp) > 20:
        df_temp['score_quartile'] = pd.qcut(df_temp['smart_score_categories_crypto'], q=4, 
                                            labels=['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'],
                                            duplicates='drop')
        crypto_wr = df_temp['win_rate_categories_crypto']
        valid_wr = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
        df_temp_valid = df_temp.loc[valid_wr.index]
        
        if len(df_temp_valid) > 0:
            quartile_winrates = df_temp_valid.groupby('score_quartile')['win_rate_categories_crypto'].mean()
            axes[1, 1].bar(quartile_winrates.index, quartile_winrates.values, 
                          color=['#8B0000', '#FF4500', '#90EE90', '#006400'], 
                          edgecolor='black', alpha=0.7)
            axes[1, 1].set_xlabel('Crypto Smart Score Quartile', fontsize=12)
            axes[1, 1].set_ylabel('Average Crypto Win Rate', fontsize=12)
            axes[1, 1].set_title('Crypto Win Rate by Smart Score Quartile')
            axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    correlations = {}
    if valid_mask.sum() > 10:
        r1, p1 = pearsonr(crypto_scores[valid_mask], crypto_winrates[valid_mask])
        correlations['crypto_score_vs_crypto_winrate'] = {
            'correlation': r1,
            'p_value': p1,
            'significant': p1 < 0.05
        }
    
    return fig, correlations


def plot_crypto_vs_overall_performance(df, figsize=(16, 12), save=False, path=None):
    df_crypto = filter_crypto_traders(df)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Crypto vs Overall Performance Comparison', fontsize=16, fontweight='bold')
    
    overall_wr = df_crypto['win_rate']
    crypto_wr = df_crypto['win_rate_categories_crypto']
    valid_mask = (crypto_wr > 0) & (crypto_wr.notna()) & (overall_wr.notna())
    
    axes[0, 0].scatter(overall_wr[valid_mask], crypto_wr[valid_mask], alpha=0.5, s=30, color='#F7931A')
    axes[0, 0].plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='y=x line')
    if valid_mask.sum() > 10:
        corr = overall_wr[valid_mask].corr(crypto_wr[valid_mask])
        axes[0, 0].set_title(f'Overall vs Crypto Win Rate (r={corr:.3f})')
    axes[0, 0].set_xlabel('Overall Win Rate', fontsize=12)
    axes[0, 0].set_ylabel('Crypto Win Rate', fontsize=12)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    diff = crypto_wr[valid_mask] - overall_wr[valid_mask]
    axes[0, 1].hist(diff, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=2)
    axes[0, 1].axvline(diff.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean Diff: {diff.mean():.2%}')
    axes[0, 1].set_xlabel('Crypto WR - Overall WR', fontsize=12)
    axes[0, 1].set_ylabel('Number of Traders', fontsize=12)
    axes[0, 1].set_title('Win Rate Difference Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    crypto_volume = df_crypto['most_traded_categories_crypto']
    total_volume = df_crypto[['most_traded_categories_politics', 'most_traded_categories_sport',
                              'most_traded_categories_music', 'most_traded_categories_crypto',
                              'most_traded_categories_mentions', 'most_traded_categories_weather',
                              'most_traded_categories_culture', 'most_traded_categories_other']].sum(axis=1)
    
    crypto_pct = (crypto_volume / total_volume * 100).replace([np.inf, -np.inf], np.nan).dropna()
    
    axes[1, 0].hist(crypto_pct, bins=30, edgecolor='black', alpha=0.7, color='#F7931A')
    axes[1, 0].axvline(crypto_pct.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {crypto_pct.mean():.1f}%')
    axes[1, 0].set_xlabel('Crypto Volume %', fontsize=12)
    axes[1, 0].set_ylabel('Number of Traders', fontsize=12)
    axes[1, 0].set_title('Crypto Specialization (% of Total Volume)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    df_temp = df_crypto.copy()
    df_temp['crypto_pct'] = crypto_pct
    df_temp = df_temp[df_temp['crypto_pct'].notna()]
    
    specialists = df_temp[df_temp['crypto_pct'] >= 50]
    generalists = df_temp[df_temp['crypto_pct'] < 50]
    
    specialist_wr = specialists['win_rate_categories_crypto']
    specialist_wr = specialist_wr[(specialist_wr > 0) & (specialist_wr.notna())]
    generalist_wr = generalists['win_rate_categories_crypto']
    generalist_wr = generalist_wr[(generalist_wr > 0) & (generalist_wr.notna())]
    
    if len(specialist_wr) > 0 and len(generalist_wr) > 0:
        data = [generalist_wr.values, specialist_wr.values]
        bp = axes[1, 1].boxplot(data, labels=['Generalists\n(<50% crypto)', 'Specialists\n(≥50% crypto)'],
                               patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['boxes'][1].set_facecolor('#F7931A')
        
        t_stat, p_val = ttest_ind(generalist_wr, specialist_wr)
        sig_text = "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        axes[1, 1].set_title(f'Crypto Win Rate: Specialists vs Generalists {sig_text}\n(p={p_val:.4f})')
    
    axes[1, 1].set_ylabel('Crypto Win Rate', fontsize=12)
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    comparison_stats = {
        'crypto_traders_count': len(df_crypto),
        'avg_crypto_winrate': crypto_wr[valid_mask].mean() if valid_mask.sum() > 0 else None,
        'avg_overall_winrate': overall_wr[valid_mask].mean() if valid_mask.sum() > 0 else None,
        'avg_crypto_specialization': crypto_pct.mean() if len(crypto_pct) > 0 else None,
        'specialists_count': len(specialists),
        'generalists_count': len(generalists)
    }
    
    return fig, comparison_stats


def get_crypto_performance_summary(df):
    df_crypto = filter_crypto_traders(df)
    
    crypto_wr = df_crypto['win_rate_categories_crypto']
    crypto_wr_valid = crypto_wr[(crypto_wr > 0) & (crypto_wr.notna())]
    
    crypto_scores = df_crypto['smart_score_categories_crypto']
    crypto_scores_valid = crypto_scores[crypto_scores.notna()]
    
    crypto_volume = df_crypto['most_traded_categories_crypto']
    total_volume = df_crypto[['most_traded_categories_politics', 'most_traded_categories_sport',
                              'most_traded_categories_music', 'most_traded_categories_crypto',
                              'most_traded_categories_mentions', 'most_traded_categories_weather',
                              'most_traded_categories_culture', 'most_traded_categories_other']].sum(axis=1)
    crypto_pct = (crypto_volume / total_volume * 100).replace([np.inf, -np.inf], np.nan)
    
    summary = {
        'total_crypto_traders': len(df_crypto),
        'crypto_win_rate': {
            'mean': crypto_wr_valid.mean() if len(crypto_wr_valid) > 0 else None,
            'median': crypto_wr_valid.median() if len(crypto_wr_valid) > 0 else None,
            'std': crypto_wr_valid.std() if len(crypto_wr_valid) > 0 else None,
            'count': len(crypto_wr_valid)
        },
        'crypto_smart_score': {
            'mean': crypto_scores_valid.mean() if len(crypto_scores_valid) > 0 else None,
            'median': crypto_scores_valid.median() if len(crypto_scores_valid) > 0 else None,
            'std': crypto_scores_valid.std() if len(crypto_scores_valid) > 0 else None
        },
        'crypto_specialization': {
            'mean_pct': crypto_pct.mean() if crypto_pct.notna().sum() > 0 else None,
            'specialists_50pct': (crypto_pct >= 50).sum(),
            'specialists_80pct': (crypto_pct >= 80).sum()
        },
        'total_crypto_volume': crypto_volume.sum()
    }
    
    return summary

