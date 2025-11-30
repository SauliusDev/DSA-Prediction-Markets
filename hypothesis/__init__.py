"""
Hypothesis Testing Module for Polymarket Trader Analysis

This module provides reusable functions for statistical hypothesis testing
on trader performance data.
"""

from .trader_type_anova import (
    anova_trader_types,
    prepare_anova_groups,
    check_anova_assumptions,
    perform_anova,
    post_hoc_analysis,
)

__version__ = '1.0.0'
__author__ = 'Ąžuolas Saulius Balbieris'

__all__ = [
    'anova_trader_types',
    'prepare_anova_groups',
    'check_anova_assumptions',
    'perform_anova',
    'post_hoc_analysis',
]

