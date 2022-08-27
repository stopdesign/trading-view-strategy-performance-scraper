
import json
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
        self.accept_cookies()
        self.wait_for_chart_to_appear()

    def wait_for_chart_to_appear(self):
        FindChartElements.find_chart_element(self.driver)
        return self

    def clean_all_overlays(self):
        self.check_and_close_popups()
        self.__change_full_screen_state_footer(False)
        # __clear_overlays_with_right_click()
        SearchShortcutAction.remove_indicators(self.driver)
        return self

    def check_and_close_popups(self):
        FindChartElements.check_and_close_popups(self.driver)

    def run_strategy(self, strategy_content: str):
        self.check_and_close_popups()
        RunStrategy.load_strategy_on_chart(self.driver, strategy_content)
        return self

    def extract_strategy_report(self, output: dict, strategy_name: str):
        stats = RunStrategy.extract_strategy_report(self.driver)
        output[strategy_name] = stats
        return self

    def change_time_interval_to(self, new_time_interval: TimeInterval):
        chart_page = FindChartElements.find_whole_page_element(self.driver)
        chart_page.send_keys(new_time_interval.value)
        WebDriverKeyEventUtils.send_key_event_enter(self.driver)
        return self

    def change_symbol_to(self, symbol: Symbol):
        SearchShortcutAction.change_symbol(self.driver)
        WebDriverKeyEventUtils.send_key_events(self.driver, keys_to_press=[symbol.coin_name])
        desired_symbol_element = FindChartElements.find_new_search_symbol_matching(symbol, self.driver)
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
