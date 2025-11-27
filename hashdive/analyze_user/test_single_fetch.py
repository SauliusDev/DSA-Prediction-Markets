import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from hashdive.api.hashdiveService import HashdiveService, HashdiveRequest

async def main():
    service = HashdiveService()
    user_address = "0xbce95071a5a1c15a65bc257d38ba3bed06e903e9"
    
    payload_path = "temp/requests/analyze_user.json"
    with open(payload_path, 'r') as f:
        base_payload = json.load(f)
    
    base_payload['rerunScript']['queryString'] = f"user_address={user_address}"
    
    request = HashdiveRequest(
        market_question=base_payload['rerunScript']['queryString'],
        page_name=base_payload['rerunScript']['pageName'],
        timezone=base_payload['rerunScript']['contextInfo']['timezone'],
        timezone_offset=base_payload['rerunScript']['contextInfo']['timezoneOffset'],
        locale=base_payload['rerunScript']['contextInfo']['locale'],
        color_scheme=base_payload['rerunScript']['contextInfo']['colorScheme']
    )
    
    messages = []
    async def message_callback(message: dict, count: int):
        messages.append(message)
        print(f"Received message {count}")
    
    print(f"Fetching data for {user_address}...")
    response = await service.analyze_market(
        request=request,
        max_messages=200,
        timeout_seconds=120,
        message_callback=message_callback,
        use_pool=False
    )
    
    print(f"\nTotal messages received: {len(messages)}")
    print(f"Success: {response.success}")
    if not response.success:
        print(f"Error: {response.error}")
    
    if messages:
        print(f"\nFirst message keys: {messages[0].keys()}")
        print(f"First message: {json.dumps(messages[0], indent=2)[:500]}")

if __name__ == "__main__":
    asyncio.run(main())

