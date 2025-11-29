# EDA Module Documentation

Professional, reusable plotting functions for Polymarket trader analysis.

## Overview

This module provides clean, Jupyter-friendly functions for exploratory data analysis. Each function:
- ✅ Accepts a DataFrame as input
- ✅ Returns figure objects (not just saving to disk)
- ✅ Optionally saves figures with `save=True`
- ✅ Returns statistics/summaries alongside plots
- ✅ Has no print spam or auto-execution

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### In Jupyter Notebook

```python
import pandas as pd
from eda import performance, categories, trader_types, risk

# Load data
df = pd.read_csv('data/users_data.csv')

# Generate a plot
fig, stats = performance.plot_win_rate_distribution(df)
fig.show()  # or plt.show()

print(f"Mean win rate: {stats['mean']:.2%}")
```

### Generate All Plots at Once

```python
from eda import generate_full_report

# Generate all plots and summaries
report = generate_full_report(df, save=True, output_dir='eda/visualizations/report')

# Access individual figures
report['performance']['win_rate'].show()
report['categories']['volumes'].show()

# Access summaries
print(report['summaries']['performance'])
```

## Module Structure

```
eda/
├── __init__.py           # Main imports and convenience functions
├── performance.py        # Win rate, smart score analysis
├── categories.py         # Category volumes, specialization
├── trader_types.py       # Trader type prevalence, performance
├── risk.py               # Betting probability, risk profiles
└── README.md            # This file
```

## Available Functions

### Performance Module (`eda.performance`)

#### `plot_win_rate_distribution(df, figsize=(18,5), save=False, path=None)`
Plots win rate histogram, box plot, and density plot.

**Returns:**
- `fig`: matplotlib Figure object
- `stats`: dict with mean, median, std, quartiles

**Example:**
```python
from eda.performance import plot_win_rate_distribution

fig, stats = plot_win_rate_distribution(df)
fig.show()
print(f"Median win rate: {stats['median']:.2%}")
```

#### `plot_smart_score_analysis(df, figsize=(16,12), save=False, path=None)`
Comprehensive smart score analysis with correlations.

**Returns:**
- `fig`: matplotlib Figure object
- `correlations`: dict with correlation coefficients and p-values

**Example:**
```python
from eda.performance import plot_smart_score_analysis

fig, corr = plot_smart_score_analysis(df)
fig.show()
print(f"Smart Score vs Win Rate: r={corr['smart_score_vs_winrate']['correlation']:.3f}")
print(f"Significant: {corr['smart_score_vs_winrate']['significant']}")
```

#### `get_performance_summary(df)`
Get summary statistics without plotting.

**Returns:** dict with performance metrics

---

### Categories Module (`eda.categories`)

#### `plot_category_volumes(df, figsize=(16,6), save=False, path=None)`
Bar and pie charts of trading volume by category.

**Returns:**
- `fig`: matplotlib Figure object
- `volumes`: pandas Series with category volumes

#### `plot_category_winrates(df, figsize=(16,12), save=False, path=None)`
Win rate distributions for each category.

**Returns:**
- `fig`: matplotlib Figure object
- `stats`: dict with win rate stats by category

#### `plot_specialization_analysis(df, figsize=(12,7), save=False, path=None)`
Category diversification distribution.

**Returns:**
- `fig`: matplotlib Figure object
- `specialization_stats`: dict with specialization metrics

#### `get_category_summary(df)`
Get category summary without plotting.

---

### Trader Types Module (`eda.trader_types`)

#### `plot_trader_type_prevalence(df, figsize=(16,6), save=False, path=None)`
Trader type distribution and types per trader.

**Returns:**
- `fig`: matplotlib Figure object
- `type_counts`: dict with counts and percentages

#### `plot_performance_by_type(df, figsize=(18,14), save=False, path=None)`
Performance metrics by trader type.

**Returns:**
- `fig`: matplotlib Figure object
- `performance`: dict with performance by type

#### `plot_type_cooccurrence(df, figsize=(14,12), save=False, path=None)`
Heatmap of trader type co-occurrence.

**Returns:**
- `fig`: matplotlib Figure object
- `cooccurrence`: pandas DataFrame matrix

#### `get_trader_type_summary(df)`
Get trader type summary without plotting.

---

### Risk Module (`eda.risk`)

#### `plot_betting_probability_distribution(df, figsize=(16,12), save=False, path=None)`
Overall betting probability distribution across ranges.

**Returns:**
- `fig`: matplotlib Figure object
- `distribution`: dict with betting statistics

#### `plot_winrate_by_probability_range(df, figsize=(14,8), save=False, path=None)`
Box plots of win rate by betting probability range.

**Returns:**
- `fig`: matplotlib Figure object
- `correlations`: dict with correlation stats

#### `get_risk_behavior_summary(df)`
Get risk behavior summary without plotting.

---

## Convenience Functions

### `plot_all_performance(df, save=False, output_dir=None)`
Generate all performance plots at once.

### `plot_all_categories(df, save=False, output_dir=None)`
Generate all category plots at once.

### `plot_all_trader_types(df, save=False, output_dir=None)`
Generate all trader type plots at once.

### `plot_all_risk(df, save=False, output_dir=None)`
Generate all risk behavior plots at once.

### `generate_full_report(df, save=False, output_dir='eda/visualizations/report')`
Generate complete EDA report with all plots and summaries.

**Returns:** dict with all figures and summary statistics

**Example:**
```python
from eda import generate_full_report

report = generate_full_report(df, save=True)

# Access any figure
report['performance']['win_rate'].show()
report['categories']['volumes'].show()
report['trader_types']['prevalence'].show()
report['risk']['distribution'].show()

# Access summaries
print(report['summaries']['performance'])
print(report['summaries']['categories'])
```

---

## Usage Patterns

### Pattern 1: Interactive Analysis in Jupyter

```python
import pandas as pd
from eda import performance

df = pd.read_csv('data/users_data.csv')

# Generate plot
fig, stats = performance.plot_win_rate_distribution(df)
fig.show()

# Use the statistics
print(f"Mean: {stats['mean']:.2%}")
print(f"Median: {stats['median']:.2%}")
```

### Pattern 2: Save All Plots for Report

```python
from eda import generate_full_report

df = pd.read_csv('data/users_data.csv')

# Generate and save everything
report = generate_full_report(df, save=True, output_dir='eda/visualizations/report')

print("All plots saved!")
```

### Pattern 3: Custom Analysis Workflow

```python
from eda import performance, categories, trader_types, risk

df = pd.read_csv('data/users_data.csv')

# Get summaries first
perf_summary = performance.get_performance_summary(df)
cat_summary = categories.get_category_summary(df)

print(f"Profitable traders: {perf_summary['profitable_percentage']:.1f}%")
print(f"Most popular category: {cat_summary['most_popular_category']}")

# Then generate specific plots
fig1, _ = performance.plot_win_rate_distribution(df)
fig2, _ = categories.plot_category_volumes(df)

fig1.show()
fig2.show()
```

---

## Design Philosophy

This module follows professional data science library design:

1. **No side effects**: Functions don't print or auto-save unless requested
2. **Return values**: Always return figure objects for flexibility
3. **Reusability**: Each function can be called multiple times with different data
4. **Jupyter-friendly**: Works seamlessly in notebooks with `plt.show()`
5. **Optional saving**: Save to disk only when `save=True`
6. **Statistics included**: Return both plots and numerical summaries

---

## Comparison: Old vs New

### ❌ Old Approach (Script-based)

```python
# performance_distribution.py
df = pd.read_csv(...)  # Hardcoded path
plt.plot(...)
plt.savefig("output.png")  # Always saves
print("Analysis complete!")  # Spam

# Can't reuse in notebook!
```

### ✅ New Approach (Function-based)

```python
# performance.py
def plot_win_rate_distribution(df, save=False, path=None):
    fig, ax = plt.subplots()
    ax.hist(df['win_rate'])
    
    if save and path:
        fig.savefig(path)
    
    return fig, stats

# Clean, reusable, Jupyter-friendly!
```

---

## Author

**Ąžuolas Saulius Balbieris**  
DSA 210 - Introduction to Data Science  
2025-2026 Fall Semester

