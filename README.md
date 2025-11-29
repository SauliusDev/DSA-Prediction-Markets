# What Makes a Successful Prediction Market Trader?
**Course:** DSA 210 – Introduction to Data Science (2025–2026 Fall)

**Student:** Ąžuolas Saulius Balbieris (37825)

## Table of Contents
- [Motivation](#motivation)
- [The Dataset](#the-dataset)
- [Data Collection](#data-collection)
- [Research Questions](#research-questions)
- [Hypothesis Testing](#hypothesis-testing)
- [Methodology](#methodology)
- [Analysis Plan](#analysis-plan)
- [References](#references)

## Motivation

Prediction markets like Polymarket have become increasingly popular as platforms where people bet real money on real-world events—from elections to sports outcomes to cryptocurrency prices. But what actually separates successful traders from unsuccessful ones? 

I got curious about this after discovering Hashdive, a platform that tracks Polymarket traders and assigns them "Smart Scores" based on their trading behavior. These scores range from around -99 (gamblers loosing money) to 99 (elite trader). But the question remained: **what patterns do successful traders follow?**

This project aims to dig into the data and understand:
- What trading behaviors correlate with better performance?
- Do certain trader types (contrarians, trend followers, etc.) actually perform better?
- Are some market categories more profitable than others for smart traders?
- Does diversifying across many markets help or hurt your win rate?

The answers could provide practical insights for anyone interested in prediction markets, while also exploring interesting questions about human decision-making and risk-taking behavior.

## The Dataset

I collected data on **~1000 Polymarket traders** using Hashdive's proprietary API. The data collection took approximately **20 hours** due to API rate limits. 

Each trader profile contains **60+ features** including:

### Performance Metrics
- **Smart Score** (31-99): Platform's assessment of trader skill
- **Win Rate** (0-1): Percentage of profitable bets
- **Total PnL**: Net profit/loss in USD
- **Sharpe Ratio**: Risk-adjusted returns
- **Best/Worst Trade ROI**: Extreme outcomes

### Trading Behavior
- **Total Positions**: Number of bets placed
- **Number of Markets**: How many different markets traded
- **Traded Volume (30d)**: Recent trading activity
- **Betting Probability Ranges** (0.0-0.9): Where traders place bets
  - `trader_bets_0_0`: Bets on very unlikely outcomes (<10% probability)
  - `trader_bets_0_9`: Bets on very likely outcomes (>90% probability)
  - These reveal risk-taking patterns—do they hunt longshots or play it safe?

### Trader Types (Platform-Assigned)
Binary flags indicating trading style:
- **Bagholder**: Holds losing positions too long
- **Contrarian**: Bets against market consensus
- **Trend Follower**: Follows market momentum
- **Lottery Ticket**: Chases high-risk, high-reward bets
- **Whale Splash**: Makes very large bets
- **Senior/Veteran**: Experienced traders

### Category Performance
Performance broken down by market type:
- **Politics** (elections, policy outcomes)
- **Crypto** (Bitcoin price, DeFi events)
- **Sports** (game outcomes, championships)
- **Culture** (entertainment, awards)
- **Other** (weather, miscellaneous)

For each category, we have:
- Amount traded
- Category-specific smart score
- Category-specific win rate

## Data Collection

### Data Source
- **Hashdive Premium API**: A paid service that aggregates and analyzes Polymarket trader statistics
- **Sample**: ~1000 traders with Smart Scores ranging from 31 to 99
- **Collection Time**: ~20 hours (November 2024)
- **Format**: Individual JSON files per user, later aggregated into CSV

### Why This Dataset?
- **Real money, real stakes**: These are actual traders with real profit/loss
- **Behavioral data**: Not just prices, but human decision-making patterns
- **Unique features**: Trader types, betting probability preferences, category specialization

### Data Processing
Raw JSON files were parsed and flattened into a structured CSV with 60+ columns. Key transformations:
- Nested category metrics expanded into separate columns
- Trader type flags converted to binary indicators
- Probability range betting patterns normalized
- Missing values handled (some traders don't have all category data)

## Research Questions

The overarching question: **What makes a successful prediction market trader?**

This breaks down into several specific angles:

1. **Performance Drivers**: What factors correlate most strongly with win rate and profitability?
2. **Trader Type Analysis**: Do certain trading styles (contrarian, trend follower, etc.) perform better?
3. **Diversification Effect**: Does trading across more markets improve or hurt performance?
4. **Category Specialization**: Are some market categories more profitable? Do smart traders specialize or generalize?
5. **Risk Behavior**: How do betting probability preferences relate to success?
6. **Smart Score Validation**: Does the platform's "Smart Score" actually predict performance?

## Methodology

This project uses a quantitative approach:
- Clean and flatten Hashdive API data into a structured CSV  
- Perform exploratory analysis to understand distributions and relationships  
- Use correlations and basic statistical tests to evaluate factors influencing performance  

All analysis is done using Python (pandas, seaborn, scipy).

## Hypothesis Testing

After exploring the data, we'll formally test key hypotheses using statistical methods.

**Research Question**: Do different trader types (contrarian, trend follower, bagholder, etc.) have significantly different performance outcomes?
**Null Hypothesis (H₀)**: All trader types have equal mean win rates. There is no significant difference in performance across trader types.
**Alternative Hypothesis (H₁)**: At least one trader type has a significantly different mean win rate compared to others.

## Project Structure

core - utils classes
data - storage of data
eda - folder for exploratory data analysis related code
hashdive - api related data accumulation codes
steamlint - repository used for its protocols do decode binary websocket responses
eda_analysis.ipynb - documentation of EDA findings
hypothesis_testing.ipynb - documentation of hypothesis testing
ml_method.ipynb - documentation of ML implementation

## Analysis Plan

The analysis focuses on:
1. Performance distribution
2. Category-level differences
3. Trader type comparisons
4. Risk behavior patterns

## References

- [Polymarket](https://polymarket.com) - Decentralized prediction market platform
- [Hashdive](https://hashdive.com) - Polymarket trader analytics platform
- [Prediction Markets Research](https://en.wikipedia.org/wiki/Prediction_market) - Background on prediction markets

---

**Note**: This is an educational project for DSA 210. The data was collected ethically through a paid API service. No trading advice is intended or implied.
