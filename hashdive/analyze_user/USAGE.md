# User Data Fetcher - Usage Guide

## Overview

The `fetch_multiple_users.py` script fetches detailed user data from hashdive.com for multiple users listed in a CSV file. It processes users sequentially (one at a time) to respect API rate limits.

## How It Works

The pipeline follows these steps for each user:

1. **Load CSV** → Read user addresses from `data/pages/final/combined_21-99ss.csv`
2. **Fetch Data** → Connect to hashdive WebSocket API and fetch user messages
3. **Decode Messages** → Decode protobuf binary messages to JSON
4. **Classify Messages** → Identify message types using `AnalyzeUserMessageClassifier`
5. **Parse Data** → Extract structured data using `AnalyzeUserDataParser`
6. **Combine Data** → Merge API data with CSV metrics
7. **Save JSON** → Save as `{user_address}.json` in `data/users/`

## Usage

```bash
python3 hashdive/analyze_user/fetch_multiple_users.py [OPTIONS]
```

### Options

- `--limit N` - Fetch only N users (default: all users in CSV)
- `--offset N` - Start from row N in CSV (0-indexed, excludes header)
- `--refetch` - Refetch users that already exist (default: skip existing)
- `--csv PATH` - Path to CSV file (default: `data/pages/final/combined_21-99ss.csv`)
- `--output PATH` - Output directory (default: `data/users`)

### Examples

**Fetch first 10 users:**
```bash
python3 hashdive/analyze_user/fetch_multiple_users.py --limit 10
```

**Fetch 5 users starting from row 100:**
```bash
python3 hashdive/analyze_user/fetch_multiple_users.py --limit 5 --offset 100
```

**Refetch first 10 users (overwrite existing):**
```bash
python3 hashdive/analyze_user/fetch_multiple_users.py --limit 10 --refetch
```

**Fetch from custom CSV:**
```bash
python3 hashdive/analyze_user/fetch_multiple_users.py --csv path/to/users.csv --output path/to/output
```

## Performance

- **Speed**: ~5-10 seconds per user
- **Timeout**: 30 seconds total per user, 5 seconds per message
- **Rate Limiting**: 1 second delay between users
- **Sequential Processing**: One user at a time (no parallel fetching)

## Output Format

Each user is saved as `{user_address}.json`:

```json
{
  "trader_types": ["Contrarian", "Lottery Ticket"],
  "total_positions": 509,
  "current_balance": 125.5,
  "polymarket_url": "https://polymarket.com/profile/0x...",
  "rank_1d_place": "#9542",
  "rank_1d_amount": "$46.7k",
  "rank_7d_place": "#5104",
  "rank_7d_amount": "$455.3k",
  "rank_30d_place": "#2963",
  "rank_30d_amount": "$1.7M",
  "rank_all_time_place": "#9842",
  "rank_all_time_amount": "$1.9M",
  "smart_score": 99.0,
  "total_pnl": 5239.35,
  "sharpe_ratio": 9.92,
  "traded_usd_volume_last_30d_sum": 12230.0,
  "active_bets_amount": 11.31,
  "active_bets_pnl": 37.91,
  "finished_bets_amount": 3623.43,
  "finished_bets_pnl": 3839.32,
  "best_trade_roi_proc": 99800.0,
  "best_trade_roi_amount": 1996.0,
  "worst_trade_roi_proc": -29.27,
  "worst_trade_roi_amount": -9.25,
  "where_trader_bets_most": {
    "0.0": 1035.31,
    "0.5": 523.45
  },
  "user_address": "0x...",
  "win_rate": 0.387,
  "effective_count": 10.0,
  "num_markets": 509,
  "score": 99.0,
  "sum_pnl": 5239.35,
  "last_updated_block": 79493565
}
```

### Data Sources

**From Hashdive API:**
- trader_types, total_positions, current_balance, polymarket_url
- rank_1d_place, rank_1d_amount (and 7d, 30d, all_time)
- smart_score, total_pnl, sharpe_ratio
- traded_usd_volume_last_30d_sum
- active_bets_amount, active_bets_pnl
- finished_bets_amount, finished_bets_pnl
- best_trade_roi_proc, best_trade_roi_amount
- worst_trade_roi_proc, worst_trade_roi_amount
- where_trader_bets_most (price buckets)

**From CSV:**
- user_address, win_rate, effective_count, num_markets
- score, sum_pnl, last_updated_block

## Notes

- Some fields may be `null` if the user doesn't have that data
- The script automatically skips users that already have JSON files (unless `--refetch` is used)
- Failed fetches are logged but don't stop the script
- Progress is shown as `[current/total]` with message counts
- All fetching is sequential to respect API rate limits

## Troubleshooting

**Issue**: Script hangs or times out
- **Solution**: The script now uses a 30-second total timeout and 5-second per-message timeout. This should prevent hanging.

**Issue**: Some users have all null fields
- **Solution**: This is normal - some users may not have complete profiles or the page didn't load properly. The CSV data is still saved.

**Issue**: "No cookies found" error
- **Solution**: Make sure you're logged into hashdive.com in Chrome and have visited the site recently.

**Issue**: Script is too slow
- **Solution**: This is intentional to respect API rate limits. Each user takes ~5-10 seconds to fetch completely.

