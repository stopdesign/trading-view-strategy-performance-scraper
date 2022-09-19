import logging
import traceback
from usecase import ProvideExecutionConfig, ExecutionManagerTv
from utils import TimeUtils

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)


def start(should_use_random_strategy: bool, should_use_common_securities: bool):
    with TimeUtils.measure_time("Obtaining execution config took {}."):
        if should_use_common_securities:
            runtime_config = ProvideExecutionConfig.for_common_equities(should_use_random_strategy)
        else:
            runtime_config = ProvideExecutionConfig.for_all_perpetual(should_use_random_strategy)

    ExecutionManagerTv.start_obtaining_performances(runtime_config)


if __name__ == '__main__':
    try:
        logging.info("Program starting.")
        with TimeUtils.measure_time("Whole program execution took {}."):
            start(should_use_random_strategy=True, should_use_common_securities=True)
    except Exception as e:
        crash_info = f"Crashed reason: {str(e)}\n\nFull traceback: {traceback.format_exc()}"
        logging.error("Program crashed...", exc_info=True)
        # NotifierClient.send_email_error(crash_info)
    finally:
        logging.info("Program terminating.")


