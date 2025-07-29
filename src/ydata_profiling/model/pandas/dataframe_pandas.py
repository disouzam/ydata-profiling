import warnings

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.dataframe import check_dataframe, preprocess
from ydata_profiling.utils.dataframe import rename_index


@check_dataframe.register
def pandas_check_dataframe(df: pd.DataFrame) -> None:
    """def pandas_check_dataframe(df: pd.DataFrame) -> None:
    """
    Check if the input is a pandas DataFrame.

    This function verifies whether the provided input 'df' is an instance
    of pandas.DataFrame. If the input is not of the expected type,
    a warning is issued.

    Parameters:
    -----------
    df : pd.DataFrame
        The object to check for DataFrame type.

    Returns:
    --------
    None
        This function does not return a value. It only issues a warning
        if the type check fails.

    Raises:
    -------
    None
        This function does not raise exceptions, but will issue a warning
        if 'df' is not an instance of pandas.DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        warnings.warn("df is not of type pandas.DataFrame")


@preprocess.register
def pandas_preprocess(config: Settings, df: pd.DataFrame) -> pd.DataFrame:
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
    # Rename reserved column names
    df = rename_index(df)

    # Ensure that columns are strings
    df.columns = df.columns.astype("str")
    return df
