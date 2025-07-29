"""Compute statistical description of datasets."""
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from ydata_profiling.config import Settings
from ydata_profiling.model.timeseries_index import get_time_index_description


@get_time_index_description.register
def pandas_get_time_index_description(
    config: Settings,
    df: pd.DataFrame,
    table_stats: dict,
) -> dict:
    """config: Settings,
    df: pd.DataFrame,
    table_stats: dict,
) -> dict:
    """
    Retrieve the descriptive statistics for the time index of a given Pandas DataFrame.

    This function checks if the DataFrame index is either numeric or a DatetimeIndex.
    If the index is valid, it calculates the number of time series, the length of the time 
    index, the start and end dates, and the average period between index entries.

    Args:
        config (Settings): Configuration settings object for any relevant parameters.
        df (pd.DataFrame): The DataFrame from which to extract time index statistics.
        table_stats (dict): A dictionary containing statistics about the DataFrame,
                            including type counts and total record count.

    Returns:
        dict: A dictionary containing:
            - 'n_series' (int): The number of time series identified in the DataFrame.
            - 'length' (int): The total number of entries in the time index.
            - 'start' (Timestamp or numeric): The earliest entry in the index.
            - 'end' (Timestamp or numeric): The latest entry in the index.
            - 'period' (Timedelta or numeric): The average period between entries in the index.
        
        If the index is not a valid type, an empty dictionary is returned.
    """
    if not (is_numeric_dtype(df.index) or isinstance(df.index, pd.DatetimeIndex)):
        return {}

    n_series = table_stats["types"].get("TimeSeries", 0)
    length = table_stats["n"]
    start = df.index.min()
    end = df.index.max()
    period = abs(np.diff(df.index)).mean()
    if isinstance(df.index, pd.DatetimeIndex):
        period = pd.Timedelta(period)

    return {
        "n_series": n_series,
        "length": length,
        "start": start,
        "end": end,
        "period": period,
    }
