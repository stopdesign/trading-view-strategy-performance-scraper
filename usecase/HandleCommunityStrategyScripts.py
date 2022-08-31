from itertools import repeat
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

import requests

from model.Strategy import Strategy
from utils import ScraperUtils, TimeUtils, FileUtils

__MAX_TREAD_POOL_WORKERS = 32


def request_community_strategies(max_count: int) -> List[Strategy]:
    url = "https://www.tradingview.com/pubscripts-suggest-json/?search=strategy&offset={}"
    strategies = []
    offset = 0
    while len(strategies) < max_count:
        scripts_raw = requests.get(url.format(offset)).json()["results"]
        with ThreadPoolExecutor(max_workers=__MAX_TREAD_POOL_WORKERS) as executor:
            for strategy_info in executor.map(__extract_strategy_from, scripts_raw):
                if strategy_info:
                    strategies.append(strategy_info)
        offset += 50

    return strategies


def store_community_strategy(strategies: List[Strategy], output_dir: str):
    with ThreadPoolExecutor(max_workers=__MAX_TREAD_POOL_WORKERS) as executor:
        executor.map(__write_strategy_to, repeat(f"{output_dir}/external"), strategies)


def __write_strategy_to(folder: str, strategy: Strategy):
    output_folder = f"{folder}/{TimeUtils.get_time_stamp_formatted('%d-%b-%yT%H-%M')}"
    filename = f"{ScraperUtils.extract_everything_but_symbols_from(strategy.name, separator='_')}" \
               f"-v{strategy.version}-external.pinescript"
    path = f"{output_folder}/{filename}"
    # logging.info(f"Storing file at {path}")
    FileUtils.create_folders_with_file(filename, output_folder)
    FileUtils.write_file(path, strategy.script)


def __extract_strategy_from(strategy_raw: dict) -> Optional[Strategy]:
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

    def __is_strategy_repainted(content: str) -> bool:
        if "security(" in content:
            if "barmerge.lookahead_on" in content:
                return True
            elif "//@version=2" in content or \
                    "//@version=1" in content or \
                    "//@version" not in content:
                return True
        else:
            return False

    script_name = strategy_raw["scriptName"]
    script_version = ScraperUtils.extract_int_number_from(strategy_raw["version"])
    script_content = __extract_strategy_script()
    if script_content is not None and \
            "strategy(" in script_content and \
            not __is_strategy_repainted(script_content):
        return Strategy(name=script_name, script=script_content, version=script_version)
    else:
        return None
