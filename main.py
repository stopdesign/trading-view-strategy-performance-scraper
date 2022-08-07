import logging
import traceback

import EnvConfig
from driver.ScraperDriver import ScraperDriver
from network import NotifierClient
from sites.tradingview.TvHomePage import TvHomePage
from usecase import SendDataUseCase
from utils import TimeUtils, FileUtils

logging.basicConfig(format='[%(asctime)s.%(msecs)03d][%(levelname)s]:  %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)


def obtain_data(driver: ScraperDriver):
    homepage = TvHomePage(driver)
    scan_results = homepage \
        .login("radmi.b.4@gmail.com", "xtn8ubd_RKV.abg_hya") \
        .select_chart() \
        .clean_all_overlays() \
        .run_strategy(FileUtils.read_file("strategies/ema&vwap&macd.txt"))
        # .hide_sidebar()
        # .select_filter_with(EnvConfig.filter_name()) \
        # .wait(2) \
        # .extract_data()
    return []


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
