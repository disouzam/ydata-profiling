import warnings

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.dataframe import check_dataframe, preprocess


@check_dataframe.register
def spark_check_dataframe(df: DataFrame) -> None:
    """def spark_check_dataframe(df: DataFrame) -> None:
    """
    Check if the provided object is a PySpark DataFrame.

    This function verifies whether the input `df` is an instance of 
    `pyspark.sql.dataframe.DataFrame`. If the input is not of the 
    expected type, a warning is issued.

    Parameters:
    ----------
    df : DataFrame
        The object to be checked.

    Returns:
    -------
    None
    """
    if not isinstance(df, DataFrame):
        warnings.warn("df is not of type pyspark.sql.dataframe.DataFrame")


@preprocess.register
def spark_preprocess(config: Settings, df: DataFrame) -> DataFrame:
    """Preprocess the dataframe

    - Appends the index to the dataframe when it contains information
    - Rename the "index" column to "df_index", if exists
    - Convert the DataFrame's columns to str

    Args:
        config: report Settings object
        df: the pandas DataFrame

    Returns:
        The preprocessed DataFrame
    """

    def _check_column_map_type(df: DataFrame, column_name: str) -> bool:
        """
    Check if the specified column in the DataFrame is of type MapType.

    This function inspects the schema of the given DataFrame and checks 
    whether the data type of the specified column starts with "MapType". 
    It returns True if the column is of type MapType, otherwise it returns False.

    Parameters:
    df (DataFrame): The DataFrame to inspect.
    column_name (str): The name of the column to check.

    Returns:
    bool: True if the column is of type MapType, False otherwise.
    """
        return str(df.select(column_name).schema[0].dataType).startswith("MapType")

    columns_to_remove = list(
        filter(lambda x: _check_column_map_type(df, x), df.columns)
    )

    # raise warning and filter if this isn't empty
    if columns_to_remove:
        warnings.warn(
            f"""spark dataframes profiling does not handle MapTypes. Column(s) { ','.join(columns_to_remove) } will be ignored.
            To fix this, consider converting your MapType into a StructTypes of StructFields i.e.
            {{'key1':'value1',...}} -> [('key1','value1'), ...], or extracting the key,value pairs out
            into individual columns using pyspark.sql.functions.explode.
            """
        )
        columns_to_keep = list(
            filter(lambda x: not _check_column_map_type(df, x), df.columns)
        )
        return df.select(*columns_to_keep)

    else:
        return df
