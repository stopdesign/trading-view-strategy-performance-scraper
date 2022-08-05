from pandas import DataFrame


def remove_percentage_from(df: DataFrame, column_name: str) -> DataFrame:
    return df[column_name].str.strip("%")


def remove_percentage_values_from(df: DataFrame) -> DataFrame:
    for column_name in df:
        if "%" in column_name:
            df[column_name] = remove_percentage_from(df, column_name)
    return df
