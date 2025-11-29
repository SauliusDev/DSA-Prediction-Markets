import asyncio
import json
import os
import sys
import pandas as pd
import subprocess
import base64
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from hashdive.api.hashdiveWS import HashdiveWSClient, create_hashdive_config
from hashdive.api.hashdiveCookies import get_cookies_from_chrome
from hashdive.parser.AnalyzeUserDataParser import AnalyzeUserDataParser
from hashdive.parser.AnalyzeUserMessageClassifier import AnalyzeUserMessageClassifier

MANUAL_COOKIES = {
    "ajs_anonymous_id": None,
    "_streamlit_user": None,
    "_streamlit_xsrf": None,
}
MANUAL_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"fetch_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Create a rotating file handler that creates new files when size limit is reached
# maxBytes: 100MB per file
# backupCount: keep 5 backup files (total ~500MB max)
rotating_handler = RotatingFileHandler(
    log_file,
    maxBytes=100 * 1024 * 1024,  # 100 MB
    backupCount=5,
    encoding='utf-8'
)
rotating_handler.setLevel(logging.INFO)  # Only log INFO and above to file
rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Console handler for real-time monitoring (can be more verbose)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,  # Overall level
    handlers=[rotating_handler, console_handler]
)
logger = logging.getLogger(__name__)

def encode_frame(payload_json, schema="BackMsg"):
    try:
        payload_str = json.dumps(payload_json)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        encoder_path = os.path.join(script_dir, '..', 'parser', 'protobuf_encoder.js')
        
        result = subprocess.run(
            ["node", encoder_path, schema],
            input=payload_str.encode("utf-8"),
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Encoder error:", e.stderr.decode())
        return None

def decode_frame(data: str, schema="ForwardMsg"):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        decoder_path = os.path.join(script_dir, '..', 'parser', 'protobuf_decoder.js')
        
        result = subprocess.run(
            ["node", decoder_path, schema],
            input=data,
            capture_output=True,
            text=True,
            check=True
        )
        decoded_json = json.loads(result.stdout)
        return decoded_json
    except subprocess.CalledProcessError as e:
        print("Decoder error:", e.stderr)
        return None
    except json.JSONDecodeError:
        print("Failed to parse JSON output.")
        return None

def extract_plotly_chart_data(plotly_json_string: str) -> Optional[Dict[str, Any]]:
    try:
        # Parse the outer JSON
        outer_data = json.loads(plotly_json_string)
        
        # Navigate to the spec field and parse it
        spec_string = outer_data['delta']['newElement']['plotlyChart']['spec']
        spec_data = json.loads(spec_string)
        
        # Extract the main data from the first trace
        trace = spec_data['data'][0]
        
        # Get theta (categories) and r (values)
        categories = trace.get('theta', [])
        values = trace.get('r', [])
        
        # Remove duplicate last element (polar charts repeat first point)
        if len(categories) > 1 and categories[0] == categories[-1]:
            categories = categories[:-1]
            values = values[:-1]
        
        # Create a dictionary mapping categories to values
        data_dict = dict(zip(categories, values))
        
        return data_dict
        
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.debug(f"Could not extract Plotly data: {e}")
        return None

def add_category_metrics(user_data: Dict[str, Any]) -> Dict[str, Any]:
    charts_to_extract = [
        'most_traded_categories_chart',
        'smart_score_by_category',
        'win_rate_by_category'
    ]
    
    extracted_data = {}
    
    for chart_name in charts_to_extract:
        if chart_name in user_data:
            chart_data = extract_plotly_chart_data(user_data[chart_name])
            if chart_data:
                # Create a clean field name
                clean_name = chart_name.replace('_chart', '').replace('_by_category', '_categories')
                extracted_data[clean_name] = chart_data
                logger.debug(f"Extracted {clean_name}: {len(chart_data)} categories")
    
    if extracted_data:
        user_data['category_metrics'] = extracted_data
        logger.info(f"Added category_metrics with {len(extracted_data)} metric types")
        
        # Remove the original chart strings to save space
        for chart_name in charts_to_extract:
            if chart_name in user_data:
                del user_data[chart_name]
                logger.debug(f"Removed original chart field: {chart_name}")
    
    return user_data

class MultiUserFetcher:
    def __init__(self, csv_path: str, output_dir: str, limit: Optional[int] = None, 
                 offset: int = 0, refetch: bool = False, use_manual_cookies: bool = False):
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.limit = limit
        self.offset = offset
        self.refetch = refetch
        self.parser = AnalyzeUserDataParser()
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get cookies (manual or from Chrome)
        if use_manual_cookies and any(MANUAL_COOKIES.values()):
            logger.info("Using manual cookies from script configuration")
            self.cookies = {}
            
            # Use manual cookies if provided
            for name in ["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"]:
                if MANUAL_COOKIES.get(name):
                    self.cookies[name] = MANUAL_COOKIES[name]
                    logger.info(f"Using manual cookie: {name}")
            
            # Fetch missing cookies from Chrome
            if len(self.cookies) < 3:
                logger.info("Fetching missing cookies from Chrome...")
                chrome_cookies = get_cookies_from_chrome(
                    domain="hashdive.com",
                    names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
                    show_debug=False
                )
                if chrome_cookies:
                    for name, value in chrome_cookies.items():
                        if name not in self.cookies:
                            self.cookies[name] = value
                            logger.info(f"Fetched {name} from Chrome")
        else:
            logger.info("Fetching cookies from Chrome")
            self.cookies = get_cookies_from_chrome(
                domain="hashdive.com",
                names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
                show_debug=False
            )
        
        if not self.cookies or len(self.cookies) < 3:
            raise Exception("No cookies found for hashdive.com. Visit hashdive.com in Chrome first.")
        
        user_agent = MANUAL_USER_AGENT if use_manual_cookies else None
        self.config = create_hashdive_config(self.cookies, user_agent=user_agent)
        
    def load_users_from_csv(self):
        df = pd.read_csv(self.csv_path)
        
        if self.offset > 0:
            df = df.iloc[self.offset:]
        
        if self.limit:
            df = df.head(self.limit)
        
        return df
    
    def should_fetch_user(self, user_address: str) -> bool:
        output_file = os.path.join(self.output_dir, f"{user_address}.json")
        
        if os.path.exists(output_file) and not self.refetch:
            return False
        
        return True
    
    async def fetch_user_data(self, user_address: str) -> list:
        logger.info(f"Starting fetch for user: {user_address}")
        
        payload = {
            'rerunScript': {
                'queryString': f'user_address={user_address}',
                'widgetStates': {},
                'pageScriptHash': '',
                'pageName': 'Analyze_User',
                'contextInfo': {
                    'timezone': 'Europe/Istanbul',
                    'timezoneOffset': -180,
                    'locale': 'en-US',
                    'url': 'https://hashdive.com/Analyze_User',
                    'isEmbedded': False,
                    'colorScheme': 'light'
                }
            }
        }
        
        logger.debug(f"Payload query string: {payload['rerunScript']['queryString']}")
        
        encoded_payload = encode_frame(payload_json=payload, schema="BackMsg")
        if not encoded_payload:
            logger.error("Failed to encode payload")
            raise Exception("Failed to encode payload")
        
        messages = []
        message_count = 0
        
        async with HashdiveWSClient(self.config) as ws_client:
            if not await ws_client.send_binary(encoded_payload):
                logger.error("Failed to send payload to WebSocket")
                raise Exception("Failed to send payload")
            
            logger.debug("Payload sent, waiting for messages...")
            await asyncio.sleep(2)  # Give server time to process

            user_folder = f"logs/user_data/{user_address}"
            os.makedirs(user_folder, exist_ok=True)
            
            # Wait for messages with long timeouts - script will finish when it receives the completion message
            # timeout_per_message: 120s (2 minutes between messages)
            # total_timeout: None (no total timeout - wait for scriptFinished)
            async for ws_message in ws_client.receive_messages(max_messages=500, timeout_per_message=900, total_timeout=None):
                message_count += 1
                decoded = None
                if ws_message.message_type == 'binary':
                    content_bytes = ws_message.content if isinstance(ws_message.content, bytes) else ws_message.content.encode()
                    b64_str = base64.b64encode(content_bytes).decode()
                    decoded = decode_frame(data=b64_str)
                    if decoded:
                        filename = f"{user_folder}/message_{message_count}.json"
                        with open(filename, 'w') as f:
                            json.dump(decoded, f, indent=2)
                        logger.debug(f"Saved message {message_count} to {filename}")
                        
                        messages.append(decoded)
                        logger.debug(f"Message {message_count}: Binary decoded, keys: {list(decoded.keys())}")
                elif ws_message.message_type == 'text':
                    try:
                        decoded = json.loads(ws_message.content)

                        filename = f"{user_folder}/message_{message_count}.json"
                        with open(filename, 'w') as f:
                            json.dump(decoded, f, indent=2)
                        logger.debug(f"Saved message {message_count} to {filename}")

                        messages.append(decoded)
                        logger.debug(f"Message {message_count}: Text decoded, keys: {list(decoded.keys())}")
                    except json.JSONDecodeError:
                        logger.warning(f"Message {message_count}: Failed to decode text message")
                    
                if decoded and decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                    logger.info(f"Script finished successfully after {message_count} messages")
                    break

        logger.info(f"Received total {len(messages)} messages for {user_address}")
        
        # Warn if no messages received - likely auth/cookie issue
        if len(messages) == 0:
            logger.warning(f"Received 0 messages for {user_address} - possible authentication issue or rate limiting")
            logger.warning("Try refreshing cookies: visit hashdive.com in Chrome and ensure you're logged in")
        
        return messages
    
    async def process_user(self, row: pd.Series, index: int, total: int):
        user_address = row['user_address']
        
        if not self.should_fetch_user(user_address):
            print(f"[{index}/{total}] Skipping {user_address} (already exists)")
            return True
        
        logger.info(f"[{index}/{total}] Processing user: {user_address}")
        print(f"[{index}/{total}] Fetching data for {user_address}...", flush=True)
        
        try:
            messages = await self.fetch_user_data(user_address)
            print(f"[{index}/{total}] Received {len(messages)} messages", flush=True)
            logger.info(f"[{index}/{total}] Received {len(messages)} messages")
            
            logger.debug(f"Parsing messages for {user_address}")
            parsed_data = self.parser.parse_user_messages(messages)
            
            non_null_fields = [k for k, v in parsed_data.items() if v is not None and v != [] and v != {}]
            logger.info(f"Parsed data has {len(non_null_fields)} non-null fields: {non_null_fields}")
            
            parsed_data['user_address'] = user_address
            parsed_data['win_rate'] = float(row['win_rate'])
            parsed_data['effective_count'] = float(row['effective_count'])
            parsed_data['num_markets'] = int(row['num_markets'])
            # parsed_data['sum_pnl'] = float(row['sum_pnl'])
            parsed_data['fetched_at'] = datetime.now(timezone.utc).isoformat()
            
            # Extract and add category metrics from chart data
            parsed_data = add_category_metrics(parsed_data)
            
            output_file = os.path.join(self.output_dir, f"{user_address}.json")
            with open(output_file, 'w') as f:
                json.dump(parsed_data, f, indent=2)
            
            logger.info(f"[{index}/{total}] Successfully saved {user_address}")
            print(f"[{index}/{total}] ✓ Saved {user_address}", flush=True)
            return True
            
        except Exception as e:
            logger.error(f"[{index}/{total}] Error processing {user_address}: {str(e)}", exc_info=True)
            print(f"[{index}/{total}] ✗ Error fetching {user_address}: {str(e)}")
            return False
    
    async def run(self):
        df = self.load_users_from_csv()
        total = len(df)
        
        logger.info(f"Starting fetch for {total} users (offset: {self.offset}, limit: {self.limit})")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Refetch existing: {self.refetch}")
        logger.info(f"Log file: {log_file}")
        
        print(f"Starting fetch for {total} users (offset: {self.offset}, limit: {self.limit})")
        print(f"Output directory: {self.output_dir}")
        print(f"Refetch existing: {self.refetch}")
        print(f"Log file: {log_file}\n")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            user_address = row['user_address']
            
            if not self.should_fetch_user(user_address):
                skip_count += 1
                logger.info(f"[{idx}/{total}] Skipping {user_address} (already exists)")
                print(f"[{idx}/{total}] Skipping {user_address} (already exists)")
                continue
            
            result = await self.process_user(row, idx, total)
            
            if result:
                success_count += 1
            else:
                error_count += 1
            
            await asyncio.sleep(1)
        
        logger.info(f"=== Summary ===")
        logger.info(f"Total users: {total}")
        logger.info(f"Successfully fetched: {success_count}")
        logger.info(f"Skipped (already exist): {skip_count}")
        logger.info(f"Errors: {error_count}")
        
        print(f"\n=== Summary ===")
        print(f"Total users: {total}")
        print(f"Successfully fetched: {success_count}")
        print(f"Skipped (already exist): {skip_count}")
        print(f"Errors: {error_count}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch user data from hashdive for multiple users')
    parser.add_argument('--limit', type=int, default=None, help='Number of users to fetch (default: all)')
    parser.add_argument('--offset', type=int, default=0, help='Offset to start from (default: 0)')
    parser.add_argument('--refetch', action='store_true', help='Refetch users that already exist')
    parser.add_argument('--csv', type=str, default='data/pages/final/combined_31-99ss.csv', 
                        help='Path to CSV file with user addresses')
    parser.add_argument('--output', type=str, default='data/users', 
                        help='Output directory for user JSON files')
    parser.add_argument('--manual-cookies', action='store_true',
                        help='Use manual cookies defined in the script instead of Chrome cookies')
    
    args = parser.parse_args()
    
    fetcher = MultiUserFetcher(
        csv_path=args.csv,
        output_dir=args.output,
        limit=args.limit,
        offset=args.offset,
        refetch=args.refetch,
        use_manual_cookies=args.manual_cookies
    )
    
    asyncio.run(fetcher.run())

if __name__ == "__main__":
    main()

