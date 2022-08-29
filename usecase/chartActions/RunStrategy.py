import datetime
import json
import math
from time import sleep
from typing import Dict, Optional, List

import pyperclip
from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from model.Trade import Trade
from usecase.chartActions import FindChartElements
from utils import WebDriverKeyEventUtils, ScraperUtils


def load_strategy_on_chart(driver: BaseDriver, strategy_content: str):
    def __open_editor_editor_window():
        # pine_script_editor_window = driver.wait_and_get_element(3, By.ID, "bottom-area")
        xpath = "//button[@data-name='toggle-visibility-button']"
        visibility_footer_window_btn = driver.wait_and_get_element(3, By.XPATH, xpath)
        is_footer_window_minimized = json.loads(visibility_footer_window_btn.get_attribute("data-active"))
        if is_footer_window_minimized:
            visibility_footer_window_btn.click()
            FindChartElements.change_full_screen_state_footer(driver, False)
        footer_tabs = driver.wait_and_get_element(5, By.ID, "footer-chart-panel")
        try:
            pinescript_editor_window = driver.wait_and_get_element(1, By.CLASS_NAME, "tv-script-editor-container")
            is_pine_editor_tab_visible = ScraperUtils.extract_number_only_from(
                pinescript_editor_window.get_attribute("style")) > 0
            if not is_pine_editor_tab_visible:
                footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Pine Editor')]").click()
        except TimeoutException:
            footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Pine Editor')]").click()

        pine_editor_tabs = driver.wait_and_get_element(5, By.ID, "tv-script-pine-editor-header-root")
        pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='open-script']").click()

        indicator_type_script = driver.wait_and_get_element(5, By.XPATH, "//div[@data-name='menu-inner']") \
            .find_element(By.XPATH, "//span[contains(text(), 'Indicator')]")
        indicator_type_script.click()

    def __clear_content_and_enter_strategy():
        pyperclip.copy(strategy_content)
        WebDriverKeyEventUtils.send_key_event_select_all_and_paste(driver)

    def __add_to_chart():
        pine_editor_tabs = driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
        pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

    FindChartElements.check_and_close_popups(driver)
    __open_editor_editor_window()
    __clear_content_and_enter_strategy()
    __add_to_chart()
    # self.__change_full_screen_state_footer(True)


def extract_strategy_overview(driver: BaseDriver) -> Optional[Dict]:
    def __get_first_line_number_from(index: int, fails_for_first_time=False) -> float:
        try:
            number = driver.wait_and_get_element(1, By.XPATH, f"//div[@class='report-data']//div[{index + 1}]//strong")
            float_number = ScraperUtils.extract_number_only_from(number.text)
            return float_number
        except Exception as e:
            if not fails_for_first_time:
                return __get_first_line_number_from(index, True)
            else:
                return math.nan

    def __get_second_line_number_from(index: int, fails_for_first_time=False) -> float:
        try:
            number = driver.wait_and_get_element(1, By.XPATH, f"//div[@class='report-data']//div[{index + 1}]//span")
            float_number = ScraperUtils.extract_number_only_from(number.text)
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
        xpath = "//div[contains(@class,'reports-content')]//table"
        table = driver.wait_and_get_element(3, By.XPATH, xpath)
        bs = BeautifulSoup(table.get_attribute("outerHTML"), "lxml")

        for row in bs.find_all("tbody"):
            trade_exit_row, trade_entry_row = row.find_all("tr")
            trade_exit_columns = trade_exit_row.find_all("td")
            # trade_entry_columns = trade_entry_row.find_all("td")

            profit = ScraperUtils.extract_number_only_from(
                trade_exit_columns[6].find("div", attrs={"class": "additional_percent_value"}).text)
            drawdown = ScraperUtils.extract_number_only_from(
                trade_exit_columns[9].find("div", attrs={"class": "additional_percent_value"}).text)
            date = datetime.datetime.strptime(trade_exit_columns[3].text, "%Y-%m-%d %H:%M")
            trade_number = int(ScraperUtils.extract_number_only_from(trade_exit_columns[0].text))
            output[trade_number] = {
                "date": date,
                "profit_percentage": profit,
                "drawdown_percentage": drawdown,
            }

        print()

    def __scroll_down_on_trades():
        xpath = "//table[@class='reports-content__table-pointer']//tbody"
        driver.wait_and_get_element(1, By.XPATH, xpath).click()
        WebDriverKeyEventUtils.send_key_event_page_down(driver)
        sleep(0.3)

    if __were_trades_made(driver):
        __select_strategy_list_of_trades(driver)
        trades = {}
        while 1 not in trades.keys():
            __extract_table_content_to(trades)
            __scroll_down_on_trades()
        trades_list = [Trade(trade_number, info["date"], info["profit_percentage"], info["drawdown_percentage"]) for
                       trade_number, info in trades.items()]
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
    driver.wait_and_get_element(3, By.XPATH, xpath).click()


def __select_strategy_list_of_trades(driver: BaseDriver):
    xpath = "//div[@id='bottom-area']//div[contains(@class,'tabSwitcherContainer')]//button[text()='List of Trades']"
    driver.wait_and_get_element(3, By.XPATH, xpath).click()
