import datetime
import logging
import math
from time import sleep
from typing import Dict, Optional, List

import pyperclip
from bs4 import BeautifulSoup, Tag
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from model.Trade import Trade
from usecase.chartActions import FindChartElements
from utils import WebDriverKeyEventUtils, ScraperUtils


def load_strategy_on_chart(driver: BaseDriver, strategy_content: str, attempts_to_load: int = 0):
    def __open_pine_editor_window():
        __open_footer_chart_panel_button_with(driver, "Pine Editor")

    def __open_free_indicator_tab():
        try:
            xpath = "//div[@id='tv-script-pine-editor-header-root']//div[@data-name='open-script']"
            driver.wait_and_get_element(2, By.XPATH, xpath).click()
            xpath = "//div[@data-name='menu-inner']//span[contains(text(), 'Indicator')]"
            driver.wait_and_get_element(1, By.XPATH, xpath).click()
        except Exception as e:
            raise e

    def __clear_content_and_enter_strategy():
        pyperclip.copy(strategy_content)
        WebDriverKeyEventUtils.send_key_event_select_all_and_paste(driver)

    def __add_to_chart():
        pine_editor_tabs = driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
        pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

    def __did_script_loaded_successfully() -> bool:
        _xpath = "//div[contains(@class,'tv-script-console-text')]//div[last()]"
        last_console_message = driver.wait_and_get_element(1, By.XPATH, _xpath)
        return "error" not in last_console_message.get_attribute("class")

    max_attempts_to_load = 3
    FindChartElements.check_and_close_popups(driver)
    __open_pine_editor_window()
    __open_free_indicator_tab()
    __clear_content_and_enter_strategy()
    __add_to_chart()
    if __did_script_loaded_successfully():
        __open_footer_chart_panel_button_with(driver, "Strategy Tester")
        return
    else:
        if attempts_to_load < max_attempts_to_load:
            logging.info(f"Retrying loading script again to the screen.")
            load_strategy_on_chart(driver, strategy_content, attempts_to_load+1)
        else:
            raise Exception(f"Unable to load script on the screen after {max_attempts_to_load} attempts...")


def extract_strategy_overview(driver: BaseDriver) -> Optional[Dict]:
    def __get_first_line_number_from(index: int, fails_for_first_time=False) -> float:
        try:
            number = driver.wait_and_get_element(1, By.XPATH, f"//div[@class='report-data']//div[{index + 1}]//strong")
            float_number = ScraperUtils.extract_float_number_from(number.text)
            return float_number
        except Exception as e:
            if not fails_for_first_time:
                return __get_first_line_number_from(index, True)
            else:
                return math.nan

    def __get_second_line_number_from(index: int, fails_for_first_time=False) -> float:
        try:
            number = driver.wait_and_get_element(1, By.XPATH, f"//div[@class='report-data']//div[{index + 1}]//span")
            float_number = ScraperUtils.extract_float_number_from(number.text)
            return float_number
        except Exception as e:
            if not fails_for_first_time:
                return __get_second_line_number_from(index, True)
            else:
                return math.nan

    if __were_trades_made(driver):
        __select_strategy_overview(driver)
        return {
            "netProfit": __get_second_line_number_from(0),
            "totalTrades": __get_first_line_number_from(1),
            "profitable": __get_first_line_number_from(2),
            "profitFactor": __get_first_line_number_from(3),
            "maxDrawdown": __get_second_line_number_from(4),
            "avgTrade": __get_second_line_number_from(5),
            "avgBarsInTrade": __get_first_line_number_from(6),
        }
    else:
        return None


def extract_strategy_trades(driver: BaseDriver) -> Optional[List[Trade]]:
    def __extract_table_content_to(output: dict):
        def __extract_text_from_tag(tag: Tag) -> Optional[str]:
            if tag is None:
                # trade not finished and still opened
                return None
            else:
                return tag.text

        def __extract_table_content(has_failed_once: bool = False) -> str:
            try:
                xpath = "//div[contains(@class,'reports-content')]//table"
                table = driver.wait_and_get_element(1, By.XPATH, xpath)
                return table.get_attribute("outerHTML")
            except Exception as e:
                if has_failed_once:
                    raise e
                else:
                    return __extract_table_content(True)

        def __has_trade_closed() -> bool:
            return profit_text is not None

        bs = BeautifulSoup(__extract_table_content(), "lxml")

        for row in bs.find_all("tbody"):
            trade_exit_row, trade_entry_row = row.find_all("tr")
            trade_exit_columns = trade_exit_row.find_all("td")
            # trade_entry_columns = trade_entry_row.find_all("td")

            profit_text = __extract_text_from_tag(
                trade_exit_columns[6].find("div", attrs={"class": "additional_percent_value"}))
            trade_number = int(ScraperUtils.extract_float_number_from(__extract_text_from_tag(trade_exit_columns[0])))

            if __has_trade_closed():
                profit = ScraperUtils.extract_float_number_from(profit_text)
                drawdown = ScraperUtils.extract_float_number_from(
                    __extract_text_from_tag(trade_exit_columns[9].find("div", attrs={"class": "additional_percent_value"})))
                date = datetime.datetime.strptime(__extract_text_from_tag(trade_exit_columns[3]), "%Y-%m-%d %H:%M")
                output[trade_number] = {
                    "date": date,
                    "profit_percentage": profit,
                    "drawdown_percentage": drawdown,
                }
            else:
                output[trade_number] = None

    def __scroll_down_on_trades():
        try:
            xpath = "//table[@class='reports-content__table-pointer']"
            driver.wait_and_get_element(1, By.XPATH, xpath).click()
            WebDriverKeyEventUtils.send_key_event_page_down(driver)
            sleep(0.3)
        except:
            pass

    if __were_trades_made(driver):
        __select_strategy_list_of_trades(driver)
        trades = {}
        while 1 not in trades.keys():
            __extract_table_content_to(trades)
            __scroll_down_on_trades()
        trades_list = [Trade(trade_number, info["date"], info["profit_percentage"], info["drawdown_percentage"]) for
                       trade_number, info in trades.items() if info is not None]
        return trades_list
    else:
        return None


def __were_trades_made(driver: BaseDriver) -> bool:
    try:
        __select_strategy_overview(driver)
        sleep(2)
        xpath = "//div[@class='report-data']//div[@class='data-item']"
        driver.wait_and_get_elements(1, By.XPATH, xpath)  # await for them to show
        return True
    except TimeoutException as e:
        return False


def __select_strategy_overview(driver: BaseDriver):
    xpath = "//div[@id='bottom-area']//div[contains(@class,'tabSwitcherContainer')]//button[text()='Overview']"
    driver.wait_and_get_element(1, By.XPATH, xpath).click()


def __select_strategy_list_of_trades(driver: BaseDriver):
    xpath = "//div[@id='bottom-area']//div[contains(@class,'tabSwitcherContainer')]//button[text()='List of Trades']"
    driver.wait_and_get_element(1, By.XPATH, xpath).click()


def __open_footer_chart_panel_button_with(driver: BaseDriver, text: str):
    try:
        xpath = f"//div[@id='footer-chart-panel']//div[@data-active='false']//span[text()='{text}']"
        driver.wait_and_get_element(1, By.XPATH, xpath).click()
    except TimeoutException:
        pass
