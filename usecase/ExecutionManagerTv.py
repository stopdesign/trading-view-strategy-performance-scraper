import logging
from typing import Optional

from driver.ScraperDriver import ScraperDriver
from model.ExecutionConfig import ExecutionConfig
from model.RuntimeConfig import RuntimeConfig
from network import PerformanceServerClient
from network.PerformanceServerClient import NetworkError
from sites.tradingview.TvChartPage import TvChartPage
from sites.tradingview.TvHomePage import TvHomePage
from usecase import ProvideRuntimeConfig
from utils import TimeUtils, FileUtils


def obtain_strategy_performance_data_for(chart_page: TvChartPage,
                                         execution_config: ExecutionConfig,
                                         should_add_trades: bool = True) -> dict:
    def __add_strategy_report_to(output: dict, overview_report: dict, trades_report: list):
        strategy_name = strategy.name
        if strategy.name not in output.keys():
            output[strategy_name] = {"script": strategy.script}

        coin_name = symbol.equity_name
        interval_value = interval.value

        if coin_name not in output[strategy_name].keys():
            output[strategy_name][coin_name] = {}

        report = overview_report
        if len(trades_report) > 0:
            report["trades"] = trades_report
        output[strategy_name][coin_name][interval_value] = overview_report

    logging.info(f"Obtaining performance data for "
                 f"{len(execution_config.strategies)} strategies, "
                 f"{len(execution_config.symbols)} symbols and "
                 f"{len(execution_config.intervals)} time intervals.")

    performance_report = {}
    for strategy in execution_config.strategies:
        with TimeUtils.measure_time("Obtaining stats for strategy " + strategy.name + " took {}."):
            chart_page.clean_all_overlays() \
                .add_strategy_to_chart(strategy.script) \
                .change_footer_window_full_size(should_maximize_it=True)
            for symbol in execution_config.symbols:
                chart_page.change_symbol_to(symbol).remove_possible_advert_overlay()
                with TimeUtils.measure_time("Obtaining stats for symbol " + symbol.equity_name + " took {}."):
                    for interval in execution_config.intervals:
                        chart_page.change_time_interval_to(interval).remove_possible_advert_overlay()
                        strategy_overview_stats = chart_page.extract_strategy_overview_report()
                        strategy_trades_stats = chart_page.extract_strategy_trades_report() if should_add_trades else []
                        if strategy_overview_stats is not None:
                            __add_strategy_report_to(performance_report, strategy_overview_stats, strategy_trades_stats)
                            logging.info(
                                f"Added report for {symbol.equity_name} and interval {interval.value}: "
                                f"{strategy_overview_stats}")
                            FileUtils.write_json(execution_config.output_file_name, performance_report)

                        else:
                            logging.info(f"No report found for {symbol.equity_name} and interval {interval.value}.")
    return performance_report


def setup_driver(headless: bool = False) -> ScraperDriver:
    return ScraperDriver(headless)


def login(driver: ScraperDriver) -> TvChartPage:
    return TvHomePage(driver) \
        .login("radmi.b.4@gmail.com", "xtn8ubd_RKV.abg_hya") \
        .select_chart() \
        .clean_all_overlays()


def start_obtaining_performances(execution_config: ExecutionConfig):
    driver = setup_driver()
    page = login(driver)
    has_loaded_strategy = False
    while True:
        try:
            with TimeUtils.measure_time("Obtaining runtime config took {}."):
                runtime_config = ProvideRuntimeConfig.request_runtime_config_for(execution_config)

            if has_loaded_strategy is False:
                with TimeUtils.measure_time("Adding strategy to chart took {}."):
                    page.clean_all_overlays()\
                        .add_strategy_to_chart(runtime_config.strategy.script)
                    has_loaded_strategy = True

            with TimeUtils.measure_time(
                    "Obtaining performance for strategy " + runtime_config.strategy.name + " took {}."):
                performance = __obtain_performance_for(runtime_config, page, should_add_trades=False)

            with TimeUtils.measure_time(
                    "Uploading performance for strategy " + runtime_config.strategy.name + " took {}."):
                __upload_performance(performance, runtime_config)

        except NetworkError as e:
            __clean_up_on_crash(e, driver, runtime_config)
            raise e
        except Exception as e:
            __clean_up_on_crash(e, driver, runtime_config)
            start_obtaining_performances(execution_config)


def __clean_up_on_crash(e: Exception, driver: ScraperDriver, runtime_config: Optional[RuntimeConfig]):
    logging.error(e, exc_info=True)
    try:
        driver.close()
    except Exception as e:
        logging.error("Can't close driver.", e)
    if runtime_config:
        PerformanceServerClient.delete_runtime_config(runtime_config.id)


def __obtain_performance_for(runtime_config: RuntimeConfig,
                             chart_page: TvChartPage,
                             should_add_trades: bool) -> dict:
    chart_page.decline_cookies() \
        .remove_possible_advert_overlay() \
        .change_footer_window_full_size(should_maximize_it=True) \
        .change_symbol_to(runtime_config.symbol) \
        .change_time_interval_to(runtime_config.time_interval)

    strategy_performance = chart_page.extract_strategy_overview_report()
    # TODO add it to the server
    # strategy_trades = chart_page.extract_strategy_trades_report() if should_add_trades else []
    return strategy_performance.to_json()


def __upload_performance(performance: dict, runtime_config: RuntimeConfig):
    performance_payload = {
        "symbol": runtime_config.symbol.to_json(),
        "strategy": runtime_config.strategy.to_json(),
        "timeIntervals": [{
            runtime_config.time_interval.value: performance
        }]
    }
    PerformanceServerClient.upload_performance(performance_payload)
