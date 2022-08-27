from time import sleep
from typing import List, Optional, Union

import pyperclip
import json
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from sites.tradingview.TvBasePage import TvBasePage
from selenium.webdriver import ActionChains, Keys

from utils import ScraperUtils


class TvChartPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page("https://www.tradingview.com/chart/")
        self.accept_cookies()
        self.wait_for_chart_to_appear()

    def wait_for_chart_to_appear(self):
        self.__get_chart_element()
        return self

    # def extract_data(self) -> DataFrame:
    #     self.driver.wait_and_get_element(5, By.CLASS_NAME, "tv-data-table")
    #     table_content = ScraperUtils.extract_tv_table_unwanted_info(self.driver)
    #     table_content = DataFrameUtils.remove_percentage_values_from(table_content)
    #     return table_content

    def clean_all_overlays(self):
        # def __is_overlay_on_screen(source: str) -> bool:
        #     soup = BeautifulSoup(source, "lxml")
        #     overlays = soup.find_all("div", {"data-name": "legend-source-item"})
        #     print(f"Overlays count: {len(overlays)}")
        #     return len(overlays) > 0
        def __scroll_to_no_candles():
            def __move_to_end_of_candles_to_the_right():
                send_key_events(self.driver, holding_down_keys=[Keys.COMMAND, Keys.ALT], keys_to_press=[Keys.ARROW_RIGHT])
                # ActionChains(self.driver) \
                #     .key_down(Keys.COMMAND).key_down(Keys.ALT).send_keys(Keys.ARROW_RIGHT) \
                #     .key_up(Keys.ALT).key_up(Keys.COMMAND) \
                #     .perform()

            def __move_chart_further_to_the_right():
                send_key_events(self.driver, holding_down_keys=[Keys.ALT], keys_to_press=[Keys.ARROW_RIGHT])
                # ActionChains(self.driver) \
                #     .key_down(Keys.ALT).send_keys(Keys.ARROW_RIGHT).key_up(Keys.ALT) \
                #     .perform()

            __move_to_end_of_candles_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()
            sleep(0.1)
            __move_chart_further_to_the_right()

        def __clear_overlays_with_right_click():
            __scroll_to_no_candles()

            chart = self.__get_chart_element()
            ActionChains(self.driver).context_click(chart).perform()
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
            chart = self.__get_chart_element()
            chart.click()
            send_key_events(self.driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["k"])
            xpath = "//div[@id='overlap-manager-root']//input[@data-role='search']"
            search_for_action_popup = self.driver.wait_and_get_element(3, By.XPATH, xpath)
            remove_indicators_str = "Remove Indicators"
            search_for_action_popup.send_keys(remove_indicators_str)
            xpath = "//div[@id='overlap-manager-root']//table//tr//span[text()='Remove Indicators']"
            remove_indicators = self.driver.wait_and_get_element(3, By.XPATH, xpath)
            remove_indicators.click()

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
                self.__get_overlap_manager_element().find_elements(By.TAG_NAME, "button"))
            close_button = next(close_buttons, None)
        except TimeoutException as e:
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
            # editor_window = self.driver.wait_and_get_element(3, By.CLASS_NAME, "ace_content")
            # editor_window.click()
            print()
            pyperclip.copy(strategy)
            send_key_event_select_all_and_paste(self.driver)
            # ActionChains(self.driver) \
            #     .key_down(Keys.COMMAND).send_keys("a").key_up(Keys.COMMAND) \
            #     .send_keys(Keys.DELETE) \
            #     .key_down(Keys.COMMAND).send_keys("v").key_up(Keys.COMMAND) \
            #     .perform()

        def __add_to_chart():
            pine_editor_tabs = self.driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
            pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

        self.check_and_close_popups()
        __open_editor_editor_window()
        __clear_content_and_enter_strategy()
        __add_to_chart()
        # self.__change_full_screen_state_footer(True)
        print()

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

            report_data_headline = self.driver.wait_and_get_element(5, By.CLASS_NAME, "report-data")
            report_data_headline_columns = report_data_headline.find_elements(By.CLASS_NAME, "data-item")
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
        def __get_time_interval_element_for(time_interval: TimeInterval) -> WebElement:
            xpath = f"//div[@id='overlap-manager-root']//*[contains(@class,'dropdown')]" \
                    f"//*[@data-value='{time_interval.value}']"
            return self.driver.wait_and_get_element(3, By.XPATH, xpath)

        chart_page = self.__get_whole_page_element()
        chart_page.send_keys(new_time_interval.value)
        send_key_event_enter(self.driver)
        return self

    def change_symbol_to(self, symbol: Symbol):
        def __find_symbol() -> Optional[WebElement]:
            xpath_symbol_rows = "//div[@id='overlap-manager-root']//*[contains(@class,'dialog')]" \
                                "//*[contains(@class, 'itemRow')]"
            try:
                found_symbol_rows = self.driver.wait_and_get_elements(3, By.XPATH, xpath_symbol_rows)
            except TimeoutException:
                raise RuntimeError(f"No symbols returned from TradingView for symbol {symbol}")

            for found_symbol in found_symbol_rows:
                symbol_name = found_symbol.find_element(By.XPATH, "//div[@data-name='list-item-title']")
                symbol_broker = found_symbol.find_element(By.XPATH, "//div[contains(@class,'exchangeName')]")
                if symbol_name.text == symbol.coin_name and symbol_broker.text == symbol.broker_name:
                    return found_symbol
            return None

        self.__get_whole_page_element().send_keys(symbol.coin_name)
        desired_symbol_element = __find_symbol()
        if desired_symbol_element is None:
            raise RuntimeError(f"Can't find desired symbol for {symbol}")
        else:
            desired_symbol_element.click()
        return self

    def __get_overlap_manager_element(self) -> WebElement:
        return self.driver.wait_and_get_element(3, By.ID, "overlap-manager-root")

    def __get_top_toolbar_element_symbol(self) -> WebElement:
        return self.__get_top_toolbar_elements()[0].find_element(By.ID, "header-toolbar-symbol-search")

    def __get_top_toolbar_element_interval(self) -> WebElement:
        return self.__get_top_toolbar_elements()[1]

    def __get_top_toolbar_elements(self) -> List[WebElement]:
        xpath = "//div[@class='layout__area--top']/div[contains(@class, 'toolbar')]" \
                "//*[@data-is-fake-main-panel='false']//*[contains(@class, 'group')]"
        toolbars_items = self.driver.wait_and_get_elements(3, By.XPATH, xpath)
        return toolbars_items

    def __get_chart_element(self):
        return self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")

    def __get_whole_page_element(self):
        return self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-page")

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


# <editor-fold desc="Util section">
def send_key_events(driver: WebDriver, keys_to_press: List[Union[Keys, str]], holding_down_keys: List[Keys] = None):
    holding_down_keys = [] if holding_down_keys is None else holding_down_keys

    click_action = ActionChains(driver)

    for holding_down_key in holding_down_keys:
        click_action.key_down(holding_down_key)

    for key_to_press in keys_to_press:
        click_action.send_keys(key_to_press)

    for holding_down_key in holding_down_keys:
        click_action.key_up(holding_down_key)

    click_action.perform()


def send_key_event_enter(driver: WebDriver):
    send_key_events(driver, keys_to_press=[Keys.ENTER])


def send_key_event_select_all_and_paste(driver: WebDriver):
    send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["a"])
    send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["v"])
# </editor-fold>
