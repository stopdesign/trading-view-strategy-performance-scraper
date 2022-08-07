from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from sites.tradingview.TvBasePage import TvBasePage
from selenium.webdriver import ActionChains


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
        chart = self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")
        ActionChains(self.driver).context_click(chart).perform()
        overlays_table = self.driver.wait_and_get_element(5, By.ID, "overlap-manager-root")
        remove_indicators = overlays_table.find_element(By.XPATH, "//span[contains(text(), 'Remove indicators')]")
        reset_chart = overlays_table.find_element(By.XPATH, "//span[contains(text(), 'Reset chart')]")
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
