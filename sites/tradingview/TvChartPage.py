from typing import List

import pandas as pd
from pandas import DataFrame
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from sites.tradingview.TvBasePage import TvBasePage
from utils import ScraperUtils, DataFrameUtils


class TvChartPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page("https://www.tradingview.com/chart/")
        self.accept_cookies()

    def login(self, user, password):
        pass

    def extract_data(self) -> DataFrame:
        self.driver.wait_and_get_element(5, By.CLASS_NAME, "tv-data-table")
        table_content = ScraperUtils.extract_tv_table_unwanted_info(self.driver)
        table_content = DataFrameUtils.remove_percentage_values_from(table_content)
        return table_content
