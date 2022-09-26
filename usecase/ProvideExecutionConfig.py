from typing import List

from model.ExecutionConfig import ExecutionConfig, OnExecutionEndStrategy
from model.Strategy import Strategy
from model.Symbol import Symbol, SymbolType
from model.TimeInterval import TimeInterval
from network import BinanceClient, PerformanceServerClient

__BINANCE_EXCLUDED_BASE_ASSETS = ["UST"]  # Tuk sa za6toto TV poradi nqkakva pri4ina ne gi pokazva
__BINANCE_DESIRED_QUOTE_ASSETS = ["USDT", "BUSD"]


def for_all_perpetual(should_use_random_strategy: bool) -> ExecutionConfig:
    strategy = __get_strategy(should_use_random_strategy)
    symbols = __get_all_perpetual_binance_symbols(
        quote_assets=__BINANCE_DESIRED_QUOTE_ASSETS,
        excluded_base_assets=__BINANCE_EXCLUDED_BASE_ASSETS
    )
    time_intervals = __get_time_intervals()
    # what to do when all time frames and symbols are exhausted/done
    on_execution_ended_strategy = __get_on_execution_end_strategy(should_use_random_strategy)
    return ExecutionConfig(symbols=symbols, intervals=time_intervals,
                           strategy=strategy, onExecutionEndedStrategy=on_execution_ended_strategy)


def for_common_equities(should_use_random_strategy: bool) -> ExecutionConfig:
    strategy = __get_strategy_random() if should_use_random_strategy else __get_strategy_ema_vwap()
    symbols = __get_subset_of_different_equities()
    time_intervals = __get_time_intervals()
    # what to do when all time frames and symbols are exhausted/done
    on_execution_ended_strategy = __get_on_execution_end_strategy(should_use_random_strategy)
    return ExecutionConfig(symbols=symbols, intervals=time_intervals,
                           strategy=strategy, onExecutionEndedStrategy=on_execution_ended_strategy)


def get_new_config_with_random_strategy_for(execution_config: ExecutionConfig) -> ExecutionConfig:
    new_strategy = __get_strategy_random()
    return ExecutionConfig(symbols=execution_config.symbols,
                           intervals=execution_config.intervals,
                           strategy=new_strategy,
                           onExecutionEndedStrategy=execution_config.onExecutionEndedStrategy)


def __get_subset_of_different_equities() -> List[Symbol]:
    return [
        Symbol(equity_name="USDCAD", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="USDJPY", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="EURUSD", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="EURGBP", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="EURCAD", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="GBPUSD", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="GBPJPY", broker_name="FXCM", type=SymbolType.FOREX),
        Symbol(equity_name="AAPL", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="TSLA", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="AMZN", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="NVDA", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="BBBY", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="META", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="MSFT", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="BABA", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="NFLX", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="GOOG", broker_name="NASDAQ", type=SymbolType.STOCK),
        Symbol(equity_name="AMC", broker_name="NYSE", type=SymbolType.STOCK),
        Symbol(equity_name="DJI", broker_name="DJ", type=SymbolType.INDEX),
        Symbol(equity_name="SPX", broker_name="SP", type=SymbolType.INDEX),
        Symbol(equity_name="NIFTY", broker_name="NSE", type=SymbolType.INDEX),
        Symbol(equity_name="ES", broker_name="CME_MINI", type=SymbolType.INDEX),
        Symbol(equity_name="GER30", broker_name="GLOBALPRIME", type=SymbolType.INDEX),
        Symbol(equity_name="CRUDEOIL", broker_name="MCX", type=SymbolType.COMMODITY),
        Symbol(equity_name="NATURALGAS", broker_name="MCX", type=SymbolType.COMMODITY),
        Symbol(equity_name="BTCUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="ETHUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="ETCUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="SOLUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="APEUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="EOSUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="XRPUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="BNBUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
        Symbol(equity_name="ATOMUSDTPERP", broker_name="BINANCE", type=SymbolType.CRYPTO),
    ]


def __get_all_perpetual_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_perpetual()
    return [Symbol(equity_name=s['symbol'] + "PERP", broker_name="BINANCE", type=SymbolType.CRYPTO)
            for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_all_spot_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_spot()
    return [Symbol(equity_name=s['symbol'], broker_name="BINANCE", type=SymbolType.CRYPTO)
            for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_strategy(should_use_random_strategy):
    return __get_strategy_random() if should_use_random_strategy else __get_strategy_ema_vwap()


def __get_strategy_ema_vwap() -> Strategy:
    # strategy = PerformanceServerClient.request_strategy(name="ema&vwap&macd", version=1)
    strategy = PerformanceServerClient.request_strategy(name="ema&vwap&macd", version=2)
    return Strategy.from_mongo_server_response(strategy)


def __get_strategy_random() -> Strategy:
    strategy = PerformanceServerClient.request_random_strategy()
    return Strategy.from_mongo_server_response(strategy)


def __get_time_intervals() -> List[TimeInterval]:
    # return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
    #         TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4]
    return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
            TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4,
            TimeInterval.D, TimeInterval.W]
    # return [TimeInterval.M30, TimeInterval.H1, TimeInterval.H2,
            # TimeInterval.H3, TimeInterval.H4]


def __get_on_execution_end_strategy(should_use_random_strategy):
    return OnExecutionEndStrategy.SELECT_NEW_RANDOM_STRATEGY if should_use_random_strategy else OnExecutionEndStrategy.FINISH_EXECUTION
