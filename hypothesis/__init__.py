"""
Hypothesis Testing Module for Polymarket Trader Analysis

This module provides reusable functions for statistical hypothesis testing
on trader performance data.

Usage:
------
```python
import pandas as pd
from hypothesis import anova_trader_types

# Load data
df = pd.read_csv('data/users_data.csv')

# Run ANOVA test
results = anova_trader_types(df, visualize=True)
print(f"F-statistic: {results['f_statistic']:.4f}")
print(f"p-value: {results['p_value']:.10f}")
```

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

from .trader_type_anova import (
    anova_trader_types,
    prepare_anova_groups,
    check_anova_assumptions,
    perform_anova,
    post_hoc_analysis,
    visualize_anova_results
)

__version__ = '1.0.0'
__author__ = 'Ąžuolas Saulius Balbieris'

__all__ = [
    'anova_trader_types',
    'prepare_anova_groups',
    'check_anova_assumptions',
    'perform_anova',
    'post_hoc_analysis',
    'visualize_anova_results'
]

