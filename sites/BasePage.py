from abc import abstractmethod

from driver.BaseDriver import BaseDriver


class BasePage:

    def __init__(self, driver: BaseDriver):
        self.driver = driver

    @abstractmethod
    def decline_cookies(self):
        raise NotImplemented()
