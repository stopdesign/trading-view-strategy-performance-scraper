import logging
from typing import Optional, Dict

import requests


def request_community_strategies(max_count: int) -> list:
    def __extract_strategy_from(strategy_raw) -> Optional[Dict]:
        def __extract_strategy_script() -> Optional[str]:
            if strategy_raw["scriptSource"] is not None and len(strategy_raw["scriptSource"]) > 0:
                return strategy_raw["scriptSource"]

            logging.info("Requesting hidden script data")
            hidden_script_url = "https://pine-facade.tradingview.com/pine-facade/get/{}/last?no_4xx=false" \
                .format(strategy_raw["scriptIdPart"])
            r = requests.get(hidden_script_url).json()
            if "code" in r.keys() and r["code"] != 200:
                return None
            else:
                return r["source"]

        script_name = strategy_raw["scriptName"]
        script_content = __extract_strategy_script()
        if script_content is not None and "strategy(" in script_name:
            return {
                "name": script_name,
                "script": script_content
            }
        else:
            return None

    url = "https://www.tradingview.com/pubscripts-suggest-json/?search=strategy&offset={}"
    strategies = []
    offset = 0
    count = 1
    while len(strategies) < max_count:
        scripts_raw = requests.get(url.format(offset)).json()["results"]
        for strategy in scripts_raw:
            logging.info(f"{count}: Extracting data")
            strategy_info = __extract_strategy_from(strategy)
            if strategy_info is not None:
                strategies.append(strategy_info)
            count += 1
        # strategies += strategies_only
        offset += 50
        print()

    return strategies
