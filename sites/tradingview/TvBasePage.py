from time import sleep

from driver.BaseDriver import BaseDriver
from sites.BasePage import BasePage
from selenium.webdriver.common.by import By


class TvBasePage(BasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)

    def accept_cookies(self):
        # try:
        #     self.__accept_cookies()
        # finally:
        #     return self
        return self

    def __accept_cookies(self):
        accept_btn = self.driver.wait_and_get_element(5, By.ID, "acceptCookies")
        accept_btn.click()

    def wait(self, seconds):
        sleep(seconds)
        return self
