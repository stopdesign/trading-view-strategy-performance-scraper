import logging
import traceback

import EnvConfig
from driver.ScraperDriver import ScraperDriver
from network import NotifierClient
from usecase import SendDataUseCase, ProvideExecutionConfig, ExecutionManagerTv, HandleCommunityStrategyScripts
from utils import TimeUtils, FileUtils

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)


def test():
    scripts = HandleCommunityStrategyScripts.request_community_strategies(500)
    print()


def obtain_strategies_performance(driver: ScraperDriver, should_use_external_scripts: bool):
    if should_use_external_scripts:
        return obtain_strategies_performance_from_external_scripts(driver)
    else:
        return obtain_strategies_performance_from_local_scripts(driver)


def obtain_strategies_performance_from_local_scripts(driver: ScraperDriver) -> dict:
    execution_config = ProvideExecutionConfig.for_all_perpetual_symbols_local_scripts()
    chart_page = ExecutionManagerTv.login(driver)
    strategies_report = ExecutionManagerTv \
        .obtain_strategy_performance_data_for(chart_page, execution_config, should_add_trades=True)
    return strategies_report


def obtain_strategies_performance_from_external_scripts(driver: ScraperDriver) -> dict:
    max_amount_of_external_strategies = 50
    should_store_locally_external_strategies = True
    execution_config = ProvideExecutionConfig \
        .for_all_equities_external_scripts(max_amount_of_external_strategies,
                                           should_store_locally_external_strategies)
    chart_page = ExecutionManagerTv.login(driver)
    strategies_report = ExecutionManagerTv \
        .obtain_strategy_performance_data_for(chart_page, execution_config, should_add_trades=False)
    return strategies_report
    pass


def write_to_json(strategy_performance, should_use_external_scripts: bool):
    output_folder = "output"
    filename = f"{TimeUtils.get_time_stamp_formatted('%d-%b-%yT%H-%M-%S')}-" \
               f"{'external' if should_use_external_scripts else 'internal'}.json"
    path = f"{output_folder}/{filename}"
    FileUtils.create_folders_with_file(filename, output_folder)
    FileUtils.write_json(path, strategy_performance)


def start(should_use_external_scripts: bool):
    with TimeUtils.measure_time("Setting up chrome driver took {}."):
        driver = ScraperDriver(headless=False)

    with TimeUtils.measure_time("Obtaining strategies performance data took {}."):
        strategies_performance = obtain_strategies_performance(driver, should_use_external_scripts)

    with TimeUtils.measure_time("Storing data took {}."):
        write_to_json(strategies_performance, should_use_external_scripts)

    logging.info("Done!")


if __name__ == '__main__':
    try:
        logging.info("Program starting.")
        with TimeUtils.measure_time("Whole program execution took {}."):
            # start(should_use_external_scripts=False)
            start(should_use_external_scripts=True)
            # test()
    except Exception as e:
        crash_info = f"Crashed reason: {str(e)}\n\nFull traceback: {traceback.format_exc()}"
        logging.error("Program crashed...", exc_info=True)
        # NotifierClient.send_email_error(crash_info)
    finally:
        logging.info("Program terminating.")
