import logging
import traceback

import EnvConfig
from driver.ScraperDriver import ScraperDriver
from network import NotifierClient
from usecase import SendDataUseCase, ProvideExecutionConfig, ExecutionManagerTv
from utils import TimeUtils
from utils.ScraperUtils import extract_number_only_from

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)


def obtain_strategies_performance(driver: ScraperDriver) -> dict:
    execution_config = ProvideExecutionConfig.for_all_perpetual_binance_symbols()
    chart_page = ExecutionManagerTv.login(driver)
    strategies_report = ExecutionManagerTv.obtain_strategy_performance_data_for(chart_page, execution_config)
    return strategies_report


def start():
    with TimeUtils.measure_time("Setting up chrome driver took {}."):
        driver = ScraperDriver(headless=False)

    with TimeUtils.measure_time("Obtaining strategies performance data took {}."):
        strategies_performance = obtain_strategies_performance(driver)

    print()


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
