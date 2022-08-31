from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor

import requests


def request_community_strategies(max_count: int) -> list:
    url = "https://www.tradingview.com/pubscripts-suggest-json/?search=strategy&offset={}"
    strategies = []
    offset = 0
    while len(strategies) < max_count:
        scripts_raw = requests.get(url.format(offset)).json()["results"]
        with ThreadPoolExecutor() as executor:
            for strategy_info in executor.map(__extract_strategy_from, scripts_raw):
                if strategy_info:
                    strategies.append(strategy_info)
        offset += 50

    return strategies


def __extract_strategy_from(strategy_raw: dict) -> Optional[Dict]:
    def __extract_strategy_script() -> Optional[str]:
        if strategy_raw["scriptSource"] is not None and len(strategy_raw["scriptSource"]) > 0:
            return strategy_raw["scriptSource"]

        # logging.info("Requesting hidden script data")
        hidden_script_url = "https://pine-facade.tradingview.com/pine-facade/get/{}/last?no_4xx=false" \
            .format(strategy_raw["scriptIdPart"])
        r = requests.get(hidden_script_url).json()
        if "code" in r.keys() and r["code"] != 200:
            return None
        else:
            return r["source"]
    script_name = strategy_raw["scriptName"]

    script_content = __extract_strategy_script()
    if script_content is not None and "strategy(" in script_content:
        return {
            "name": script_name,
            "script": script_content
        }
    else:
        return None
