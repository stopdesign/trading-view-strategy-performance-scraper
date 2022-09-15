from typing import List

from model.ExecutionConfig import ExecutionConfig
from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from network import BinanceClient
from usecase import HandleCommunityStrategyScripts
from utils import FileUtils, TimeUtils

__BINANCE_EXCLUDED_BASE_ASSETS = ["UST"]  # Tuk sa za6toto TV poradi nqkakva pri4ina ne gi pokazva
__BINANCE_DESIRED_QUOTE_ASSETS = ["USDT", "BUSD"]


def for_all_perpetual_symbols_local_scripts() -> ExecutionConfig:
    symbols = __get_all_perpetual_binance_symbols(
        quote_assets=__BINANCE_DESIRED_QUOTE_ASSETS,
        excluded_base_assets=__BINANCE_EXCLUDED_BASE_ASSETS
    )
    time_intervals = __get_time_intervals()
    strategies = __get_strategies()
    output_file_name = __get_output_file_name(is_for_external_scripts=False)
    return ExecutionConfig(symbols=symbols, intervals=time_intervals,
                           strategies=strategies, output_file_name=output_file_name)


def for_all_equities_external_scripts(max_amount_scripts: int, should_store_strategies: bool) -> ExecutionConfig:
    symbols = __get_subset_of_different_equities()
    time_intervals = __get_time_intervals()
    with TimeUtils.measure_time("Downloading " + str(max_amount_scripts) + " scripts took {}."):
        # strategies = __get_community_tv_strategies(max_amount_scripts)
        strategies = __get_strategies_from_folder("strategies/external/31-Aug-22T22-50-new-desired-7")
    if should_store_strategies:
        with TimeUtils.measure_time("Persisting " + str(len(strategies)) + " scripts took {}."):
            HandleCommunityStrategyScripts.store_community_strategy(strategies, "strategies")

    output_file_name = __get_output_file_name(is_for_external_scripts=True)
    return ExecutionConfig(symbols=symbols, intervals=time_intervals,
                           strategies=strategies, output_file_name=output_file_name)


def __get_subset_of_different_equities() -> List[Symbol]:
    return [
        Symbol(equity_name="USDCAD", broker_name="FXCM"),
        Symbol(equity_name="USDJPY", broker_name="FXCM"),
        Symbol(equity_name="EURUSD", broker_name="FXCM"),
        Symbol(equity_name="EURGBP", broker_name="FXCM"),
        Symbol(equity_name="EURCAD", broker_name="FXCM"),
        Symbol(equity_name="GBPUSD", broker_name="FXCM"),
        Symbol(equity_name="GBPJPY", broker_name="FXCM"),
        Symbol(equity_name="AAPL", broker_name="NASDAQ"),
        Symbol(equity_name="TSLA", broker_name="NASDAQ"),
        Symbol(equity_name="AMZN", broker_name="NASDAQ"),
        Symbol(equity_name="NVDA", broker_name="NASDAQ"),
        Symbol(equity_name="BBBY", broker_name="NASDAQ"),
        Symbol(equity_name="META", broker_name="NASDAQ"),
        Symbol(equity_name="MSFT", broker_name="NASDAQ"),
        Symbol(equity_name="BABA", broker_name="NASDAQ"),
        Symbol(equity_name="NFLX", broker_name="NASDAQ"),
        Symbol(equity_name="GOOG", broker_name="NASDAQ"),
        Symbol(equity_name="AMC", broker_name="NYSE"),
        Symbol(equity_name="DJI", broker_name="DJ"),
        Symbol(equity_name="SPX", broker_name="SP"),
        Symbol(equity_name="NIFTY", broker_name="NSE"),
        Symbol(equity_name="ES", broker_name="CME_MINI"),
        Symbol(equity_name="CRUDEOIL", broker_name="MCX"),
        Symbol(equity_name="NATURALGAS", broker_name="MCX"),
        Symbol(equity_name="GER30", broker_name="GLOBALPRIME"),
        Symbol(equity_name="BTCUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="ETHUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="ETCUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="SOLUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="APEUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="EOSUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="XRPUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="BNBUSDTPERP", broker_name="BINANCE"),
        Symbol(equity_name="ATOMUSDTPERP", broker_name="BINANCE"),
    ]


def __get_all_perpetual_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_perpetual()
    return [Symbol(equity_name=s['symbol'] + "PERP", broker_name="BINANCE") for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_all_spot_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_spot()
    return [Symbol(equity_name=s['symbol'], broker_name="BINANCE") for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_time_intervals() -> List[TimeInterval]:
    return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
            TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4,
            TimeInterval.D, TimeInterval.W]
    # return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30]


def __get_strategies() -> List[Strategy]:
    return [
        Strategy(name="ema&vwap&macd",
                 script=FileUtils.read_file("strategies/ema&vwap&macd.pinescript"),
                 version=1)
    ]


def __get_community_tv_strategies(max_amount: int) -> List[Strategy]:
    return HandleCommunityStrategyScripts.request_community_strategies(max_amount)


def __get_strategies_from_folder(folder_name: str) -> List[Strategy]:
    files = FileUtils.read_all_files_in(folder_name)
    return [Strategy(name=f["name"], script=f["content"], version=1) for f in files]


def __get_output_file_name(is_for_external_scripts: bool) -> str:
    directory = FileUtils.get_path_for("output", "performance")
    file_name = f"{TimeUtils.get_time_stamp_formatted('%d-%b-%yT%H-%M')}-" \
                f"{'external' if is_for_external_scripts else 'local'}.json"
    return FileUtils.create_folders_with_file(file_name, directory)