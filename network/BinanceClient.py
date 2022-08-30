
import requests
from requests import Response

import EnvConfig


def request_all_symbols_spot() -> list:
    return __fetch_symbols(should_get_spot=True)


def request_all_symbols_perpetual() -> list:
    return __fetch_symbols(should_get_spot=False)


def __fetch_symbols(should_get_spot: bool = False) -> list:
    url_futures = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    url_spot = "https://api.binance.us/api/v3/exchangeInfo"
    r = __make_binance_request(url_spot if should_get_spot else url_futures)
    return r.json()["symbols"]


def __make_binance_request(url: str) -> Response:
    proxies = {'https': 'http://192.168.0.86:8118',
               'http': 'http://192.168.0.86:8118'} if __do_I_need_proxies() else None
    return requests.get(url, proxies=proxies)


def __do_I_need_proxies() -> bool:
    return not EnvConfig.running_on_server()
