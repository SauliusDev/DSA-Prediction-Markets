

import requests

url = "https://hashdive.com/api/get_api_usage"
headers = {"x-api-key": "730b7191b0ab05142e5aa3bccc1fb2132083d605ba4c57e0fc0e8bfcfb44d1a1"}

res = requests.get(url, headers=headers)
print(res)