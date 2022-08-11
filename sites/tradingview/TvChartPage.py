import pyperclip
import json
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver
from sites.tradingview.TvBasePage import TvBasePage
from selenium.webdriver import ActionChains, Keys


class TvChartPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page("https://www.tradingview.com/chart/")
        self.accept_cookies()
        self.wait_for_chart_to_appear()

    def wait_for_chart_to_appear(self):
        self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")
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
        self.check_and_close_popups()
        self.__change_full_screen_state_footer(False)
        chart = self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")
        ActionChains(self.driver).context_click(chart).perform()
        context_overlay_menu = self.driver.wait_and_get_element(5, By.CLASS_NAME, "context-menu")
        remove_indicators = context_overlay_menu.find_element(By.XPATH, "//span[contains(text(), 'Remove indicators')]")
        reset_chart = context_overlay_menu.find_element(By.XPATH, "//span[contains(text(), 'Reset chart')]")
        # https://stackoverflow.com/a/44914767
        remove_indicators.click()
        try:
            reset_chart.click()
        except StaleElementReferenceException as e:
            pass
        return self

    def check_and_close_popups(self):
        try:
            close_buttons = filter(
                lambda button: "close-button" in button.get_attribute("class") or
                               "closeButton" in button.get_attribute("class"),
                self.driver.wait_and_get_element(1, By.ID, "overlap-manager-root").find_elements(By.TAG_NAME, "button"))
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
            is_footer_window_minimize = json.loads(visibility_footer_window_btn.get_attribute("data-active"))
            if is_footer_window_minimize:
                visibility_footer_window_btn.click()
                self.__change_full_screen_state_footer(False)
            footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Pine Editor')]").click()
            pine_editor_tabs = self.driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
            pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='open-script']").click()
            indicator_type_script = self.driver.wait_and_get_element(3, By.XPATH, "//div[@data-name='menu-inner']") \
                .find_element(By.XPATH, "//span[contains(text(), 'Indicator')]")
            indicator_type_script.click()

        def __clear_content_and_enter_strategy():
            # editor_window = self.driver.wait_and_get_element(3, By.CLASS_NAME, "ace_content")
            # editor_window.click()
            print()
            pyperclip.copy(strategy)
            ActionChains(self.driver) \
                .key_down(Keys.COMMAND).send_keys("a").key_up(Keys.COMMAND) \
                .send_keys(Keys.DELETE) \
                .key_down(Keys.COMMAND).send_keys("v").key_up(Keys.COMMAND) \
                .perform()

        def __add_to_chart():
            pine_editor_tabs = self.driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
            pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

        self.check_and_close_popups()
        __open_editor_editor_window()
        __clear_content_and_enter_strategy()
        __add_to_chart()
        self.__change_full_screen_state_footer(True)
        print()

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
