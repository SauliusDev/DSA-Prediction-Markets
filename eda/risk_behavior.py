"""
EDA Part 4: Risk Behavior Analysis

This script analyzes trader betting probability preferences and risk-taking behavior.
We explore where traders place their bets on the probability spectrum (longshots vs safe bets)
and how these preferences correlate with performance.

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
print("RISK BEHAVIOR ANALYSIS")
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
viz_dir = 'eda/visualizations/risk_behavior' if os.path.exists('eda/visualizations') else 'visualizations/risk_behavior'
os.makedirs(viz_dir, exist_ok=True)

# Define betting pattern features
betting_pattern_features = [
    'trader_bets_0_0', 'trader_bets_0_1', 'trader_bets_0_2',
    'trader_bets_0_3', 'trader_bets_0_4', 'trader_bets_0_5',
    'trader_bets_0_6', 'trader_bets_0_7', 'trader_bets_0_8',
    'trader_bets_0_9'
]

# Probability range labels
prob_labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
               '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']

# ============================================================================
# SECTION 1: OVERALL BETTING PROBABILITY DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("1. BETTING PROBABILITY DISTRIBUTION")
print("="*80)

# Calculate total bets in each probability range
total_bets_by_range = df[betting_pattern_features].sum()
total_bets = total_bets_by_range.sum()

print("\nTotal Bets by Probability Range:")
for idx, (col, count) in enumerate(total_bets_by_range.items()):
    pct = (count / total_bets) * 100 if total_bets > 0 else 0
    print(f"  {prob_labels[idx]:10s}: {count:12,.0f} bets ({pct:5.1f}%)")

# Identify most and least popular ranges
max_range_idx = total_bets_by_range.argmax()
min_range_idx = total_bets_by_range.argmin()

print(f"\nMost Popular Range: {prob_labels[max_range_idx]} ({total_bets_by_range.iloc[max_range_idx]:,.0f} bets)")
print(f"Least Popular Range: {prob_labels[min_range_idx]} ({total_bets_by_range.iloc[min_range_idx]:,.0f} bets)")

# Categorize betting behavior
# Longshot hunters: >50% of bets in 0-20% range
# Safe players: >50% of bets in 80-100% range
# Balanced: everything else

def categorize_risk_profile(row):
    """Categorize trader based on betting patterns"""
    total = row[betting_pattern_features].sum()
    if total == 0:
        return 'Unknown'
    
    longshot_bets = row['trader_bets_0_0'] + row['trader_bets_0_1']
    safe_bets = row['trader_bets_0_8'] + row['trader_bets_0_9']
    
    longshot_pct = longshot_bets / total
    safe_pct = safe_bets / total
    
    if longshot_pct > 0.5:
        return 'Longshot Hunter'
    elif safe_pct > 0.5:
        return 'Safe Player'
    else:
        return 'Balanced'

df['risk_profile'] = df.apply(categorize_risk_profile, axis=1)

risk_profile_counts = df['risk_profile'].value_counts()
print(f"\nRisk Profile Distribution:")
for profile, count in risk_profile_counts.items():
    pct = (count / len(df)) * 100
    print(f"  {profile:20s}: {count:4d} traders ({pct:5.1f}%)")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Betting Probability Distribution Analysis', fontsize=16, fontweight='bold')

# Bar chart of total bets by range
colors = plt.cm.RdYlGn(np.linspace(0, 1, len(prob_labels)))
axes[0, 0].bar(prob_labels, total_bets_by_range.values, color=colors, edgecolor='black', alpha=0.8)
axes[0, 0].set_xlabel('Probability Range', fontsize=12)
axes[0, 0].set_ylabel('Total Number of Bets', fontsize=12)
axes[0, 0].set_title('Distribution of Bets Across Probability Ranges')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Pie chart
axes[0, 1].pie(total_bets_by_range.values, labels=prob_labels, autopct='%1.1f%%',
               colors=colors, startangle=90)
axes[0, 1].set_title('Bet Distribution by Probability Range')

# Risk profile distribution
profile_colors = {'Longshot Hunter': 'red', 'Balanced': 'orange', 'Safe Player': 'green', 'Unknown': 'gray'}
profile_color_list = [profile_colors.get(p, 'gray') for p in risk_profile_counts.index]
axes[1, 0].bar(risk_profile_counts.index, risk_profile_counts.values, 
               color=profile_color_list, edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Risk Profile', fontsize=12)
axes[1, 0].set_ylabel('Number of Traders', fontsize=12)
axes[1, 0].set_title('Trader Risk Profile Distribution')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Average betting pattern per trader
avg_bets_per_trader = df[betting_pattern_features].mean()
axes[1, 1].plot(prob_labels, avg_bets_per_trader.values, marker='o', linewidth=2, 
                markersize=8, color='steelblue')
axes[1, 1].set_xlabel('Probability Range', fontsize=12)
axes[1, 1].set_ylabel('Average Bets per Trader', fontsize=12)
axes[1, 1].set_title('Average Betting Pattern')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{viz_dir}/betting_probability_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/betting_probability_distribution.png")

# ============================================================================
# SECTION 2: DETAILED PROBABILITY RANGE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("2. DETAILED PROBABILITY RANGE ANALYSIS")
print("="*80)

# Calculate correlation between each probability range and performance
print("\nCorrelation: Betting in Each Range vs Win Rate:")
for idx, col in enumerate(betting_pattern_features):
    # Only consider traders who placed bets in this range
    traders_in_range = df[df[col] > 0]
    if len(traders_in_range) > 10:
        corr = traders_in_range[col].corr(traders_in_range['win_rate'])
        print(f"  {prob_labels[idx]:10s}: {corr:7.3f}")

# Analyze extreme behaviors
print("\nExtreme Betting Behaviors:")

# Longshot specialists (>80% of bets in 0-20% range)
df['longshot_pct'] = (df['trader_bets_0_0'] + df['trader_bets_0_1']) / df[betting_pattern_features].sum(axis=1)
longshot_specialists = df[df['longshot_pct'] > 0.8]
print(f"\nLongshot Specialists (>80% bets on 0-20% probability):")
print(f"  Count: {len(longshot_specialists)}")
if len(longshot_specialists) > 0:
    print(f"  Avg Win Rate: {longshot_specialists['win_rate'].mean():.2%}")
    print(f"  Avg PnL: ${longshot_specialists['total_pnl'].mean():,.2f}")

# Safe bet specialists (>80% of bets in 80-100% range)
df['safe_pct'] = (df['trader_bets_0_8'] + df['trader_bets_0_9']) / df[betting_pattern_features].sum(axis=1)
safe_specialists = df[df['safe_pct'] > 0.8]
print(f"\nSafe Bet Specialists (>80% bets on 80-100% probability):")
print(f"  Count: {len(safe_specialists)}")
if len(safe_specialists) > 0:
    print(f"  Avg Win Rate: {safe_specialists['win_rate'].mean():.2%}")
    print(f"  Avg PnL: ${safe_specialists['total_pnl'].mean():,.2f}")

# Middle range specialists (>60% of bets in 40-60% range)
df['middle_pct'] = (df['trader_bets_0_4'] + df['trader_bets_0_5']) / df[betting_pattern_features].sum(axis=1)
middle_specialists = df[df['middle_pct'] > 0.6]
print(f"\nMiddle Range Specialists (>60% bets on 40-60% probability):")
print(f"  Count: {len(middle_specialists)}")
if len(middle_specialists) > 0:
    print(f"  Avg Win Rate: {middle_specialists['win_rate'].mean():.2%}")
    print(f"  Avg PnL: ${middle_specialists['total_pnl'].mean():,.2f}")

# Visualization: Win Rate by Betting Probability Range (Box Plots)
fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle('Win Rate by Betting Probability Range', fontsize=16, fontweight='bold')

# For each probability range, get win rates of traders who bet in that range
winrate_by_prob_range = []
prob_range_labels = []

for idx, col in enumerate(betting_pattern_features):
    # Only include traders who placed bets in this range
    traders_in_range = df[df[col] > 0]
    if len(traders_in_range) >= 5:  # Minimum sample size
        winrate_by_prob_range.append(traders_in_range['win_rate'].values)
        prob_range_labels.append(prob_labels[idx])

# Create box plots
bp = ax.boxplot(winrate_by_prob_range, 
                labels=prob_range_labels,
                patch_artist=True,
                showmeans=True,
                meanline=True,
                widths=0.6)

# Color the boxes with a gradient (red to green)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(prob_range_labels)))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Customize the plot
ax.set_xlabel('Betting Probability Range', fontsize=14, fontweight='bold')
ax.set_ylabel('Win Rate', fontsize=14, fontweight='bold')
ax.set_title('Win Rate Distribution by Betting Probability Range', fontsize=14, pad=15)
ax.tick_params(axis='x', rotation=45, labelsize=11)
ax.tick_params(axis='y', labelsize=11)
ax.grid(True, alpha=0.3, axis='y')

# Add a horizontal line for overall average
ax.axhline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2, 
           alpha=0.7, label=f'Overall Avg: {df["win_rate"].mean():.2%}')
ax.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig(f'{viz_dir}/detailed_probability_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/detailed_probability_analysis.png")

print("\n" + "="*80)
print(f"Analysis complete! Check the '{viz_dir}' folder for charts.")
print("="*80)
