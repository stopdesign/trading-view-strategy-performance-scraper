import logging
from typing import Optional

from driver.ScraperDriver import ScraperDriver
from model.ExecutionConfig import ExecutionConfig, OnExecutionEndStrategy
from model.RuntimeConfig import RuntimeConfig
from network import PerformanceServerClient
from network.PerformanceServerClient import NetworkError, RuntimeConfigExhaustedException
from sites.tradingview.TvChartPage import TvChartPage
from sites.tradingview.TvHomePage import TvHomePage
from usecase import ProvideRuntimeConfig, ProvideExecutionConfig
from utils import TimeUtils


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
                    page.clean_all_overlays() \
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
        except RuntimeConfigExhaustedException as e:
            logging.info(e)
            __on_strategy_performance_extraction_finished(execution_config)
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


def __on_strategy_performance_extraction_finished(execution_config: ExecutionConfig):
    if execution_config.onExecutionEndedStrategy == OnExecutionEndStrategy.SELECT_NEW_RANDOM_STRATEGY:
        new_exec_config = ProvideExecutionConfig.get_new_config_with_random_strategy_for(execution_config)
        logging.info(f"Restarting program with new config: {new_exec_config}")
        start_obtaining_performances(new_exec_config)
    elif execution_config.onExecutionEndedStrategy == OnExecutionEndStrategy.FINISH_EXECUTION:
        logging.info(f"Performance extraction for strategy "
                     f"{execution_config.strategy.name} v{execution_config.strategy.version} "
                     f"is done. Terminating...")
    else:
        logging.error(f"Not handled OnExecutionEndStrategy '{execution_config.onExecutionEndedStrategy}'."
                      f"Terminating...")


def __upload_performance(performance: dict, runtime_config: RuntimeConfig):
    performance_payload = {
        "symbol": runtime_config.symbol.to_json(),
        "strategy": runtime_config.strategy.to_json(),
        "timeIntervals": [{
            runtime_config.time_interval.value: performance
        }]
    }
    PerformanceServerClient.upload_performance(performance_payload)
