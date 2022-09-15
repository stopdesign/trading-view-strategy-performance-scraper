from typing import List

from model.ExecutionConfig import ExecutionConfig
from model.RuntimeConfig import RuntimeConfig
from model.Strategy import Strategy
from model.Symbol import Symbol, SymbolType
from model.TimeInterval import TimeInterval
from network import BinanceClient, PerformanceServerClient

__BINANCE_EXCLUDED_BASE_ASSETS = ["UST"]  # Tuk sa za6toto TV poradi nqkakva pri4ina ne gi pokazva
__BINANCE_DESIRED_QUOTE_ASSETS = ["USDT", "BUSD"]


def for_all_perpetual(should_use_random_strategy: bool) -> RuntimeConfig:
    strategy = __get_strategy_random() if should_use_random_strategy else __get_strategy_ema_vwap()
    symbols = __get_all_perpetual_binance_symbols(
        quote_assets=__BINANCE_DESIRED_QUOTE_ASSETS,
        excluded_base_assets=__BINANCE_EXCLUDED_BASE_ASSETS
    )
    time_intervals = __get_time_intervals()
    execution_config = ExecutionConfig(symbols=symbols, intervals=time_intervals, strategy=strategy)
    return __request_runtime_config_for(execution_config)


def for_all_equities(should_use_random_strategy: bool) -> RuntimeConfig:
    strategy = __get_strategy_random() if should_use_random_strategy else __get_strategy_ema_vwap()
    symbols = __get_subset_of_different_equities()
    time_intervals = __get_time_intervals()
    execution_config = ExecutionConfig(symbols=symbols, intervals=time_intervals, strategy=strategy)
    return __request_runtime_config_for(execution_config)


def __request_runtime_config_for(execution_config: ExecutionConfig) -> RuntimeConfig:
    symbols = [
        {
            "name": s.equity_name,
            "broker": s.broker_name,
            "type": s.type.value
        } for s in execution_config.symbols
    ]
    time_intervals = [t.value for t in execution_config.intervals]
    payload = {
        "strategy": execution_config.strategy,
        "symbols": symbols,
        "timeIntervals": time_intervals
    }
    raw_config = PerformanceServerClient.request_runtime_config(payload)
    return RuntimeConfig.from_mongo_server_response(raw_config)


def __get_subset_of_different_equities() -> List[Symbol]:
    return [
        Symbol(equity_name="USDCAD", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="USDJPY", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="EURUSD", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="EURGBP", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="EURCAD", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="GBPUSD", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="GBPJPY", broker_name="FXCM", _type=SymbolType.FOREX),
        Symbol(equity_name="AAPL", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="TSLA", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="AMZN", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="NVDA", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="BBBY", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="META", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="MSFT", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="BABA", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="NFLX", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="GOOG", broker_name="NASDAQ", _type=SymbolType.STOCK),
        Symbol(equity_name="AMC", broker_name="NYSE", _type=SymbolType.STOCK),
        Symbol(equity_name="DJI", broker_name="DJ", _type=SymbolType.INDEX),
        Symbol(equity_name="SPX", broker_name="SP", _type=SymbolType.INDEX),
        Symbol(equity_name="NIFTY", broker_name="NSE", _type=SymbolType.INDEX),
        Symbol(equity_name="ES", broker_name="CME_MINI", _type=SymbolType.INDEX),
        Symbol(equity_name="GER30", broker_name="GLOBALPRIME", _type=SymbolType.INDEX),
        Symbol(equity_name="CRUDEOIL", broker_name="MCX", _type=SymbolType.COMMODITY),
        Symbol(equity_name="NATURALGAS", broker_name="MCX", _type=SymbolType.COMMODITY),
        Symbol(equity_name="BTCUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="ETHUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="ETCUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="SOLUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="APEUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="EOSUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="XRPUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="BNBUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
        Symbol(equity_name="ATOMUSDTPERP", broker_name="BINANCE", _type=SymbolType.CRYPTO),
    ]


def __get_all_perpetual_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_perpetual()
    return [Symbol(equity_name=s['symbol'] + "PERP", broker_name="BINANCE", _type=SymbolType.CRYPTO)
            for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_all_spot_binance_symbols(quote_assets: list, excluded_base_assets: list) -> List[Symbol]:
    raw_symbols = BinanceClient.request_all_symbols_spot()
    return [Symbol(equity_name=s['symbol'], broker_name="BINANCE", _type=SymbolType.CRYPTO)
            for s in raw_symbols
            if s['quoteAsset'] in quote_assets and s['baseAsset'] not in excluded_base_assets]


def __get_strategy_ema_vwap() -> Strategy:
    strategy = PerformanceServerClient.request_strategy(name="ema&vwap&macd", version=1)
    return Strategy.from_mongo_server_response(strategy)


def __get_strategy_random() -> Strategy:
    strategy = PerformanceServerClient.request_random_strategy()
    return Strategy.from_mongo_server_response(strategy)


def __get_time_intervals() -> List[TimeInterval]:
    return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
            TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4,
            TimeInterval.D, TimeInterval.W]
    # return [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30]
