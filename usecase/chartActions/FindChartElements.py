from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver


def find_overlap_manager_element(driver: BaseDriver) -> WebElement:
    return driver.wait_and_get_element(5, By.ID, "overlap-manager-root")


def find_top_toolbar_element_symbol(driver: BaseDriver) -> WebElement:
    return find_top_toolbar_elements(driver)[0].find_element(By.ID, "header-toolbar-symbol-search")


def find_top_toolbar_element_interval(driver: BaseDriver) -> WebElement:
    return find_top_toolbar_elements(driver)[1]


def find_top_toolbar_elements(driver: BaseDriver) -> List[WebElement]:
    xpath = "//div[@class='layout__area--top']/div[contains(@class, 'toolbar')]" \
            "//*[@data-is-fake-main-panel='false']//*[contains(@class, 'group')]"
    toolbars_items = driver.wait_and_get_elements(5, By.XPATH, xpath)
    return toolbars_items


def find_chart_element(driver: BaseDriver):
    return driver.wait_and_get_element(5, By.CLASS_NAME, "chart-widget")


def find_whole_page_element(driver: BaseDriver):
    return driver.wait_and_get_element(5, By.CLASS_NAME, "chart-page")