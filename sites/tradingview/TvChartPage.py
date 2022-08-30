import json
import logging
from typing import Dict, Optional, List

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from sites.tradingview.TvBasePage import TvBasePage

from usecase.chartActions import FindChartElements, SearchShortcutAction, RunStrategy
from utils import WebDriverKeyEventUtils


class TvChartPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page("https://www.tradingview.com/chart/")
        self.decline_cookies()
        self.wait_for_chart_to_appear()

    def wait_for_chart_to_appear(self):
        FindChartElements.find_chart_element(self.driver)
        return self

    def clean_all_overlays(self):
        SearchShortcutAction.remove_indicators(self.driver)
        return self

    def check_and_close_popups(self):
        FindChartElements.check_and_close_popups(self.driver)
        return self

    def add_strategy_to_chart(self, strategy_content: str):
        self.check_and_close_popups()
        RunStrategy.load_strategy_on_chart(self.driver, strategy_content)
        return self

    def change_footer_window_full_size(self, should_maximize_it: bool):
        xpath = "//div[@id='footer-chart-panel']//button[@data-name='toggle-maximize-button']"
        try:
            maximize_footer_btn = self.driver.wait_and_get_element(1, By.XPATH, xpath)
        except TimeoutException:
            return self
        is_footer_window_maximized = json.loads(maximize_footer_btn.get_attribute("data-active"))
        if is_footer_window_maximized != should_maximize_it:
            maximize_footer_btn.click()
        return self

    def extract_strategy_overview_report(self) -> Optional[Dict]:
        stats = RunStrategy.extract_strategy_overview(self.driver)
        return stats

    def extract_strategy_trades_report(self) -> Optional[List]:
        trades = RunStrategy.extract_strategy_trades(self.driver)
        return trades

    def change_time_interval_to(self, new_time_interval: TimeInterval):
        SearchShortcutAction.change_interval(self.driver)
        WebDriverKeyEventUtils.send_key_events(self.driver, keys_to_press=[new_time_interval.value])
        WebDriverKeyEventUtils.send_key_event_enter(self.driver)
        return self

    def change_symbol_to(self, symbol: Symbol, trial_attempts: int = 3):
        should_fail_attempt = trial_attempts + 1
        for i in range(0, should_fail_attempt):
            try:
                SearchShortcutAction.change_symbol(self.driver)
                WebDriverKeyEventUtils.type_text_with_delay(self.driver, text=symbol.coin_name)
                desired_symbol_element = FindChartElements.find_new_search_symbol_matching(symbol, self.driver)
                desired_symbol_element.click()
                return self
            except Exception as e:
                if i < should_fail_attempt:
                    logging.info(f"Failed attempt number {i + 1} to select symbol {symbol}... Trying again")
                    WebDriverKeyEventUtils.send_key_event_escape(self.driver)
                else:
                    raise e
            finally:
                return self
        return self

    def remove_possible_advert_overlay(self):
        try:
            xpath = "//div[@data-role='toast-container']//button[contains(@class,'close-button')]"
            self.driver.wait_and_get_element(1, By.XPATH, xpath).click()
            xpath = "//div[@id='overlap-manager-root']//button[contains(@class,'close-button')]"
            self.driver.wait_and_get_element(1, By.XPATH, xpath).click()
        except TimeoutException:
            pass
        finally:
            return self
