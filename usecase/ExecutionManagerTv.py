import logging

from driver.ScraperDriver import ScraperDriver
from model.ExecutionConfig import ExecutionConfig
from sites.tradingview.TvChartPage import TvChartPage
from sites.tradingview.TvHomePage import TvHomePage
from utils import TimeUtils


def obtain_strategy_performance_data_for(chart_page: TvChartPage,
                                         execution_config: ExecutionConfig) -> dict:
    def __add_strategy_report_to(output: dict, report: dict):
        strategy_name = strategy.name
        if strategy.name not in output.keys():
            output[strategy_name] = {"script": strategy.script}

        coin_name = symbol.coin_name
        interval_value = interval.value

        if coin_name not in output[strategy_name].keys():
            output[strategy_name][coin_name] = {}

        output[strategy_name][coin_name][interval_value] = report

    logging.info(f"Obtaining performance data for "
                 f"{len(execution_config.strategies)} strategies, "
                 f"{len(execution_config.symbols)} symbols and "
                 f"{len(execution_config.intervals)} time intervals.")

    performance_report = {}
    for strategy in execution_config.strategies:
        with TimeUtils.measure_time("Obtaining stats for strategy " + strategy.name + " took {}."):
            chart_page.add_strategy_to_chart(strategy.script)
            for symbol in execution_config.symbols:
                chart_page.change_symbol_to(symbol).remove_possible_advert_overlay()
                with TimeUtils.measure_time("Obtaining stats for symbol " + symbol.coin_name + " took {}."):
                    for interval in execution_config.intervals:
                        chart_page.change_time_interval_to(interval)
                        performance_stats = chart_page.extract_strategy_report()
                        __add_strategy_report_to(performance_report, performance_stats)
                        logging.info(
                            f"Added report for {symbol.coin_name} and interval {interval.value}: {performance_stats}")
            chart_page.clean_all_overlays()
    return performance_report


def login(driver: ScraperDriver) -> TvChartPage:
    return TvHomePage(driver) \
        .login("radmi.b.4@gmail.com", "xtn8ubd_RKV.abg_hya") \
        .select_chart() \
        .clean_all_overlays()
