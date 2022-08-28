from time import sleep

from driver.BaseDriver import BaseDriver
from sites.BasePage import BasePage
from selenium.webdriver.common.by import By


class TvBasePage(BasePage):

    def __init__(self, driver: BaseDriver):
        super().__init__(driver)

    def decline_cookies(self):
        try:
            self.__decline_cookies()
        finally:
            return self
        # return self

    def __decline_cookies(self):
        xpath = "//div[@data-role='toast-container']//span[text()='Manage preferences']"
        self.driver.wait_and_get_element(3, By.XPATH, xpath).click()
        xpath = "//div[@id='overlap-manager-root']//span[text()='Save preferences']"
        self.driver.wait_and_get_element(3, By.XPATH, xpath).click()

    def wait(self, seconds):
        sleep(seconds)
        return self
