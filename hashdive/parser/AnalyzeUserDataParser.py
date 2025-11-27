import json
import re
import logging
from typing import Dict, Any, Optional, List
from .AnalyzeUserMessageClassifier import AnalyzeUserMessageClassifier, UserMessageType

logger = logging.getLogger(__name__)

class AnalyzeUserDataParser:
    
    def __init__(self):
        self.classifier = AnalyzeUserMessageClassifier()
    
    def parse_user_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"Parsing {len(messages)} messages")
        user_data = {
            "trader_types": [],
            "total_positions": None,
            "active_since_date": None,
            "active_since_days": None,
            "current_balance": None,
            "polymarket_url": None,
            "rank_1d_place": None,
            "rank_1d_amount": None,
            "rank_7d_place": None,
            "rank_7d_amount": None,
            "rank_30d_place": None,
            "rank_30d_amount": None,
            "rank_all_time_place": None,
            "rank_all_time_amount": None,
            "smart_score": None,
            "total_pnl": None,
            "sharpe_ratio": None,
            "traded_usd_volume_last_30d_sum": None,
            "active_bets_amount": None,
            "active_bets_pnl": None,
            "finished_bets_amount": None,
            "finished_bets_pnl": None,
            # "finished_bets_table": None,
            "best_trade_roi_proc": None,
            "best_trade_roi_amount": None,
            "worst_trade_roi_proc": None,
            "worst_trade_roi_amount": None,
            # "finished_trades_chart": None,
            # "distribution_roi_chart": None,
            # "overall_pnl_profit": None,
            # "overall_pnl_loss": None,
            # "most_traded_categories_chart": None,
            # "smart_score_by_category": None,
            # "win_rate_by_category": None,
            # "recent_trades_table": None,
            "where_trader_bets_most": None
        }
        
        message_types_found = {}
        for idx, message in enumerate(messages):
            classified = self.classifier.classify_message(message)
            
            msg_type = classified.message_type.value
            message_types_found[msg_type] = message_types_found.get(msg_type, 0) + 1
            
            if classified.message_type == UserMessageType.TRADER_TYPE:
                trader_type_text = self._extract_trader_type(message)
                logger.debug(f"Extracted trader_type: {trader_type_text}")
                if trader_type_text and trader_type_text not in user_data["trader_types"]:
                    user_data["trader_types"].append(trader_type_text)
            
            # elif classified.message_type == UserMessageType.TRADER_TYPE_DESC:
            #     trader_type_info = self._extract_trader_type_desc(message)
            #     if current_trader_type and trader_type_info:
            #         current_trader_type["type_info"] = trader_type_info
            #         user_data["trader_types"].append(current_trader_type)
            #         current_trader_type = None
            
            elif classified.message_type == UserMessageType.STATS_TOTAL_POSITIONS:
                user_data["total_positions"] = self._extract_total_positions(message)
            
            elif classified.message_type == UserMessageType.STATS_ACTIVE_SINCE:
                active_since_data = self._extract_active_since(message)
                user_data["active_since_date"] = active_since_data.get("date")
                user_data["active_since_days"] = active_since_data.get("days")
            
            elif classified.message_type == UserMessageType.STATS_CURRENT_BALANCE:
                user_data["current_balance"] = self._extract_current_balance(message)
            
            elif classified.message_type == UserMessageType.VIEW_ON_POLYMARKET:
                user_data["polymarket_url"] = self._extract_polymarket_url(message)
            
            elif classified.message_type == UserMessageType.RANK_1D:
                rank_data = self._extract_rank(message)
                user_data["rank_1d_place"] = rank_data.get("place")
                user_data["rank_1d_amount"] = rank_data.get("amount")
            
            elif classified.message_type == UserMessageType.RANK_7D:
                rank_data = self._extract_rank(message)
                user_data["rank_7d_place"] = rank_data.get("place")
                user_data["rank_7d_amount"] = rank_data.get("amount")
            
            elif classified.message_type == UserMessageType.RANK_30D:
                rank_data = self._extract_rank(message)
                user_data["rank_30d_place"] = rank_data.get("place")
                user_data["rank_30d_amount"] = rank_data.get("amount")
            
            elif classified.message_type == UserMessageType.RANK_ALLTIME:
                rank_data = self._extract_rank(message)
                user_data["rank_all_time_place"] = rank_data.get("place")
                user_data["rank_all_time_amount"] = rank_data.get("amount")
            
            elif classified.message_type == UserMessageType.SMART_SCORE_SUMMARY:
                score_data = self._extract_smart_score_summary(message)
                user_data["smart_score"] = score_data.get("smart_score")
                user_data["total_pnl"] = score_data.get("total_pnl")
            
            # elif classified.message_type == UserMessageType.HISTORICAL_PNL_CHART:
            #     user_data["historical_pnl"] = json.dumps(message)
            
            elif classified.message_type == UserMessageType.SHARPE_RATIO:
                user_data["sharpe_ratio"] = self._extract_sharpe_ratio(message)
            
            elif classified.message_type == UserMessageType.TRADED_VOLUME_30D:
                volume_data = self._extract_traded_volume(message)
                user_data["traded_usd_volume_last_30d_sum"] = volume_data.get("sum")
                # user_data["traded_usd_volume_last_30d_chart"] = json.dumps(message)
            
            elif classified.message_type == UserMessageType.ACTIVE_BETS_SUM:
                bets_data = self._extract_active_bets_sum(message)
                user_data["active_bets_amount"] = bets_data.get("amount")
                user_data["active_bets_pnl"] = bets_data.get("pnl")
            
            # elif classified.message_type == UserMessageType.ACTIVE_BETS_TABLE:
            #     user_data["active_bets_table"] = json.dumps(message)
            
            elif classified.message_type == UserMessageType.FINISHED_BETS_SUM:
                bets_data = self._extract_finished_bets_sum(message)
                user_data["finished_bets_amount"] = bets_data.get("amount")
                user_data["finished_bets_pnl"] = bets_data.get("pnl")
            
            # elif classified.message_type == UserMessageType.FINISHED_BETS_TABLE:
            #     user_data["finished_bets_table"] = json.dumps(message)
            
            elif classified.message_type == UserMessageType.BEST_TRADE:
                trade_data = self._extract_trade_data(message)
                user_data["best_trade_roi_proc"] = trade_data.get("roi_proc")
                user_data["best_trade_roi_amount"] = trade_data.get("roi_amount")
            
            elif classified.message_type == UserMessageType.WORST_TRADE:
                trade_data = self._extract_trade_data(message)
                user_data["worst_trade_roi_proc"] = trade_data.get("roi_proc")
                user_data["worst_trade_roi_amount"] = trade_data.get("roi_amount")
            
            # elif classified.message_type == UserMessageType.FINISHED_TRADES_CHART:
            #     user_data["finished_trades_chart"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.DISTRIBUTION_ROI:
            #     user_data["distribution_roi_chart"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.OVERALL_PNL_PROFIT:
            #     user_data["overall_pnl_profit"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.OVERALL_PNL_LOSS:
            #     user_data["overall_pnl_loss"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.MOST_TRADED_CATEGORIES:
            #     user_data["most_traded_categories_chart"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.SMART_SCORE_BY_CATEGORY:
            #     user_data["smart_score_by_category"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.WIN_RATE_BY_CATEGORY:
            #     user_data["win_rate_by_category"] = json.dumps(message)
            
            # elif classified.message_type == UserMessageType.RECENT_TRADES_TABLE:
            #     user_data["recent_trades_table"] = json.dumps(message)
            
            elif classified.message_type == UserMessageType.WHERE_TRADER_BETS_MOST:
                user_data["where_trader_bets_most"] = self._extract_price_buckets(message)
        
        logger.info(f"Message types found: {message_types_found}")
        non_null_count = sum(1 for v in user_data.values() if v is not None and v != [] and v != {})
        logger.info(f"Extracted {non_null_count} non-null fields from messages")
        
        return user_data
    
    def _extract_trader_type(self, message: Dict[str, Any]) -> Optional[str]:
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            match = re.search(r':.*?\[(.*?)\]', markdown_body)
            if match:
                trader_type = match.group(1)
                trader_type = re.sub(r':material/[^\s]+\s*', '', trader_type)
                trader_type = re.sub(r'\s*\([^)]+\)\s*', '', trader_type)
                return trader_type.strip()
        except Exception:
            pass
        return None
    
    def _extract_trader_type_desc(self, message: Dict[str, Any]) -> Optional[str]:
        try:
            return message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
        except Exception:
            pass
        return None
    
    def _extract_total_positions(self, message: Dict[str, Any]) -> Optional[int]:
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            match = re.search(r'>(\d+)</div>', markdown_body)
            if match:
                return int(match.group(1))
        except Exception:
            pass
        return None
    
    def _extract_active_since(self, message: Dict[str, Any]) -> Dict[str, Optional[str]]:
        result = {"date": None, "days": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            date_match = re.search(r'color: #312e81;">([A-Za-z]+ \d{4})</div>', markdown_body)
            days_match = re.search(r'color: #1e1b4b;">(\d+) days</div>', markdown_body)
            
            if date_match:
                result["date"] = date_match.group(1)
            if days_match:
                result["days"] = int(days_match.group(1))
        except Exception:
            pass
        return result
    
    def _extract_current_balance(self, message: Dict[str, Any]) -> Optional[float]:
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            match = re.search(r'<span>([\d,]+\.?\d*)</span>', markdown_body)
            if match:
                return float(match.group(1).replace(',', ''))
        except Exception:
            pass
        return None
    
    def _extract_polymarket_url(self, message: Dict[str, Any]) -> Optional[str]:
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            match = re.search(r'href="(https://polymarket\.com/profile/[^"]+)"', markdown_body)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None
    
    def _extract_rank(self, message: Dict[str, Any]) -> Dict[str, Optional[str]]:
        result = {"place": None, "amount": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            rank_match = re.search(r'Rank: #(\d+)', markdown_body)
            amount_match = re.search(r'\$([\d.]+[kKmM]?)', markdown_body)
            if rank_match:
                result["place"] = f"#{rank_match.group(1)}"
            if amount_match:
                result["amount"] = f"${amount_match.group(1)}"
        except Exception:
            pass
        return result
    
    def _extract_smart_score_summary(self, message: Dict[str, Any]) -> Dict[str, Optional[float]]:
        result = {"smart_score": None, "total_pnl": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            score_match = re.search(r'Smart Score: <strong>([\d.]+)</strong>', markdown_body)
            pnl_match = re.search(r'Total PnL: <strong>\$([\d,]+\.?\d*)</strong>', markdown_body)
            
            if score_match:
                result["smart_score"] = float(score_match.group(1))
            if pnl_match:
                result["total_pnl"] = float(pnl_match.group(1).replace(',', ''))
        except Exception:
            pass
        return result
    
    def _extract_sharpe_ratio(self, message: Dict[str, Any]) -> Optional[float]:
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            match = re.search(r'Sharpe Ratio: <span>([\d.]+)</span>', markdown_body)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        return None
    
    def _extract_traded_volume(self, message: Dict[str, Any]) -> Dict[str, Optional[float]]:
        result = {"sum": None}
        try:
            metric = message.get('delta', {}).get('newElement', {}).get('metric', {})
            body = metric.get('body', '')
            match = re.search(r'\$([\d,]+)', body)
            if match:
                result["sum"] = float(match.group(1).replace(',', ''))
        except Exception:
            pass
        return result
    
    def _extract_active_bets_sum(self, message: Dict[str, Any]) -> Dict[str, Optional[float]]:
        result = {"amount": None, "pnl": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            amount_match = re.search(r'font-size: 26px[^>]*>\s*\$([\d,]+\.?\d*)', markdown_body)
            pnl_match = re.search(r'PnL:.*?<span[^>]*>\s*\$([\d,]+\.?\d*)', markdown_body)
            
            if amount_match:
                result["amount"] = float(amount_match.group(1).replace(',', ''))
            if pnl_match:
                result["pnl"] = float(pnl_match.group(1).replace(',', ''))
        except Exception:
            pass
        return result
    
    def _extract_finished_bets_sum(self, message: Dict[str, Any]) -> Dict[str, Optional[float]]:
        result = {"amount": None, "pnl": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            amount_match = re.search(r'font-size: 26px[^>]*>\s*\$([\d,]+\.?\d*)', markdown_body)
            pnl_match = re.search(r'PnL:.*?<span[^>]*>\s*\$([\d,]+\.?\d*)', markdown_body)
            
            if amount_match:
                result["amount"] = float(amount_match.group(1).replace(',', ''))
            if pnl_match:
                result["pnl"] = float(pnl_match.group(1).replace(',', ''))
        except Exception:
            pass
        return result
    
    def _extract_trade_data(self, message: Dict[str, Any]) -> Dict[str, Optional[float]]:
        result = {"roi_proc": None, "roi_amount": None}
        try:
            markdown_body = message.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
            proc_match = re.search(r'>([+−\-]?[\d,]+\.?\d*)%<', markdown_body)
            amount_match = re.search(r'\(([+−\-]?)\$([\d,]+\.?\d*)\)', markdown_body)
            
            if proc_match:
                proc_str = proc_match.group(1).replace(',', '').replace('−', '-').replace('+', '')
                result["roi_proc"] = float(proc_str)
            if amount_match:
                sign = '-' if amount_match.group(1) in ['−', '-'] else ''
                amount_str = sign + amount_match.group(2).replace(',', '')
                result["roi_amount"] = float(amount_str)
        except Exception:
            pass
        return result
    
    def _extract_price_buckets(self, message: Dict[str, Any]) -> Optional[Dict[str, float]]:
        try:
            plotly_chart = message.get('delta', {}).get('newElement', {}).get('plotlyChart', {})
            spec_str = plotly_chart.get('spec', '')
            
            if spec_str:
                spec_data = json.loads(spec_str)
                data = spec_data.get('data', [])
                
                if data and len(data) > 0:
                    x_values = data[0].get('x', [])
                    y_values = data[0].get('y', [])
                    
                    price_buckets = {}
                    for i, price_bucket in enumerate(x_values):
                        if i < len(y_values):
                            price_buckets[price_bucket] = round(y_values[i], 2)
                    
                    return price_buckets
        except Exception as e:
            pass
        return None

