from abc import ABC, abstractmethod
from typing import List

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class BaseDriver(ABC, WebDriver):

    @abstractmethod
    def load_page(self, url):
        raise NotImplemented()

    @abstractmethod
    def wait_to_load(self, timeout: float, by: By, match_value: str):
        raise NotImplemented()

    @abstractmethod
    def wait_and_get_element(self, timeout: float, by: By, selector: str) -> WebElement:
        raise NotImplemented()

    @abstractmethod
    def wait_and_get_elements(self, timeout: float, by: By, selector: str) -> List[WebElement]:
        raise NotImplemented()
