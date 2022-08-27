from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from usecase.chartActions import FindChartElements
from utils import WebDriverKeyEventUtils


def remove_indicators(driver: BaseDriver):
    __open_search_action_menu_and_click(driver, "Remove Indicators")


def change_symbol(driver: BaseDriver):
    __open_search_action_menu_and_click(driver, "Change Symbol")


def __open_search_action_menu_and_click(driver: BaseDriver, action_to_select: str):
    chart = FindChartElements.find_chart_element(driver)
    chart.click()
    WebDriverKeyEventUtils.send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["k"])
    overlay_manager_element = FindChartElements.find_overlap_manager_element(driver)
    xpath = "//input[@data-role='search']"
    search_for_action_popup = overlay_manager_element.find_element(By.XPATH, xpath)
    search_for_action_popup.send_keys(action_to_select)
    xpath = f"//table//tr//span"
    action_elements = overlay_manager_element.find_elements(By.XPATH, xpath)
    for action_element in action_elements:
        if action_to_select.lower() in action_element.text.lower():
            action_element.click()
            return
    raise RuntimeError(f"No action element found from the search tool or "
                       f"function popup which contains '{action_to_select}'")