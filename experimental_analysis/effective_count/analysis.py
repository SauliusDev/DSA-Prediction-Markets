import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_data(path='../../data/users_data.csv'):
    return pd.read_csv(path)


def plot_effective_count_distribution(df, figsize=(18, 5), save=False, path=None):
    ec = df['effective_count'].dropna()
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle('Effective Count Distribution', fontsize=16, fontweight='bold')
    
    axes[0].hist(ec, bins=50, edgecolor='black', alpha=0.7, color='#3498db')
    axes[0].axvline(ec.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {ec.mean():.2f}')
    axes[0].axvline(ec.median(), color='green', linestyle='--', linewidth=2, 
                    label=f'Median: {ec.median():.2f}')
    axes[0].set_xlabel('Effective Count', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('Effective Count Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    box = axes[1].boxplot(ec, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#3498db')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Effective Count', fontsize=12)
    axes[1].set_title('Effective Count Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    ec.plot(kind='density', ax=axes[2], color='#3498db', linewidth=2)
    axes[2].axvline(ec.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {ec.mean():.2f}')
    axes[2].set_xlabel('Effective Count', fontsize=12)
    axes[2].set_ylabel('Density', fontsize=12)
    axes[2].set_title('Effective Count Density Plot')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    stats = {
        'mean': ec.mean(),
        'median': ec.median(),
        'std': ec.std(),
        'min': ec.min(),
        'max': ec.max(),
        'q1': ec.quantile(0.25),
        'q3': ec.quantile(0.75),
        'count': len(ec)
    }
    
    return fig, stats


def plot_effective_count_vs_pnl(df, figsize=(16, 12), save=False, path=None):
    ec = df['effective_count']
    pnl = df['total_pnl']
    valid_mask = ec.notna() & pnl.notna()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Effective Count vs PnL Analysis', fontsize=16, fontweight='bold')
    
    if valid_mask.sum() > 10:
        corr_p, p_val_p = pearsonr(ec[valid_mask], pnl[valid_mask])
        corr_s, p_val_s = spearmanr(ec[valid_mask], pnl[valid_mask])
        
        axes[0, 0].scatter(ec[valid_mask], pnl[valid_mask], alpha=0.5, s=30, color='#3498db')
        z = np.polyfit(ec[valid_mask], pnl[valid_mask], 1)
        p = np.poly1d(z)
        x_sorted = np.sort(ec[valid_mask])
        axes[0, 0].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                       label=f'Pearson r={corr_p:.3f}\nSpearman ρ={corr_s:.3f}')
        axes[0, 0].set_xlabel('Effective Count', fontsize=12)
        axes[0, 0].set_ylabel('Total PnL', fontsize=12)
        axes[0, 0].set_title('Effective Count vs Total PnL')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    pnl_clipped = pnl[valid_mask].clip(lower=pnl[valid_mask].quantile(0.05), 
                                        upper=pnl[valid_mask].quantile(0.95))
    axes[0, 1].scatter(ec[valid_mask], pnl_clipped, alpha=0.5, s=30, color='#e74c3c')
    axes[0, 1].set_xlabel('Effective Count', fontsize=12)
    axes[0, 1].set_ylabel('Total PnL (5-95 percentile)', fontsize=12)
    axes[0, 1].set_title('Effective Count vs PnL (Outliers Clipped)')
    axes[0, 1].grid(True, alpha=0.3)
    
    df_temp = df[valid_mask].copy()
    df_temp['ec_quartile'] = pd.qcut(df_temp['effective_count'], q=4, 
                                      labels=['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'],
                                      duplicates='drop')
    
    quartile_pnl = df_temp.groupby('ec_quartile')['total_pnl'].agg(['mean', 'median'])
    x_pos = np.arange(len(quartile_pnl))
    width = 0.35
    
    axes[1, 0].bar(x_pos - width/2, quartile_pnl['mean'], width, 
                   label='Mean PnL', color='#3498db', edgecolor='black', alpha=0.7)
    axes[1, 0].bar(x_pos + width/2, quartile_pnl['median'], width, 
                   label='Median PnL', color='#2ecc71', edgecolor='black', alpha=0.7)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(quartile_pnl.index)
    axes[1, 0].set_xlabel('Effective Count Quartile', fontsize=12)
    axes[1, 0].set_ylabel('PnL', fontsize=12)
    axes[1, 0].set_title('PnL by Effective Count Quartile')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    pnl_by_quartile = [df_temp[df_temp['ec_quartile'] == q]['total_pnl'].values 
                       for q in quartile_pnl.index]
    bp = axes[1, 1].boxplot(pnl_by_quartile, labels=quartile_pnl.index, patch_artist=True)
    colors = ['#8B0000', '#FF4500', '#90EE90', '#006400']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1, 1].set_xlabel('Effective Count Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Total PnL', fontsize=12)
    axes[1, 1].set_title('PnL Distribution by Effective Count Quartile')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    correlations = {
        'pearson': {'r': corr_p, 'p_value': p_val_p, 'significant': p_val_p < 0.05},
        'spearman': {'rho': corr_s, 'p_value': p_val_s, 'significant': p_val_s < 0.05}
    }
    
    return fig, correlations


def plot_effective_count_vs_winrate(df, figsize=(16, 12), save=False, path=None):
    ec = df['effective_count']
    wr = df['win_rate']
    valid_mask = ec.notna() & wr.notna() & (wr > 0)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Effective Count vs Win Rate Analysis', fontsize=16, fontweight='bold')
    
    if valid_mask.sum() > 10:
        corr_p, p_val_p = pearsonr(ec[valid_mask], wr[valid_mask])
        corr_s, p_val_s = spearmanr(ec[valid_mask], wr[valid_mask])
        
        axes[0, 0].scatter(ec[valid_mask], wr[valid_mask], alpha=0.5, s=30, color='#9b59b6')
        z = np.polyfit(ec[valid_mask], wr[valid_mask], 1)
        p = np.poly1d(z)
        x_sorted = np.sort(ec[valid_mask])
        axes[0, 0].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                       label=f'Pearson r={corr_p:.3f}\nSpearman ρ={corr_s:.3f}')
        axes[0, 0].set_xlabel('Effective Count', fontsize=12)
        axes[0, 0].set_ylabel('Win Rate', fontsize=12)
        axes[0, 0].set_title('Effective Count vs Win Rate')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].hexbin(ec[valid_mask], wr[valid_mask], gridsize=30, cmap='YlOrRd', mincnt=1)
    axes[0, 1].set_xlabel('Effective Count', fontsize=12)
    axes[0, 1].set_ylabel('Win Rate', fontsize=12)
    axes[0, 1].set_title('Effective Count vs Win Rate (Density)')
    plt.colorbar(axes[0, 1].collections[0], ax=axes[0, 1], label='Count')
    axes[0, 1].grid(True, alpha=0.3)
    
    df_temp = df[valid_mask].copy()
    df_temp['ec_quartile'] = pd.qcut(df_temp['effective_count'], q=4, 
                                      labels=['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'],
                                      duplicates='drop')
    
    quartile_wr = df_temp.groupby('ec_quartile')['win_rate'].mean()
    axes[1, 0].bar(quartile_wr.index, quartile_wr.values, 
                   color=['#8B0000', '#FF4500', '#90EE90', '#006400'], 
                   edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Effective Count Quartile', fontsize=12)
    axes[1, 0].set_ylabel('Average Win Rate', fontsize=12)
    axes[1, 0].set_title('Win Rate by Effective Count Quartile')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    wr_by_quartile = [df_temp[df_temp['ec_quartile'] == q]['win_rate'].values 
                      for q in quartile_wr.index]
    bp = axes[1, 1].boxplot(wr_by_quartile, labels=quartile_wr.index, patch_artist=True)
    colors = ['#8B0000', '#FF4500', '#90EE90', '#006400']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1, 1].set_xlabel('Effective Count Quartile', fontsize=12)
    axes[1, 1].set_ylabel('Win Rate', fontsize=12)
    axes[1, 1].set_title('Win Rate Distribution by Effective Count Quartile')
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
    ec = df['effective_count']
    pnl = df['total_pnl']
    wr = df['win_rate']
    valid_mask = ec.notna() & pnl.notna() & wr.notna() & (wr > 0)
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Effective Count: Combined Performance Analysis', fontsize=16, fontweight='bold')
    
    df_temp = df[valid_mask].copy()
    df_temp['ec_decile'] = pd.qcut(df_temp['effective_count'], q=10, labels=False, duplicates='drop')
    
    decile_stats = df_temp.groupby('ec_decile').agg({
        'effective_count': 'mean',
        'total_pnl': 'mean',
        'win_rate': 'mean'
    }).reset_index()
    
    axes[0, 0].plot(decile_stats['ec_decile'], decile_stats['total_pnl'], 
                    marker='o', linewidth=2, markersize=8, color='#3498db')
    axes[0, 0].set_xlabel('Effective Count Decile', fontsize=12)
    axes[0, 0].set_ylabel('Average PnL', fontsize=12)
    axes[0, 0].set_title('PnL Trend by Effective Count Decile')
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(decile_stats['ec_decile'], decile_stats['win_rate'], 
                    marker='s', linewidth=2, markersize=8, color='#2ecc71')
    axes[0, 1].set_xlabel('Effective Count Decile', fontsize=12)
    axes[0, 1].set_ylabel('Average Win Rate', fontsize=12)
    axes[0, 1].set_title('Win Rate Trend by Effective Count Decile')
    axes[0, 1].grid(True, alpha=0.3)
    
    scatter = axes[0, 2].scatter(ec[valid_mask], pnl[valid_mask], 
                                  c=wr[valid_mask], cmap='RdYlGn', 
                                  alpha=0.6, s=30)
    plt.colorbar(scatter, ax=axes[0, 2], label='Win Rate')
    axes[0, 2].set_xlabel('Effective Count', fontsize=12)
    axes[0, 2].set_ylabel('Total PnL', fontsize=12)
    axes[0, 2].set_title('EC vs PnL (colored by Win Rate)')
    axes[0, 2].grid(True, alpha=0.3)
    
    df_temp['wr_category'] = pd.cut(df_temp['win_rate'], 
                                     bins=[0, 0.25, 0.5, 0.75, 1.0],
                                     labels=['0-25%', '25-50%', '50-75%', '75-100%'])
    
    for cat in df_temp['wr_category'].unique():
        subset = df_temp[df_temp['wr_category'] == cat]
        axes[1, 0].scatter(subset['effective_count'], subset['total_pnl'], 
                          alpha=0.5, s=30, label=f'WR: {cat}')
    axes[1, 0].set_xlabel('Effective Count', fontsize=12)
    axes[1, 0].set_ylabel('Total PnL', fontsize=12)
    axes[1, 0].set_title('EC vs PnL by Win Rate Category')
    axes[1, 0].legend(fontsize=9)
    axes[1, 0].grid(True, alpha=0.3)
    
    df_temp['ec_category'] = pd.qcut(df_temp['effective_count'], q=3, 
                                      labels=['Low EC', 'Medium EC', 'High EC'],
                                      duplicates='drop')
    
    ec_cats = df_temp['ec_category'].unique()
    for cat in ec_cats:
        subset = df_temp[df_temp['ec_category'] == cat]
        axes[1, 1].scatter(subset['win_rate'], subset['total_pnl'], 
                          alpha=0.5, s=30, label=cat)
    axes[1, 1].set_xlabel('Win Rate', fontsize=12)
    axes[1, 1].set_ylabel('Total PnL', fontsize=12)
    axes[1, 1].set_title('Win Rate vs PnL by EC Category')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    corr_matrix = df_temp[['effective_count', 'total_pnl', 'win_rate']].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                ax=axes[1, 2], fmt='.3f', square=True)
    axes[1, 2].set_title('Correlation Matrix')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig, corr_matrix


def get_effective_count_summary(df):
    ec = df['effective_count'].dropna()
    pnl = df['total_pnl'].dropna()
    wr = df['win_rate']
    wr_valid = wr[(wr > 0) & wr.notna()]
    
    valid_mask = df['effective_count'].notna() & df['total_pnl'].notna()
    corr_ec_pnl = df.loc[valid_mask, 'effective_count'].corr(df.loc[valid_mask, 'total_pnl'])
    
    valid_mask2 = df['effective_count'].notna() & df['win_rate'].notna() & (df['win_rate'] > 0)
    corr_ec_wr = df.loc[valid_mask2, 'effective_count'].corr(df.loc[valid_mask2, 'win_rate'])
    
    summary = {
        'effective_count': {
            'mean': ec.mean(),
            'median': ec.median(),
            'std': ec.std(),
            'min': ec.min(),
            'max': ec.max(),
            'count': len(ec)
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
            'ec_vs_pnl': corr_ec_pnl,
            'ec_vs_winrate': corr_ec_wr
        }
    }
    
    return summary


def generate_report(df, save=False, output_dir='data'):
    import os
    if save:
        os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("GENERATING EFFECTIVE COUNT ANALYSIS REPORT")
    print("="*80)
    print(f"Analyzing {len(df)} traders")
    
    figures = {}
    
    if save:
        path1 = f"{output_dir}/effective_count_distribution.png"
        path2 = f"{output_dir}/effective_count_vs_pnl.png"
        path3 = f"{output_dir}/effective_count_vs_winrate.png"
        path4 = f"{output_dir}/effective_count_combined.png"
    else:
        path1 = path2 = path3 = path4 = None
    
    fig1, stats1 = plot_effective_count_distribution(df, save=save, path=path1)
    fig2, stats2 = plot_effective_count_vs_pnl(df, save=save, path=path2)
    fig3, stats3 = plot_effective_count_vs_winrate(df, save=save, path=path3)
    fig4, stats4 = plot_combined_analysis(df, save=save, path=path4)
    
    figures['distribution'] = fig1
    figures['vs_pnl'] = fig2
    figures['vs_winrate'] = fig3
    figures['combined'] = fig4
    
    summary = get_effective_count_summary(df)
    
    print("\n" + "="*80)
    print("EFFECTIVE COUNT ANALYSIS COMPLETE")
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

