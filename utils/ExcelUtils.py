import pandas as pd
from pandas import DataFrame


def write_to_excel_from_df(df: DataFrame, output_name):
    sheet_name = "Watchlist"
    with pd.ExcelWriter(output_name) as writer:
        df.to_excel(writer, startrow=0, header=True, sheet_name=sheet_name)
        for column in df.columns:
            # new_width = 50
            new_width = len(column) + 5
            col_idx = df.columns.get_loc(column)
            writer.sheets[sheet_name].set_column(col_idx, col_idx, new_width)
