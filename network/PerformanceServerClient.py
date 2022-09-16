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
    response = auth_get_request_payload(endpoint, search_params)
    return __return_json_only_on_success(response)[0]


def request_random_strategy() -> dict:
    endpoint = "/strategy"
    response = auth_get_request_url_params(endpoint, random=1)
    return __return_json_only_on_success(response)[0]


def request_runtime_config(payload: dict) -> dict:
    endpoint = "/runtimeConfig"
    response = auth_get_request_payload(endpoint, payload)
    return __return_json_only_on_success(response)


def delete_runtime_config(obj_id: str):
    endpoint = "/runtimeConfig"
    payload = {"id": obj_id}
    response = auth_delete_request(endpoint, payload)
    if response.status_code != 200:
        raise RuntimeError(f"Deleting config from server returned "
                           f"{response.status_code}: {response.text}.")


def upload_performance(performance: dict) -> list:
    endpoint = "/performance"
    response = auth_put_request(endpoint, performance)
    return __return_json_only_on_success(response)


def auth_get_request_url_params(endpoint: str, **url_params) -> Response:
    url = __base_url + endpoint
    return requests.get(url, auth=(__user, __pass), params=url_params)


def auth_get_request_payload(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.get(url, auth=(__user, __pass), json=payload)


def auth_post_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.post(url, auth=(__user, __pass), json=payload)


def auth_put_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.put(url, auth=(__user, __pass), json=payload)


def auth_delete_request(endpoint: str, payload: Optional[Dict] = None) -> Response:
    url = __base_url + endpoint
    return requests.delete(url, auth=(__user, __pass), json=payload)


def __return_json_only_on_success(response: Response) -> json:
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise RuntimeError(f"Server returned error {response.status_code}: {response.text}...")
