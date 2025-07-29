import os
from datetime import datetime
from typing import Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_file_1d, histogram_compute


def file_summary(series: pd.Series) -> dict:
    """

    Args:
        series: series to summarize

    Returns:

    """

    # Transform
    stats = series.map(lambda x: os.stat(x))

    def convert_datetime(x: float) -> str:
        """
    Convert a timestamp to a formatted datetime string.

    This function takes a Unix timestamp (in seconds) as input and 
    returns a string representing the corresponding date and time 
    formatted as "YYYY-MM-DD HH:MM:SS".

    Args:
        x (float): The Unix timestamp to be converted.

    Returns:
        str: A string representing the formatted date and time.
    """
    return datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")"""
        return datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")

    # Transform some more
    summary = {
        "file_size": stats.map(lambda x: x.st_size),
        "file_created_time": stats.map(lambda x: x.st_ctime).map(convert_datetime),
        "file_accessed_time": stats.map(lambda x: x.st_atime).map(convert_datetime),
        "file_modified_time": stats.map(lambda x: x.st_mtime).map(convert_datetime),
    }
    return summary


@describe_file_1d.register
def pandas_describe_file_1d(
    config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """
    Generate a descriptive summary for a 1-dimensional pandas Series.

    This function checks if the given Series contains NaN values and raises
    a ValueError if any are found. It also ensures that the Series has a 
    string accessor (.str). The function updates the provided summary
    dictionary with statistics from the Series and a histogram of file sizes.

    Parameters:
    ---------
    config : Settings
        A configuration object containing settings for the summary.
    series : pd.Series
        A pandas Series object containing the 1-dimensional data to be described.
    summary : dict
        A dictionary to be updated with the descriptive summary and histogram.

    Returns:
    -------
    Tuple[Settings, pd.Series, dict]
        A tuple containing the updated configuration, the original Series, 
        and the updated summary dictionary.

    Raises:
    -------
    ValueError: If the Series contains NaN values or does not have a .str accessor.

    Example:
    --------
    config = Settings()
    series = pd.Series(["data1", "data2", "data3"])
    summary = {}
    updated_config, updated_series, updated_summary = pandas_describe_file_1d(config, series, summary)
    """
    if series.hasnans:
        raise ValueError("May not contain NaNs")
    if not hasattr(series, "str"):
        raise ValueError("series should have .str accessor")

    summary.update(file_summary(series))
    summary.update(
        histogram_compute(
            config,
            summary["file_size"],
            summary["file_size"].nunique(),
            name="histogram_file_size",
        )
    )

    return config, series, summary
