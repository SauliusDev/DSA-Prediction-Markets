import asyncio
import json
import os
import sys
import subprocess
import base64
import re
import pyarrow as pa
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hashdive.api.hashdiveWS import HashdiveWSClient, create_hashdive_config
from hashdive.api.hashdiveCookies import get_cookies_from_chrome

def encode_frame(payload_json, schema="BackMsg"):
    try:
        payload_str = json.dumps(payload_json)
        result = subprocess.run(
            ["node", "hashdive/parser/protobuf_encoder.js", schema],
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
        result = subprocess.run(
            ["node", "hashdive/parser/protobuf_decoder.js", schema],
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

def decode_arrow_data(arrow_data_dict):
    try:
        base64_data = arrow_data_dict.get('data', '')
        if not base64_data:
            return None
        
        binary_data = base64.b64decode(base64_data)
        reader = pa.ipc.open_stream(binary_data)
        table = reader.read_all()
        df = table.to_pandas()
        return df
    except Exception as e:
        print(f"Error decoding arrow data: {e}")
        return None

def extract_page_count(message_data):
    try:
        markdown_body = message_data.get('delta', {}).get('newElement', {}).get('markdown', {}).get('body', '')
        match = re.search(r'Page\s+\d+\s+of\s+(\d+)', markdown_body)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Error extracting page count: {e}")
    return None

def create_page_payload(page_number):
    payload = {
        'rerunScript': {
            'queryString': '',
            'widgetStates': {
                'widgets': [
                    {'id': '$$ID-0cb17bdcbd1740d63048e184ffcfb05a-None', 'intValue': 1},
                    {'id': '$$ID-722e11493fb8cf2cc3c629fa05297af5-None', 'intValue': 49180},
                    {'id': '$$ID-963aac8d9b3cf128d81781468ba5cd07-None', 'doubleValue': -10021171.71951889},
                    {'id': '$$ID-a7a5308fbc35e070dc7fd49c2447e848-None', 'doubleValue': 22053933.752321757},
                    {'id': '$$ID-b91c6ad4c45863922c3dcea830dc6929-None', 'stringValue': 'Score'},
                    {'id': '$$ID-014928b09ab447e44c83623b196b2267-None', 'doubleArrayValue': {'data': [21, 99]}},
                    {'id': '$$ID-67cb5ea9255d46ef710a70b99a6299b7-None', 'doubleArrayValue': {'data': [0, 100]}},
                    {'id': '$$ID-433bd2cd7fb93bbe0a44103640794828-None', 'intValue': 0},
                    {'id': '$$ID-7a46b1f0524835f00b5ba274521d8f7f-None', 'intValue': page_number}
                ]
            },
            'pageScriptHash': '95cbe618bfafb7437263346d6c8503d2',
            'pageName': '',
            'fragmentId': '',
            'cachedMessageHashes': ['3a41fe9df8c1ade2604e52d289d709d6'],
            'contextInfo': {
                'timezone': 'Europe/Istanbul',
                'timezoneOffset': -180,
                'locale': 'en-US',
                'url': 'https://hashdive.com/Trader_explorer',
                'isEmbedded': False,
                'colorScheme': 'light'
            }
        }
    }
    return payload

async def fetch_page(ws_client, page_number):
    print(f"\nFetching page {page_number}...")
    
    payload = create_page_payload(page_number)
    encoded_payload = encode_frame(payload_json=payload, schema="BackMsg")
    
    if not encoded_payload:
        print(f"Failed to encode payload for page {page_number}")
        return None, None
    
    if not await ws_client.send_binary(encoded_payload):
        print(f"Failed to send payload for page {page_number}")
        return None, None
    
    await asyncio.sleep(1)
    
    page_count = None
    dataframe = None
    message_count = 0
    
    async for ws_message in ws_client.receive_messages(max_messages=100, timeout_per_message=None, total_timeout=30):
        message_count += 1
        
        decoded = None
        if ws_message.message_type == 'binary':
            content_bytes = ws_message.content if isinstance(ws_message.content, bytes) else ws_message.content.encode()
            b64_str = base64.b64encode(content_bytes).decode()
            decoded = decode_frame(data=b64_str)
        else:
            try:
                decoded = json.loads(ws_message.content)
            except json.JSONDecodeError:
                pass
        
        if decoded:
            if page_count is None:
                extracted_count = extract_page_count(decoded)
                if extracted_count:
                    page_count = extracted_count
                    print(f"Found total pages: {page_count}")
            
            arrow_data = decoded.get('delta', {}).get('newElement', {}).get('arrowDataFrame', {})
            if arrow_data and dataframe is None:
                dataframe = decode_arrow_data(arrow_data)
                if dataframe is not None:
                    print(f"Page {page_number}: Decoded {len(dataframe)} rows")
            
            if decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                print(f"Page {page_number}: Script finished after {message_count} messages")
                break
    
    return page_count, dataframe

async def main():
    cookies = get_cookies_from_chrome(
        domain="hashdive.com",
        names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
        show_debug=False
    )
    
    if not cookies:
        print("No cookies found")
        return
    
    config = create_hashdive_config(cookies)
    
    os.makedirs("pages", exist_ok=True)
    
    async with HashdiveWSClient(config) as ws_client:
        total_pages = None
        current_page = 1
        
        page_count, df = await fetch_page(ws_client, current_page)
        
        if page_count:
            total_pages = page_count
        
        if df is not None:
            csv_path = f"pages/page_{current_page}.csv"
            df.to_csv(csv_path, index=False)
            print(f"Saved: {csv_path}")
        
        if total_pages is None:
            print("Could not determine total pages")
            return
        
        print(f"\nTotal pages to fetch: {total_pages}")
        
        for page_num in range(2, total_pages + 1):
            _, df = await fetch_page(ws_client, page_num)
            
            if df is not None:
                csv_path = f"pages/page_{page_num}.csv"
                df.to_csv(csv_path, index=False)
                print(f"Saved: {csv_path}")
            else:
                print(f"Failed to fetch data for page {page_num}")
            
            await asyncio.sleep(0.5)
    
    print(f"\n\nCompleted! Fetched {total_pages} pages")
    print(f"All CSV files saved in 'pages/' directory")

if __name__ == "__main__":
    asyncio.run(main())

