#!/usr/bin/env python3
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from hashdive.api.hashdiveWS import HashdiveWSClient, create_hashdive_config
from hashdive.api.hashdiveCookies import get_cookies_from_chrome

MANUAL_COOKIES = {
    "ajs_anonymous_id": None,
    "_streamlit_user": None,
    "_streamlit_xsrf": None,
}
MANUAL_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

def test_cookies(use_manual=False):
    print("=" * 60)
    print("STEP 1: Testing Cookie Retrieval")
    print("=" * 60)
    
    if use_manual and any(MANUAL_COOKIES.values()):
        print("\nUsing MANUAL cookies from script...")
        cookies = {}
        
        for name in ["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"]:
            if MANUAL_COOKIES.get(name):
                cookies[name] = MANUAL_COOKIES[name]
                print(f"  ✓ Using manual {name}")
        
        if len(cookies) < 3:
            print("\nFetching missing cookies from Chrome...")
            chrome_cookies = get_cookies_from_chrome(
                domain="hashdive.com",
                names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
                show_debug=False
            )
            if chrome_cookies:
                for name, value in chrome_cookies.items():
                    if name not in cookies:
                        cookies[name] = value
                        print(f"  ✓ Fetched {name} from Chrome")
    else:
        print("\nFetching cookies from Chrome...")
        cookies = get_cookies_from_chrome(
            domain="hashdive.com",
            names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
            show_debug=True
        )
    if not cookies:
        print("\n❌ FAILED: No cookies found!")
        return None
    
    print(f"\n✓ Found {len(cookies)} cookies:")
    for name, value in cookies.items():
        print(f"  - {name}: {value[:20]}..." if len(value) > 20 else f"  - {name}: {value}")
    
    return cookies

async def test_connection(cookies, use_manual=False):
    print("\n" + "=" * 60)
    print("STEP 2: Testing WebSocket Connection")
    print("=" * 60)
    
    config = create_hashdive_config(cookies, user_agent=MANUAL_USER_AGENT if use_manual else None)
    print(f"\nConnecting to: {config.url}")
    
    try:
        async with HashdiveWSClient(config) as ws_client:
            print("✓ WebSocket connection established")
            
            print("\nSending test payload...")
            
            import json
            import subprocess
            
            payload = {
                'rerunScript': {
                    'queryString': 'user_address=0x04dbe94fc549e2bfff09aec1cd9d02960adaf0fd',
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
            
            payload_str = json.dumps(payload)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            encoder_path = os.path.join(script_dir, '..', 'parser', 'protobuf_encoder.js')
            
            result = subprocess.run(
                ["node", encoder_path, "BackMsg"],
                input=payload_str.encode("utf-8"),
                capture_output=True,
                check=True
            )
            encoded_payload = result.stdout
            
            if not await ws_client.send_binary(encoded_payload):
                print("❌ Failed to send payload")
                return False
            
            print("✓ Payload sent successfully")
            print("\nWaiting for response messages...")
            
            message_count = 0
            start_time = asyncio.get_event_loop().time()
            
            async for message in ws_client.receive_messages(max_messages=3, timeout_per_message=5, total_timeout=10):
                message_count += 1
                print(f"  ✓ Received message #{message_count} ({message.message_type}, {message.size} bytes)")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            print(f"\n{'='*60}")
            print(f"RESULT: Received {message_count} messages in {elapsed:.1f} seconds")
            print(f"{'='*60}")
            
            if message_count == 0:
                print("\n❌ CONNECTION ISSUE DETECTED!")
                print("\nPossible causes:")
                print("1. Cookies are expired - visit hashdive.com in Chrome and refresh")
                print("2. Rate limiting - wait a few minutes before trying again")
                print("3. Session expired - close and reopen Chrome, visit hashdive.com")
                print("4. Server is down - check if hashdive.com is accessible")
                return False
            else:
                print("\n✓ CONNECTION WORKING!")
                print("Your cookies are valid and the server is responding.")
                return True
                
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test hashdive.com connection')
    parser.add_argument('--manual', action='store_true',
                        help='Use manual cookies defined in the script')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("HASHDIVE CONNECTION TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test cookies
    cookies = test_cookies(use_manual=args.manual)
    if not cookies:
        sys.exit(1)
    
    success = asyncio.run(test_connection(cookies, use_manual=args.manual))
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

