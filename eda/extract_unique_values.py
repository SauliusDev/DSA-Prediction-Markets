import json
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict

"""
================================================================================
UNIQUE VALUES ANALYSIS - 938 FILES
================================================================================

TRADER_TYPES (11 unique values):
--------------------------------------------------------------------------------
  - Bagholder
  - Contrarian
  - Lottery Ticket
  - New
  - Novice
  - Reverse Cramer
  - Senior
  - Trend Follower
  - Veteran
  - Waiting for the Money
  - Whale Splash

================================================================================
WHERE_TRADER_BETS_MOST KEYS (10 unique values):
--------------------------------------------------------------------------------
  - 0.0
  - 0.1
  - 0.2
  - 0.3
  - 0.4
  - 0.5
  - 0.6
  - 0.7
  - 0.8
  - 0.9

================================================================================
CATEGORY NAMES (8 unique values):
(Used in most_traded_categories, smart_score_categories, win_rate_categories)
--------------------------------------------------------------------------------
  - Crypto
  - Culture
  - Mentions
  - Music
  - Other
  - Politics
  - Sport
  - Weather

================================================================================
"""


class UniqueValuesExtractor:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.trader_types = set()
        self.where_trader_bets_most_keys = set()
        self.category_names = set()
        self.total_files = 0
        
    def extract_from_file(self, file_path: Path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                if 'trader_types' in data and data['trader_types']:
                    for trader_type in data['trader_types']:
                        self.trader_types.add(trader_type)
                
                if 'where_trader_bets_most' in data and data['where_trader_bets_most']:
                    for key in data['where_trader_bets_most'].keys():
                        self.where_trader_bets_most_keys.add(key)
                
                if 'category_metrics' in data and data['category_metrics']:
                    for metric_type in ['most_traded_categories', 'smart_score_categories', 'win_rate_categories']:
                        if metric_type in data['category_metrics'] and data['category_metrics'][metric_type]:
                            for category in data['category_metrics'][metric_type].keys():
                                self.category_names.add(category)
                                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def extract_all(self):
        json_files = list(self.data_dir.glob('*.json'))
        self.total_files = len(json_files)
        
        for json_file in json_files:
            self.extract_from_file(json_file)
    
    def print_results(self):
        print(f"\n{'='*80}")
        print(f"UNIQUE VALUES ANALYSIS - {self.total_files} FILES")
        print(f"{'='*80}\n")
        
        print(f"TRADER_TYPES ({len(self.trader_types)} unique values):")
        print(f"{'-'*80}")
        for trader_type in sorted(self.trader_types):
            print(f"  - {trader_type}")
        
        print(f"\n{'='*80}")
        print(f"WHERE_TRADER_BETS_MOST KEYS ({len(self.where_trader_bets_most_keys)} unique values):")
        print(f"{'-'*80}")
        for key in sorted(self.where_trader_bets_most_keys, key=lambda x: float(x)):
            print(f"  - {key}")
        
        print(f"\n{'='*80}")
        print(f"CATEGORY NAMES ({len(self.category_names)} unique values):")
        print(f"(Used in most_traded_categories, smart_score_categories, win_rate_categories)")
        print(f"{'-'*80}")
        for category in sorted(self.category_names):
            print(f"  - {category}")
        
        print(f"\n{'='*80}\n")
    
    def get_results_dict(self) -> Dict:
        return {
            'total_files': self.total_files,
            'trader_types': sorted(list(self.trader_types)),
            'where_trader_bets_most_keys': sorted(list(self.where_trader_bets_most_keys), key=lambda x: float(x)),
            'category_names': sorted(list(self.category_names))
        }


if __name__ == '__main__':
    data_dir = '/Users/azuolasbalbieris/dev/dsa-polymarket/data/users'
    
    extractor = UniqueValuesExtractor(data_dir)
    extractor.extract_all()
    extractor.print_results()

