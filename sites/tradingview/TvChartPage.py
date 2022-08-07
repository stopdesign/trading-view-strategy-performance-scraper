
from selenium.common import StaleElementReferenceException
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

    def login(self, user, password):
        pass

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

        chart = self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")
        ActionChains(self.driver).context_click(chart).perform()
        xpath = "//span[contains(text(), 'Remove indicators')]"
        remove_indicators = self.driver.wait_and_get_element(5, By.XPATH, xpath)
        # https://stackoverflow.com/a/44914767
        try:
            remove_indicators.click()
        except StaleElementReferenceException as e:
            pass
        return self

    def remove_chart_overlays(self):
        chart = self.driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")
        ActionChains(self.driver).context_click(chart).perform()
        self.driver.wait_and_get_element(5, By.XPATH, "//span[contains(text(), 'Remove indicators')]").click()