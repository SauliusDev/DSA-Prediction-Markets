import json
import csv
from pathlib import Path
from typing import Dict, List, Any


class JsonToCsvConverter:
    def __init__(self, data_dir: str, output_file: str):
        self.data_dir = Path(data_dir)
        self.output_file = output_file
        
        self.trader_types = [
            'Bagholder', 'Contrarian', 'Lottery Ticket', 'New', 'Novice',
            'Reverse Cramer', 'Senior', 'Trend Follower', 'Veteran',
            'Waiting for the Money', 'Whale Splash'
        ]
        
        self.bet_ranges = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']
        
        self.categories = ['Politics', 'Sport', 'Music', 'Crypto', 'Mentions', 'Weather', 'Culture', 'Other']
        
        self.excluded_fields = {
            'active_bets_pnl', 'active_since_date', 'active_since_days',
            'rank_30d_amount', 'rank_30d_place', 'rank_7d_amount', 'rank_7d_place',
            'rank_all_time_amount', 'rank_all_time_place', 'sharpe_ratio',
            'where_trader_bets_most', 'polymarket_url', 'fetched_at', 'category_metrics'
        }
        
    def get_csv_headers(self) -> List[str]:
        headers = [
            'user_address',
            'total_positions',
            'current_balance',
            'rank_1d_place',
            'rank_1d_amount',
            'smart_score',
            'total_pnl',
            'traded_usd_volume_last_30d_sum',
            'active_bets_amount',
            'finished_bets_amount',
            'finished_bets_pnl',
            'best_trade_roi_proc',
            'best_trade_roi_amount',
            'worst_trade_roi_proc',
            'worst_trade_roi_amount',
            'win_rate',
            'effective_count',
            'num_markets'
        ]
        
        for trader_type in self.trader_types:
            headers.append(f"trader_type_{trader_type.lower().replace(' ', '_')}")
        
        for bet_range in self.bet_ranges:
            headers.append(f"trader_bets_{bet_range.replace('.', '_')}")
        
        for category in self.categories:
            headers.append(f"most_traded_categories_{category.lower()}")
        
        for category in self.categories:
            headers.append(f"smart_score_categories_{category.lower()}")
        
        for category in self.categories:
            headers.append(f"win_rate_categories_{category.lower()}")
        
        return headers
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        row = {}
        
        row['user_address'] = data.get('user_address', '')
        row['total_positions'] = data.get('total_positions', 0)
        row['current_balance'] = data.get('current_balance', 0)
        row['rank_1d_place'] = data.get('rank_1d_place', '')
        row['rank_1d_amount'] = data.get('rank_1d_amount', '')
        row['smart_score'] = data.get('smart_score', 0)
        row['total_pnl'] = data.get('total_pnl', 0) if data.get('total_pnl') is not None else 0
        row['traded_usd_volume_last_30d_sum'] = data.get('traded_usd_volume_last_30d_sum', 0)
        row['active_bets_amount'] = data.get('active_bets_amount', 0)
        row['finished_bets_amount'] = data.get('finished_bets_amount', 0)
        row['finished_bets_pnl'] = data.get('finished_bets_pnl', 0)
        row['best_trade_roi_proc'] = data.get('best_trade_roi_proc', 0)
        row['best_trade_roi_amount'] = data.get('best_trade_roi_amount', 0)
        row['worst_trade_roi_proc'] = data.get('worst_trade_roi_proc', 0)
        row['worst_trade_roi_amount'] = data.get('worst_trade_roi_amount', 0)
        row['win_rate'] = data.get('win_rate', 0)
        row['effective_count'] = data.get('effective_count', 0)
        row['num_markets'] = data.get('num_markets', 0)
        
        user_trader_types = data.get('trader_types', [])
        if user_trader_types is None:
            user_trader_types = []
        for trader_type in self.trader_types:
            key = f"trader_type_{trader_type.lower().replace(' ', '_')}"
            row[key] = 1 if trader_type in user_trader_types else 0
        
        where_bets = data.get('where_trader_bets_most', {})
        if where_bets is None:
            where_bets = {}
        for bet_range in self.bet_ranges:
            key = f"trader_bets_{bet_range.replace('.', '_')}"
            row[key] = where_bets.get(bet_range, 0)
        
        category_metrics = data.get('category_metrics', {})
        if category_metrics is None:
            category_metrics = {}
        
        most_traded = category_metrics.get('most_traded_categories', {})
        if most_traded is None:
            most_traded = {}
        for category in self.categories:
            key = f"most_traded_categories_{category.lower()}"
            row[key] = most_traded.get(category, 0)
        
        smart_score_cats = category_metrics.get('smart_score_categories', {})
        if smart_score_cats is None:
            smart_score_cats = {}
        for category in self.categories:
            key = f"smart_score_categories_{category.lower()}"
            row[key] = smart_score_cats.get(category, 0)
        
        win_rate_cats = category_metrics.get('win_rate_categories', {})
        if win_rate_cats is None:
            win_rate_cats = {}
        for category in self.categories:
            key = f"win_rate_categories_{category.lower()}"
            row[key] = win_rate_cats.get(category, 0)
        
        return row
    
    def convert_all(self):
        json_files = sorted(list(self.data_dir.glob('*.json')))
        total_files = len(json_files)
        
        headers = self.get_csv_headers()
        
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for i, json_file in enumerate(json_files, 1):
                try:
                    row = self.process_file(json_file)
                    writer.writerow(row)
                    
                    if i % 100 == 0:
                        print(f"Processed {i}/{total_files} files...")
                        
                except Exception as e:
                    print(f"Error processing {json_file}: {e}")
        
        print(f"\nConversion complete! {total_files} files processed.")
        print(f"CSV saved to: {self.output_file}")


if __name__ == '__main__':
    data_dir = '/Users/azuolasbalbieris/dev/dsa-polymarket/data/users'
    output_file = '/Users/azuolasbalbieris/dev/dsa-polymarket/data/users_data.csv'
    
    converter = JsonToCsvConverter(data_dir, output_file)
    converter.convert_all()

