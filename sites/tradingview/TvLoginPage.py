from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from sites.tradingview.TvBasePage import TvBasePage


class TvLoginPage(TvBasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)

    def login(self, username: str, password: str):
        login_dropdown = self.driver.wait_and_get_element(5, By.CLASS_NAME, "tv-header__user-menu-button")
        login_dropdown.click()
        sign_in_btn = self.driver.wait_and_get_element(5, By.CLASS_NAME, "header-user-menu-sign-in")
        sign_in_btn.click()

        by_email_btn = self.driver.wait_and_get_element(5, By.CLASS_NAME, "tv-signin-dialog__toggle-email")
        by_email_btn.click()

        return self

