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

async def fetch_user_data(user_address):
    with open("temp/requests/analyze_user.json", 'r') as f:
        payload = json.load(f)
    
    payload['rerunScript']['queryString'] = f"user_address={user_address}"
    
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
    
    user_folder = f"temp/user_data/{user_address}"
    os.makedirs(user_folder, exist_ok=True)
    
    async with HashdiveWSClient(config) as ws_client:
        if not await ws_client.send_binary(encoded_payload):
            print("Failed to send payload")
            return
        
        await asyncio.sleep(1)
        
        message_count = 0
        async for ws_message in ws_client.receive_messages(max_messages=300, timeout_per_message=10, total_timeout=120):
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
                    print(f"Saved message {message_count} to {filename}")
            else:
                try:
                    decoded = json.loads(ws_message.content)
                    filename = f"{user_folder}/message_{message_count}.json"
                    with open(filename, 'w') as f:
                        json.dump(decoded, f, indent=2)
                    print(f"Saved message {message_count} to {filename}")
                except json.JSONDecodeError:
                    filename = f"{user_folder}/message_{message_count}.json"
                    with open(filename, 'w') as f:
                        json.dump({"text": ws_message.content}, f, indent=2)
                    print(f"Saved message {message_count} to {filename}")
            
            if decoded and decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                print(f"Script finished successfully after {message_count} messages")
                break
    
    print(f"Total messages saved: {message_count}")

async def main():
    user_address = "0xf1f06f49be8ce5681752ae80e660aeaace6858df"
    
    if len(sys.argv) > 1:
        user_address = sys.argv[1]
    
    print(f"Fetching data for user: {user_address}")
    await fetch_user_data(user_address)

if __name__ == "__main__":
    asyncio.run(main())

