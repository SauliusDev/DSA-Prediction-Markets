# Manual Cookie Configuration Guide

## Overview

Both `test_connection.py` and `fetch_multiple_users.py` now support manual cookie configuration. This is useful when:
- Chrome cookies are not accessible
- You want to use specific cookie values
- You're debugging cookie issues
- You want to use fresh cookies from your browser

## How to Use Manual Cookies

### Step 1: Get Your Cookies from Chrome

1. **Open Chrome** and visit https://hashdive.com
2. **Open DevTools**: 
   - Mac: `Cmd + Option + I`
   - Windows: `F12`
3. **Go to Application tab** → **Cookies** → **https://hashdive.com**
4. **Copy the cookie values**:
   - `ajs_anonymous_id`
   - `_streamlit_user`
   - `_streamlit_xsrf`

### Step 2: Set Cookies in the Script

#### For test_connection.py

Edit the file and find the `MANUAL_COOKIES` section at the top:

```python
# MANUAL COOKIE OVERRIDE (set to None to use Chrome cookies)
MANUAL_COOKIES = {
    "ajs_anonymous_id": "4bf6f2a5-59f3-4871-aa35-f3193197055a",  # Your value here
    "_streamlit_user": "2|1:0|10:1763898495|15:_streamlit_user|904:eyJ...",  # Your value here
    "_streamlit_xsrf": "2|406aa2c1|9f2a9fd6b61e9d67774cfeb1491b2eb2|1763898074",  # Your value here
}
```

**Important:** 
- Copy the FULL cookie value (they can be very long, especially `_streamlit_user`)
- Keep the quotes around the values
- Set to `None` to auto-fetch from Chrome instead

#### For fetch_multiple_users.py

Same process - edit the `MANUAL_COOKIES` section at the top of the file:

```python
# MANUAL COOKIE OVERRIDE (set to None to use Chrome cookies)
MANUAL_COOKIES = {
    "ajs_anonymous_id": "your-value-here",
    "_streamlit_user": "your-value-here",
    "_streamlit_xsrf": "2|406aa2c1|9f2a9fd6b61e9d67774cfeb1491b2eb2|1763898074",
}
```

### Step 3: Run with Manual Cookies

#### Test Connection

```bash
# Use manual cookies
python3 hashdive/analyze_user/test_connection.py --manual

# Use Chrome cookies (default)
python3 hashdive/analyze_user/test_connection.py
```

#### Fetch Users

```bash
# Use manual cookies
python3 hashdive/analyze_user/fetch_multiple_users.py --manual-cookies --limit 10

# Use Chrome cookies (default)
python3 hashdive/analyze_user/fetch_multiple_users.py --limit 10
```

## Example: Your Current Cookie

Based on your request, here's how to set just the `_streamlit_xsrf` cookie:

**In test_connection.py or fetch_multiple_users.py:**

```python
MANUAL_COOKIES = {
    "ajs_anonymous_id": None,  # Will auto-fetch from Chrome
    "_streamlit_user": None,    # Will auto-fetch from Chrome
    "_streamlit_xsrf": "2|406aa2c1|9f2a9fd6b61e9d67774cfeb1491b2eb2|1763898074",  # Your manual value
}
```

Then run:
```bash
python3 hashdive/analyze_user/test_connection.py --manual
```

The script will:
- Use your manual `_streamlit_xsrf` value
- Auto-fetch `ajs_anonymous_id` and `_streamlit_user` from Chrome

## Hybrid Mode (Mix Manual + Auto)

You can mix manual and automatic cookies:

```python
MANUAL_COOKIES = {
    "ajs_anonymous_id": "4bf6f2a5-59f3-4871-aa35-f3193197055a",  # Manual
    "_streamlit_user": None,    # Auto-fetch from Chrome
    "_streamlit_xsrf": "2|406aa2c1|9f2a9fd6b61e9d67774cfeb1491b2eb2|1763898074",  # Manual
}
```

## Getting Fresh Cookies

### Method 1: From Chrome DevTools (Recommended)

1. Visit https://hashdive.com in Chrome
2. Open DevTools → Application → Cookies
3. Copy the cookie values
4. Paste into `MANUAL_COOKIES`

### Method 2: From Chrome Cookie File (Advanced)

The cookie diagnostic script shows you the current cookies:

```bash
python3 hashdive/analyze_user/diagnose_cookies.py
```

But note: If cookies are expired, you need to refresh them in the browser first.

## Troubleshooting

### "Still getting 0 messages with manual cookies"

Even with manual cookies, if they're expired, you'll still get 0 messages. Check:

1. **Cookie age**: Run the diagnostic to see if cookies are expired
   ```bash
   python3 hashdive/analyze_user/diagnose_cookies.py
   ```

2. **Get fresh cookies**: Visit hashdive.com, navigate around, then copy fresh cookies

3. **Verify in browser**: Make sure you can actually see data on hashdive.com

### "Cookie value is too long"

The `_streamlit_user` cookie can be 1000+ characters. That's normal. Make sure you copy the ENTIRE value.

### "Script says cookies not found"

If you set manual cookies but don't use the `--manual` or `--manual-cookies` flag, the script will ignore them and try to fetch from Chrome.

**Always use the flag:**
```bash
python3 hashdive/analyze_user/test_connection.py --manual
python3 hashdive/analyze_user/fetch_multiple_users.py --manual-cookies
```

## When to Use Manual Cookies

✅ **Use manual cookies when:**
- Chrome cookies are expired but you have fresh ones from DevTools
- Testing with specific cookie values
- Chrome cookie database is locked
- Running in an environment without Chrome

❌ **Don't use manual cookies when:**
- Chrome cookies are working fine (just use auto-fetch)
- You're not sure if your manual cookies are fresh
- You don't understand what cookies are for

## Security Note

⚠️ **Never share your cookies publicly!** They contain your session information and could allow someone to impersonate you on hashdive.com.

## Quick Reference

### Test with manual cookies:
```bash
# 1. Edit test_connection.py - set MANUAL_COOKIES
# 2. Run with --manual flag
python3 hashdive/analyze_user/test_connection.py --manual
```

### Fetch with manual cookies:
```bash
# 1. Edit fetch_multiple_users.py - set MANUAL_COOKIES
# 2. Run with --manual-cookies flag
python3 hashdive/analyze_user/fetch_multiple_users.py --manual-cookies --limit 10
```

### Back to auto-fetch:
```bash
# Just don't use the flag
python3 hashdive/analyze_user/test_connection.py
python3 hashdive/analyze_user/fetch_multiple_users.py --limit 10
```

