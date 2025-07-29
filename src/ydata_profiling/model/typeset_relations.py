import functools
from typing import Callable, Dict

import numpy as np
import pandas as pd
from pandas.api import types as pdt
from visions.backends.pandas.series_utils import series_handle_nulls

from ydata_profiling.config import Settings
from ydata_profiling.utils.versions import is_pandas_1


def is_nullable(series: pd.Series, state: dict) -> bool:
    """
    Check if the given Pandas Series is nullable.

    This function determines if the provided Series contains any non-null values. 
    It returns True if the Series has no null values and False otherwise.

    Parameters:
    ----------
    series : pd.Series
        The Pandas Series to be checked for null values.
    
    state : dict
        A dictionary that may include additional state information (currently not used in the function).

    Returns:
    -------
    bool
        True if the Series has no null values, False if it does.
    """
    return series.count() > 0


def try_func(fn: Callable) -> Callable:
    """
    A decorator that wraps a function to provide error handling.

    This decorator catches any exceptions raised by the wrapped function
    and returns `False` instead of propagating the exception. It is
    useful when you want to safely execute a function that may fail,
    particularly when working with pandas Series.

    Parameters:
    fn (Callable): The function to be wrapped. It should accept at least
                   a pandas Series as its first argument, followed by
                   any additional positional and keyword arguments.

    Returns:
    Callable: A new function that wraps the original function with error
              handling. The wrapped function will return `True` if the
              original function executes successfully, or `False` if an
              exception is raised.

    Example:
        @try_func
        def process_data(series: pd.Series) -> bool:
            # Some processing logic that might raise an exception
            return True

    Note:
        Be cautious when using a broad exception catch; it may hide
        unexpected errors. Consider specifying the exception types to catch.
    """
    @functools.wraps(fn)
    def inner(series: pd.Series, *args, **kwargs) -> bool:
        try:
            return fn(series, *args, **kwargs)
        except:  # noqa: E722
            return False

    return inner


def string_is_bool(series: pd.Series, state: dict, k: Dict[str, bool]) -> bool:
    """
    Determines if all string elements in a given pandas Series are present in the keys of a specified dictionary.

    Parameters:
    ----------
    series : pd.Series
        A pandas Series containing string elements to be checked.
    
    state : dict
        A dictionary containing any necessary contextual information, which may be used for additional handling or processing.
    
    k : Dict[str, bool]
        A dictionary whose keys will be checked against the string values in the Series.

    Returns:
    -------
    bool
        Returns True if all lowercased strings in the Series are present in the keys of the dictionary `k`, 
        and False otherwise. Returns False if the Series has a categorical dtype.

    Notes:
    -----
    This function is decorated with `@series_handle_nulls` and `@try_func`, which may provide additional handling
    for null values and error handling, respectively.
    """
    @series_handle_nulls
    @try_func
    def tester(s: pd.Series, state: dict) -> bool:
        return s.str.lower().isin(k.keys()).all()

    if isinstance(series.dtype, pd.CategoricalDtype):
        return False

    return tester(series, state)


def string_to_bool(series: pd.Series, state: dict, k: Dict[str, bool]) -> pd.Series:
    """```python
def string_to_bool(series: pd.Series, state: dict, k: Dict[str, bool]) -> pd.Series:
    """
    Convert a pandas Series of strings to boolean values based on a provided mapping.

    This function takes a pandas Series containing string values, converts them to lowercase, 
    and maps them to boolean values using a specified dictionary. The mapping dictionary 
    should have string keys corresponding to the lowercase versions of the entries in the Series 
    and boolean values.

    Parameters:
    ----------
    series : pd.Series
        A pandas Series containing string values to be converted to boolean.

    state : dict
        A dictionary containing additional state information (not used directly in this function).

    k : Dict[str, bool]
        A dictionary mapping lowercase string values to boolean values. 
        For example, {'true': True, 'false': False}.

    Returns:
    -------
    pd.Series
        A pandas Series containing the mapped boolean values. 
        If a string does not exist in the mapping dictionary, the result will be NaN for that entry.
    """
    return series.str.lower().map(k)"""
    return series.str.lower().map(k)


def numeric_is_category(series: pd.Series, state: dict, k: Settings) -> bool:
    """
    Determines if a given numeric pandas Series can be considered categorical based on 
    the number of unique values within a defined threshold.

    Parameters:
    series (pd.Series): A pandas Series containing numeric values to be evaluated.
    state (dict): A dictionary representing the current state, which may contain additional context (unused in this function).
    k (Settings): An instance of the Settings class, which provides configuration parameters, including 
                  the low categorical threshold.

    Returns:
    bool: True if the number of unique values in the series is between 1 and the low categorical threshold; 
           False otherwise.
    """
    n_unique = series.nunique()
    threshold = k.vars.num.low_categorical_threshold
    return 1 <= n_unique <= threshold


def to_category(series: pd.Series, state: dict) -> pd.Series:
    """```python
def to_category(series: pd.Series, state: dict) -> pd.Series:
    """
    Convert a pandas Series to a categorical string format.

    This function takes a pandas Series and converts its values to a string type. 
    If the Series contains NaN values, they are replaced with the appropriate `np.nan` 
    representation. The resulting Series will be of the string dtype.

    Parameters:
    ----------
    series : pd.Series
        The input pandas Series to be converted. It may contain NaN values.
    
    state : dict
        A dictionary that can be used for state management or configuration, if applicable 
        (not utilized in the current implementation).

    Returns:
    -------
    pd.Series
        A pandas Series with values converted to string dtype, with NaN values handled appropriately.
    """
    hasnans = series.hasnans
    val = series.astype(str)
    if hasnans:
        val = val.replace("nan", np.nan)
        val = val.replace("<NA>", np.nan)

    return val.astype("string")


@series_handle_nulls
def series_is_string(series: pd.Series, state: dict) -> bool:
    """def series_is_string(series: pd.Series, state: dict) -> bool:
    """
    Check if all elements in the given pandas Series are strings.

    This function evaluates whether the first five elements of the Series
    are of string type. It also attempts to convert the entire Series to strings
    and checks if the conversion matches the original values. If any exceptions
    (TypeError or ValueError) are raised during this process, it assumes the
    Series does not contain only string values.

    Args:
        series (pd.Series): The pandas Series to evaluate.
        state (dict): A dictionary that may contain state information, 
                      but is not used in this function.

    Returns:
        bool: True if all elements in the Series are strings, otherwise False.
    """
    if not all(isinstance(v, str) for v in series.values[0:5]):
        return False
    try:
        return (series.astype(str).values == series.values).all()
    except (TypeError, ValueError):
        return False


@series_handle_nulls
def string_is_category(series: pd.Series, state: dict, k: Settings) -> bool:
    """String is category, if the following conditions are met
    - has at least one and less or equal distinct values as threshold
    - (distinct values / count of all values) is less than threshold
    - is not bool"""
    n_unique = series.nunique()
    unique_threshold = k.vars.cat.percentage_cat_threshold
    threshold = k.vars.cat.cardinality_threshold
    return (
        1 <= n_unique <= threshold
        and (
            n_unique / series.size < unique_threshold
            if unique_threshold <= 1
            else n_unique / series.size <= unique_threshold
        )
        and not string_is_bool(series, state, k.vars.bool.mappings)
    )


@series_handle_nulls
def string_is_datetime(series: pd.Series, state: dict) -> bool:
    """If we can transform data to datetime and at least one is valid date."""
    try:
        return not string_to_datetime(series, state).isna().all()
    except:  # noqa: E722
        return False


@series_handle_nulls
def string_is_numeric(series: pd.Series, state: dict, k: Settings) -> bool:
    """
    Determines whether the provided Pandas Series can be considered numeric.

    This function checks if the input series contains boolean data types. 
    If it does, the function immediately returns False. It then attempts 
    to convert the series to a float type and checks for any numeric 
    conversion errors. If the series contains NaN values and has no other 
    valid numeric entries, it also returns False.

    Finally, the function checks if the series is categorized as numeric 
    based on the provided state and settings. 

    Parameters:
    ----------
    series : pd.Series
        A Pandas Series to be evaluated.
    
    state : dict
        A dictionary containing contextual data which might influence 
        the evaluation of the series.
    
    k : Settings
        An object containing configuration settings relevant to the 
        numeric evaluation.

    Returns:
    -------
    bool
        Returns True if the series can be classified as numeric, 
        otherwise returns False.
    """
    if pdt.is_bool_dtype(series) or object_is_bool(series, state):
        return False

    try:
        _ = series.astype(float)
        r = pd.to_numeric(series, errors="coerce")
        if r.hasnans and r.count() == 0:
            return False
    except:  # noqa: E722
        return False

    return not numeric_is_category(series, state, k)


def string_to_datetime(series: pd.Series, state: dict) -> pd.Series:
    """
    Converts a pandas Series of string date representations into datetime objects.

    This function checks the version of pandas being used and calls the appropriate 
    function to convert the series to datetime. If the pandas version is 1.0 or higher, 
    it uses the default `pd.to_datetime` method. For earlier versions, it uses the 
    `pd.to_datetime` method with a mixed format.

    Parameters:
    ----------
    series : pd.Series
        A pandas Series containing string representations of dates.
    
    state : dict
        A dictionary containing any additional state information that may be needed 
        for processing (currently not used in the function).

    Returns:
    -------
    pd.Series
        A pandas Series with the converted datetime objects.
    """
    if is_pandas_1():
        return pd.to_datetime(series)
    return pd.to_datetime(series, format="mixed")


def string_to_numeric(series: pd.Series, state: dict) -> pd.Series:
    """
    Converts a pandas Series of strings to numeric values.

    This function attempts to convert each element in the provided pandas Series
    to a numeric type. Non-convertible values will be set to NaN.

    Parameters:
    -----------
    series : pd.Series
        A pandas Series containing string representations of numbers.
    
    state : dict
        A dictionary containing additional state information (not used in this implementation).

    Returns:
    --------
    pd.Series
        A pandas Series with the converted numeric values. Non-convertible elements are replaced with NaN.
    """
    return pd.to_numeric(series, errors="coerce")"""
    return pd.to_numeric(series, errors="coerce")


hasnan_bool_name = "boolean"


def to_bool(series: pd.Series) -> pd.Series:
    """
    Convert a pandas Series to boolean dtype.
    
    This function takes a pandas Series as input and converts its 
    data type to boolean. If the Series contains any NaN values, 
    the resulting dtype will be a nullable boolean. Otherwise, 
    it will be converted to a standard boolean type.

    Parameters:
    ----------
    series : pd.Series
        The input pandas Series to be converted to boolean.

    Returns:
    -------
    pd.Series
        A new pandas Series with boolean dtype.
        
    Notes:
    -----
    The conversion utilizes the 'hasnans' attribute of the Series 
    to determine the appropriate dtype for conversion.
    """
    dtype = hasnan_bool_name if series.hasnans else bool
    return series.astype(dtype)


@series_handle_nulls
def object_is_bool(series: pd.Series, state: dict) -> bool:
    """
    Check if a pandas Series contains only boolean values.

    This function evaluates whether a given pandas Series, 
    which must be of object data type, contains exclusively 
    boolean values (True and False). 

    It returns True if all items in the Series are either 
    True or False, and returns False in any other cases 
    (including if the Series is not of object dtype or 
    if there's an error during the evaluation).

    Parameters:
    -----------
    series : pd.Series
        The pandas Series to be checked for boolean values.

    state : dict
        A dictionary that can be used to store or pass additional 
        state information (not used in this function).

    Returns:
    --------
    bool
        True if all items in the Series are boolean; otherwise, False.
    """
    if pdt.is_object_dtype(series):
        bool_set = {True, False}
        try:
            ret = all(item in bool_set for item in series)
        except:  # noqa: E722
            ret = False

        return ret
    return False
