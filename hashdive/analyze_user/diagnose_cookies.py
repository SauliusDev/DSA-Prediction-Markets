#!/usr/bin/env python3
"""
Detailed cookie diagnostic tool for hashdive.com
"""
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from hashdive.api.hashdiveCookies import get_cookies_from_chrome

def decode_streamlit_cookie(cookie_value):
    """Try to decode Streamlit cookie format: version|signature|timestamp|..."""
    try:
        parts = cookie_value.split('|')
        if len(parts) >= 3:
            version = parts[0]
            signature_type = parts[1]
            
            # Try to find timestamp
            for part in parts:
                if part.startswith('10:'):
                    timestamp_str = part[3:]
                    try:
                        timestamp = int(timestamp_str)
                        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        return {
                            'version': version,
                            'timestamp': timestamp,
                            'datetime': dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
                            'age_hours': (datetime.now(timezone.utc) - dt).total_seconds() / 3600,
                            'valid': True
                        }
                    except:
                        pass
        return {'valid': False, 'reason': 'Could not parse timestamp'}
    except Exception as e:
        return {'valid': False, 'reason': str(e)}

def diagnose_cookies():
    """Diagnose cookie issues."""
    print("=" * 70)
    print("HASHDIVE COOKIE DIAGNOSTIC")
    print("=" * 70)
    
    # Get cookies
    print("\n1. Retrieving cookies from Chrome...")
    cookies = get_cookies_from_chrome(
        domain="hashdive.com",
        names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
        show_debug=False
    )
    
    if not cookies:
        print("❌ CRITICAL: No cookies found!")
        print("\nThis means:")
        print("  - Chrome is not running OR")
        print("  - You haven't visited hashdive.com in Chrome OR")
        print("  - Chrome's cookie database is locked")
        print("\nFix:")
        print("  1. Open Chrome")
        print("  2. Visit https://hashdive.com")
        print("  3. Close Chrome completely")
        print("  4. Run this script again")
        return False
    
    print(f"✓ Found {len(cookies)} cookies\n")
    
    # Check each cookie
    print("2. Analyzing cookies...")
    print("-" * 70)
    
    all_valid = True
    
    # Check ajs_anonymous_id
    if 'ajs_anonymous_id' in cookies:
        value = cookies['ajs_anonymous_id']
        print(f"\n📍 ajs_anonymous_id")
        print(f"   Value: {value[:40]}...")
        print(f"   Length: {len(value)} chars")
        if len(value) > 30:
            print(f"   Status: ✓ Looks valid (UUID format)")
        else:
            print(f"   Status: ⚠️  Suspiciously short")
            all_valid = False
    else:
        print(f"\n❌ ajs_anonymous_id: MISSING")
        all_valid = False
    
    # Check _streamlit_user
    if '_streamlit_user' in cookies:
        value = cookies['_streamlit_user']
        print(f"\n📍 _streamlit_user")
        print(f"   Value: {value[:60]}...")
        print(f"   Length: {len(value)} chars")
        
        decoded = decode_streamlit_cookie(value)
        if decoded['valid']:
            print(f"   Timestamp: {decoded['datetime']}")
            print(f"   Age: {decoded['age_hours']:.1f} hours")
            
            if decoded['age_hours'] < 0:
                print(f"   Status: ❌ INVALID - Timestamp is in the future!")
                print(f"           This cookie is corrupted or system clock is wrong")
                all_valid = False
            elif decoded['age_hours'] > 24:
                print(f"   Status: ⚠️  EXPIRED - Cookie is {decoded['age_hours']:.1f} hours old")
                print(f"           Streamlit sessions typically expire after 24 hours")
                all_valid = False
            elif decoded['age_hours'] > 12:
                print(f"   Status: ⚠️  OLD - Cookie is {decoded['age_hours']:.1f} hours old")
                print(f"           May expire soon, consider refreshing")
            else:
                print(f"   Status: ✓ Valid and fresh")
        else:
            print(f"   Status: ❌ Could not decode - {decoded['reason']}")
            all_valid = False
    else:
        print(f"\n❌ _streamlit_user: MISSING")
        all_valid = False
    
    # Check _streamlit_xsrf
    if '_streamlit_xsrf' in cookies:
        value = cookies['_streamlit_xsrf']
        print(f"\n📍 _streamlit_xsrf")
        print(f"   Value: {value[:60]}...")
        print(f"   Length: {len(value)} chars")
        
        # XSRF tokens should be reasonably long
        if len(value) > 20:
            print(f"   Status: ✓ Looks valid")
        else:
            print(f"   Status: ⚠️  Suspiciously short")
            all_valid = False
    else:
        print(f"\n❌ _streamlit_xsrf: MISSING")
        all_valid = False
    
    # System clock check
    print("\n" + "-" * 70)
    print("\n3. System clock check...")
    now = datetime.now(timezone.utc)
    print(f"   Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Current time (local): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if system time is reasonable (between 2020 and 2030)
    if now.year < 2020 or now.year > 2030:
        print(f"   Status: ❌ System clock appears to be wrong!")
        all_valid = False
    else:
        print(f"   Status: ✓ System clock looks correct")
    
    # Final diagnosis
    print("\n" + "=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)
    
    if all_valid:
        print("\n✓ All cookies appear valid")
        print("\nHowever, if you're still getting 0 messages, the issue is likely:")
        print("  1. Rate limiting - wait 30-60 minutes before trying again")
        print("  2. Server-side session expired - refresh the page in Chrome")
        print("  3. Account/IP blocked - check if you can access hashdive.com")
    else:
        print("\n❌ Cookie issues detected!")
        print("\nRECOMMENDED FIX:")
        print("  1. Close Chrome completely (Cmd+Q on Mac)")
        print("  2. Open Chrome")
        print("  3. Visit https://hashdive.com")
        print("  4. Navigate to a user page (e.g., click on a trader)")
        print("  5. Verify the page loads with data")
        print("  6. Close Chrome completely again (Cmd+Q)")
        print("  7. Wait 5 seconds")
        print("  8. Run this diagnostic again")
    
    print("\n" + "=" * 70)
    
    return all_valid

def main():
    try:
        result = diagnose_cookies()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

