import logging
import traceback

import EnvConfig
from driver.ScraperDriver import ScraperDriver
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from network import NotifierClient
from sites.tradingview.TvHomePage import TvHomePage
from usecase import SendDataUseCase
from utils import TimeUtils, FileUtils

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)


def __build_strategies_scripts() -> dict:
    return {
        "ema&vwap&macd": FileUtils.read_file("strategies/ema&vwap&macd.pinescript")
    }


def __build_time_frames_and_symbols() -> list:
    default_time_intervals = [TimeInterval.M5, TimeInterval.M15, TimeInterval.M30,
                              TimeInterval.H1, TimeInterval.H2, TimeInterval.H3, TimeInterval.H4,
                              TimeInterval.D, TimeInterval.W]
    return [
        {
            "symbol": Symbol("BTCUSDTPERP", "BINANCE"),
            "intervals": default_time_intervals
        },
        {
            "symbol": Symbol("ETHUSDTPERP", "BINANCE"),
            "intervals": default_time_intervals
        },
        {
            "symbol": Symbol("XRPUSDTPERP", "BINANCE"),
            "intervals": default_time_intervals
        },
    ]


def __add_strategy_report_to(output: dict, strategy_name: str, symbol: Symbol, interval: TimeInterval, report: dict):
    if strategy_name not in output.keys():
        output[strategy_name] = {}

    coin_name = symbol.coin_name
    interval_value = interval.value

    if coin_name not in output[strategy_name].keys():
        output[strategy_name][coin_name] = {}

    output[strategy_name][coin_name][interval_value] = report


def obtain_data(driver: ScraperDriver) -> dict:
    homepage = TvHomePage(driver)
    strategies_report = {}
    page = homepage \
        .login("radmi.b.4@gmail.com", "xtn8ubd_RKV.abg_hya") \
        .select_chart() \
        .clean_all_overlays()
        # .change_time_interval_to(TimeInterval.H1) \
        # .change_symbol_to(Symbol("ETHUSDTPERP", "BINANCE"))

    strategies = __build_strategies_scripts()
    time_frames_and_symbols = __build_time_frames_and_symbols()
    for strategy_name, strategy_script in strategies.items():
        page.add_strategy_to_chart(strategy_script)
        for time_frames_and_symbol in time_frames_and_symbols:
            symbol = time_frames_and_symbol["symbol"]
            intervals = time_frames_and_symbol["intervals"]
            page.change_symbol_to(symbol)
            for interval in intervals:
                page.change_time_interval_to(interval)
                performance_stats = page.extract_strategy_report()
                __add_strategy_report_to(strategies_report, strategy_name, symbol, interval, performance_stats)
                logging.info(f"Added report for {symbol.coin_name} and interval {interval.value}: {performance_stats}")
        page.clean_all_overlays()

    return strategies_report


def start():
    with TimeUtils.measure_time("Setting up chrome driver took {}."):
        driver = ScraperDriver(headless=False)

    with TimeUtils.measure_time("Obtaining market cap data took {}."):
        crypto_entries = obtain_data(driver)


if __name__ == '__main__':
    try:
        logging.info("Program starting.")
        with TimeUtils.measure_time("Whole program execution took {}."):
            start()
    except Exception as e:
        crash_info = f"Crashed reason: {str(e)}\n\nFull traceback: {traceback.format_exc()}"
        logging.error("Program crashed...", exc_info=True)
        # NotifierClient.send_email_error(crash_info)
    finally:
        logging.info("Program terminating.")
