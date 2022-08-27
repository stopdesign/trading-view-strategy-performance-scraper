import logging
from time import sleep
from typing import Optional

import pyperclip
import json
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from sites.tradingview.TvBasePage import TvBasePage
from selenium.webdriver import Keys

from usecase.chartActions import FindChartElements
from utils import ScraperUtils, WebDriverKeyEventUtils


class TvChartPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page("https://www.tradingview.com/chart/")
        self.accept_cookies()
        self.wait_for_chart_to_appear()

    def wait_for_chart_to_appear(self):
        FindChartElements.find_chart_element(self.driver)
        return self

    def clean_all_overlays(self):
        def __scroll_to_no_candles():
            def __move_to_end_of_candles_to_the_right():
                WebDriverKeyEventUtils.send_key_events(self.driver,
                                                       holding_down_keys=[Keys.COMMAND, Keys.ALT],
                                                       keys_to_press=[Keys.ARROW_RIGHT])

            def __move_chart_further_to_the_right():
                WebDriverKeyEventUtils.send_key_events(self.driver,
                                                       holding_down_keys=[Keys.ALT],
                                                       keys_to_press=[Keys.ARROW_RIGHT])

            __move_to_end_of_candles_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()

        def __clear_overlays_with_right_click():
            __scroll_to_no_candles()

            chart = FindChartElements.find_chart_element(self.driver)
            WebDriverKeyEventUtils.send_right_click_event(self.driver, chart)
            context_overlay_menu = self.driver.wait_and_get_element(5, By.CLASS_NAME, "context-menu")
            remove_indicators = context_overlay_menu.find_element(By.XPATH,
                                                                  "//span[contains(text(), 'Remove indicators')]")
            reset_chart = context_overlay_menu.find_element(By.XPATH, "//span[contains(text(), 'Reset chart')]")
            # https://stackoverflow.com/a/44914767
            remove_indicators.click()
            try:
                reset_chart.click()
            except StaleElementReferenceException as e:
                pass

        def __clear_overlays_with_shortcuts():
            self.__open_search_action_menu_and_click("Remove Indicators")

        self.check_and_close_popups()
        self.__change_full_screen_state_footer(False)
        # __clear_overlays_with_right_click()
        __clear_overlays_with_shortcuts()
        return self

    def check_and_close_popups(self):
        try:
            close_buttons = filter(
                lambda button: "close-button" in button.get_attribute("class") or
                               "closeButton" in button.get_attribute("class"),
                FindChartElements.find_overlap_manager_element(self.driver).find_elements(By.TAG_NAME, "button"))
            close_button = next(close_buttons, None)
        except TimeoutException:
            logging.info("No popups found for closing...")
            return
        if close_button:
            close_button.click()

    def run_strategy(self, strategy_content: str):
        self.check_and_close_popups()
        footer_tabs = self.driver.wait_and_get_element(5, By.ID, "footer-chart-panel")
        strategy_tester = footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Strategy Tester')]")
        self.__load_strategy_on_chart(footer_tabs, strategy_content)
        return self

    def __load_strategy_on_chart(self, footer_tabs: WebElement, strategy: str):
        def __open_editor_editor_window():
            # pine_script_editor_window = self.driver.wait_and_get_element(3, By.ID, "bottom-area")
            xpath = "//button[@data-name='toggle-visibility-button']"
            visibility_footer_window_btn = self.driver.wait_and_get_element(3, By.XPATH, xpath)
            is_footer_window_minimized = json.loads(visibility_footer_window_btn.get_attribute("data-active"))
            if is_footer_window_minimized:
                visibility_footer_window_btn.click()
                self.__change_full_screen_state_footer(False)
            footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Pine Editor')]").click()
            pine_editor_tabs = self.driver.wait_and_get_element(5, By.ID, "tv-script-pine-editor-header-root")
            pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='open-script']").click()
            indicator_type_script = self.driver.wait_and_get_element(5, By.XPATH, "//div[@data-name='menu-inner']") \
                .find_element(By.XPATH, "//span[contains(text(), 'Indicator')]")
            indicator_type_script.click()

        def __clear_content_and_enter_strategy():
            pyperclip.copy(strategy)
            WebDriverKeyEventUtils.send_key_event_select_all_and_paste(self.driver)

        def __add_to_chart():
            pine_editor_tabs = self.driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
            pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

        self.check_and_close_popups()
        __open_editor_editor_window()
        __clear_content_and_enter_strategy()
        __add_to_chart()
        # self.__change_full_screen_state_footer(True)

    def extract_strategy_report_to(self, output: dict, strategy_name: str):
        def __read_strategy_report_summary() -> dict:
            def __get_first_line_number_from(web_element: WebElement) -> float:
                number = web_element.find_element(By.TAG_NAME, "strong")
                float_number = ScraperUtils.extract_number_only_from(number.text)
                return float_number

            def __get_second_line_number_from(web_element: WebElement) -> float:
                number = web_element.find_element(By.CLASS_NAME, "additional_percent_value")
                float_number = ScraperUtils.extract_number_only_from(number.text)
                return float_number

            xpath = "//div[@class='report-data']//div[@class='data-item']"
            report_data_headline_columns = self.driver.wait_and_get_elements(5, By.XPATH, xpath)
            return {
                "netProfit": __get_second_line_number_from(report_data_headline_columns[0]),
                "totalTrades": __get_first_line_number_from(report_data_headline_columns[1]),
                "profitable": __get_first_line_number_from(report_data_headline_columns[2]),
                "profitFactor": __get_first_line_number_from(report_data_headline_columns[3]),
                "maxDrawdown": __get_second_line_number_from(report_data_headline_columns[4]),
                "avgTrade": __get_second_line_number_from(report_data_headline_columns[5]),
                "avgBarsInTrade": __get_first_line_number_from(report_data_headline_columns[6]),
            }

        stats = __read_strategy_report_summary()
        output[strategy_name] = stats
        return self

    def change_time_interval_to(self, new_time_interval: TimeInterval):
        chart_page = FindChartElements.find_whole_page_element(self.driver)
        chart_page.send_keys(new_time_interval.value)
        WebDriverKeyEventUtils.send_key_event_enter(self.driver)
        return self

    def change_symbol_to(self, symbol: Symbol):
        def __find_symbol() -> Optional[WebElement]:
            xpath_symbol_rows = "//div[@id='overlap-manager-root']//*[contains(@class,'dialog')]" \
                                "//*[contains(@class, 'itemRow')]"
            try:
                found_symbol_rows = self.driver.wait_and_get_elements(5, By.XPATH, xpath_symbol_rows)
            except TimeoutException:
                raise RuntimeError(f"No symbols returned from TradingView for symbol {symbol}")

            for found_symbol in found_symbol_rows:
                symbol_name = found_symbol.find_element(By.XPATH, "//div[@data-name='list-item-title']")
                symbol_broker = found_symbol.find_element(By.XPATH, "//div[contains(@class,'exchangeName')]")
                if symbol_name.text == symbol.coin_name and symbol_broker.text == symbol.broker_name:
                    return symbol_name
            return None

        self.__open_search_action_menu_and_click("Change Symbol")
        WebDriverKeyEventUtils.send_key_events(self.driver, keys_to_press=[symbol.coin_name])
        desired_symbol_element = __find_symbol()
        if desired_symbol_element is None:
            raise RuntimeError(f"Can't find desired symbol for {symbol}")
        else:
            desired_symbol_element.click()
        return self

    def __change_full_screen_state_footer(self, should_be_full_screen: bool):
        try:
            xpath = "//button[@data-name='toggle-maximize-button']"
            maximize_button = self.driver.wait_and_get_element(3, By.XPATH, xpath)
        except TimeoutException:
            return self
        is_maximized = json.loads(maximize_button.get_attribute("data-active"))
        if is_maximized != should_be_full_screen:
            maximize_button.click()
        return self

    def __open_search_action_menu_and_click(self, action_to_select: str):
        chart = FindChartElements.find_chart_element(self.driver)
        chart.click()
        WebDriverKeyEventUtils.send_key_events(self.driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["k"])
        overlay_manager_element = FindChartElements.find_overlap_manager_element(self.driver)
        xpath = "//input[@data-role='search']"
        search_for_action_popup = overlay_manager_element.find_element(By.XPATH, xpath)
        search_for_action_popup.send_keys(action_to_select)
        xpath = f"//table//tr//span"
        action_elements = overlay_manager_element.find_elements(By.XPATH, xpath)
        for action_element in action_elements:
            if action_to_select.lower() in action_element.text.lower():
                action_element.click()
                return
        raise RuntimeError(f"No action element found from the search tool or "
                           f"function popup which contains '{action_to_select}'")
