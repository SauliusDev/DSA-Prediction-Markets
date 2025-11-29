"""
EDA Part 2: Category Performance Analysis

This script analyzes trading performance across different market categories
(Politics, Crypto, Sports, etc.). We explore which categories are most profitable,
how traders specialize, and create 3D visualizations of category performance.

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("CATEGORY PERFORMANCE ANALYSIS")
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
print(f"✓ Loaded {len(df)} traders")

# Set up visualization directory
viz_dir = 'eda/visualizations/category_analysis' if os.path.exists('eda/visualizations') else 'visualizations/category_analysis'
os.makedirs(viz_dir, exist_ok=True)

# Define category features
category_volume_cols = [
    'most_traded_categories_politics', 'most_traded_categories_sport',
    'most_traded_categories_music', 'most_traded_categories_crypto',
    'most_traded_categories_mentions', 'most_traded_categories_weather',
    'most_traded_categories_culture', 'most_traded_categories_other'
]

category_winrate_cols = [
    'win_rate_categories_politics', 'win_rate_categories_sport',
    'win_rate_categories_music', 'win_rate_categories_crypto'
]

category_smartscore_cols = [
    'smart_score_categories_politics', 'smart_score_categories_sport',
    'smart_score_categories_music', 'smart_score_categories_crypto'
]

# ============================================================================
# SECTION 1: CATEGORY TRADING VOLUME ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("1. CATEGORY TRADING VOLUME ANALYSIS")
print("="*80)

# Calculate total volume per category
category_volumes = df[category_volume_cols].sum()
category_volumes.index = [col.replace('most_traded_categories_', '').title() for col in category_volumes.index]
category_volumes = category_volumes.sort_values(ascending=False)

print("\nTotal Trading Volume by Category:")
for cat, vol in category_volumes.items():
    pct = (vol / category_volumes.sum()) * 100
    print(f"  {cat:12s}: {vol:10,.0f} ({pct:5.1f}%)")

# Most popular categories
print(f"\nMost Popular Category: {category_volumes.index[0]} ({category_volumes.iloc[0]:,.0f} trades)")
print(f"Least Popular Category: {category_volumes.index[-1]} ({category_volumes.iloc[-1]:,.0f} trades)")

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Category Trading Volume Analysis', fontsize=16, fontweight='bold')

# Bar chart
colors = plt.cm.Set3(range(len(category_volumes)))
axes[0].bar(category_volumes.index, category_volumes.values, color=colors, edgecolor='black', alpha=0.8)
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
plt.savefig(f'{viz_dir}/category_volumes.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/category_volumes.png")

# ============================================================================
# SECTION 2: CATEGORY-SPECIFIC WIN RATES
# ============================================================================
print("\n" + "="*80)
print("2. CATEGORY-SPECIFIC WIN RATE ANALYSIS")
print("="*80)

# Calculate average win rates by category (excluding zeros/NaN)
category_winrates = {}
for col in category_winrate_cols:
    cat_name = col.replace('win_rate_categories_', '').title()
    # Filter out zeros and NaN
    valid_data = df[col][(df[col] > 0) & (df[col].notna())]
    if len(valid_data) > 0:
        category_winrates[cat_name] = {
            'mean': valid_data.mean(),
            'median': valid_data.median(),
            'std': valid_data.std(),
            'count': len(valid_data)
        }

print("\nAverage Win Rates by Category:")
for cat, stats in sorted(category_winrates.items(), key=lambda x: x[1]['mean'], reverse=True):
    print(f"  {cat:12s}: Mean={stats['mean']:.2%}, Median={stats['median']:.2%}, "
          f"Std={stats['std']:.2%} (n={stats['count']})")

# Find best and worst categories
best_cat = max(category_winrates.items(), key=lambda x: x[1]['mean'])
worst_cat = min(category_winrates.items(), key=lambda x: x[1]['mean'])

print(f"\nBest Performing Category: {best_cat[0]} (avg win rate: {best_cat[1]['mean']:.2%})")
print(f"Worst Performing Category: {worst_cat[0]} (avg win rate: {worst_cat[1]['mean']:.2%})")

# Visualization: Box plots comparing win rates across categories
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Win Rate Distribution by Category', fontsize=16, fontweight='bold')

for idx, col in enumerate(category_winrate_cols):
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

plt.tight_layout()
plt.savefig(f'{viz_dir}/category_winrates.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/category_winrates.png")

# ============================================================================
# SECTION 3: CATEGORY SPECIALIZATION ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3. CATEGORY SPECIALIZATION ANALYSIS")
print("="*80)

# Calculate specialization index using entropy
# Lower entropy = more specialized, Higher entropy = more diversified

def calculate_specialization_entropy(row):
    """Calculate entropy of category distribution (measure of diversification)"""
    volumes = row[category_volume_cols].values
    volumes = volumes[volumes > 0]  # Remove zeros
    if len(volumes) == 0:
        return np.nan
    # Normalize to probabilities and ensure float type
    probs = volumes.astype(float) / volumes.sum()
    return entropy(probs, base=2)  # Use base 2 for bits

df['specialization_entropy'] = df.apply(calculate_specialization_entropy, axis=1)

# Count number of categories each trader participates in
df['num_categories'] = (df[category_volume_cols] > 0).sum(axis=1)

print(f"\nSpecialization Statistics:")
print(f"  Average number of categories per trader: {df['num_categories'].mean():.2f}")
print(f"  Median number of categories: {df['num_categories'].median():.0f}")
print(f"  Max categories traded: {df['num_categories'].max():.0f}")

# Categorize traders
specialists = df[df['num_categories'] <= 2]
generalists = df[df['num_categories'] >= 5]
moderate = df[(df['num_categories'] > 2) & (df['num_categories'] < 5)]

print(f"\nTrader Distribution:")
print(f"  Specialists (≤2 categories): {len(specialists)} ({len(specialists)/len(df)*100:.1f}%)")
print(f"  Moderate (3-4 categories): {len(moderate)} ({len(moderate)/len(df)*100:.1f}%)")
print(f"  Generalists (≥5 categories): {len(generalists)} ({len(generalists)/len(df)*100:.1f}%)")

# Performance comparison
print(f"\nPerformance by Specialization Level:")
print(f"  Specialists - Avg Win Rate: {specialists['win_rate'].mean():.2%}, Avg PnL: ${specialists['total_pnl'].mean():,.2f}")
print(f"  Moderate    - Avg Win Rate: {moderate['win_rate'].mean():.2%}, Avg PnL: ${moderate['total_pnl'].mean():,.2f}")
print(f"  Generalists - Avg Win Rate: {generalists['win_rate'].mean():.2%}, Avg PnL: ${generalists['total_pnl'].mean():,.2f}")

# Correlation between specialization and performance
corr_spec_winrate = df['num_categories'].corr(df['win_rate'])
corr_spec_pnl = df['num_categories'].corr(df['total_pnl'])

print(f"\nCorrelation Analysis:")
print(f"  Number of categories vs Win Rate: {corr_spec_winrate:.3f}")
print(f"  Number of categories vs PnL: {corr_spec_pnl:.3f}")

# Visualization - Only one chart: Distribution of Category Diversification
fig, ax = plt.subplots(figsize=(12, 7))
fig.suptitle('Category Specialization Analysis', fontsize=16, fontweight='bold')

# Number of categories distribution
ax.hist(df['num_categories'], bins=range(1, df['num_categories'].max()+2), 
        edgecolor='black', alpha=0.7, color='steelblue')
ax.set_xlabel('Number of Categories Traded', fontsize=12)
ax.set_ylabel('Number of Traders', fontsize=12)
ax.set_title('Distribution of Category Diversification')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{viz_dir}/specialization_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/specialization_analysis.png")

# ============================================================================
# SECTION 4: CATEGORY-SPECIFIC SMART SCORES
# ============================================================================
print("\n" + "="*80)
print("4. CATEGORY-SPECIFIC SMART SCORE ANALYSIS")
print("="*80)

# Analyze smart scores by category
category_smartscores = {}
for col in category_smartscore_cols:
    cat_name = col.replace('smart_score_categories_', '').title()
    valid_data = df[col][(df[col].notna())]
    if len(valid_data) > 0:
        category_smartscores[cat_name] = {
            'mean': valid_data.mean(),
            'median': valid_data.median(),
            'std': valid_data.std(),
            'count': len(valid_data)
        }

print("\nAverage Smart Scores by Category:")
for cat, stats in sorted(category_smartscores.items(), key=lambda x: x[1]['mean'], reverse=True):
    print(f"  {cat:12s}: Mean={stats['mean']:.2f}, Median={stats['median']:.2f}, "
          f"Std={stats['std']:.2f} (n={stats['count']})")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("KEY FINDINGS SUMMARY")
print("="*80)

print(f"\n1. Category Popularity:")
print(f"   - Most traded: {category_volumes.index[0]} ({category_volumes.iloc[0]:,.0f} trades)")
print(f"   - Accounts for {(category_volumes.iloc[0]/category_volumes.sum())*100:.1f}% of all trading")

print(f"\n2. Category Profitability:")
if len(category_winrates) > 0:
    print(f"   - Best performing: {best_cat[0]} (avg win rate: {best_cat[1]['mean']:.2%})")
    print(f"   - Worst performing: {worst_cat[0]} (avg win rate: {worst_cat[1]['mean']:.2%})")

print(f"\n3. Specialization Insights:")
print(f"   - {len(specialists)/len(df)*100:.1f}% of traders are specialists (≤2 categories)")
print(f"   - Specialists avg win rate: {specialists['win_rate'].mean():.2%}")
print(f"   - Generalists avg win rate: {generalists['win_rate'].mean():.2%}")
if corr_spec_winrate > 0:
    print(f"   - More diversification correlates with HIGHER win rates")
else:
    print(f"   - More diversification correlates with LOWER win rates")

print(f"\n4. Smart Trader Category Preferences:")
# Determine primary category for analysis
def get_primary_category(row):
    """Determine trader's primary category"""
    volumes = row[category_volume_cols]
    if volumes.sum() == 0:
        return 'None'
    max_cat = volumes.idxmax()
    return max_cat.replace('most_traded_categories_', '').title()

df['primary_category'] = df.apply(get_primary_category, axis=1)
top_performers = df[df['smart_score'] > df['smart_score'].quantile(0.75)]
top_primary_cat = top_performers['primary_category'].value_counts().iloc[0]
print(f"   - Top 25% smart traders primarily trade in: {top_primary_cat}")

print("\n" + "="*80)
print(f"Analysis complete! Check the '{viz_dir}' folder for charts.")
print("="*80)

