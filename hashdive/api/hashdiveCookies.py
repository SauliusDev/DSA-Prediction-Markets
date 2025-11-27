import browser_cookie3

"""
Hashdive cookies:

ajs_anonymous_id="4bf6f2a5-59f3-4871-aa35-f3193197055a"
_streamlit_user="2|1:0|10:1761033441|15:_streamlit_user|904:eyJpc3MiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwgImF6cCI6ICI2NDMzNTI0NzIzOTAtaTkwZjJycG0waHV1aWM3OW9icThzdGQ5YjRlZmNrbDAuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCAiYXVkIjogIjY0MzM1MjQ3MjM5MC1pOTBmMnJwbTBodXVpYzc5b2JxOHN0ZDliNGVmY2tsMC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsICJzdWIiOiAiMTEwNzM3NjAwOTMxMTcyMTY1NDY5IiwgImVtYWlsIjogImF6dW9sYXNiYWxiaWVyaXNAZ21haWwuY29tIiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImF0X2hhc2giOiAiNzR1TU5WbnVueTg5UlJUNU9xVVZFdyIsICJub25jZSI6ICJyTDQ1S1VLem0yc1V6cGlNNXkzeCIsICJuYW1lIjogIlx1MDEwNFx1MDE3ZXVvbGFzIEJhbGJpZXJpcyIsICJwaWN0dXJlIjogImh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lnTGhDRWtsVFd4c0VxMXdMalhSREJlMXZuaFFNOG9pU3c0TTBNVFNCaTlZN0JZLUp3PXM5Ni1jIiwgImdpdmVuX25hbWUiOiAiXHUwMTA0XHUwMTdldW9sYXMiLCAiZmFtaWx5X25hbWUiOiAiQmFsYmllcmlzIiwgImlhdCI6IDE3NjEwMzM0NDEsICJleHAiOiAxNzYxMDM3MDQxLCAib3JpZ2luIjogImh0dHBzOi8vaGFzaGRpdmUuY29tIiwgImlzX2xvZ2dlZF9pbiI6IHRydWV9|20d42735a9d008d0f0effa7d0772d66be98cbbfbb4e0e3cdd71851c9ed753f99"
_streamlit_xsrf="2|7e81cd65|d87b8edaa06dd26d618475fa7ee3a4bc|1761853713"
"""

def get_cookies_from_chrome(domain="hashdive.com", names=None, show_debug=False):
    """
    Read cookies for `domain` from the local Chrome profile using browser_cookie3.
    Returns a cookie header string like "name1=val1; name2=val2".
    `names` (optional) - list of cookie names to keep (if None, returns all cookies for domain).
    Requires: pip install browser-cookie3
    """
    try:
        cj = browser_cookie3.chrome(domain_name=domain)
    except Exception:
        cj = browser_cookie3.load()

    cookies = {}
    for cookie in cj:
        cookie_domain = cookie.domain or ""
        if domain.endswith(cookie_domain.lstrip(".")) or cookie_domain.endswith(domain) or domain in cookie_domain:
            if names is None or cookie.name in names:
                cookies[cookie.name] = cookie.value

    if show_debug:
        for cookie in cookies:
            print(cookie+"\n")

    return cookies