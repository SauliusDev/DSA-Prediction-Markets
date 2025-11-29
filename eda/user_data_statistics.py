import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

"""
================================================================================
TOTAL FILES ANALYZED: 938
================================================================================

FIELD NAME                                         NULL       NON-NULL   ZERO       EMPTY     
------------------------------------------------------------------------------------------
active_bets_amount                                 0          938        629        0         
active_bets_pnl                                    202        736        585        0         
active_since_date                                  780        158        0          0         
active_since_days                                  780        158        0          0         
best_trade_roi_amount                              0          938        0          0         
best_trade_roi_proc                                0          938        0          0         
category_metrics                                   0          938        0          0         
current_balance                                    0          938        143        0         
effective_count                                    0          938        0          0         
fetched_at                                         0          938        0          0         
finished_bets_amount                               0          938        0          0         
finished_bets_pnl                                  4          934        0          0         
num_markets                                        0          938        0          0         
polymarket_url                                     0          938        0          0         
rank_1d_amount                                     0          938        0          0         
rank_1d_place                                      0          938        0          0         
rank_30d_amount                                    463        475        0          0         
rank_30d_place                                     463        475        0          0         
rank_7d_amount                                     382        556        0          0         
rank_7d_place                                      382        556        0          0         
rank_all_time_amount                               608        330        0          0         
rank_all_time_place                                608        330        0          0         
sharpe_ratio                                       152        786        1          0         
smart_score                                        0          938        0          0         
total_pnl                                          1          937        0          0         
total_positions                                    0          938        0          0         
traded_usd_volume_last_30d_sum                     0          938        492        0         
trader_types                                       0          938        0          0         
user_address                                       0          938        0          0         
where_trader_bets_most                             13         925        0          0         
win_rate                                           0          938        0          0         
worst_trade_roi_amount                             4          934        0          0         
worst_trade_roi_proc                               4          934        0          0         

================================================================================
CATEGORY METRICS STATISTICS
================================================================================

CATEGORY        PRESENT         ZERO            MISSING        
------------------------------------------------------------
Politics        2192            113             509            
Sport           1974            182             658            
Music           425             75              2314           
Crypto          1918            197             699            
Mentions        365             61              2388           
Weather         523             139             2152           
Culture         992             172             1650           
Other           1287            202             1325      
"""


class UserDataStatistics:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.total_files = 0
        self.field_stats = defaultdict(lambda: {
            'total': 0,
            'null': 0,
            'non_null': 0,
            'zero': 0,
            'empty_dict': 0,
            'empty_list': 0
        })
        self.category_stats = {
            'Politics': {'present': 0, 'zero': 0, 'missing': 0},
            'Sport': {'present': 0, 'zero': 0, 'missing': 0},
            'Music': {'present': 0, 'zero': 0, 'missing': 0},
            'Crypto': {'present': 0, 'zero': 0, 'missing': 0},
            'Mentions': {'present': 0, 'zero': 0, 'missing': 0},
            'Weather': {'present': 0, 'zero': 0, 'missing': 0},
            'Culture': {'present': 0, 'zero': 0, 'missing': 0},
            'Other': {'present': 0, 'zero': 0, 'missing': 0}
        }
        
    def analyze_value(self, value: Any, field_name: str):
        stats = self.field_stats[field_name]
        stats['total'] += 1
        
        if value is None:
            stats['null'] += 1
        else:
            stats['non_null'] += 1
            if isinstance(value, (int, float)) and value == 0:
                stats['zero'] += 1
            elif isinstance(value, dict) and len(value) == 0:
                stats['empty_dict'] += 1
            elif isinstance(value, list) and len(value) == 0:
                stats['empty_list'] += 1
                
    def analyze_nested_dict(self, data: Dict, prefix: str = ''):
        for key, value in data.items():
            field_name = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict) and key not in ['where_trader_bets_most', 'category_metrics']:
                self.analyze_nested_dict(value, field_name)
            else:
                self.analyze_value(value, field_name)
                
    def analyze_category_metrics(self, category_metrics: Dict):
        if not category_metrics:
            return
            
        for metric_type in ['most_traded_categories', 'smart_score_categories', 'win_rate_categories']:
            if metric_type in category_metrics:
                categories = category_metrics[metric_type]
                for category in self.category_stats.keys():
                    if category in categories:
                        value = categories[category]
                        if value == 0 or value == 0.0:
                            self.category_stats[category]['zero'] += 1
                        else:
                            self.category_stats[category]['present'] += 1
                    else:
                        self.category_stats[category]['missing'] += 1
                        
    def analyze_all_files(self):
        json_files = list(self.data_dir.glob('*.json'))
        self.total_files = len(json_files)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    self.analyze_nested_dict(data)
                    
                    if 'category_metrics' in data:
                        self.analyze_category_metrics(data['category_metrics'])
                        
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                
    def print_statistics(self):
        print(f"\n{'='*80}")
        print(f"TOTAL FILES ANALYZED: {self.total_files}")
        print(f"{'='*80}\n")
        
        print(f"{'FIELD NAME':<50} {'NULL':<10} {'NON-NULL':<10} {'ZERO':<10} {'EMPTY':<10}")
        print(f"{'-'*90}")
        
        for field_name in sorted(self.field_stats.keys()):
            stats = self.field_stats[field_name]
            empty_count = stats['empty_dict'] + stats['empty_list']
            
            print(f"{field_name:<50} {stats['null']:<10} {stats['non_null']:<10} {stats['zero']:<10} {empty_count:<10}")
            
        print(f"\n{'='*80}")
        print(f"CATEGORY METRICS STATISTICS")
        print(f"{'='*80}\n")
        
        print(f"{'CATEGORY':<15} {'PRESENT':<15} {'ZERO':<15} {'MISSING':<15}")
        print(f"{'-'*60}")
        
        for category, stats in self.category_stats.items():
            print(f"{category:<15} {stats['present']:<15} {stats['zero']:<15} {stats['missing']:<15}")
            
    def get_statistics_dict(self) -> Dict:
        return {
            'total_files': self.total_files,
            'field_stats': dict(self.field_stats),
            'category_stats': self.category_stats
        }


if __name__ == '__main__':
    data_dir = '/Users/azuolasbalbieris/dev/dsa-polymarket/data/users'
    
    stats = UserDataStatistics(data_dir)
    stats.analyze_all_files()
    stats.print_statistics()

