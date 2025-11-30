"""
Simple Trader Type ANOVA

Performs only ONE-WAY ANOVA on win rates across trader types.
No assumption checks, no post-hoc tests, no visualization.

Author: Ąžuolas Saulius Balbieris
Course: DSA 210 - Introduction to Data Science
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from tabulate import tabulate

# Which trader-type indicator columns define a group
TRADER_TYPE_COLS = [
    'trader_type_bagholder', 'trader_type_contrarian',
    'trader_type_lottery_ticket', 'trader_type_new',
    'trader_type_novice', 'trader_type_reverse_cramer',
    'trader_type_senior', 'trader_type_trend_follower',
    'trader_type_veteran', 'trader_type_waiting_for_the_money',
    'trader_type_whale_splash'
]

# Human-friendly names
TYPE_DISPLAY_NAMES = {
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

def anova_trader_types(df: pd.DataFrame, min_sample_size: int = 10) -> dict:
    """
    Performs a simple ONE-WAY ANOVA on win_rate grouped by trader types.
    Returns: F-statistic, p-value, group names, group means.
    """

    groups = []
    group_names = []

    for col in TRADER_TYPE_COLS:
        subset = df[df[col] == 1]['win_rate']
        if len(subset) >= min_sample_size:
            groups.append(subset.values)
            group_names.append(TYPE_DISPLAY_NAMES[col])

    f_stat, p_value = stats.f_oneway(*groups)
    means = {name: float(np.mean(group)) for name, group in zip(group_names, groups)}

    results = {
        "f_statistic": f_stat,
        "p_value": p_value,
        "group_names": group_names,
        "means": means
    }

    return results