from typing import Any, Dict, Optional, Sequence, Tuple, TypeVar

from multimethod import multimethod

from ydata_profiling.config import Settings

T = TypeVar("T")


@multimethod
def get_duplicates(
    config: Settings, df: T, supported_columns: Sequence
) -> Tuple[Dict[str, Any], Optional[T]]:
    """config: Settings, df: T, supported_columns: Sequence
) -> Tuple[Dict[str, Any], Optional[T]]:
    """
    Retrieve duplicate entries from a DataFrame based on the specified settings.

    This function is designed to identify and return duplicate records in the given 
    DataFrame `df` according to the criteria defined in the `config` settings. 
    The function also takes in a list of `supported_columns` which dictates 
    the columns to be considered when searching for duplicates.

    Args:
        config (Settings): Configuration settings that define how to identify 
                           duplicates.
        df (T): The DataFrame from which duplicates are to be identified.
        supported_columns (Sequence): A sequence of column names to consider when 
                                      looking for duplicates.

    Returns:
        Tuple[Dict[str, Any], Optional[T]]: A tuple containing a dictionary with 
                                              information about the duplicates found, 
                                              and an optional DataFrame of the duplicates 
                                              themselves. The first element of the tuple 
                                              provides details, while the second element 
                                              may be None if no duplicates were found or 
                                              if the implementation does not return them.

    Raises:
        NotImplementedError: This function is not implemented and raises an exception 
                             if called.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()
