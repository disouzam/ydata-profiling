"""Compute statistical description of datasets."""

from typing import Any

from multimethod import multimethod

from ydata_profiling.config import Settings


@multimethod
def get_time_index_description(
    config: Settings,
    df: Any,
    table_stats: dict,
) -> dict:
    """```python
@multimethod
def get_time_index_description(
    config: Settings,
    df: Any,
    table_stats: dict,
) -> dict:
    """
    Generate a description of the time index based on the provided configuration settings, DataFrame,
    and table statistics.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class containing configuration options for generating the time index description.
    df : Any
        The DataFrame containing the data to be analyzed. The type should be specified based on the application's needs.
    table_stats : dict
        A dictionary containing statistical information about the table, which may be used to inform the description logic.

    Returns:
    -------
    dict
        A dictionary containing the description of the time index, structured according to the application's requirements.

    Raises:
    ------
    NotImplementedError
        Indicates that the function must be implemented in a subclass or extended method.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()
