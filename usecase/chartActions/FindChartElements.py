import json
import logging
from typing import List, Optional

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver
from model.Symbol import Symbol
from utils import WebDriverKeyEventUtils


def find_overlap_manager_element(driver: BaseDriver) -> WebElement:
    return driver.wait_and_get_element(5, By.ID, "overlap-manager-root")


def find_top_toolbar_element_symbol(driver: BaseDriver) -> WebElement:
    return find_top_toolbar_elements(driver)[0].find_element(By.ID, "header-toolbar-symbol-search")


def find_top_toolbar_element_interval(driver: BaseDriver) -> WebElement:
    return find_top_toolbar_elements(driver)[1]


def find_top_toolbar_elements(driver: BaseDriver) -> List[WebElement]:
    xpath = "//div[@class='layout__area--top']/div[contains(@class, 'toolbar')]" \
            "//*[@data-is-fake-main-panel='false']//*[contains(@class, 'group')]"
    toolbars_items = driver.wait_and_get_elements(5, By.XPATH, xpath)
    return toolbars_items


def find_chart_element(driver: BaseDriver):
    return driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")


def find_whole_page_element(driver: BaseDriver):
    return driver.wait_and_get_element(5, By.CLASS_NAME, "chart-page")


def change_full_screen_state_footer(driver: BaseDriver, should_be_full_screen: bool):
    try:
        xpath = "//button[@data-name='toggle-maximize-button']"
        maximize_button = driver.wait_and_get_element(3, By.XPATH, xpath)
    except TimeoutException:
        return
    is_maximized = json.loads(maximize_button.get_attribute("data-active"))
    if is_maximized != should_be_full_screen:
        maximize_button.click()


def check_and_close_popups(driver: BaseDriver):
    try:
        close_buttons = filter(
            lambda button: "close-button" in button.get_attribute("class") or
                           "closeButton" in button.get_attribute("class"),
            find_overlap_manager_element(driver).find_elements(By.TAG_NAME, "button"))
        close_button = next(close_buttons, None)
    except TimeoutException:
        logging.info("No popups found for closing...")
        return
    if close_button:
        close_button.click()


def find_new_search_symbol_matching(symbol: Symbol, driver: BaseDriver) -> WebElement:
    xpath_symbol_rows = "//div[@id='overlap-manager-root']//*[contains(@class,'dialog')]" \
                        "//*[contains(@class, 'itemRow')]"
    try:
        found_symbol_rows = driver.wait_and_get_elements(5, By.XPATH, xpath_symbol_rows)
    except TimeoutException:
        raise RuntimeError(f"No symbols returned from TradingView for symbol {symbol}")

    for found_symbol in found_symbol_rows:
        symbol_name = found_symbol.find_element(By.XPATH, "//div[@data-name='list-item-title']")
        symbol_broker = found_symbol.find_element(By.XPATH, "//div[contains(@class,'exchangeName')]")
        if symbol_name.text == symbol.coin_name and symbol_broker.text == symbol.broker_name:
            return symbol_name
    raise RuntimeError(f"Can't find desired symbol for {symbol}")

