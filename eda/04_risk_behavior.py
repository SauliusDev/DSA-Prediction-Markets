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
viz_dir = 'eda/visualizations' if os.path.exists('eda/visualizations') else 'visualizations'
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
plt.savefig(f'{viz_dir}/14_betting_probability_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/14_betting_probability_distribution.png")

# ============================================================================
# SECTION 2: RISK PROFILE VS PERFORMANCE
# ============================================================================
print("\n" + "="*80)
print("2. RISK PROFILE VS PERFORMANCE")
print("="*80)

# Analyze performance by risk profile
risk_performance = df[df['risk_profile'] != 'Unknown'].groupby('risk_profile').agg({
    'win_rate': ['mean', 'median', 'std'],
    'total_pnl': ['mean', 'median', 'std'],
    'smart_score': ['mean', 'median'],
    'user_address': 'count'
}).round(4)

print("\nPerformance by Risk Profile:")
print(risk_performance)

# Detailed comparison
for profile in ['Longshot Hunter', 'Balanced', 'Safe Player']:
    if profile in df['risk_profile'].values:
        traders = df[df['risk_profile'] == profile]
        profitable_pct = (traders['total_pnl'] > 0).sum() / len(traders) * 100
        
        print(f"\n{profile}:")
        print(f"  Count: {len(traders)}")
        print(f"  Avg Win Rate: {traders['win_rate'].mean():.2%}")
        print(f"  Median Win Rate: {traders['win_rate'].median():.2%}")
        print(f"  Avg PnL: ${traders['total_pnl'].mean():,.2f}")
        print(f"  Median PnL: ${traders['total_pnl'].median():,.2f}")
        print(f"  Avg Smart Score: {traders['smart_score'].mean():.2f}")
        print(f"  Profitable: {profitable_pct:.1f}%")

# Statistical test: ANOVA
profiles_for_test = ['Longshot Hunter', 'Balanced', 'Safe Player']
groups_winrate = []
for profile in profiles_for_test:
    if profile in df['risk_profile'].values:
        traders = df[df['risk_profile'] == profile]
        if len(traders) >= 10:
            groups_winrate.append(traders['win_rate'].values)

if len(groups_winrate) >= 2:
    f_stat, p_value = stats.f_oneway(*groups_winrate)
    print(f"\nANOVA Test (Win Rate across Risk Profiles):")
    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  P-value: {p_value:.6f}")
    if p_value < 0.05:
        print(f"  → Statistically significant difference! (p < 0.05)")
    else:
        print(f"  → No statistically significant difference (p ≥ 0.05)")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Performance by Risk Profile', fontsize=16, fontweight='bold')

# Win rate comparison
profiles = ['Longshot Hunter', 'Balanced', 'Safe Player']
avg_winrates = [df[df['risk_profile'] == p]['win_rate'].mean() for p in profiles]
colors_perf = ['red', 'orange', 'green']

axes[0, 0].bar(profiles, avg_winrates, color=colors_perf, edgecolor='black', alpha=0.7)
axes[0, 0].axhline(df['win_rate'].mean(), color='blue', linestyle='--', linewidth=2,
                   label=f'Overall Avg: {df["win_rate"].mean():.2%}')
axes[0, 0].set_ylabel('Average Win Rate', fontsize=12)
axes[0, 0].set_title('Win Rate by Risk Profile')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='y')

# PnL comparison
avg_pnls = [df[df['risk_profile'] == p]['total_pnl'].mean() for p in profiles]
axes[0, 1].bar(profiles, avg_pnls, color=colors_perf, edgecolor='black', alpha=0.7)
axes[0, 1].axhline(0, color='black', linestyle='-', linewidth=2)
axes[0, 1].set_ylabel('Average PnL ($)', fontsize=12)
axes[0, 1].set_title('PnL by Risk Profile')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Box plot comparison
winrate_data = []
for profile in profiles:
    traders = df[df['risk_profile'] == profile]
    winrate_data.append(traders['win_rate'].values)

bp = axes[1, 0].boxplot(winrate_data, labels=profiles, patch_artist=True)
for patch, color in zip(bp['boxes'], colors_perf):
    patch.set_facecolor(color)
axes[1, 0].set_ylabel('Win Rate', fontsize=12)
axes[1, 0].set_title('Win Rate Distribution by Risk Profile')
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Smart score comparison
avg_scores = [df[df['risk_profile'] == p]['smart_score'].mean() for p in profiles]
axes[1, 1].bar(profiles, avg_scores, color=colors_perf, edgecolor='black', alpha=0.7)
axes[1, 1].set_ylabel('Average Smart Score', fontsize=12)
axes[1, 1].set_title('Smart Score by Risk Profile')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{viz_dir}/15_performance_by_risk_profile.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/15_performance_by_risk_profile.png")

# ============================================================================
# SECTION 3: DETAILED PROBABILITY RANGE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3. DETAILED PROBABILITY RANGE ANALYSIS")
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

# Visualization: Heatmap of betting patterns
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
fig.suptitle('Detailed Probability Range Analysis', fontsize=16, fontweight='bold')

# Heatmap: Top performers vs betting patterns
top_performers = df.nlargest(100, 'win_rate')
bottom_performers = df.nsmallest(100, 'win_rate')

top_avg_pattern = top_performers[betting_pattern_features].mean()
bottom_avg_pattern = bottom_performers[betting_pattern_features].mean()
overall_avg_pattern = df[betting_pattern_features].mean()

pattern_comparison = pd.DataFrame({
    'Top 100': top_avg_pattern.values,
    'Bottom 100': bottom_avg_pattern.values,
    'Overall': overall_avg_pattern.values
}, index=prob_labels)

pattern_comparison.T.plot(kind='bar', ax=axes[0], width=0.8)
axes[0].set_xlabel('Trader Group', fontsize=12)
axes[0].set_ylabel('Average Bets', fontsize=12)
axes[0].set_title('Betting Patterns: Top vs Bottom Performers')
axes[0].legend(title='Probability Range', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0].tick_params(axis='x', rotation=0)
axes[0].grid(True, alpha=0.3, axis='y')

# Scatter: Longshot % vs Win Rate
axes[1].scatter(df['longshot_pct'], df['win_rate'], alpha=0.5, s=30)
z = np.polyfit(df['longshot_pct'].fillna(0), df['win_rate'], 1)
p = np.poly1d(z)
x_line = np.linspace(0, 1, 100)
axes[1].plot(x_line, p(x_line), "r--", linewidth=2, 
             label=f'Correlation: {df["longshot_pct"].corr(df["win_rate"]):.3f}')
axes[1].set_xlabel('Longshot Percentage (0-20% bets)', fontsize=12)
axes[1].set_ylabel('Win Rate', fontsize=12)
axes[1].set_title('Longshot Betting vs Win Rate')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{viz_dir}/16_detailed_probability_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/16_detailed_probability_analysis.png")

# ============================================================================
# SECTION 4: RISK-ADJUSTED PERFORMANCE
# ============================================================================
print("\n" + "="*80)
print("4. RISK-ADJUSTED PERFORMANCE ANALYSIS")
print("="*80)

# Calculate risk metrics
# Risk score: Higher = more risky (more bets on extremes)
df['risk_score'] = (df['trader_bets_0_0'] + df['trader_bets_0_1'] + 
                    df['trader_bets_0_8'] + df['trader_bets_0_9']) / df[betting_pattern_features].sum(axis=1)

# Categorize by risk level
df['risk_level'] = pd.qcut(df['risk_score'].fillna(0), q=3, labels=['Low Risk', 'Medium Risk', 'High Risk'], 
                            duplicates='drop')

print("\nPerformance by Risk Level:")
for risk_level in ['Low Risk', 'Medium Risk', 'High Risk']:
    traders = df[df['risk_level'] == risk_level]
    if len(traders) > 0:
        print(f"\n{risk_level} ({len(traders)} traders):")
        print(f"  Avg Win Rate: {traders['win_rate'].mean():.2%}")
        print(f"  Avg PnL: ${traders['total_pnl'].mean():,.2f}")
        print(f"  Avg Smart Score: {traders['smart_score'].mean():.2f}")

# Correlation
corr_risk_winrate = df['risk_score'].corr(df['win_rate'])
corr_risk_pnl = df['risk_score'].corr(df['total_pnl'])

print(f"\nCorrelation Analysis:")
print(f"  Risk Score vs Win Rate: {corr_risk_winrate:.3f}")
print(f"  Risk Score vs PnL: {corr_risk_pnl:.3f}")

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Risk-Adjusted Performance', fontsize=16, fontweight='bold')

# Risk level performance
risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
risk_winrates = [df[df['risk_level'] == r]['win_rate'].mean() for r in risk_levels if r in df['risk_level'].values]
risk_colors = ['green', 'orange', 'red']

axes[0].bar(risk_levels[:len(risk_winrates)], risk_winrates, color=risk_colors[:len(risk_winrates)], 
            edgecolor='black', alpha=0.7)
axes[0].set_ylabel('Average Win Rate', fontsize=12)
axes[0].set_title('Win Rate by Risk Level')
axes[0].grid(True, alpha=0.3, axis='y')

# Risk score vs Win rate scatter
axes[1].scatter(df['risk_score'], df['win_rate'], alpha=0.5, s=30)
z = np.polyfit(df['risk_score'].fillna(0), df['win_rate'], 1)
p = np.poly1d(z)
x_line = np.linspace(0, 1, 100)
axes[1].plot(x_line, p(x_line), "r--", linewidth=2, label=f'Correlation: {corr_risk_winrate:.3f}')
axes[1].set_xlabel('Risk Score (0=Low, 1=High)', fontsize=12)
axes[1].set_ylabel('Win Rate', fontsize=12)
axes[1].set_title('Risk Score vs Win Rate')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{viz_dir}/17_risk_adjusted_performance.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved visualization: {viz_dir}/17_risk_adjusted_performance.png")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("KEY FINDINGS SUMMARY")
print("="*80)

print(f"\n1. Betting Preferences:")
print(f"   - Most popular range: {prob_labels[max_range_idx]} ({(total_bets_by_range.iloc[max_range_idx]/total_bets)*100:.1f}% of bets)")
print(f"   - {risk_profile_counts.get('Longshot Hunter', 0)} traders are longshot hunters")
print(f"   - {risk_profile_counts.get('Safe Player', 0)} traders are safe players")
print(f"   - {risk_profile_counts.get('Balanced', 0)} traders are balanced")

print(f"\n2. Performance by Risk Profile:")
best_profile = max(profiles, key=lambda p: df[df['risk_profile'] == p]['win_rate'].mean())
worst_profile = min(profiles, key=lambda p: df[df['risk_profile'] == p]['win_rate'].mean())
print(f"   - Best performing: {best_profile} ({df[df['risk_profile'] == best_profile]['win_rate'].mean():.2%} avg win rate)")
print(f"   - Worst performing: {worst_profile} ({df[df['risk_profile'] == worst_profile]['win_rate'].mean():.2%} avg win rate)")

if 'p_value' in locals() and p_value < 0.05:
    print(f"\n3. Statistical Significance:")
    print(f"   - Risk profile DOES significantly affect performance (p={p_value:.4f})")
else:
    print(f"\n3. Statistical Significance:")
    print(f"   - No statistically significant difference between risk profiles")

print(f"\n4. Risk-Return Relationship:")
if corr_risk_winrate > 0:
    print(f"   - Higher risk correlates with BETTER performance")
else:
    print(f"   - Higher risk correlates with WORSE performance")
print(f"   - Correlation: {corr_risk_winrate:.3f}")

print("\n" + "="*80)
print(f"All EDA analysis complete! Check the '{viz_dir}' folder for all charts.")
print("="*80)

