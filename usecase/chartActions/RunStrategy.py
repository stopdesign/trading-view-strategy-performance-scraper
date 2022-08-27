import json

import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver.BaseDriver import BaseDriver
from usecase.chartActions import FindChartElements
from utils import WebDriverKeyEventUtils, ScraperUtils


def load_strategy_on_chart(driver: BaseDriver, strategy_content: str):
    def __open_editor_editor_window():
        # pine_script_editor_window = driver.wait_and_get_element(3, By.ID, "bottom-area")
        xpath = "//button[@data-name='toggle-visibility-button']"
        visibility_footer_window_btn = driver.wait_and_get_element(3, By.XPATH, xpath)
        is_footer_window_minimized = json.loads(visibility_footer_window_btn.get_attribute("data-active"))
        if is_footer_window_minimized:
            visibility_footer_window_btn.click()
            FindChartElements.change_full_screen_state_footer(driver, False)
        footer_tabs.find_element(By.XPATH, "//span[contains(text(), 'Pine Editor')]").click()
        pine_editor_tabs = driver.wait_and_get_element(5, By.ID, "tv-script-pine-editor-header-root")
        pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='open-script']").click()
        indicator_type_script = driver.wait_and_get_element(5, By.XPATH, "//div[@data-name='menu-inner']") \
            .find_element(By.XPATH, "//span[contains(text(), 'Indicator')]")
        indicator_type_script.click()

    def __clear_content_and_enter_strategy():
        pyperclip.copy(strategy_content)
        WebDriverKeyEventUtils.send_key_event_select_all_and_paste(driver)

    def __add_to_chart():
        pine_editor_tabs = driver.wait_and_get_element(3, By.ID, "tv-script-pine-editor-header-root")
        pine_editor_tabs.find_element(By.XPATH, "//div[@data-name='add-script-to-chart']").click()

    footer_tabs = driver.wait_and_get_element(5, By.ID, "footer-chart-panel")
    
    FindChartElements.check_and_close_popups(driver)
    __open_editor_editor_window()
    __clear_content_and_enter_strategy()
    __add_to_chart()
    # self.__change_full_screen_state_footer(True)


def extract_strategy_report(driver: BaseDriver) -> dict:
    def __get_first_line_number_from(web_element: WebElement) -> float:
        number = web_element.find_element(By.TAG_NAME, "strong")
        float_number = ScraperUtils.extract_number_only_from(number.text)
        return float_number

    def __get_second_line_number_from(web_element: WebElement) -> float:
        number = web_element.find_element(By.CLASS_NAME, "additional_percent_value")
        float_number = ScraperUtils.extract_number_only_from(number.text)
        return float_number

    xpath = "//div[@class='report-data']//div[@class='data-item']"
    report_data_headline_columns = driver.wait_and_get_elements(5, By.XPATH, xpath)
    return {
        "netProfit": __get_second_line_number_from(report_data_headline_columns[0]),
        "totalTrades": __get_first_line_number_from(report_data_headline_columns[1]),
        "profitable": __get_first_line_number_from(report_data_headline_columns[2]),
        "profitFactor": __get_first_line_number_from(report_data_headline_columns[3]),
        "maxDrawdown": __get_second_line_number_from(report_data_headline_columns[4]),
        "avgTrade": __get_second_line_number_from(report_data_headline_columns[5]),
        "avgBarsInTrade": __get_first_line_number_from(report_data_headline_columns[6]),
    }
