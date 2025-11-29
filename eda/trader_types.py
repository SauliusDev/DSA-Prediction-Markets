"""
EDA Part 3: Trader Type Comparison Analysis

This script analyzes different trader types (contrarian, bagholder, trend follower, etc.)
and compares their performance. We explore which trading styles are most successful
and analyze type combinations.

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("TRADER TYPE COMPARISON ANALYSIS")
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
viz_dir = 'eda/visualizations/trader_types' if os.path.exists('eda/visualizations') else 'visualizations/trader_types'
os.makedirs(viz_dir, exist_ok=True)

# Define trader type features
trader_type_features = [
    'trader_type_bagholder', 'trader_type_contrarian',
    'trader_type_lottery_ticket', 'trader_type_new',
    'trader_type_novice', 'trader_type_reverse_cramer',
    'trader_type_senior', 'trader_type_trend_follower',
    'trader_type_veteran', 'trader_type_waiting_for_the_money',
    'trader_type_whale_splash'
]

# Clean type names for display
type_display_names = {
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

# ============================================================================
# SECTION 1: TRADER TYPE PREVALENCE
# ============================================================================
print("\n" + "="*80)
print("1. TRADER TYPE PREVALENCE")
print("="*80)

# Count traders of each type
type_counts = {}
for col in trader_type_features:
    type_name = type_display_names[col]
    count = df[col].sum()
    pct = (count / len(df)) * 100
    type_counts[type_name] = {'count': count, 'percentage': pct}

# Sort by count
type_counts_sorted = dict(sorted(type_counts.items(), key=lambda x: x[1]['count'], reverse=True))

print("\nTrader Type Distribution:")
for type_name, type_stats in type_counts_sorted.items():
    print(f"  {type_name:20s}: {type_stats['count']:4d} traders ({type_stats['percentage']:5.1f}%)")

# Check how many types each trader has
df['num_types'] = df[trader_type_features].sum(axis=1)
print(f"\nTypes per Trader:")
print(f"  Average: {df['num_types'].mean():.2f} types")
print(f"  Median: {df['num_types'].median():.0f} types")
print(f"  Max: {df['num_types'].max():.0f} types")

# Distribution of number of types
type_count_dist = df['num_types'].value_counts().sort_index()
print(f"\nDistribution:")
for num_types, count in type_count_dist.items():
    pct = (count / len(df)) * 100
    print(f"  {int(num_types)} type(s): {count} traders ({pct:.1f}%)")

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Trader Type Prevalence', fontsize=16, fontweight='bold')

# Bar chart of type counts
type_names = list(type_counts_sorted.keys())
type_values = [v['count'] for v in type_counts_sorted.values()]
colors = plt.cm.Set3(range(len(type_names)))

axes[0].barh(type_names, type_values, color=colors, edgecolor='black', alpha=0.8)
axes[0].set_xlabel('Number of Traders', fontsize=12)
axes[0].set_ylabel('Trader Type', fontsize=12)
axes[0].set_title('Trader Type Distribution')
axes[0].grid(True, alpha=0.3, axis='x')

# Distribution of number of types per trader
axes[1].bar(type_count_dist.index, type_count_dist.values, color='steelblue', edgecolor='black', alpha=0.7)
axes[1].set_xlabel('Number of Types per Trader', fontsize=12)
axes[1].set_ylabel('Number of Traders', fontsize=12)
axes[1].set_title('Distribution of Types per Trader')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{viz_dir}/trader_type_prevalence.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/trader_type_prevalence.png")

# ============================================================================
# SECTION 2: PERFORMANCE BY TRADER TYPE
# ============================================================================
print("\n" + "="*80)
print("2. PERFORMANCE BY TRADER TYPE")
print("="*80)

# Calculate performance metrics for each type
type_performance = {}

for col in trader_type_features:
    type_name = type_display_names[col]
    type_traders = df[df[col] == 1]
    
    if len(type_traders) > 0:
        type_performance[type_name] = {
            'count': len(type_traders),
            'avg_winrate': type_traders['win_rate'].mean(),
            'median_winrate': type_traders['win_rate'].median(),
            'avg_pnl': type_traders['total_pnl'].mean(),
            'median_pnl': type_traders['total_pnl'].median(),
            'avg_smart_score': type_traders['smart_score'].mean(),
            'profitable_pct': (type_traders['total_pnl'] > 0).sum() / len(type_traders) * 100
        }

# Sort by average win rate
type_performance_sorted = dict(sorted(type_performance.items(), 
                                     key=lambda x: x[1]['avg_winrate'], 
                                     reverse=True))

print("\nPerformance Metrics by Trader Type (sorted by win rate):")
print(f"{'Type':20s} {'Count':>6s} {'Avg WR':>8s} {'Med WR':>8s} {'Avg PnL':>12s} {'Profitable':>11s}")
print("-" * 80)
for type_name, perf_stats in type_performance_sorted.items():
    print(f"{type_name:20s} {perf_stats['count']:6d} {perf_stats['avg_winrate']:7.2%} "
          f"{perf_stats['median_winrate']:7.2%} ${perf_stats['avg_pnl']:10,.2f} {perf_stats['profitable_pct']:10.1f}%")

# Identify best and worst performing types
best_type = list(type_performance_sorted.keys())[0]
worst_type = list(type_performance_sorted.keys())[-1]

print(f"\nBest Performing Type: {best_type}")
print(f"  Average Win Rate: {type_performance_sorted[best_type]['avg_winrate']:.2%}")
print(f"  Average PnL: ${type_performance_sorted[best_type]['avg_pnl']:,.2f}")

print(f"\nWorst Performing Type: {worst_type}")
print(f"  Average Win Rate: {type_performance_sorted[worst_type]['avg_winrate']:.2%}")
print(f"  Average PnL: ${type_performance_sorted[worst_type]['avg_pnl']:,.2f}")

# Statistical test: ANOVA to see if differences are significant
# Prepare data for ANOVA
groups_winrate = []
group_labels = []
for col in trader_type_features:
    type_traders = df[df[col] == 1]
    if len(type_traders) >= 10:  # Only include types with sufficient sample size
        groups_winrate.append(type_traders['win_rate'].values)
        group_labels.append(type_display_names[col])

if len(groups_winrate) > 2:
    f_stat, p_value = stats.f_oneway(*groups_winrate)
    print(f"\nANOVA Test (Win Rate across Trader Types):")
    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  P-value: {p_value:.6f}")
    if p_value < 0.05:
        print(f"  → Statistically significant difference detected! (p < 0.05)")
    else:
        print(f"  → No statistically significant difference (p ≥ 0.05)")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Performance by Trader Type', fontsize=16, fontweight='bold')

# Win rate by type
type_names_perf = list(type_performance_sorted.keys())
avg_winrates = [v['avg_winrate'] for v in type_performance_sorted.values()]
colors_perf = ['green' if wr > df['win_rate'].mean() else 'red' for wr in avg_winrates]

axes[0, 0].barh(type_names_perf, avg_winrates, color=colors_perf, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
                   label=f'Overall Avg: {df["win_rate"].mean():.2%}')
axes[0, 0].set_xlabel('Average Win Rate', fontsize=12)
axes[0, 0].set_ylabel('Trader Type', fontsize=12)
axes[0, 0].set_title('Average Win Rate by Type')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='x')

# PnL by type
avg_pnls = [v['avg_pnl'] for v in type_performance_sorted.values()]
colors_pnl = ['green' if pnl > 0 else 'red' for pnl in avg_pnls]

axes[0, 1].barh(type_names_perf, avg_pnls, color=colors_pnl, edgecolor='black', alpha=0.7)
axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=2)
axes[0, 1].set_xlabel('Average PnL ($)', fontsize=12)
axes[0, 1].set_ylabel('Trader Type', fontsize=12)
axes[0, 1].set_title('Average PnL by Type')
axes[0, 1].grid(True, alpha=0.3, axis='x')

# Box plot comparison (top 5 most common types)
top_5_types = list(type_counts_sorted.keys())[:5]
winrate_data = []
labels = []
for type_name in top_5_types:
    col = [k for k, v in type_display_names.items() if v == type_name][0]
    type_traders = df[df[col] == 1]
    winrate_data.append(type_traders['win_rate'].values)
    labels.append(type_name)

bp = axes[1, 0].boxplot(winrate_data, labels=labels, patch_artist=True)
for patch, color in zip(bp['boxes'], plt.cm.Set3(range(len(labels)))):
    patch.set_facecolor(color)
axes[1, 0].set_ylabel('Win Rate', fontsize=12)
axes[1, 0].set_title('Win Rate Distribution (Top 5 Types)')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Profitable percentage by type
profitable_pcts = [v['profitable_pct'] for v in type_performance_sorted.values()]
axes[1, 1].barh(type_names_perf, profitable_pcts, color='lightgreen', edgecolor='black', alpha=0.7)
axes[1, 1].axvline(50, color='red', linestyle='--', linewidth=2, label='50% threshold')
axes[1, 1].set_xlabel('Percentage Profitable (%)', fontsize=12)
axes[1, 1].set_ylabel('Trader Type', fontsize=12)
axes[1, 1].set_title('Percentage of Profitable Traders by Type')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(f'{viz_dir}/performance_by_type.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/performance_by_type.png")

# ============================================================================
# SECTION 3: TRADER TYPE COMBINATIONS
# ============================================================================
print("\n" + "="*80)
print("3. TRADER TYPE COMBINATIONS ANALYSIS")
print("="*80)

# Create co-occurrence matrix
cooccurrence = pd.DataFrame(0, index=trader_type_features, columns=trader_type_features)

for i, type1 in enumerate(trader_type_features):
    for j, type2 in enumerate(trader_type_features):
        if i != j:
            # Count traders who have both types
            both = ((df[type1] == 1) & (df[type2] == 1)).sum()
            cooccurrence.loc[type1, type2] = both

# Rename for display
cooccurrence.index = [type_display_names[t] for t in cooccurrence.index]
cooccurrence.columns = [type_display_names[t] for t in cooccurrence.columns]

print("\nMost Common Type Combinations:")
# Get top combinations
combinations = []
for i in range(len(cooccurrence)):
    for j in range(i+1, len(cooccurrence)):
        count = cooccurrence.iloc[i, j]
        if count > 0:
            combinations.append((cooccurrence.index[i], cooccurrence.columns[j], count))

combinations_sorted = sorted(combinations, key=lambda x: x[2], reverse=True)[:10]
for idx, (type1, type2, count) in enumerate(combinations_sorted, 1):
    print(f"  {idx:2d}. {type1} + {type2}: {count} traders")

# Analyze performance of combinations
print("\nPerformance of Top Combinations:")
for type1, type2, count in combinations_sorted[:5]:
    col1 = [k for k, v in type_display_names.items() if v == type1][0]
    col2 = [k for k, v in type_display_names.items() if v == type2][0]
    combo_traders = df[(df[col1] == 1) & (df[col2] == 1)]
    if len(combo_traders) > 0:
        print(f"\n  {type1} + {type2}:")
        print(f"    Count: {len(combo_traders)}")
        print(f"    Avg Win Rate: {combo_traders['win_rate'].mean():.2%}")
        print(f"    Avg PnL: ${combo_traders['total_pnl'].mean():,.2f}")

# Visualization: Heatmap of co-occurrence
fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(cooccurrence, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Number of Traders'}, ax=ax)
ax.set_title('Trader Type Co-occurrence Matrix', fontsize=14, fontweight='bold')
ax.set_xlabel('Trader Type', fontsize=12)
ax.set_ylabel('Trader Type', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{viz_dir}/type_cooccurrence.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/type_cooccurrence.png")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("KEY FINDINGS SUMMARY")
print("="*80)

print(f"\n1. Type Prevalence:")
most_common = list(type_counts_sorted.keys())[0]
least_common = list(type_counts_sorted.keys())[-1]
print(f"   - Most common type: {most_common} ({type_counts_sorted[most_common]['count']} traders)")
print(f"   - Least common type: {least_common} ({type_counts_sorted[least_common]['count']} traders)")
print(f"   - Average types per trader: {df['num_types'].mean():.2f}")

print(f"\n2. Performance Rankings:")
print(f"   - Best performing: {best_type} (avg win rate: {type_performance_sorted[best_type]['avg_winrate']:.2%})")
print(f"   - Worst performing: {worst_type} (avg win rate: {type_performance_sorted[worst_type]['avg_winrate']:.2%})")

if 'p_value' in locals() and p_value < 0.05:
    print(f"\n3. Statistical Significance:")
    print(f"   - ANOVA test shows SIGNIFICANT differences between types (p={p_value:.4f})")
    print(f"   - Trader type DOES matter for performance!")
else:
    print(f"\n3. Statistical Significance:")
    print(f"   - No statistically significant difference detected")

print(f"\n4. Type Combinations:")
if len(combinations_sorted) > 0:
    top_combo = combinations_sorted[0]
    print(f"   - Most common combination: {top_combo[0]} + {top_combo[1]} ({top_combo[2]} traders)")

print("\n" + "="*80)
print(f"Analysis complete! Check the '{viz_dir}' folder for charts.")
print("="*80)

