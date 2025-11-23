# Hashdive Smart Score Analysis
**Course:** DSA 210 – Introduction to Data Science (2025–2026 Fall)

**Student:** Ąžuolas Saulius Balbieris (37825)

## 1. Motivation
Hashdive assigns every Polymarket trader a **Smart Score** (ranging from -100 to 100). This score is meant to measure a trader's consistency, risk awareness, and overall profitability.

The goal of this project is to analyze the correlation between the Smart Score and **actual trading outcomes**, specifically:
* Win Rate and PnL (Profit and Loss)
* Account age and balance
* Position size and preferred market entry probabilities
* Maybe more future metrics as I do research on data collection abilities

## 2. Data collection
* **Hashdive (premium API/UI)** 
  * Official api for basic info about user: User account age etc.
  * Scraping web data for for intricate data: Smart Score, Win Rate, PnL, Sharpe Ratio, total positions, account balance, and category-specific statistics.
* **Polymarket Free API**  
  * Category metadata and simple time features (e.g., account age in days).

The final data would be organized into json format. For this many parsing function will be implemented. 

## 3. Methodology

### 3.1 Data Collection Process

**Sample Selection:**
- Target sample size: 500-1000 Polymarket users across different Smart Score ranges
- Stratified sampling to ensure representation across score brackets:
  - High performers (Score > 40): ~200 users
  - Mid-range (Score 0-40): ~400 users  
  - Low performers (Score < 0): ~200 users
- Minimum activity threshold: Users with at least 10 completed trades

**Data Collection Pipeline:**
1. **Hashdive API/Scraping:**
   - User Smart Score (primary metric)
   - Total PnL (USD)
   - Win Rate (%)
   - Sharpe Ratio
   - Total positions traded
   - Current balance
   - Active days since registration
   - Category-specific statistics (Politics, Crypto, Culture, etc.)
   - Trading behavior metrics:
     - Average entry price
     - Position size distribution
     - Best/worst trade ROI
     - Active vs. finished bets ratio
2. **Polymarket API:**
   - Account creation date
   - Market category metadata
   - Trading volume over time

**Data Storage:**
- JSON format with nested structure for user profiles
- Each user record contains: `{user_id, smart_score, pnl, win_rate, sharpe_ratio, ...}`
- Parsing functions to normalize scraped HTML/API responses into structured format

### 3.2 Data Analysis Approach

**Phase 1: Exploratory Data Analysis (EDA)**
- Descriptive statistics for all numerical variables
- Distribution analysis (histograms, box plots) for Smart Score, PnL, Win Rate
- Correlation matrix using both Pearson and Spearman coefficients
- Scatter plots: Smart Score vs. PnL, Smart Score vs. Win Rate
- Category-wise performance comparison
- Identify outliers and data quality issues

**Phase 2: Correlation Analysis**
- Primary hypothesis test: Smart Score correlation with realized PnL
- Secondary correlations:
  - Smart Score vs. Win Rate
  - Smart Score vs. Sharpe Ratio
  - Account age vs. performance metrics
  - Position size strategy vs. profitability
- Statistical significance testing (p-values < 0.05)

**Phase 3: Predictive Modeling**
- **Target variables:** PnL, Win Rate
- **Features:** Smart Score, account age, total positions, balance, Sharpe Ratio, category preferences, entry price patterns

**Models to implement:**
1. Linear Regression (baseline)
2. Random Forest Regressor (capture non-linear relationships)
3. Gradient Boosting (XGBoost/LightGBM) if needed

**Model Evaluation:**
- Train/test split: 80/20
- Cross-validation (5-fold)
- Metrics: R², MAE, RMSE
- Feature importance analysis
- Residual analysis

**Phase 4: Insights & Interpretation**
- Identify which features most strongly predict trading success
- Validate whether Smart Score is a reliable predictor
- Analyze trading patterns of high-Smart-Score users:
  - Do they prefer certain probability ranges?
  - Do they trade specific categories more?
  - How does their position sizing differ?

## 4. Data usage
1.  **Exploratory Data Analysis (EDA):** Calculate correlations (Spearman/Pearson), analyze distributions, and plot Smart Score against PnL/Win Rate.
2.  **Modeling:** Use linear and tree-based models (e.g., Random Forest) to predict PnL/Win Rate based on Smart Score and other account features.
3.  **Evaluation:** Assess model performance using $R^2$, MAE, and correlation strengths, and determine feature importance.
I expect the **Smart Score** to correlate positively with Win Rate and risk-adjusted PnL. Because users with high scores are anticipated to exhibit more consistent and disciplined trading behavior.

Realted Links:
* [What is polymarket?](https://en.wikipedia.org/wiki/Polymarket)
* [Hashdive Smart Score Documentation](https://hashdive.com/documentation)
* [Polymarket API](https://docs.polymarket.com/developers/gamma-markets-api/overview)
* [Hashdive Premium API](https://hashdive.com/API_documentation)
