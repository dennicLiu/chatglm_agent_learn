from typing import Optional
import requests
import urllib.parse
BASE_URL = 'http://127.0.0.1:3006/engine/tools/'

def process_request(endpoint: str, method: str = 'GET', params: Optional[dict] = None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'accept': 'application/json'}
    response = getattr(requests, method.lower())(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")

    return response.json()

def search_product(params):
    query = params.get("query", "")
    encoded_product_name = urllib.parse.quote(query)
    return process_request(f'product/{encoded_product_name}')

def pick_order(params):
    query = params.get("query", "default")
    encoded_query = urllib.parse.quote(query)
    return process_request(f'order/{encoded_query}')

def cancel_order(params):
    query = params.get("query", "default")
    return process_request(f'order/{query}/3', 'PUT')

tools_mapping = {
    "search_product": search_product,
    "pick_order": pick_order,
    "cancel_order": cancel_order
}
