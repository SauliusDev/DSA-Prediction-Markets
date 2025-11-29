"""
EDA Part 1: Performance Distribution Analysis

This script analyzes the overall performance distribution of Polymarket traders.
We examine win rates, PnL, smart scores, and identify what separates successful
traders from unsuccessful ones.

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("POLYMARKET TRADER PERFORMANCE ANALYSIS")
print("="*80)
print("\nLoading data...")

# Load data (handle both running from eda/ and from project root)
import os
if os.path.exists('data/users_data.csv'):
    data_path = 'data/users_data.csv'
elif os.path.exists('../data/users_data.csv'):
    data_path = '../data/users_data.csv'
else:
    raise FileNotFoundError("Could not find users_data.csv. Please run from project root or eda/ directory.")

df = pd.read_csv(data_path)
print(f"✓ Loaded {len(df)} traders with {df.shape[1]} features")

# ============================================================================
# SECTION 1: WIN RATE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("1. WIN RATE DISTRIBUTION ANALYSIS")
print("="*80)

print("\nBasic Statistics:")
print(f"  Mean win rate: {df['win_rate'].mean():.2%}")
print(f"  Median win rate: {df['win_rate'].median():.2%}")
print(f"  Std deviation: {df['win_rate'].std():.2%}")
print(f"  Min: {df['win_rate'].min():.2%}")
print(f"  Max: {df['win_rate'].max():.2%}")

# Quartile analysis
q1 = df['win_rate'].quantile(0.25)
q2 = df['win_rate'].quantile(0.50)
q3 = df['win_rate'].quantile(0.75)

print(f"\nQuartiles:")
print(f"  Q1 (25th percentile): {q1:.2%}")
print(f"  Q2 (50th percentile): {q2:.2%}")
print(f"  Q3 (75th percentile): {q3:.2%}")

# Identify outliers
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outliers_low = df[df['win_rate'] < lower_bound]
outliers_high = df[df['win_rate'] > upper_bound]

print(f"\nOutliers:")
print(f"  Exceptionally low performers: {len(outliers_low)} traders (win rate < {lower_bound:.2%})")
print(f"  Exceptionally high performers: {len(outliers_high)} traders (win rate > {upper_bound:.2%})")

# Create win rate visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Win Rate Distribution Analysis', fontsize=16, fontweight='bold')

# Histogram
axes[0].hist(df['win_rate'], bins=40, edgecolor='black', alpha=0.7, color='steelblue')
axes[0].axvline(df['win_rate'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["win_rate"].mean():.2%}')
axes[0].axvline(df['win_rate'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: {df["win_rate"].median():.2%}')
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
axes[2].axvline(df['win_rate'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["win_rate"].mean():.2%}')
axes[2].set_xlabel('Win Rate', fontsize=12)
axes[2].set_ylabel('Density', fontsize=12)
axes[2].set_title('Win Rate Density Plot')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
# Save to correct path
viz_dir = 'eda/visualizations/performance_distribution' if os.path.exists('eda/visualizations') else 'visualizations/performance_distribution'
os.makedirs(viz_dir, exist_ok=True)
plt.savefig(f'{viz_dir}/win_rate_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/win_rate_distribution.png")

# ============================================================================
# SECTION 2: SMART SCORE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("2. SMART SCORE ANALYSIS")
print("="*80)

print(f"\nSmart Score Statistics:")
print(f"  Mean: {df['smart_score'].mean():.2f}")
print(f"  Median: {df['smart_score'].median():.2f}")
print(f"  Std deviation: {df['smart_score'].std():.2f}")
print(f"  Min: {df['smart_score'].min():.2f}")
print(f"  Max: {df['smart_score'].max():.2f}")

# Smart score distribution
print(f"\nSmart Score Distribution:")
for pct in [10, 25, 50, 75, 90]:
    val = df['smart_score'].quantile(pct/100)
    print(f"  {pct}th percentile: {val:.2f}")

# Correlation analysis: Smart Score vs Performance
corr_score_winrate = df['smart_score'].corr(df['win_rate'])
corr_score_pnl = df['smart_score'].corr(df['total_pnl'])

print(f"\nCorrelation Analysis:")
print(f"  Smart Score vs Win Rate: {corr_score_winrate:.3f}")
print(f"  Smart Score vs Total PnL: {corr_score_pnl:.3f}")

# Statistical significance test
from scipy.stats import pearsonr
r_winrate, p_winrate = pearsonr(df['smart_score'], df['win_rate'])
r_pnl, p_pnl = pearsonr(df['smart_score'], df['total_pnl'])

print(f"\nStatistical Significance:")
print(f"  Smart Score vs Win Rate: r={r_winrate:.3f}, p-value={p_winrate:.4f}")
if p_winrate < 0.05:
    print(f"    → Statistically significant correlation!")
else:
    print(f"    → Not statistically significant")
    
print(f"  Smart Score vs PnL: r={r_pnl:.3f}, p-value={p_pnl:.4f}")
if p_pnl < 0.05:
    print(f"    → Statistically significant correlation!")
else:
    print(f"    → Not statistically significant")

# Smart Score Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Smart Score Analysis', fontsize=16, fontweight='bold')

# Use 10th percentile as minimum (to exclude extreme outliers) and 100 as max
score_min = df['smart_score'].quantile(0.10)  # 10th percentile
score_max = 100  # Fixed maximum

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

# Smart Score vs PnL (remove extreme outliers for better visualization)
pnl_threshold = df['total_pnl'].quantile(0.995)  # Remove top 0.5%
df_pnl_filtered = df[df['total_pnl'] <= pnl_threshold]
axes[1, 0].scatter(df_pnl_filtered['smart_score'], df_pnl_filtered['total_pnl'], alpha=0.5, s=30, color='green')
z = np.polyfit(df_pnl_filtered['smart_score'], df_pnl_filtered['total_pnl'], 1)
p = np.poly1d(z)
axes[1, 0].plot(df_pnl_filtered['smart_score'].sort_values(), p(df_pnl_filtered['smart_score'].sort_values()), 
                "r--", linewidth=2, label=f'Correlation: {corr_score_pnl:.3f}')
axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=1)
axes[1, 0].set_xlabel('Smart Score', fontsize=12)
axes[1, 0].set_ylabel('Total PnL ($)', fontsize=12)
axes[1, 0].set_title('Smart Score vs Total PnL (top 0.5% excluded)')
axes[1, 0].set_xlim(score_min - 2, score_max + 2)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Performance by Smart Score Quartile
df['score_quartile'] = pd.qcut(df['smart_score'], q=4, labels=['Q1\n(Lowest)', 'Q2', 'Q3', 'Q4\n(Highest)'])
quartile_winrates = df.groupby('score_quartile')['win_rate'].mean()
axes[1, 1].bar(quartile_winrates.index, quartile_winrates.values, 
               color=['red', 'orange', 'lightgreen', 'darkgreen'], edgecolor='black', alpha=0.7)
axes[1, 1].set_xlabel('Smart Score Quartile', fontsize=12)
axes[1, 1].set_ylabel('Average Win Rate', fontsize=12)
axes[1, 1].set_title('Win Rate by Smart Score Quartile')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{viz_dir}/smart_score_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/smart_score_analysis.png")

print("\n" + "="*80)
print(f"Analysis complete! Check the '{viz_dir}' folder for charts.")
print("="*80)