import logging
import traceback
from typing import Tuple, Dict, Optional

from driver.ScraperDriver import ScraperDriver
from model.RuntimeConfig import RuntimeConfig
from network import NotifierClient
from usecase import SendDataUseCase, ProvideExecutionConfig, ExecutionManagerTv, HandleCommunityStrategyScripts
from utils import TimeUtils, FileUtils

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)

StrategyPerformanceReturnType = Dict
ProgramReturnType = Tuple[RuntimeConfig, Optional[StrategyPerformanceReturnType]]


def obtain_strategy_performance(driver: ScraperDriver, should_use_random_strategy: bool) \
        -> ProgramReturnType:
    should_use_common_securities = True
    if should_use_common_securities:
        return obtain_performance_for_common_securities(driver, should_use_random_strategy)
    else:
        return obtain_performance_for_all_perpetual(driver, should_use_random_strategy)


def obtain_performance_for_all_perpetual(driver: ScraperDriver, should_use_random_strategy: bool) \
        -> ProgramReturnType:
    runtime_config = ProvideExecutionConfig.for_all_perpetual(should_use_random_strategy)
    return __obtain_performance_for(runtime_config, driver, False)


def obtain_performance_for_common_securities(driver: ScraperDriver, should_use_random_strategy: bool) \
        -> ProgramReturnType:
    runtime_config = ProvideExecutionConfig.for_common_equities(should_use_random_strategy)
    return __obtain_performance_for(runtime_config, driver, False)


def __obtain_performance_for(runtime_config: RuntimeConfig, driver: ScraperDriver,
                             should_add_trades: bool) -> ProgramReturnType:
    try:
        chart_page = ExecutionManagerTv.login(driver)
        strategies_report = ExecutionManagerTv \
            .obtain_strategy_performance_data_for(chart_page, runtime_config, should_add_trades)
        return runtime_config, strategies_report
    except Exception as exc:
        logging.error(exc, exc_info=True)
        return runtime_config, None


def upload_report(runtime_config: RuntimeConfig, strategy_performance: StrategyPerformanceReturnType):
    # TODO upload performance and delete runtime config
    pass


def start(should_use_random_strategy: bool):
    with TimeUtils.measure_time("Setting up chrome driver took {}."):
        driver = ScraperDriver(headless=False)

    with TimeUtils.measure_time("Obtaining strategy performance data took {}."):
        runtime_config, strategies_performance = obtain_strategy_performance(driver, should_use_random_strategy)

    with TimeUtils.measure_time("Uploading report took {}."):
        upload_report(runtime_config, strategies_performance)

    logging.info("Done!")


if __name__ == '__main__':
    try:
        logging.info("Program starting.")
        with TimeUtils.measure_time("Whole program execution took {}."):
            start(should_use_random_strategy=False)
    except Exception as e:
        crash_info = f"Crashed reason: {str(e)}\n\nFull traceback: {traceback.format_exc()}"
        logging.error("Program crashed...", exc_info=True)
        # NotifierClient.send_email_error(crash_info)
    finally:
        logging.info("Program terminating.")
