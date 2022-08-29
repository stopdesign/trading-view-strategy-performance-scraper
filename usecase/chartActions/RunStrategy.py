import json
import math
from time import sleep
from typing import Dict, Optional

import pyperclip
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
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


def extract_strategy_overview(driver: BaseDriver) -> Optional[Dict]:
    if __were_trades_made(driver):
        pass
    else:
        return None


def __were_trades_made(driver: BaseDriver) -> bool:
    try:
        sleep(2)
        xpath = "//div[@class='report-data']//div[@class='data-item']"
        driver.wait_and_get_elements(1, By.XPATH, xpath)  # await for them to show
        return True
    except TimeoutException:
        return False
