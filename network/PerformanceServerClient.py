import json
from typing import Dict, Optional

import requests
from requests import Response

import EnvConfig

__user = "chochko"
__pass = EnvConfig.user_pass_chochko()
__base_url = EnvConfig.performance_server_address()


def request_strategy(**search_params) -> dict:
    endpoint = "/strategy"
    response = auth_get_request_url_params(endpoint, search_params)
    return json.loads(response.text)[0]


def request_random_strategy() -> dict:
    return request_strategy(random=1)


def request_runtime_config(payload: dict) -> dict:
    endpoint = "/runtimeConfig"
    response = auth_get_request_payload(endpoint, payload)
    return json.loads(response.text)


def auth_get_request_url_params(endpoint: str, url_params: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.get(url, auth=(__user, __pass), params=url_params)


def auth_get_request_payload(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.get(url, auth=(__user, __pass), data=payload)


def auth_post_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.post(url, auth=(__user, __pass), data=payload)


def auth_put_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.put(url, auth=(__user, __pass), data=payload)


def auth_delete_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.delete(url, auth=(__user, __pass), data=payload)
