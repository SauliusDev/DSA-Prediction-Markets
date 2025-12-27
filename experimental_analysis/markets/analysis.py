import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import warnings
import os
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_data(path='../../data/users_data.csv'):
    return pd.read_csv(path)


def plot_markets_distribution(df, figsize=(18, 5), save=False, path=None):
    nm = df['num_markets'].dropna()
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle('Number of Markets Traded Distribution', fontsize=16, fontweight='bold')
    
    axes[0].hist(nm, bins=50, edgecolor='black', alpha=0.7, color='#1abc9c')
    axes[0].axvline(nm.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {nm.mean():.0f}')
    axes[0].axvline(nm.median(), color='blue', linestyle='--', linewidth=2, 
                    label=f'Median: {nm.median():.0f}')
    axes[0].set_xlabel('Number of Markets', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('Markets Traded Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    box = axes[1].boxplot(nm, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#1abc9c')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Number of Markets', fontsize=12)
    axes[1].set_title('Markets Traded Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    nm.plot(kind='density', ax=axes[2], color='#1abc9c', linewidth=2)
    axes[2].axvline(nm.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {nm.mean():.0f}')
    axes[2].set_xlabel('Number of Markets', fontsize=12)
    axes[2].set_ylabel('Density', fontsize=12)
    axes[2].set_title('Markets Traded Density Plot')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    stats = {
        'mean': nm.mean(),
        'median': nm.median(),
        'std': nm.std(),
        'min': nm.min(),
        'max': nm.max(),
        'q1': nm.quantile(0.25),
        'q3': nm.quantile(0.75),
        'count': len(nm)
    }
    
    return fig, stats


def plot_markets_vs_pnl(df, figsize=(16, 12), save=False, path=None):
    nm = df['num_markets']
    pnl = df['total_pnl']
    valid_mask = nm.notna() & pnl.notna()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Number of Markets vs PnL Analysis', fontsize=16, fontweight='bold')
    
    corr_p, p_val_p = pearsonr(nm[valid_mask], pnl[valid_mask])
    corr_s, p_val_s = spearmanr(nm[valid_mask], pnl[valid_mask])
    
    axes[0, 0].scatter(nm[valid_mask], pnl[valid_mask], alpha=0.5, s=30, color='#1abc9c')
    z = np.polyfit(nm[valid_mask], pnl[valid_mask], 1)
    p = np.poly1d(z)
    x_sorted = np.sort(nm[valid_mask])
    axes[0, 0].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                   label=f'Pearson r={corr_p:.3f}\nSpearman ρ={corr_s:.3f}')
    axes[0, 0].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 0].set_ylabel('Total PnL ($)', fontsize=12)
    axes[0, 0].set_title('Markets vs Total PnL')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    pnl_clipped = pnl[valid_mask].clip(lower=pnl[valid_mask].quantile(0.05), 
                                        upper=pnl[valid_mask].quantile(0.95))
    axes[0, 1].scatter(nm[valid_mask], pnl_clipped, alpha=0.5, s=30, color='#e74c3c')
    axes[0, 1].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 1].set_ylabel('Total PnL (5-95 percentile)', fontsize=12)
    axes[0, 1].set_title('Markets vs PnL (Outliers Clipped)')
    axes[0, 1].grid(True, alpha=0.3)
    
    df_temp = df[valid_mask].copy()
    df_temp['markets_quartile'] = pd.qcut(df_temp['num_markets'], q=4, 
                                           labels=['Q1\n(Fewest)', 'Q2', 'Q3', 'Q4\n(Most)'],
                                           duplicates='drop')
    
    quartile_pnl = df_temp.groupby('markets_quartile')['total_pnl'].agg(['mean', 'median'])
    x_pos = np.arange(len(quartile_pnl))
    width = 0.35
    
    axes[1, 0].bar(x_pos - width/2, quartile_pnl['mean'], width, 
                   label='Mean PnL', color='#1abc9c', edgecolor='black', alpha=0.7)
    axes[1, 0].bar(x_pos + width/2, quartile_pnl['median'], width, 
                   label='Median PnL', color='#2ecc71', edgecolor='black', alpha=0.7)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(quartile_pnl.index)
    axes[1, 0].set_xlabel('Markets Traded Quartile', fontsize=12)
    axes[1, 0].set_ylabel('PnL ($)', fontsize=12)
    axes[1, 0].set_title('PnL by Markets Quartile')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    pnl_by_quartile = [df_temp[df_temp['markets_quartile'] == q]['total_pnl'].values 
                       for q in quartile_pnl.index]
    bp = axes[1, 1].boxplot(pnl_by_quartile, labels=quartile_pnl.index, patch_artist=True)
    colors = ['#8B0000', '#FF4500', '#90EE90', '#006400']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1, 1].set_xlabel('Markets Traded Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Total PnL ($)', fontsize=12)
    axes[1, 1].set_title('PnL Distribution by Markets Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    correlations = {
        'pearson': {'r': corr_p, 'p_value': p_val_p, 'significant': p_val_p < 0.05},
        'spearman': {'rho': corr_s, 'p_value': p_val_s, 'significant': p_val_s < 0.05}
    }
    
    return fig, correlations


def plot_markets_vs_winrate(df, figsize=(16, 12), save=False, path=None):
    nm = df['num_markets']
    wr = df['win_rate']
    valid_mask = nm.notna() & wr.notna() & (wr > 0)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Number of Markets vs Win Rate Analysis', fontsize=16, fontweight='bold')
    
    corr_p, p_val_p = pearsonr(nm[valid_mask], wr[valid_mask])
    corr_s, p_val_s = spearmanr(nm[valid_mask], wr[valid_mask])
    
    axes[0, 0].scatter(nm[valid_mask], wr[valid_mask], alpha=0.5, s=30, color='#9b59b6')
    z = np.polyfit(nm[valid_mask], wr[valid_mask], 1)
    p = np.poly1d(z)
    x_sorted = np.sort(nm[valid_mask])
    axes[0, 0].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                   label=f'Pearson r={corr_p:.3f}\nSpearman ρ={corr_s:.3f}')
    axes[0, 0].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 0].set_ylabel('Win Rate', fontsize=12)
    axes[0, 0].set_title('Markets vs Win Rate')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].hexbin(nm[valid_mask], wr[valid_mask], gridsize=30, cmap='YlOrRd', mincnt=1)
    axes[0, 1].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 1].set_ylabel('Win Rate', fontsize=12)
    axes[0, 1].set_title('Markets vs Win Rate (Density)')
    plt.colorbar(axes[0, 1].collections[0], ax=axes[0, 1], label='Count')
    axes[0, 1].grid(True, alpha=0.3)
    
    df_temp = df[valid_mask].copy()
    df_temp['markets_quartile'] = pd.qcut(df_temp['num_markets'], q=4, 
                                           labels=['Q1\n(Fewest)', 'Q2', 'Q3', 'Q4\n(Most)'],
                                           duplicates='drop')
    
    quartile_wr = df_temp.groupby('markets_quartile')['win_rate'].mean()
    axes[1, 0].bar(quartile_wr.index, quartile_wr.values, 
                   color=['#8B0000', '#FF4500', '#90EE90', '#006400'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Markets Traded Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Average Win Rate', fontsize=12)
    axes[1, 0].set_title('Win Rate by Markets Quartile')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    wr_by_quartile = [df_temp[df_temp['markets_quartile'] == q]['win_rate'].values 
                      for q in quartile_wr.index]
    bp = axes[1, 1].boxplot(wr_by_quartile, labels=quartile_wr.index, patch_artist=True)
    colors = ['#8B0000', '#FF4500', '#90EE90', '#006400']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1, 1].set_xlabel('Markets Traded Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Win Rate', fontsize=12)
    axes[1, 1].set_title('Win Rate Distribution by Markets Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    correlations = {
        'pearson': {'r': corr_p, 'p_value': p_val_p, 'significant': p_val_p < 0.05},
        'spearman': {'rho': corr_s, 'p_value': p_val_s, 'significant': p_val_s < 0.05}
    }
    
    return fig, correlations


def plot_combined_analysis(df, figsize=(18, 10), save=False, path=None):
    nm = df['num_markets']
    pnl = df['total_pnl']
    wr = df['win_rate']
    ec = df['effective_count']
    valid_mask = nm.notna() & pnl.notna() & wr.notna() & (wr > 0)
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Markets Traded: Combined Performance Analysis', fontsize=16, fontweight='bold')
    
    df_temp = df[valid_mask].copy()
    df_temp['markets_decile'] = pd.qcut(df_temp['num_markets'], q=10, labels=False, duplicates='drop')
    
    decile_stats = df_temp.groupby('markets_decile').agg({
        'num_markets': 'mean',
        'total_pnl': 'mean',
        'win_rate': 'mean'
    }).reset_index()
    
    axes[0, 0].plot(decile_stats['markets_decile'], decile_stats['total_pnl'], 
                    marker='o', linewidth=2, markersize=8, color='#1abc9c')
    axes[0, 0].set_xlabel('Markets Decile', fontsize=12)
    axes[0, 0].set_ylabel('Average PnL ($)', fontsize=12)
    axes[0, 0].set_title('PnL Trend by Markets Decile')
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(decile_stats['markets_decile'], decile_stats['win_rate'], 
                    marker='s', linewidth=2, markersize=8, color='#2ecc71')
    axes[0, 1].set_xlabel('Markets Decile', fontsize=12)
    axes[0, 1].set_ylabel('Average Win Rate', fontsize=12)
    axes[0, 1].set_title('Win Rate Trend by Markets Decile')
    axes[0, 1].grid(True, alpha=0.3)
    
    scatter = axes[0, 2].scatter(nm[valid_mask], pnl[valid_mask], 
                                  c=wr[valid_mask], cmap='RdYlGn', 
                                  alpha=0.6, s=30)
    plt.colorbar(scatter, ax=axes[0, 2], label='Win Rate')
    axes[0, 2].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 2].set_ylabel('Total PnL ($)', fontsize=12)
    axes[0, 2].set_title('Markets vs PnL (colored by Win Rate)')
    axes[0, 2].grid(True, alpha=0.3)
    
    valid_mask2 = valid_mask & ec.notna()
    if valid_mask2.sum() > 10:
        corr, _ = pearsonr(nm[valid_mask2], ec[valid_mask2])
        axes[1, 0].scatter(nm[valid_mask2], ec[valid_mask2], alpha=0.5, s=30, color='#e67e22')
        axes[1, 0].set_xlabel('Number of Markets', fontsize=12)
        axes[1, 0].set_ylabel('Effective Count', fontsize=12)
        axes[1, 0].set_title(f'Markets vs Effective Count (r={corr:.3f})')
        axes[1, 0].grid(True, alpha=0.3)
    
    df_temp['markets_category'] = pd.qcut(df_temp['num_markets'], q=3, 
                                           labels=['Few Markets', 'Medium', 'Many Markets'],
                                           duplicates='drop')
    
    for cat in df_temp['markets_category'].unique():
        subset = df_temp[df_temp['markets_category'] == cat]
        axes[1, 1].scatter(subset['win_rate'], subset['total_pnl'], 
                          alpha=0.5, s=30, label=cat)
    axes[1, 1].set_xlabel('Win Rate', fontsize=12)
    axes[1, 1].set_ylabel('Total PnL ($)', fontsize=12)
    axes[1, 1].set_title('Win Rate vs PnL by Markets Category')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    corr_cols = ['num_markets', 'total_pnl', 'win_rate']
    if 'effective_count' in df.columns:
        corr_cols.append('effective_count')
    corr_matrix = df_temp[corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                ax=axes[1, 2], fmt='.3f', square=True)
    axes[1, 2].set_title('Correlation Matrix')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, corr_matrix


def get_markets_summary(df):
    nm = df['num_markets'].dropna()
    pnl = df['total_pnl'].dropna()
    wr = df['win_rate']
    wr_valid = wr[(wr > 0) & wr.notna()]
    
    valid_mask = df['num_markets'].notna() & df['total_pnl'].notna()
    corr_nm_pnl = df.loc[valid_mask, 'num_markets'].corr(df.loc[valid_mask, 'total_pnl'])
    
    valid_mask2 = df['num_markets'].notna() & df['win_rate'].notna() & (df['win_rate'] > 0)
    corr_nm_wr = df.loc[valid_mask2, 'num_markets'].corr(df.loc[valid_mask2, 'win_rate'])
    
    summary = {
        'num_markets': {
            'mean': nm.mean(),
            'median': nm.median(),
            'std': nm.std(),
            'min': nm.min(),
            'max': nm.max(),
            'count': len(nm)
        },
        'total_pnl': {
            'mean': pnl.mean(),
            'median': pnl.median(),
            'std': pnl.std()
        },
        'win_rate': {
            'mean': wr_valid.mean(),
            'median': wr_valid.median(),
            'count': len(wr_valid)
        },
        'correlations': {
            'markets_vs_pnl': corr_nm_pnl,
            'markets_vs_winrate': corr_nm_wr
        }
    }
    
    return summary


def generate_report(df, save=False, output_dir='data'):
    if save:
        os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("GENERATING MARKETS ANALYSIS REPORT")
    print("="*80)
    print(f"Analyzing {len(df)} traders")
    
    figures = {}
    
    if save:
        path1 = f"{output_dir}/markets_distribution.png"
        path2 = f"{output_dir}/markets_vs_pnl.png"
        path3 = f"{output_dir}/markets_vs_winrate.png"
        path4 = f"{output_dir}/markets_combined.png"
    else:
        path1 = path2 = path3 = path4 = None
    
    fig1, stats1 = plot_markets_distribution(df, save=save, path=path1)
    fig2, stats2 = plot_markets_vs_pnl(df, save=save, path=path2)
    fig3, stats3 = plot_markets_vs_winrate(df, save=save, path=path3)
    fig4, stats4 = plot_combined_analysis(df, save=save, path=path4)
    
    figures['distribution'] = fig1
    figures['vs_pnl'] = fig2
    figures['vs_winrate'] = fig3
    figures['combined'] = fig4
    
    summary = get_markets_summary(df)
    
    print("\n" + "="*80)
    print("MARKETS ANALYSIS COMPLETE")
    print("="*80)
    
    if save:
        print(f"\nAll figures saved to: {output_dir}/")
    
    return {
        'figures': figures,
        'summary': summary,
        'distribution_stats': stats1,
        'pnl_correlations': stats2,
        'winrate_correlations': stats3,
        'correlation_matrix': stats4
    }


if __name__ == '__main__':
    df = load_data()
    report = generate_report(df, save=True, output_dir='data')
    print("\nSummary:")
    print(report['summary'])

