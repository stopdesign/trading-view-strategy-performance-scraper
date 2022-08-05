from typing import List

import pandas as pd
from pandas import DataFrame
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from sites.tradingview.TvBasePage import TvBasePage
from utils import ScraperUtils, DataFrameUtils


class TvHomePage(TvBasePage):
    __url = "https://www.tradingview.com/crypto-screener/"

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)
        self.driver.load_page(self.__url)
        self.accept_cookies()

    def login(self, user, password):
        timeout = 3
        login_dropdown = self.driver.wait_and_get_element(timeout, By.CLASS_NAME, "tv-header__user-menu-button")
        login_dropdown.click()
        xpath = '//div[contains(text(), "Sign in")]'
        sign_in_btn = self.driver.wait_and_get_element(timeout, By.XPATH, xpath)
        sign_in_btn.click()
        by_email_btn = self.driver.wait_and_get_element(timeout, By.CLASS_NAME, "tv-signin-dialog__toggle-email")
        by_email_btn.click()

        input_user = self.driver.wait_and_get_element(timeout, By.XPATH, "//input[@name='username']")
        input_password = self.driver.wait_and_get_element(timeout, By.XPATH, "//input[@name='password']")
        sign_in_elem = self.driver.wait_and_get_element(timeout, By.XPATH, "//button[@type='submit']")
        input_user.click()
        self.wait(0.5)
        input_user.send_keys(user)
        input_password.click()
        self.wait(0.5)
        input_password.send_keys(password)
        sign_in_elem.click()
        return self

    def hide_sidebar(self):
        sidebar = self.driver.wait_and_get_element(5, By.CLASS_NAME, "widgetbar-pages")
        if sidebar.size['width'] > 10:  # if sidebar is visible on the screen
            random_widget_in_sidebar = self.driver.wait_and_get_element(5, By.XPATH, "//div[@data-name='notes']")
            random_widget_in_sidebar.click()  # once to switch the window to it
            self.wait(0.1)
            random_widget_in_sidebar.click()  # second time to hide it
        return self

    def select_filter_with(self, filter_name: str):
        def is_filter_selected(element) -> bool:
            return element.text == filter_name

        saved_filters = self.driver.wait_and_get_element(5, By.XPATH, "//div[@data-name='screener-filter-sets']")
        if is_filter_selected(saved_filters):
            return self
        else:
            saved_filters.click()
            xpath = f"//*[contains(text(), \"{filter_name}\")]"
            filter_element = self.driver.wait_and_get_element(5, By.XPATH, xpath)
            self.driver.scroll_to(filter_element)
            filter_element.click()
            return self

    def extract_data(self) -> DataFrame:
        self.driver.wait_and_get_element(5, By.CLASS_NAME, "tv-data-table")
        table_content = ScraperUtils.extract_tv_table_unwanted_info(self.driver)
        table_content = DataFrameUtils.remove_percentage_values_from(table_content)
        return table_content
