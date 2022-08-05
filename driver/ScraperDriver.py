import logging
from typing import List

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import EnvConfig
from driver.BaseDriver import BaseDriver


class ScraperDriver(BaseDriver):

    def __init__(self,
                 headless: bool):
        driver_options = self.__get_headless_options() if headless else self.__get_basic_options()
        super().__init__(options=driver_options)
        # super().maximize_window()
        logging.info(f"Driver initialized.")

    def load_page(self, url):
        super().get(url)
        super().implicitly_wait(1)

    @classmethod
    def __get_headless_options(cls):
        options = Options()
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        # The location of the chrome binary
        # options.binary_location = driver_path
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-logging")
        options.add_argument("--mute-audio")
        # The user agent the browser is pretending to be
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/74.0.3729.169 Safari/537.36')

        return options

    @classmethod
    def __get_basic_options(cls):
        return webdriver.ChromeOptions()

    # @classmethod
    # def __get_installed_chrome_options(cls):
    #     import subprocess
    #     subprocess.Popen(
    #         r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222', shell=True)
    #
    #     options = webdriver.ChromeOptions()
    #     options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #     options.add_argument(
    #         '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #         'Chrome/74.0.3729.169 Safari/537.36')
    #
    #     return options

    @classmethod
    def __get_installed_chrome_options(cls):
        import subprocess
        subprocess.Popen(
            r'"/Applications/Google\ Chrome.app" --remote-debugging-port=9222', shell=True)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/74.0.3729.169 Safari/537.36')

        return options

    def wait_to_load(self, timeout: float, by: By, match_value: str):
        try:
            element_present = EC.presence_of_element_located((by, match_value))
            WebDriverWait(self, timeout).until(element_present)
        except TimeoutException as e:
            logging.info(f"Timed out waiting for page to load with matched value '{match_value}'")
            raise e

    def wait_and_get_element(self, timeout: float, by: By, selector: str) -> WebElement:
        self.wait_to_load(timeout, by, selector)
        return self.find_element(by, selector)

    def wait_and_get_elements(self, timeout: float, by: By, selector: str) -> List[WebElement]:
        self.wait_to_load(timeout, by, selector)
        return self.find_elements(by, selector)

    def scroll_to(self, element: WebElement) -> ActionChains:
        return ActionChains(self).move_to_element(element).perform()
