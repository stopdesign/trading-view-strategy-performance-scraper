from typing import List

from model.ExecutionConfig import ExecutionConfig
from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from network import BinanceClient
from utils import FileUtils

__BINANCE_EXCLUDED_BASE_ASSETS = ["UST"]  # Tuk sa za6toto TV poradi nqkakva pri4ina ne gi pokazva
__BINANCE_DESIRED_QUOTE_ASSETS = ["USDT", "BUSD"]


def for_all_perpetual_binance_symbols() -> ExecutionConfig:
    symbols = __get_all_perpetual_binance_symbols(
        quote_assets=__BINANCE_DESIRED_QUOTE_ASSETS,
        excluded_base_assets=__BINANCE_EXCLUDED_BASE_ASSETS
    )
    time_intervals = __get_time_intervals()
    strategies = __get_strategies()
    return ExecutionConfig(symbols=symbols, intervals=time_intervals, strategies=strategies)


def __get_all_perpetual_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_perpetual()
    return [Symbol(coin_name=s['symbol'] + "PERP", broker_name="BINANCE") for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_all_spot_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_spot()
    return [Symbol(coin_name=s['symbol'], broker_name="BINANCE") for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_time_intervals() -> List[TimeInterval]:
    return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
            TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4,
            TimeInterval.D, TimeInterval.W]


def __get_strategies() -> List[Strategy]:
    return [
        Strategy(name="ema&vwap&macd", script=FileUtils.read_file("strategies/ema&vwap&macd.pinescript"))
    ]
