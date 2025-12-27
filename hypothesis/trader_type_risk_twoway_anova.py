import pandas as pd
import numpy as np
import scipy.stats as stats
from tabulate import tabulate

TRADER_TYPE_COLS = [
    'trader_type_bagholder', 'trader_type_contrarian',
    'trader_type_lottery_ticket', 'trader_type_new',
    'trader_type_novice', 'trader_type_reverse_cramer',
    'trader_type_senior', 'trader_type_trend_follower',
    'trader_type_veteran', 'trader_type_waiting_for_the_money',
    'trader_type_whale_splash'
]

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

def assign_risk_profile(df: pd.DataFrame) -> pd.Series:
    betting_cols = [f'trader_bets_0_{i}' for i in range(10)]
    
    risk_profile = []
    
    for idx, row in df.iterrows():
        bets = row[betting_cols].values
        total_bets = np.sum(bets)  
        
        if total_bets == 0:
            risk_profile.append('Unknown')
            continue
        
        proportions = bets / total_bets
        
        longshot_prop = np.sum(proportions[0:2])
        safe_prop = np.sum(proportions[8:10])
        
        if longshot_prop > 0.5:
            risk_profile.append('Longshot Hunter')
        elif safe_prop > 0.5:
            risk_profile.append('Safe Player')
        else:
            risk_profile.append('Balanced')
    
    return pd.Series(risk_profile, index=df.index, name='risk_profile')

def two_way_anova(df: pd.DataFrame, min_sample_size: int = 5) -> dict:
    df = df.copy()
    df['risk_profile'] = assign_risk_profile(df)
    
    df = df[df['risk_profile'] != 'Unknown']  # pyright: ignore[reportAssignmentType]
    
    groups_data = []
    group_labels = []
    
    for trader_col in TRADER_TYPE_COLS:
        for risk_prof in ['Longshot Hunter', 'Balanced', 'Safe Player']:
            mask = (df[trader_col] == 1) & (df['risk_profile'] == risk_prof)
            subset = df[mask]['win_rate']
            
            if len(subset) >= min_sample_size:
                groups_data.append(subset.values)  # pyright: ignore[reportAssignmentType]
                group_labels.append({
                    'trader_type': TYPE_DISPLAY_NAMES[trader_col],
                    'risk_profile': risk_prof,
                    'n': len(subset),
                    'mean': float(np.mean(subset))
                })
    
    overall_mean = df['win_rate'].mean()
    grand_total = len(df)
    
    ss_total = np.sum((df['win_rate'] - overall_mean) ** 2)
    
    trader_type_means = {}
    for trader_col in TRADER_TYPE_COLS:
        subset = df[df[trader_col] == 1]['win_rate']
        if len(subset) > 0:
            trader_type_means[TYPE_DISPLAY_NAMES[trader_col]] = {
                'mean': float(np.mean(subset)),
                'n': len(subset)
            }
    
    risk_means = {}
    for risk_prof in ['Longshot Hunter', 'Balanced', 'Safe Player']:
        subset = df[df['risk_profile'] == risk_prof]['win_rate']
        if len(subset) > 0:
            risk_means[risk_prof] = {
                'mean': float(np.mean(subset)),
                'n': len(subset)
            }
    
    ss_trader = sum(
        info['n'] * (info['mean'] - overall_mean) ** 2 
        for info in trader_type_means.values()
    )
    
    ss_risk = sum(
        info['n'] * (info['mean'] - overall_mean) ** 2 
        for info in risk_means.values()
    )
    
    ss_within = 0
    for group in groups_data:
        ss_within += np.sum((group - np.mean(group)) ** 2)
    
    ss_interaction = ss_total - ss_trader - ss_risk - ss_within
    
    df_trader = len(trader_type_means) - 1
    df_risk = len(risk_means) - 1
    df_interaction = df_trader * df_risk
    df_within = grand_total - len(groups_data)
    
    ms_trader = ss_trader / df_trader if df_trader > 0 else 0
    ms_risk = ss_risk / df_risk if df_risk > 0 else 0
    ms_interaction = ss_interaction / df_interaction if df_interaction > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    
    f_trader = ms_trader / ms_within if ms_within > 0 else 0
    f_risk = ms_risk / ms_within if ms_within > 0 else 0
    f_interaction = ms_interaction / ms_within if ms_within > 0 else 0
    
    p_trader = 1 - stats.f.cdf(f_trader, df_trader, df_within) if f_trader > 0 else 1
    p_risk = 1 - stats.f.cdf(f_risk, df_risk, df_within) if f_risk > 0 else 1
    p_interaction = 1 - stats.f.cdf(f_interaction, df_interaction, df_within) if f_interaction > 0 else 1
    
    results = {
        'main_effect_trader_type': {
            'F': f_trader,
            'p_value': p_trader,
            'df': (df_trader, df_within),
            'means': trader_type_means
        },
        'main_effect_risk_profile': {
            'F': f_risk,
            'p_value': p_risk,
            'df': (df_risk, df_within),
            'means': risk_means
        },
        'interaction_effect': {
            'F': f_interaction,
            'p_value': p_interaction,
            'df': (df_interaction, df_within)
        },
        'cell_means': group_labels,
        'grand_mean': float(overall_mean)
    }
    
    return results

def format_results(results: dict) -> str:
    output = []
    
    output.append("=" * 70)
    output.append("TWO-WAY ANOVA: TRADER TYPE × RISK PROFILE")
    output.append("=" * 70)
    
    output.append(f"\nGrand Mean Win Rate: {results['grand_mean']*100:.2f}%")
    
    output.append("\n" + "-" * 70)
    output.append("MAIN EFFECT: TRADER TYPE")
    output.append("-" * 70)
    trader_effect = results['main_effect_trader_type']
    output.append(f"F({trader_effect['df'][0]}, {trader_effect['df'][1]}) = {trader_effect['F']:.4f}")
    output.append(f"p-value = {trader_effect['p_value']:.4e}")
    output.append(f"Significant: {'YES' if trader_effect['p_value'] < 0.05 else 'NO'}")
    
    output.append("\n" + "-" * 70)
    output.append("MAIN EFFECT: RISK PROFILE")
    output.append("-" * 70)
    risk_effect = results['main_effect_risk_profile']
    output.append(f"F({risk_effect['df'][0]}, {risk_effect['df'][1]}) = {risk_effect['F']:.4f}")
    output.append(f"p-value = {risk_effect['p_value']:.4e}")
    output.append(f"Significant: {'YES' if risk_effect['p_value'] < 0.05 else 'NO'}")
    
    output.append("\n" + "-" * 70)
    output.append("INTERACTION EFFECT: TRADER TYPE × RISK PROFILE")
    output.append("-" * 70)
    interaction = results['interaction_effect']
    output.append(f"F({interaction['df'][0]}, {interaction['df'][1]}) = {interaction['F']:.4f}")
    output.append(f"p-value = {interaction['p_value']:.4e}")
    output.append(f"Significant: {'YES' if interaction['p_value'] < 0.05 else 'NO'}")
    
    output.append("\n" + "-" * 70)
    output.append("CELL MEANS (Trader Type × Risk Profile)")
    output.append("-" * 70)
    
    table_data = []
    for cell in results['cell_means']:
        table_data.append([
            cell['trader_type'],
            cell['risk_profile'],
            f"{cell['mean']*100:.2f}%",
            cell['n']
        ])
    
    output.append(tabulate(
        table_data,
        headers=['Trader Type', 'Risk Profile', 'Mean Win Rate', 'N'],
        tablefmt='pretty'
    ))
    
    output.append("\n" + "=" * 70)
    
    return "\n".join(output)

