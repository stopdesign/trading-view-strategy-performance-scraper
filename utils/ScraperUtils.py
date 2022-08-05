import pandas as pd
import re
from pandas import DataFrame


def extract_tv_table_unwanted_info(driver) -> DataFrame:
    html_raw = driver.page_source
    html_content = re.sub(r'<span class="tv-screener__description.*span>', "", html_raw)  # replaces the 2nd row description on each ticker
    html_content = re.sub(r'<div class="js-field-total(\s|\d|\w|"|>|-|_|\.)*</div>', "", html_content)  # replaces the number of found tickers in the header
    html_content = re.sub(r'<span class="js-field-value(\s|\d|\w|"|>|-|_|\.)*</span>', "", html_content)  # replaces the custom filtered values on each column as second row
    table = extract_head_and_body_from_table(html_content, 1)
    return table


def extract_head_and_body_from_table(html_content, table_position) -> DataFrame:
    # https://towardsdatascience.com/all-pandas-read-html-you-should-know-for-scraping-data-from-html-tables-a3cbb5ce8274
    table = pd.read_html(html_content, keep_default_na=False)[table_position]
    table.replace('-', '0', inplace=True)
    return table
