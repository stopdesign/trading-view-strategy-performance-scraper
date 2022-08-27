from typing import List, Union

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def send_key_events(driver: WebDriver, keys_to_press: List[Union[Keys, str]], holding_down_keys: List[Keys] = None):
    holding_down_keys = [] if holding_down_keys is None else holding_down_keys

    click_action = ActionChains(driver)

    for holding_down_key in holding_down_keys:
        click_action.key_down(holding_down_key)

    for key_to_press in keys_to_press:
        click_action.send_keys(key_to_press)

    for holding_down_key in holding_down_keys:
        click_action.key_up(holding_down_key)

    click_action.perform()


def send_key_event_enter(driver: WebDriver):
    send_key_events(driver, keys_to_press=[Keys.ENTER])


def send_key_event_select_all_and_paste(driver: WebDriver):
    send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["a"])
    send_key_events(driver, holding_down_keys=[Keys.COMMAND], keys_to_press=["v"])


def send_right_click_event(driver: WebDriver, element: WebElement):
    ActionChains(driver).context_click(element).perform()