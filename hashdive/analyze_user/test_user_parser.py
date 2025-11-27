import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hashdive.parser.AnalyzeUserDataParser import AnalyzeUserDataParser

def test_parser_with_local_files():
    user_address = "0x285af1872ac997dd54367a799cb2fd9cb0d5fd1b"
    user_folder = f"temp/user_data/{user_address}"
    
    if not os.path.exists(user_folder):
        print(f"User folder not found: {user_folder}")
        return
    
    messages = []
    message_files = sorted(Path(user_folder).glob('message_*.json'), key=lambda x: int(x.stem.split('_')[1].split()[0]))
    
    print(f"Loading {len(message_files)} message files...")
    
    for message_file in message_files:
        try:
            with open(message_file, 'r') as f:
                message = json.load(f)
                messages.append(message)
        except Exception as e:
            print(f"Error loading {message_file.name}: {e}")
    
    print(f"Loaded {len(messages)} messages successfully")
    print("\nParsing user data...")
    
    parser = AnalyzeUserDataParser()
    user_data = parser.parse_user_messages(messages)
    
    output_file = f"temp/parsed_user_{user_address}.json"
    with open(output_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    print(f"\nParsed data saved to: {output_file}")
    
    print("\n=== Extracted Data Summary ===")
    print(f"Trader Types: {user_data['trader_types']}")
    
    print(f"\nTotal Positions: {user_data['total_positions']}")
    print(f"Current Balance: ${user_data['current_balance']}")
    print(f"Polymarket URL: {user_data['polymarket_url']}")
    
    print(f"\nRanks:")
    print(f"  1D: {user_data['rank_1d_place']} - {user_data['rank_1d_amount']}")
    print(f"  7D: {user_data['rank_7d_place']} - {user_data['rank_7d_amount']}")
    print(f"  30D: {user_data['rank_30d_place']} - {user_data['rank_30d_amount']}")
    print(f"  All-time: {user_data['rank_all_time_place']} - {user_data['rank_all_time_amount']}")
    
    print(f"\nSmart Score: {user_data['smart_score']}")
    print(f"Total PnL: ${user_data['total_pnl']}")
    print(f"Sharpe Ratio: {user_data['sharpe_ratio']}")
    
    print(f"\nTraded Volume (30d): ${user_data['traded_usd_volume_last_30d_sum']}")
    
    print(f"\nActive Bets:")
    print(f"  Amount: ${user_data['active_bets_amount']}")
    print(f"  PnL: ${user_data['active_bets_pnl']}")
    
    print(f"\nFinished Bets:")
    print(f"  Amount: ${user_data['finished_bets_amount']}")
    print(f"  PnL: ${user_data['finished_bets_pnl']}")
    
    print(f"\nBest Trade:")
    print(f"  ROI: {user_data['best_trade_roi_proc']}%")
    print(f"  Amount: ${user_data['best_trade_roi_amount']}")
    
    print(f"\nWorst Trade:")
    print(f"  ROI: {user_data['worst_trade_roi_proc']}%")
    print(f"  Amount: ${user_data['worst_trade_roi_amount']}")
    
    print(f"\nWhere Trader Bets Most (Price Buckets):")
    if user_data['where_trader_bets_most']:
        for bucket, volume in sorted(user_data['where_trader_bets_most'].items(), key=lambda x: float(x[0])):
            print(f"  {bucket}: ${volume:,.2f}")

if __name__ == "__main__":
    test_parser_with_local_files()

