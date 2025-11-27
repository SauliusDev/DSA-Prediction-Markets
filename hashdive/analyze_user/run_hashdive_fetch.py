import asyncio
import json
import os
import sys
import subprocess
import base64

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

async def main():
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
                    {'id': '$$ID-0586509f63dac7bb4265535e9f6227c2-None', 'intValue': 1}
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
    
    encoded_payload = encode_frame(payload_json=payload, schema="BackMsg")
    if not encoded_payload:
        print("Failed to encode payload")
        return
    
    cookies = get_cookies_from_chrome(
        domain="hashdive.com",
        names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
        show_debug=False
    )
    
    if not cookies:
        print("No cookies found")
        return
    
    config = create_hashdive_config(cookies)
    
    os.makedirs("temp", exist_ok=True)
    
    async with HashdiveWSClient(config) as ws_client:
        if not await ws_client.send_binary(encoded_payload):
            print("Failed to send payload")
            return
        
        await asyncio.sleep(1)
        
        message_count = 0
        async for ws_message in ws_client.receive_messages(max_messages=300, timeout_per_message=None, total_timeout=60):
            message_count += 1
            
            decoded = None
            if ws_message.message_type == 'binary':
                content_bytes = ws_message.content if isinstance(ws_message.content, bytes) else ws_message.content.encode()
                b64_str = base64.b64encode(content_bytes).decode()
                decoded = decode_frame(data=b64_str)
                if decoded:
                    filename = f"temp/response{message_count}.json"
                    with open(filename, 'w') as f:
                        json.dump(decoded, f, indent=2)
                    print(f"Saved message {message_count} to {filename}")
            else:
                try:
                    decoded = json.loads(ws_message.content)
                    filename = f"temp/response{message_count}.json"
                    with open(filename, 'w') as f:
                        json.dump(decoded, f, indent=2)
                    print(f"Saved message {message_count} to {filename}")
                except json.JSONDecodeError:
                    filename = f"temp/response{message_count}.json"
                    with open(filename, 'w') as f:
                        json.dump({"text": ws_message.content}, f, indent=2)
                    print(f"Saved message {message_count} to {filename}")
            
            if decoded and decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                print(f"Script finished successfully after {message_count} messages")
                break
    
    print(f"Total messages saved: {message_count}")

if __name__ == "__main__":
    asyncio.run(main())
