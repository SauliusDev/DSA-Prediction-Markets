import logging
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class UserMessageType(Enum):
    TRADER_TYPE = "trader_type"
    TRADER_TYPE_DESC = "trader_type_desc"
    STATS_TOTAL_POSITIONS = "stats_total_positions"
    STATS_ACTIVE_SINCE = "stats_active_since"
    STATS_CURRENT_BALANCE = "stats_current_balance"
    VIEW_ON_POLYMARKET = "view_on_polymarket"
    RANK_1D = "rank_1d"
    RANK_7D = "rank_7d"
    RANK_30D = "rank_30d"
    RANK_ALLTIME = "rank_alltime"
    SMART_SCORE_SUMMARY = "smart_score_summary"
    HISTORICAL_PNL_CHART = "historical_pnl_chart"
    SHARPE_RATIO = "sharpe_ratio"
    TRADED_VOLUME_30D = "traded_volume_30d"
    ACTIVE_BETS_SUM = "active_bets_sum"
    ACTIVE_BETS_TABLE = "active_bets_table"
    FINISHED_BETS_SUM = "finished_bets_sum"
    FINISHED_BETS_TABLE = "finished_bets_table"
    BEST_TRADE = "best_trade"
    WORST_TRADE = "worst_trade"
    DISTRIBUTION_ROI = "distribution_roi"
    MOST_TRADED_CATEGORIES = "most_traded_categories"
    SMART_SCORE_BY_CATEGORY = "smart_score_by_category"
    WIN_RATE_BY_CATEGORY = "win_rate_by_category"
    RECENT_TRADES_TABLE = "recent_trades_table"
    WHERE_TRADER_BETS_MOST = "where_trader_bets_most"
    UNKNOWN = "unknown"

@dataclass
class ClassifiedMessage:
    message_type: UserMessageType
    data: Dict[str, Any]
    delta_path: list

class AnalyzeUserMessageClassifier:
    
    def __init__(self):
        self.last_message_type = None
        self.rank_sequence_count = 0
        self.active_bets_seen = False
        self.finished_bets_seen = False
    
    def classify_message(self, message_data: Dict[str, Any]) -> ClassifiedMessage:
        try:
            delta_path = message_data.get('metadata', {}).get('deltaPath', [])
            message_type = self._identify_message_type(message_data)
            
            return ClassifiedMessage(
                message_type=message_type,
                data=message_data,
                delta_path=delta_path
            )
            
        except Exception as e:
            logger.error(f"Error classifying message: {e}")
            return ClassifiedMessage(
                message_type=UserMessageType.UNKNOWN,
                data=message_data,
                delta_path=[]
            )
    
    def _identify_message_type(self, message_data: Dict[str, Any]) -> UserMessageType:
        try:
            delta = message_data.get('delta', {})
            new_element = delta.get('newElement', {})
            
            content = self._extract_content(new_element)
            
            if self.last_message_type == UserMessageType.TRADER_TYPE:
                self.last_message_type = None
                return UserMessageType.TRADER_TYPE_DESC
            
            if self.last_message_type == UserMessageType.ACTIVE_BETS_SUM and not self.active_bets_seen:
                self.active_bets_seen = True
                self.last_message_type = None
                if 'arrowDataFrame' in new_element:
                    return UserMessageType.ACTIVE_BETS_TABLE
            
            if self.last_message_type == UserMessageType.FINISHED_BETS_SUM and not self.finished_bets_seen:
                self.finished_bets_seen = True
                self.last_message_type = None
                if 'arrowDataFrame' in new_element:
                    return UserMessageType.FINISHED_BETS_TABLE
            
            if self.last_message_type == UserMessageType.RANK_1D:
                self.rank_sequence_count += 1
                if self.rank_sequence_count == 1:
                    return UserMessageType.RANK_7D
                elif self.rank_sequence_count == 2:
                    return UserMessageType.RANK_30D
                elif self.rank_sequence_count == 3:
                    self.rank_sequence_count = 0
                    self.last_message_type = None
                    return UserMessageType.RANK_ALLTIME
            
            if ':material/' in content:
                self.last_message_type = UserMessageType.TRADER_TYPE
                return UserMessageType.TRADER_TYPE
            
            if '>Total Positions<' in content:
                return UserMessageType.STATS_TOTAL_POSITIONS
            
            if '>Active Since<' in content:
                return UserMessageType.STATS_ACTIVE_SINCE
            
            if 'Current Balance\n' in content or '>Current Balance<' in content:
                return UserMessageType.STATS_CURRENT_BALANCE
            
            if '<a href="https://polymarket.com/profile/' in content:
                return UserMessageType.VIEW_ON_POLYMARKET
            
            if '>Rank: ' in content:
                self.last_message_type = UserMessageType.RANK_1D
                return UserMessageType.RANK_1D
            
            if 'User Smart Score:' in content:
                return UserMessageType.SMART_SCORE_SUMMARY
            
            if 'Historical PnL' in content:
                return UserMessageType.HISTORICAL_PNL_CHART
            
            if 'Sharpe Ratio:' in content:
                return UserMessageType.SHARPE_RATIO
            
            if 'Traded USD Volume (Last 30d, daily)' in content:
                return UserMessageType.TRADED_VOLUME_30D
            
            if 'Active Bets' in content and 'PnL:' in content:
                self.last_message_type = UserMessageType.ACTIVE_BETS_SUM
                return UserMessageType.ACTIVE_BETS_SUM
            
            if 'Finished Bets' in content and 'PnL:' in content:
                self.last_message_type = UserMessageType.FINISHED_BETS_SUM
                return UserMessageType.FINISHED_BETS_SUM
            
            if 'Best trade (ROI):' in content:
                return UserMessageType.BEST_TRADE
            
            if 'Worst trade (ROI):' in content:
                return UserMessageType.WORST_TRADE
            
            if 'Distribution of ROI weighted by invested capital' in content:
                return UserMessageType.DISTRIBUTION_ROI
            
            if 'Markets traded:' in content:
                return UserMessageType.MOST_TRADED_CATEGORIES
            
            if 'Smart Score: %{r:.2f}' in content:
                return UserMessageType.SMART_SCORE_BY_CATEGORY
            
            if 'Win Rate: %{r:.2%}' in content:
                return UserMessageType.WIN_RATE_BY_CATEGORY
            
            if '"timestamp": {"label": "Timestamp"' in content and '"question": {"label": "Question"' in content:
                return UserMessageType.RECENT_TRADES_TABLE
            
            if 'Where This Trader Bets Most' in content:
                return UserMessageType.WHERE_TRADER_BETS_MOST
            
            return UserMessageType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Error identifying message type: {e}")
            return UserMessageType.UNKNOWN
    
    def _extract_content(self, new_element: Dict[str, Any]) -> str:
        content_parts = []
        
        if 'markdown' in new_element:
            body = new_element['markdown'].get('body', '')
            content_parts.append(body)
        
        if 'metric' in new_element:
            body = new_element['metric'].get('body', '')
            label = new_element['metric'].get('label', '')
            content_parts.append(label)
            content_parts.append(body)
        
        if 'plotlyChart' in new_element:
            spec = new_element['plotlyChart'].get('spec', '')
            content_parts.append(spec)
        
        if 'arrowDataFrame' in new_element:
            columns = new_element['arrowDataFrame'].get('columns', '')
            content_parts.append(str(columns))
        
        return ' '.join(content_parts)

