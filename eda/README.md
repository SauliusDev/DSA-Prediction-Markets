# Exploratory Data Analysis (EDA)

This folder contains the exploratory data analysis scripts for the Polymarket trader behavior project.

## Scripts Overview

The EDA is split into 4 comprehensive Python scripts, each focusing on a different aspect of trader behavior:

### 1. `01_performance_distribution.py`
**Focus**: Overall trader performance metrics

Analyzes:
- Win rate distribution across all traders
- Profit & Loss (PnL) patterns
- Smart score distribution and validation
- Extreme outcomes (best/worst trades)
- Performance quartiles and outliers

**Key Questions**:
- What's the typical win rate for traders?
- How is profitability distributed? (Are a few whales driving all profits?)
- Does the "smart score" actually correlate with performance?

**Outputs**: 4 visualizations (win rate, PnL, smart score, extreme outcomes)

---

### 2. `02_category_analysis.py`
**Focus**: Market category performance and specialization

Analyzes:
- Trading volume by category (Politics, Crypto, Sports, etc.)
- Category-specific win rates
- Trader specialization vs diversification
- 3D visualization of category × smart score × PnL
- Category-specific smart scores

**Key Questions**:
- Which market categories are most popular?
- Which categories are most profitable?
- Do specialists outperform generalists?
- Where do smart traders make their money?

**Outputs**: 5 visualizations (volumes, win rates, specialization, 3D scatter, heatmap)

---

### 3. `03_trader_types.py`
**Focus**: Trading style comparison

Analyzes:
- Prevalence of each trader type (contrarian, bagholder, whale, etc.)
- Performance comparison across types
- Trader type combinations
- Multi-type trader analysis
- Statistical significance testing (ANOVA)

**Key Questions**:
- Which trader types are most common?
- Do certain trading styles perform better?
- Are type combinations more successful?
- Does having multiple types help or hurt?

**Outputs**: 4 visualizations (prevalence, performance, co-occurrence, multi-type)

---

### 4. `04_risk_behavior.py`
**Focus**: Betting probability preferences and risk-taking

Analyzes:
- Betting distribution across probability ranges (0-10%, 10-20%, ..., 90-100%)
- Risk profiles (longshot hunters, safe players, balanced)
- Performance by risk profile
- Correlation between risk-taking and success
- Risk-adjusted performance metrics

**Key Questions**:
- Where do traders place most bets on the probability spectrum?
- Do longshot hunters or safe players perform better?
- Is there an optimal risk level?
- How does risk-taking correlate with win rate?

**Outputs**: 4 visualizations (probability distribution, risk profiles, detailed analysis, risk-adjusted)

---

## How to Run

### Prerequisites
Make sure you have all required packages installed:

```bash
pip install -r ../requirements.txt
```

### Running Individual Scripts

Each script can be run independently:

```bash
# From the eda directory
python 01_performance_distribution.py
python 02_category_analysis.py
python 03_trader_types.py
python 04_risk_behavior.py
```

Or from the project root:

```bash
python eda/01_performance_distribution.py
python eda/02_category_analysis.py
python eda/03_trader_types.py
python eda/04_risk_behavior.py
```

### Running All Scripts

To run all EDA scripts in sequence:

```bash
# From the eda directory
for script in 01_*.py 02_*.py 03_*.py 04_*.py; do
    echo "Running $script..."
    python "$script"
    echo "---"
done
```

---

## Output

### Console Output
Each script prints:
- Section headers and progress indicators
- Statistical summaries
- Key findings
- Correlation coefficients
- Statistical test results (ANOVA, p-values)

### Visualizations
All visualizations are saved to `eda/visualizations/` with descriptive filenames:

**Performance Distribution (01)**:
- `01_win_rate_distribution.png`
- `02_pnl_distribution.png`
- `03_smart_score_analysis.png`
- `04_extreme_outcomes.png`

**Category Analysis (02)**:
- `05_category_volumes.png`
- `06_category_winrates.png`
- `07_specialization_analysis.png`
- `08_3d_category_performance.png`
- `09_category_smartscore_heatmap.png`

**Trader Types (03)**:
- `10_trader_type_prevalence.png`
- `11_performance_by_type.png`
- `12_type_cooccurrence.png`
- `13_multitype_analysis.png`

**Risk Behavior (04)**:
- `14_betting_probability_distribution.png`
- `15_performance_by_risk_profile.png`
- `16_detailed_probability_analysis.png`
- `17_risk_adjusted_performance.png`

---

## Key Findings

After running all scripts, you'll have insights into:

1. **Performance Landscape**: Distribution of success, profitability patterns, smart score validity
2. **Category Dynamics**: Which markets are most profitable, specialization vs diversification effects
3. **Trading Styles**: Which trader types perform best, optimal type combinations
4. **Risk Behavior**: Optimal betting strategies, risk-return relationships

These findings will inform the hypothesis testing phase and help identify patterns that separate successful traders from unsuccessful ones.

---

## Notes

- All scripts use the same data source: `../data/users_data.csv`
- Scripts are independent and can be run in any order
- Visualizations use consistent styling (seaborn-v0_8-darkgrid theme)
- Statistical tests use α = 0.05 significance level
- Missing values are handled appropriately in each analysis
- Scripts include progress indicators and completion messages

---

## Next Steps

After completing the EDA:
1. Review all visualizations in the `visualizations/` folder
2. Note key patterns and correlations
3. Formulate specific hypotheses for formal testing
4. Proceed to `hypothesis_testing/` folder for statistical validation

---

**Author**: Ąžuolas Saulius Balbieris  
**Course**: DSA 210 - Introduction to Data Science  
**Date**: Fall 2025

