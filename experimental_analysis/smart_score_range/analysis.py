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


def load_data(path=None):
    if path is None:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, 'traders.csv')
    return pd.read_csv(path)


def remove_outliers_iqr(data, multiplier=1.5):
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return data[(data >= lower) & (data <= upper)]


def plot_pnl_distribution(df, figsize=(18, 10), save=False, path=None):
    pnl = df['sum_pnl'].dropna()
    pnl_clean = remove_outliers_iqr(pnl)
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'PnL Distribution (n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0, 0].hist(pnl_clean, bins=50, edgecolor='black', alpha=0.7, color='#2ecc71')
    axes[0, 0].axvline(pnl_clean.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: ${pnl_clean.mean():,.0f}')
    axes[0, 0].axvline(pnl_clean.median(), color='blue', linestyle='--', linewidth=2, 
                       label=f'Median: ${pnl_clean.median():,.0f}')
    axes[0, 0].set_xlabel('PnL ($)', fontsize=12)
    axes[0, 0].set_ylabel('Count', fontsize=12)
    axes[0, 0].set_title(f'PnL Histogram (IQR filtered, n={len(pnl_clean)})')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    box = axes[0, 1].boxplot(pnl, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#2ecc71')
    box['boxes'][0].set_alpha(0.7)
    axes[0, 1].set_ylabel('PnL ($)', fontsize=12)
    axes[0, 1].set_title('PnL Box Plot (All Data)')
    axes[0, 1].grid(True, alpha=0.3)
    
    pnl_clean.plot(kind='density', ax=axes[0, 2], color='#2ecc71', linewidth=2)
    axes[0, 2].axvline(pnl_clean.mean(), color='red', linestyle='--', linewidth=2)
    axes[0, 2].set_xlabel('PnL ($)', fontsize=12)
    axes[0, 2].set_ylabel('Density', fontsize=12)
    axes[0, 2].set_title('PnL Density (IQR filtered)')
    axes[0, 2].grid(True, alpha=0.3)
    
    df_temp = df.copy()
    df_temp['pnl_quartile'] = pd.qcut(df_temp['sum_pnl'], q=4, 
                                       labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'],
                                       duplicates='drop')
    quartile_counts = df_temp['pnl_quartile'].value_counts().sort_index()
    axes[1, 0].bar(quartile_counts.index, quartile_counts.values, 
                   color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('PnL Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Count', fontsize=12)
    axes[1, 0].set_title('Traders by PnL Quartile')
    axes[1, 0].tick_params(axis='x', rotation=15)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    quartile_stats = df_temp.groupby('pnl_quartile')['sum_pnl'].agg(['min', 'max', 'mean'])
    x_pos = np.arange(len(quartile_stats))
    axes[1, 1].bar(x_pos, quartile_stats['mean'], color='#3498db', edgecolor='black', alpha=0.7)
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(quartile_stats.index, rotation=15)
    axes[1, 1].set_xlabel('PnL Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Mean PnL ($)', fontsize=12)
    axes[1, 1].set_title('Mean PnL by Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    profitable = (pnl > 0).sum()
    unprofitable = (pnl <= 0).sum()
    axes[1, 2].pie([profitable, unprofitable], labels=['Profitable', 'Unprofitable'],
                   autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90,
                   explode=(0.02, 0))
    axes[1, 2].set_title(f'Profitability ({profitable}/{len(pnl)} profitable)')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_winrate_distribution(df, figsize=(18, 10), save=False, path=None):
    wr = df['win_rate'].dropna()
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'Win Rate Distribution (n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0, 0].hist(wr, bins=50, edgecolor='black', alpha=0.7, color='#9b59b6')
    axes[0, 0].axvline(wr.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {wr.mean():.2%}')
    axes[0, 0].axvline(wr.median(), color='blue', linestyle='--', linewidth=2, 
                       label=f'Median: {wr.median():.2%}')
    axes[0, 0].set_xlabel('Win Rate', fontsize=12)
    axes[0, 0].set_ylabel('Count', fontsize=12)
    axes[0, 0].set_title('Win Rate Histogram')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    box = axes[0, 1].boxplot(wr, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#9b59b6')
    box['boxes'][0].set_alpha(0.7)
    axes[0, 1].set_ylabel('Win Rate', fontsize=12)
    axes[0, 1].set_title('Win Rate Box Plot')
    axes[0, 1].grid(True, alpha=0.3)
    
    wr.plot(kind='density', ax=axes[0, 2], color='#9b59b6', linewidth=2)
    axes[0, 2].axvline(wr.mean(), color='red', linestyle='--', linewidth=2)
    axes[0, 2].set_xlabel('Win Rate', fontsize=12)
    axes[0, 2].set_ylabel('Density', fontsize=12)
    axes[0, 2].set_title('Win Rate Density')
    axes[0, 2].grid(True, alpha=0.3)
    
    df_temp = df.copy()
    df_temp['wr_quartile'] = pd.qcut(df_temp['win_rate'], q=4, 
                                      labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'],
                                      duplicates='drop')
    quartile_counts = df_temp['wr_quartile'].value_counts().sort_index()
    axes[1, 0].bar(quartile_counts.index, quartile_counts.values, 
                   color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Win Rate Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Count', fontsize=12)
    axes[1, 0].set_title('Traders by Win Rate Quartile')
    axes[1, 0].tick_params(axis='x', rotation=15)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    quartile_stats = df_temp.groupby('wr_quartile')['win_rate'].agg(['min', 'max', 'mean'])
    x_pos = np.arange(len(quartile_stats))
    axes[1, 1].bar(x_pos, quartile_stats['mean'], color='#9b59b6', edgecolor='black', alpha=0.7)
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(quartile_stats.index, rotation=15)
    axes[1, 1].set_xlabel('Win Rate Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Mean Win Rate', fontsize=12)
    axes[1, 1].set_title('Mean Win Rate by Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    above_50 = (wr > 0.5).sum()
    below_50 = (wr <= 0.5).sum()
    axes[1, 2].pie([above_50, below_50], labels=['>50% WR', '≤50% WR'],
                   autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90,
                   explode=(0.02, 0))
    axes[1, 2].set_title(f'Win Rate Split ({above_50}/{len(wr)} above 50%)')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_markets_distribution(df, figsize=(18, 10), save=False, path=None):
    nm = df['num_markets'].dropna()
    nm_clean = remove_outliers_iqr(nm)
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'Number of Markets Distribution (n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0, 0].hist(nm_clean, bins=50, edgecolor='black', alpha=0.7, color='#1abc9c')
    axes[0, 0].axvline(nm_clean.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {nm_clean.mean():.0f}')
    axes[0, 0].axvline(nm_clean.median(), color='blue', linestyle='--', linewidth=2, 
                       label=f'Median: {nm_clean.median():.0f}')
    axes[0, 0].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 0].set_ylabel('Count', fontsize=12)
    axes[0, 0].set_title(f'Markets Histogram (IQR filtered, n={len(nm_clean)})')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    box = axes[0, 1].boxplot(nm, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#1abc9c')
    box['boxes'][0].set_alpha(0.7)
    axes[0, 1].set_ylabel('Number of Markets', fontsize=12)
    axes[0, 1].set_title('Markets Box Plot (All Data)')
    axes[0, 1].grid(True, alpha=0.3)
    
    nm_clean.plot(kind='density', ax=axes[0, 2], color='#1abc9c', linewidth=2)
    axes[0, 2].axvline(nm_clean.mean(), color='red', linestyle='--', linewidth=2)
    axes[0, 2].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 2].set_ylabel('Density', fontsize=12)
    axes[0, 2].set_title('Markets Density (IQR filtered)')
    axes[0, 2].grid(True, alpha=0.3)
    
    df_temp = df.copy()
    df_temp['markets_quartile'] = pd.qcut(df_temp['num_markets'], q=4, 
                                           labels=['Q1 (Fewest)', 'Q2', 'Q3', 'Q4 (Most)'],
                                           duplicates='drop')
    quartile_counts = df_temp['markets_quartile'].value_counts().sort_index()
    axes[1, 0].bar(quartile_counts.index, quartile_counts.values, 
                   color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Markets Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Count', fontsize=12)
    axes[1, 0].set_title('Traders by Markets Quartile')
    axes[1, 0].tick_params(axis='x', rotation=15)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    quartile_stats = df_temp.groupby('markets_quartile')['num_markets'].agg(['min', 'max', 'mean'])
    x_pos = np.arange(len(quartile_stats))
    axes[1, 1].bar(x_pos, quartile_stats['mean'], color='#1abc9c', edgecolor='black', alpha=0.7)
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(quartile_stats.index, rotation=15)
    axes[1, 1].set_xlabel('Markets Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Mean Markets', fontsize=12)
    axes[1, 1].set_title('Mean Markets by Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    bins = [0, 100, 500, 1000, 5000, nm.max()+1]
    labels = ['1-100', '101-500', '501-1000', '1001-5000', '5000+']
    df_temp['markets_bin'] = pd.cut(df_temp['num_markets'], bins=bins, labels=labels)
    bin_counts = df_temp['markets_bin'].value_counts().sort_index()
    axes[1, 2].bar(bin_counts.index, bin_counts.values, color='#e67e22', edgecolor='black', alpha=0.7)
    axes[1, 2].set_xlabel('Markets Range', fontsize=12)
    axes[1, 2].set_ylabel('Count', fontsize=12)
    axes[1, 2].set_title('Traders by Markets Range')
    axes[1, 2].tick_params(axis='x', rotation=15)
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_effective_count_distribution(df, figsize=(18, 10), save=False, path=None):
    ec = df['effective_count'].dropna()
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'Effective Count Distribution (n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0, 0].hist(ec, bins=50, edgecolor='black', alpha=0.7, color='#3498db')
    axes[0, 0].axvline(ec.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {ec.mean():.2f}')
    axes[0, 0].axvline(ec.median(), color='blue', linestyle='--', linewidth=2, 
                       label=f'Median: {ec.median():.2f}')
    axes[0, 0].set_xlabel('Effective Count', fontsize=12)
    axes[0, 0].set_ylabel('Count', fontsize=12)
    axes[0, 0].set_title('Effective Count Histogram')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    box = axes[0, 1].boxplot(ec, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#3498db')
    box['boxes'][0].set_alpha(0.7)
    axes[0, 1].set_ylabel('Effective Count', fontsize=12)
    axes[0, 1].set_title('Effective Count Box Plot')
    axes[0, 1].grid(True, alpha=0.3)
    
    ec.plot(kind='density', ax=axes[0, 2], color='#3498db', linewidth=2)
    axes[0, 2].axvline(ec.mean(), color='red', linestyle='--', linewidth=2)
    axes[0, 2].set_xlabel('Effective Count', fontsize=12)
    axes[0, 2].set_ylabel('Density', fontsize=12)
    axes[0, 2].set_title('Effective Count Density')
    axes[0, 2].grid(True, alpha=0.3)
    
    df_temp = df.copy()
    try:
        df_temp['ec_quartile'] = pd.qcut(df_temp['effective_count'], q=4, 
                                          labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'],
                                          duplicates='drop')
    except ValueError:
        df_temp['ec_quartile'] = pd.cut(df_temp['effective_count'], bins=4, 
                                         labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    
    quartile_counts = df_temp['ec_quartile'].value_counts().sort_index()
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71'][:len(quartile_counts)]
    axes[1, 0].bar(quartile_counts.index, quartile_counts.values, 
                   color=colors, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('EC Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Count', fontsize=12)
    axes[1, 0].set_title('Traders by EC Quartile')
    axes[1, 0].tick_params(axis='x', rotation=15)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    quartile_stats = df_temp.groupby('ec_quartile')['effective_count'].agg(['min', 'max', 'mean'])
    x_pos = np.arange(len(quartile_stats))
    axes[1, 1].bar(x_pos, quartile_stats['mean'], color='#3498db', edgecolor='black', alpha=0.7)
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(quartile_stats.index, rotation=15)
    axes[1, 1].set_xlabel('EC Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Mean EC', fontsize=12)
    axes[1, 1].set_title('Mean Effective Count by Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    ec_10 = (ec == 10).sum()
    ec_9_10 = ((ec >= 9) & (ec < 10)).sum()
    ec_below_9 = (ec < 9).sum()
    axes[1, 2].pie([ec_10, ec_9_10, ec_below_9], 
                   labels=['EC = 10', 'EC 9-10', 'EC < 9'],
                   autopct='%1.1f%%', colors=['#2ecc71', '#3498db', '#e74c3c'], 
                   startangle=90, explode=(0.02, 0, 0))
    axes[1, 2].set_title('Effective Count Distribution')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_correlations(df, figsize=(16, 12), save=False, path=None):
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Correlation Analysis', fontsize=16, fontweight='bold')
    
    valid_mask = df['win_rate'].notna() & df['sum_pnl'].notna()
    wr = df.loc[valid_mask, 'win_rate']
    pnl = df.loc[valid_mask, 'sum_pnl']
    
    corr_p, _ = pearsonr(wr, pnl)
    corr_s, _ = spearmanr(wr, pnl)
    
    axes[0, 0].scatter(wr, pnl, alpha=0.4, s=20, color='#3498db')
    axes[0, 0].set_xlabel('Win Rate', fontsize=12)
    axes[0, 0].set_ylabel('PnL ($)', fontsize=12)
    axes[0, 0].set_title(f'Win Rate vs PnL (r={corr_p:.3f}, ρ={corr_s:.3f})')
    axes[0, 0].grid(True, alpha=0.3)
    
    valid_mask2 = df['num_markets'].notna() & df['sum_pnl'].notna()
    nm = df.loc[valid_mask2, 'num_markets']
    pnl2 = df.loc[valid_mask2, 'sum_pnl']
    
    corr_p2, _ = pearsonr(nm, pnl2)
    corr_s2, _ = spearmanr(nm, pnl2)
    
    axes[0, 1].scatter(nm, pnl2, alpha=0.4, s=20, color='#1abc9c')
    axes[0, 1].set_xlabel('Number of Markets', fontsize=12)
    axes[0, 1].set_ylabel('PnL ($)', fontsize=12)
    axes[0, 1].set_title(f'Markets vs PnL (r={corr_p2:.3f}, ρ={corr_s2:.3f})')
    axes[0, 1].grid(True, alpha=0.3)
    
    valid_mask3 = df['effective_count'].notna() & df['sum_pnl'].notna()
    ec = df.loc[valid_mask3, 'effective_count']
    pnl3 = df.loc[valid_mask3, 'sum_pnl']
    
    corr_p3, _ = pearsonr(ec, pnl3)
    corr_s3, _ = spearmanr(ec, pnl3)
    
    axes[1, 0].scatter(ec, pnl3, alpha=0.4, s=20, color='#9b59b6')
    axes[1, 0].set_xlabel('Effective Count', fontsize=12)
    axes[1, 0].set_ylabel('PnL ($)', fontsize=12)
    axes[1, 0].set_title(f'EC vs PnL (r={corr_p3:.3f}, ρ={corr_s3:.3f})')
    axes[1, 0].grid(True, alpha=0.3)
    
    corr_cols = ['win_rate', 'effective_count', 'sum_pnl', 'num_markets']
    corr_matrix = df[corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                ax=axes[1, 1], fmt='.3f', square=True)
    axes[1, 1].set_title('Correlation Matrix')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, corr_matrix


def get_summary(df):
    summary = {
        'count': len(df),
        'sum_pnl': {
            'mean': df['sum_pnl'].mean(),
            'median': df['sum_pnl'].median(),
            'std': df['sum_pnl'].std(),
            'min': df['sum_pnl'].min(),
            'max': df['sum_pnl'].max(),
            'profitable_pct': (df['sum_pnl'] > 0).mean() * 100
        },
        'win_rate': {
            'mean': df['win_rate'].mean(),
            'median': df['win_rate'].median(),
            'std': df['win_rate'].std(),
            'above_50_pct': (df['win_rate'] > 0.5).mean() * 100
        },
        'num_markets': {
            'mean': df['num_markets'].mean(),
            'median': df['num_markets'].median(),
            'std': df['num_markets'].std(),
            'min': df['num_markets'].min(),
            'max': df['num_markets'].max()
        },
        'effective_count': {
            'mean': df['effective_count'].mean(),
            'median': df['effective_count'].median(),
            'ec_10_pct': (df['effective_count'] == 10).mean() * 100
        }
    }
    return summary


def generate_report(df, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("SMART SCORE RANGE ANALYSIS")
    print("="*80)
    print(f"Analyzing {len(df)} traders")
    
    plot_pnl_distribution(df, save=True, path=f"{output_dir}/pnl_distribution.png")
    plot_winrate_distribution(df, save=True, path=f"{output_dir}/winrate_distribution.png")
    plot_markets_distribution(df, save=True, path=f"{output_dir}/markets_distribution.png")
    plot_effective_count_distribution(df, save=True, path=f"{output_dir}/effective_count_distribution.png")
    plot_correlations(df, save=True, path=f"{output_dir}/correlations.png")
    
    summary = get_summary(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll figures saved to: {output_dir}/")
    
    return summary


if __name__ == '__main__':
    df = load_data()
    summary = generate_report(df, output_dir='data')
    print("\nSummary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

