from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from driver.BaseDriver import BaseDriver
from usecase.chartActions import FindChartElements
from utils import WebDriverKeyEventUtils


def remove_indicators(driver: BaseDriver):
    __open_search_action_menu_and_click(driver, "Remove Indicators")


def change_symbol(driver: BaseDriver):
    __open_search_action_menu_and_click(driver, "Change Symbol")


def change_interval(driver: BaseDriver):
    __open_search_action_menu_and_click(driver, "Change Interval")


def __open_search_action_menu_and_click(driver: BaseDriver, action_to_select: str):
    def __close_any_current_overlays():
        _xpath = "//div[@id='overlap-manager-root']//span[@data-name='close' and @data-role='button']"
        try:
            close_buttons = driver.wait_and_get_elements(0.5, By.XPATH, _xpath)
            for close_buttons in close_buttons:
                close_buttons.click()
        except TimeoutException:
            pass
        except Exception as e:
            raise e

    try:
        __close_any_current_overlays()
        driver.wait_and_get_element(1, By.ID, "footer-chart-panel").click()
        WebDriverKeyEventUtils.send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["k"])
        xpath = "//div[@data-name='globalSearch']//input[@data-role='search']"
        driver.wait_and_get_element(3, By.XPATH, xpath).send_keys(action_to_select)
    except Exception as e:
        raise e
    try:
        xpath = f"//div[@id='overlap-manager-root']//table//tr[contains(@class,'item')]" \
                f"//*[contains(text(),'{action_to_select}')]"
        driver.wait_and_get_element(2, By.XPATH, xpath).click()
    except Exception as e:
        raise RuntimeError(f"No action element found from the search tool or "
                           f"function popup which contains '{action_to_select}'")
