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
