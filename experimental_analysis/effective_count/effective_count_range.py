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


def filter_by_effective_count(df, min_ec=9, max_ec=10):
    return df[(df['effective_count'] >= min_ec) & (df['effective_count'] <= max_ec)].copy()


def plot_pnl_distribution(df, figsize=(16, 5), save=False, path=None):
    pnl = df['total_pnl'].dropna()
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(f'PnL Distribution (EC 9-10, n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0].hist(pnl, bins=30, edgecolor='black', alpha=0.7, color='#2ecc71')
    axes[0].axvline(pnl.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: ${pnl.mean():,.2f}')
    axes[0].axvline(pnl.median(), color='blue', linestyle='--', linewidth=2, 
                    label=f'Median: ${pnl.median():,.2f}')
    axes[0].set_xlabel('Total PnL ($)', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('PnL Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    box = axes[1].boxplot(pnl, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#2ecc71')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Total PnL ($)', fontsize=12)
    axes[1].set_title('PnL Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    profitable = (pnl > 0).sum()
    unprofitable = (pnl <= 0).sum()
    axes[2].pie([profitable, unprofitable], labels=['Profitable', 'Unprofitable'],
                autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
    axes[2].set_title(f'Profitability ({profitable}/{len(pnl)} profitable)')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_winrate_distribution(df, figsize=(16, 5), save=False, path=None):
    wr = df['win_rate']
    wr_valid = wr[(wr > 0) & wr.notna()]
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(f'Win Rate Distribution (EC 9-10, n={len(df)})', fontsize=16, fontweight='bold')
    
    axes[0].hist(wr_valid, bins=30, edgecolor='black', alpha=0.7, color='#9b59b6')
    axes[0].axvline(wr_valid.mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean: {wr_valid.mean():.2%}')
    axes[0].axvline(wr_valid.median(), color='blue', linestyle='--', linewidth=2, 
                    label=f'Median: {wr_valid.median():.2%}')
    axes[0].set_xlabel('Win Rate', fontsize=12)
    axes[0].set_ylabel('Number of Traders', fontsize=12)
    axes[0].set_title('Win Rate Histogram')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    box = axes[1].boxplot(wr_valid, vert=True, patch_artist=True)
    box['boxes'][0].set_facecolor('#9b59b6')
    box['boxes'][0].set_alpha(0.7)
    axes[1].set_ylabel('Win Rate', fontsize=12)
    axes[1].set_title('Win Rate Box Plot')
    axes[1].grid(True, alpha=0.3)
    
    above_50 = (wr_valid > 0.5).sum()
    below_50 = (wr_valid <= 0.5).sum()
    axes[2].pie([above_50, below_50], labels=['>50% WR', '≤50% WR'],
                autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
    axes[2].set_title(f'Win Rate Split ({above_50}/{len(wr_valid)} above 50%)')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_pnl_vs_winrate(df, figsize=(14, 10), save=False, path=None):
    pnl = df['total_pnl']
    wr = df['win_rate']
    valid_mask = pnl.notna() & wr.notna() & (wr > 0)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(f'PnL vs Win Rate Analysis (EC 9-10, n={valid_mask.sum()})', fontsize=16, fontweight='bold')
    
    if valid_mask.sum() > 5:
        corr_p, p_val_p = pearsonr(wr[valid_mask], pnl[valid_mask])
        corr_s, p_val_s = spearmanr(wr[valid_mask], pnl[valid_mask])
        
        axes[0, 0].scatter(wr[valid_mask], pnl[valid_mask], alpha=0.6, s=50, color='#3498db')
        z = np.polyfit(wr[valid_mask], pnl[valid_mask], 1)
        p = np.poly1d(z)
        x_sorted = np.sort(wr[valid_mask])
        axes[0, 0].plot(x_sorted, p(x_sorted), "r--", linewidth=2, 
                       label=f'Pearson r={corr_p:.3f}\nSpearman ρ={corr_s:.3f}')
        axes[0, 0].set_xlabel('Win Rate', fontsize=12)
        axes[0, 0].set_ylabel('Total PnL ($)', fontsize=12)
        axes[0, 0].set_title('Win Rate vs PnL')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    pnl_clipped = pnl[valid_mask].clip(lower=pnl[valid_mask].quantile(0.1), 
                                        upper=pnl[valid_mask].quantile(0.9))
    axes[0, 1].scatter(wr[valid_mask], pnl_clipped, alpha=0.6, s=50, color='#e74c3c')
    axes[0, 1].set_xlabel('Win Rate', fontsize=12)
    axes[0, 1].set_ylabel('Total PnL (10-90 percentile)', fontsize=12)
    axes[0, 1].set_title('Win Rate vs PnL (Outliers Clipped)')
    axes[0, 1].grid(True, alpha=0.3)
    
    df_temp = df[valid_mask].copy()
    df_temp['wr_bin'] = pd.cut(df_temp['win_rate'], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                               labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'])
    
    bin_pnl = df_temp.groupby('wr_bin')['total_pnl'].agg(['mean', 'median', 'count'])
    x_pos = np.arange(len(bin_pnl))
    width = 0.35
    
    axes[1, 0].bar(x_pos - width/2, bin_pnl['mean'], width, 
                   label='Mean PnL', color='#3498db', edgecolor='black', alpha=0.7)
    axes[1, 0].bar(x_pos + width/2, bin_pnl['median'], width, 
                   label='Median PnL', color='#2ecc71', edgecolor='black', alpha=0.7)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(bin_pnl.index)
    axes[1, 0].set_xlabel('Win Rate Range', fontsize=12)
    axes[1, 0].set_ylabel('PnL ($)', fontsize=12)
    axes[1, 0].set_title('PnL by Win Rate Range')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    for i, (idx, row) in enumerate(bin_pnl.iterrows()):
        axes[1, 0].annotate(f'n={int(row["count"])}', (i, max(row['mean'], row['median'])), 
                           ha='center', va='bottom', fontsize=9)
    
    pnl_by_bin = [df_temp[df_temp['wr_bin'] == b]['total_pnl'].values 
                  for b in bin_pnl.index if len(df_temp[df_temp['wr_bin'] == b]) > 0]
    labels = [b for b in bin_pnl.index if len(df_temp[df_temp['wr_bin'] == b]) > 0]
    
    if len(pnl_by_bin) > 0:
        bp = axes[1, 1].boxplot(pnl_by_bin, labels=labels, patch_artist=True)
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(pnl_by_bin)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    axes[1, 1].set_xlabel('Win Rate Range', fontsize=12)
    axes[1, 1].set_ylabel('Total PnL ($)', fontsize=12)
    axes[1, 1].set_title('PnL Distribution by Win Rate Range')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_trader_characteristics(df, figsize=(16, 10), save=False, path=None):
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'Trader Characteristics (EC 9-10, n={len(df)})', fontsize=16, fontweight='bold')
    
    if 'smart_score' in df.columns:
        ss = df['smart_score'].dropna()
        axes[0, 0].hist(ss, bins=30, edgecolor='black', alpha=0.7, color='#f39c12')
        axes[0, 0].axvline(ss.mean(), color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {ss.mean():.1f}')
        axes[0, 0].set_xlabel('Smart Score', fontsize=12)
        axes[0, 0].set_ylabel('Count', fontsize=12)
        axes[0, 0].set_title('Smart Score Distribution')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    if 'num_markets' in df.columns:
        nm = df['num_markets'].dropna()
        axes[0, 1].hist(nm, bins=30, edgecolor='black', alpha=0.7, color='#1abc9c')
        axes[0, 1].axvline(nm.mean(), color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {nm.mean():.0f}')
        axes[0, 1].set_xlabel('Number of Markets', fontsize=12)
        axes[0, 1].set_ylabel('Count', fontsize=12)
        axes[0, 1].set_title('Markets Traded Distribution')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    if 'total_positions' in df.columns:
        tp = df['total_positions'].dropna()
        axes[0, 2].hist(tp, bins=30, edgecolor='black', alpha=0.7, color='#e67e22')
        axes[0, 2].axvline(tp.mean(), color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {tp.mean():.0f}')
        axes[0, 2].set_xlabel('Total Positions', fontsize=12)
        axes[0, 2].set_ylabel('Count', fontsize=12)
        axes[0, 2].set_title('Total Positions Distribution')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
    
    trader_type_cols = [c for c in df.columns if c.startswith('trader_type_')]
    if trader_type_cols:
        type_counts = df[trader_type_cols].sum().sort_values(ascending=True)
        type_counts.index = [c.replace('trader_type_', '').replace('_', ' ').title() 
                            for c in type_counts.index]
        axes[1, 0].barh(type_counts.index, type_counts.values, color='#3498db', alpha=0.7)
        axes[1, 0].set_xlabel('Count', fontsize=12)
        axes[1, 0].set_title('Trader Types')
        axes[1, 0].grid(True, alpha=0.3, axis='x')
    
    category_cols = [c for c in df.columns if c.startswith('most_traded_categories_')]
    if category_cols:
        cat_volumes = df[category_cols].sum().sort_values(ascending=True)
        cat_volumes.index = [c.replace('most_traded_categories_', '').title() 
                            for c in cat_volumes.index]
        axes[1, 1].barh(cat_volumes.index, cat_volumes.values, color='#9b59b6', alpha=0.7)
        axes[1, 1].set_xlabel('Total Volume', fontsize=12)
        axes[1, 1].set_title('Trading Categories')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
    
    corr_data = df[['effective_count', 'total_pnl', 'win_rate', 'smart_score', 'num_markets']].dropna()
    if len(corr_data) > 5:
        corr_matrix = corr_data.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                    ax=axes[1, 2], fmt='.2f', square=True)
        axes[1, 2].set_title('Correlation Matrix')
    
    plt.tight_layout()
    
    if save and path:
        fig.savefig(path, dpi=300, bbox_inches='tight')
    
    return fig


def get_summary(df):
    ec = df['effective_count'].dropna()
    pnl = df['total_pnl'].dropna()
    wr = df['win_rate']
    wr_valid = wr[(wr > 0) & wr.notna()]
    
    summary = {
        'count': len(df),
        'effective_count': {
            'mean': ec.mean(),
            'median': ec.median(),
            'min': ec.min(),
            'max': ec.max()
        },
        'total_pnl': {
            'mean': pnl.mean(),
            'median': pnl.median(),
            'std': pnl.std(),
            'profitable_count': (pnl > 0).sum(),
            'profitable_pct': (pnl > 0).mean() * 100
        },
        'win_rate': {
            'mean': wr_valid.mean(),
            'median': wr_valid.median(),
            'above_50_pct': (wr_valid > 0.5).mean() * 100
        }
    }
    
    return summary


def generate_report(df, min_ec=9, max_ec=10, output_dir='effective_count_9_10'):
    os.makedirs(output_dir, exist_ok=True)
    
    df_filtered = filter_by_effective_count(df, min_ec, max_ec)
    
    print("="*80)
    print(f"EFFECTIVE COUNT {min_ec}-{max_ec} ANALYSIS")
    print("="*80)
    print(f"Traders in range: {len(df_filtered)} / {len(df)} ({len(df_filtered)/len(df)*100:.1f}%)")
    
    plot_pnl_distribution(df_filtered, save=True, path=f"{output_dir}/pnl_distribution.png")
    plot_winrate_distribution(df_filtered, save=True, path=f"{output_dir}/winrate_distribution.png")
    plot_pnl_vs_winrate(df_filtered, save=True, path=f"{output_dir}/pnl_vs_winrate.png")
    plot_trader_characteristics(df_filtered, save=True, path=f"{output_dir}/trader_characteristics.png")
    
    summary = get_summary(df_filtered)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll figures saved to: {output_dir}/")
    
    return summary


if __name__ == '__main__':
    df = load_data()
    summary = generate_report(df, min_ec=9, max_ec=10, output_dir='effective_count_9_10')
    print("\nSummary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

