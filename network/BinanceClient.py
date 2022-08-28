import requests

import EnvConfig


def request_all_symbols_spot() -> list:
    return __fetch_symbols(should_get_spot=True)


def request_all_symbols_perpetual() -> list:
    return __fetch_symbols(should_get_spot=False)


def __fetch_symbols(should_get_spot: bool = False) -> list:
    proxies = {'https': 'http://192.168.0.86:8118',
               'http': 'http://192.168.0.86:8118'} if __do_I_need_proxies() else None
    url_futures = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    url_spot = "https://api.binance.us/api/v3/exchangeInfo"
    r = requests.get(url_spot if should_get_spot else url_futures, proxies=proxies)
    return r.json()["symbols"]


def __do_I_need_proxies() -> bool:
    return not EnvConfig.running_on_server()
