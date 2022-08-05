from abc import abstractmethod

from driver.ScraperDriver import ScraperDriver


class BasePage:

    def __init__(self, driver: ScraperDriver):
        self.driver = driver

    @abstractmethod
    def accept_cookies(self):
        raise NotImplemented()
