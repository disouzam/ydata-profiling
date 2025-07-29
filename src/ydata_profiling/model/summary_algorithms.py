import functools
from typing import Any, Callable, Optional, Tuple, TypeVar

import numpy as np
import pandas as pd
from multimethod import multimethod
from scipy.stats import chisquare

from ydata_profiling.config import Settings

T = TypeVar("T")


def func_nullable_series_contains(fn: Callable) -> Callable:
    """
    A decorator that modifies a function to handle cases where the input 
    pandas Series may contain null (NaN) values. It first checks if the 
    Series has any NaNs. If NaNs are present, it drops them and checks 
    if the resulting Series is empty. If the Series is empty after 
    dropping NaNs, it returns False. Otherwise, it calls the original 
    function with the provided arguments.

    Args:
        fn (Callable): The function to be decorated. It should accept 
                       the following parameters:
                       - config (Settings): Configuration settings.
                       - series (pd.Series): A pandas Series to be processed.
                       - state (dict): A dictionary representing the state.
                       - *args: Additional positional arguments.
                       - **kwargs: Additional keyword arguments.

    Returns:
        Callable: A new function that wraps the original function with 
                   null handling for the pandas Series.

    Usage:
        @func_nullable_series_contains
        def some_function(config, series, state, *args, **kwargs):
            # Function implementation here
    """
    # Function implementation here"""
    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, state: dict, *args, **kwargs
    ) -> bool:
        if series.hasnans:
            series = series.dropna()
            if series.empty:
                return False

        return fn(config, series, state, *args, **kwargs)

    return inner


def histogram_compute(
    config: Settings,
    finite_values: np.ndarray,
    n_unique: int,
    name: str = "histogram",
    weights: Optional[np.ndarray] = None,
) -> dict:
    """config: Settings,
    finite_values: np.ndarray,
    n_unique: int,
    name: str = "histogram",
    weights: Optional[np.ndarray] = None,
) -> dict:
    """
    Computes the histogram of a given array of finite values.

    Parameters:
    ----------
    config : Settings
        Configuration object containing plotting settings.
    finite_values : np.ndarray
        An array of finite numerical values for which the histogram will be computed.
    n_unique : int
        The number of unique values in the finite_values array.
    name : str, optional
        The key used in the output dictionary to store the histogram data. Default is "histogram".
    weights : Optional[np.ndarray], optional
        An array of weights corresponding to the finite values. If provided, the weighted histogram will be computed.

    Returns:
    -------
    dict
        A dictionary containing the computed histogram under the provided `name` key. 
        If `finite_values` is empty, it will return a dictionary with an empty list for the histogram.
    """
    stats = {}
    if len(finite_values) == 0:
        return {name: []}
    hist_config = config.plot.histogram
    bins_arg = "auto" if hist_config.bins == 0 else min(hist_config.bins, n_unique)
    bins = np.histogram_bin_edges(finite_values, bins=bins_arg)
    if len(bins) > hist_config.max_bins:
        bins = np.histogram_bin_edges(finite_values, bins=hist_config.max_bins)
        weights = weights if weights and len(weights) == hist_config.max_bins else None

    stats[name] = np.histogram(
        finite_values, bins=bins, weights=weights, density=config.plot.histogram.density
    )

    return stats"""
    stats = {}
    if len(finite_values) == 0:
        return {name: []}
    hist_config = config.plot.histogram
    bins_arg = "auto" if hist_config.bins == 0 else min(hist_config.bins, n_unique)
    bins = np.histogram_bin_edges(finite_values, bins=bins_arg)
    if len(bins) > hist_config.max_bins:
        bins = np.histogram_bin_edges(finite_values, bins=hist_config.max_bins)
        weights = weights if weights and len(weights) == hist_config.max_bins else None

    stats[name] = np.histogram(
        finite_values, bins=bins, weights=weights, density=config.plot.histogram.density
    )

    return stats


def chi_square(
    values: Optional[np.ndarray] = None, histogram: Optional[np.ndarray] = None
) -> dict:
    """values: Optional[np.ndarray] = None, histogram: Optional[np.ndarray] = None
) -> dict:
    """
    Calculate the Chi-Square statistic and p-value for given data.

    This function computes the Chi-Square statistic for a provided set of values 
    or a pre-computed histogram. If the histogram is not provided, it is generated 
    from the values using automatic binning. If the histogram is empty or sums to zero, 
    the function returns a statistic and p-value of zero.

    Parameters:
    ----------
    values : Optional[np.ndarray], optional
        An array of values to compute the histogram from. If provided, histogram must be None.
    histogram : Optional[np.ndarray], optional
        A pre-computed histogram. If provided, values must be None.

    Returns:
    -------
    dict
        A dictionary containing the Chi-Square statistic and p-value with keys 'statistic' and 'pvalue'.
        If the histogram is empty or sums to zero, it returns {'statistic': 0, 'pvalue': 0}.
    """
    if histogram is None:
        bins = np.histogram_bin_edges(values, bins="auto")
        histogram, _ = np.histogram(values, bins=bins)
    if len(histogram) == 0 or np.sum(histogram) == 0:
        return {"statistic": 0, "pvalue": 0}
    return dict(chisquare(histogram)._asdict())"""
    if histogram is None:
        bins = np.histogram_bin_edges(values, bins="auto")
        histogram, _ = np.histogram(values, bins=bins)
    if len(histogram) == 0 or np.sum(histogram) == 0:
        return {"statistic": 0, "pvalue": 0}
    return dict(chisquare(histogram)._asdict())


def series_hashable(
    fn: Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]
) -> Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]:
    """fn: Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]
) -> Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]:
    """
    A decorator that checks if the provided summary is hashable before executing the given function.

    This decorator wraps a function that takes a configuration, a pandas Series, and a summary dictionary as inputs. 
    If the "hashable" key in the summary dictionary is set to False, it simply returns the original inputs without 
    calling the wrapped function. If "hashable" is True, it proceeds to call the wrapped function with the provided arguments.

    Parameters:
    fn (Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]): 
        The function to be wrapped, which should accept a Settings object, a pandas Series, 
        and a summary dictionary, returning a tuple of the same types.

    Returns:
    Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]:
        The wrapped function that checks the hashable condition before execution.
    """
    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, summary: dict
    ) -> Tuple[Settings, pd.Series, dict]:
        if not summary["hashable"]:
            return config, series, summary
        return fn(config, series, summary)

    return inner


def series_handle_nulls(
    fn: Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]
) -> Callable[[Settings, pd.Series, dict], Tuple[Settings, pd.Series, dict]]:
    """Decorator for nullable series"""

    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, summary: dict
    ) -> Tuple[Settings, pd.Series, dict]:
        """config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """
    Inner function that processes a pandas Series and ensures it does not contain NaN values before 
    passing it to the provided function.

    This function drops any NaN values from the input series and then calls the decorated function
    with the provided configuration, the cleaned series, and summary dictionary.

    Args:
        config (Settings): An instance of Settings containing configuration parameters.
        series (pd.Series): A pandas Series which may contain NaN values that need to be dropped.
        summary (dict): A dictionary that holds summary information.

    Returns:
        Tuple[Settings, pd.Series, dict]: A tuple containing the configuration, the cleaned series, 
        and possibly updated summary information returned by the wrapped function.
    """
        if series.hasnans:
            series = series.dropna()

        return fn(config, series, summary)

    return inner


def named_aggregate_summary(series: pd.Series, key: str) -> dict:
    """
    Generate a summary of aggregate statistics for a given pandas Series.

    This function calculates the maximum, mean, median, and minimum values 
    of the input Series and returns them in a dictionary with keys 
    prefixed by the specified key.

    Parameters:
    series (pd.Series): The input pandas Series for which the summary statistics are to be calculated.
    key (str): A string that will be used to prefix the keys in the returned dictionary.

    Returns:
    dict: A dictionary containing the maximum, mean, median, and minimum 
          values of the Series, with keys formatted as "max_{key}", 
          "mean_{key}", "median_{key}", and "min_{key}".
    """
    summary = {
        f"max_{key}": np.max(series),
        f"mean_{key}": np.mean(series),
        f"median_{key}": np.median(series),
        f"min_{key}": np.min(series),
    }

    return summary"""
    summary = {
        f"max_{key}": np.max(series),
        f"mean_{key}": np.mean(series),
        f"median_{key}": np.median(series),
        f"min_{key}": np.min(series),
    }

    return summary


@multimethod
def describe_counts(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe the counts of a given series based on the provided configuration and summary.

    This function is a multi-method that is expected to be implemented for specific types
    of series. It raises a NotImplementedError if called directly without an appropriate
    implementation.

    Parameters:
    ----------
    config : Settings
        A configuration object containing settings related to the description process.
    
    series : Any
        The data series to be analyzed and described. The type of data may vary.
    
    summary : dict
        A dictionary that holds summary statistics or other relevant information related to the series.

    Returns:
    -------
    Tuple[Settings, Any, dict]
        A tuple containing:
            - The updated configuration object.
            - The processed series after description.
            - The updated summary dictionary with additional information if applicable.

    Raises:
    ------
    NotImplementedError
        If this method is called without a specific implementation for the given series type.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_supported(
    config: Settings, series: Any, series_description: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, series_description: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe the supported features of the given series based on the provided configuration.

    This function is a multimethod and is expected to be implemented in subclasses. It raises 
    a NotImplementedError if called directly.

    Args:
        config (Settings): The configuration settings to be used for the description.
        series (Any): The series data whose features are to be described.
        series_description (dict): A dictionary containing the description or metadata of the series.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing the updated settings, the series data, 
        and the description dictionary.

    Raises:
        NotImplementedError: If this method is called directly without an implementation.
    """
    raise NotImplementedError()


@multimethod
def describe_generic(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """```python
def describe_generic(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    A multi-method that describes a generic behavior based on the provided configuration, series data, and summary dictionary.

    This function is intended to be implemented in subclasses and can be used to define specific behaviors
    for different types of series. The default implementation raises a NotImplementedError.

    Args:
        config (Settings): An instance of the Settings class that contains configuration parameters.
        series (Any): The data series to be described, which can be of any type.
        summary (dict): A dictionary containing summary information related to the series.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing the updated configuration, the processed series, and the updated summary.
    
    Raises:
        NotImplementedError: If the function is not implemented in a subclass.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_numeric_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Multi-method function to describe a one-dimensional numeric data series.

    This function is intended to be implemented in subclasses. It is
    designed to take a configuration object, a numeric series, and a
    summary dictionary as input and return processed results in the
    form of a tuple containing the modified configuration, the input
    series, and an updated summary.

    Args:
        config (Settings): A configuration object containing settings 
                           relevant to the description process.
        series (Any): A one-dimensional numeric data series to be described.
        summary (dict): A dictionary that holds summary statistics or 
                        information related to the series.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing the updated configuration,
                                     the original series, and an updated summary.

    Raises:
        NotImplementedError: This method must be implemented in a subclass.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_text_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict, Any]:
    """```python
def describe_text_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict, Any]:
    """
    Describes a one-dimensional text series based on the provided configuration and summary.

    This function is a multimethod and is expected to provide an implementation
    that describes the input text series. The actual implementation should return
    a tuple consisting of the updated configuration, the processed text series,
    the original summary dictionary, and any additional output relevant to the description.

    Parameters:
        config (Settings): Configuration settings that dictate how the text series should be processed.
        series (Any): The one-dimensional text series to be described.
        summary (dict): A dictionary containing summary information about the text series.

    Returns:
        Tuple[Settings, Any, dict, Any]: A tuple containing the updated configuration, 
        the processed series, the input summary, and any additional output.

    Raises:
        NotImplementedError: This method is intended to be overridden in subclasses and 
        will raise this exception if called directly.

    Note:
        This function uses multimethod programming, allowing for different implementations 
        based on the types of the inputs.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_date_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe a one-dimensional date series and update the provided summary.

    This function is a multimethod that is intended to provide a description
    of a one-dimensional date series based on the given configuration,
    series data, and a summary dictionary. The actual implementation
    should be provided in a derived class or another variant of this method.

    Parameters:
    config (Settings): An object containing configuration settings for the 
                       description process.
    series (Any): The one-dimensional date series data to be described.
    summary (dict): A dictionary to hold the summary information of the 
                    description results.

    Returns:
    Tuple[Settings, Any, dict]: A tuple containing updated configuration,
                                 the original or transformed series, and
                                 the updated summary dictionary.

    Raises:
    NotImplementedError: If the method is called without an implementation.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_categorical_1d(
    config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """
    Describe a 1-dimensional categorical data series.

    This function is intended to generate a description of a given 
    categorical Pandas Series, utilizing the provided configuration 
    settings and summary information. The implementation has yet 
    to be defined and will raise a NotImplementedError if called.

    Parameters:
    ----------
    config : Settings
        A configuration object containing settings for the description process.
    series : pd.Series
        A Pandas Series containing categorical data to be described.
    summary : dict
        A dictionary that holds summary information relevant to the series 
        description.

    Returns:
    -------
    Tuple[Settings, pd.Series, dict]
        A tuple containing the modified configuration, the original 
        Pandas Series, and the updated summary dictionary.

    Raises:
    ------
    NotImplementedError
        If the function is called before an implementation is provided.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_url_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe a one-dimensional URL based on the provided configuration, series, and summary.

    This function is a multimethod that takes in a configuration object, a series of data,
    and a summary dictionary. It raises a NotImplementedError, indicating that the implementation
    should be provided in a subclass or a different context.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options.
    
    series : Any
        The data series to be described. This can be any type that is relevant to the context.
    
    summary : dict
        A dictionary containing summary information related to the series.

    Returns:
    -------
    Tuple[Settings, Any, dict]
        A tuple consisting of the processed settings, the original series or modified series,
        and the updated summary dictionary.

    Raises:
    ------
    NotImplementedError
        If this method is called without a proper implementation in a subclass.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_file_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describes a 1D file based on the provided configuration, data series, and summary.

    This function is a multimethod placeholder and raises a NotImplementedError.
    It is intended to be overridden in subclasses to provide specific implementation
    for describing a 1D file.

    Parameters:
        config (Settings): An instance of the Settings class containing configuration options.
        series (Any): The data series to be described, which can be of any type.
        summary (dict): A dictionary containing summary information related to the data series.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing:
            - Updated Settings instance after processing.
            - The original or modified data series.
            - A dictionary containing the updated summary information.

    Raises:
        NotImplementedError: If this method is called directly without a concrete implementation.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_path_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describes a 1-dimensional path based on the provided configuration and series data.

    This function is designed to be part of a multi-method system and is not 
    implemented in this version. It is expected to return a tuple containing 
    the updated configuration, the processed series, and a summary dictionary.

    Parameters:
        config (Settings): The configuration settings used for processing.
        series (Any): The input data series to be described.
        summary (dict): A dictionary containing summary information.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing the updated configuration,
                                     the processed series, and the summary dictionary.

    Raises:
        NotImplementedError: This method must be implemented in a subclass.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_image_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """```python
@multimethod
def describe_image_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe a one-dimensional image based on the provided configuration and series.

    This function is intended to be overridden in a subclass. It raises a 
    NotImplementedError if called directly.

    Args:
        config (Settings): An instance of Settings containing configuration options.
        series (Any): The data series representing the one-dimensional image.
        summary (dict): A dictionary to store summary information regarding the 
                        image description.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing:
            - An updated instance of Settings.
            - Processed data series.
            - Updated summary dictionary with the description of the image.

    Raises:
        NotImplementedError: Indicates that the function must be implemented in a 
                             subclass.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def describe_boolean_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """```python
def describe_boolean_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe a boolean 1-dimensional series based on the provided configuration and summary.

    This function is a placeholder and currently raises a NotImplementedError. 
    It is intended to be overridden with an implementation that analyzes and provides
    insights into a boolean series.

    Args:
        config (Settings): Configuration settings for the description process.
        series (Any): The boolean 1-dimensional series to be described.
        summary (dict): A dictionary to hold summary statistics or results of the description.

    Returns:
        Tuple[Settings, Any, dict]: A tuple containing the updated configuration, 
        the original or transformed series, and the summary dictionary.

    Raises:
        NotImplementedError: If this method is called directly without an actual implementation.
    """
    raise NotImplementedError()


@multimethod
def describe_timeseries_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """```python
def describe_timeseries_1d(
    config: Settings, series: Any, summary: dict
) -> Tuple[Settings, Any, dict]:
    """
    Describe a 1-dimensional timeseries based on the provided configuration and summary.

    This function is designed to provide a detailed description of a 1-dimensional
    timeseries. It takes in a configuration object, the timeseries data, and a summary
    dictionary, and returns an updated configuration, the processed timeseries data,
    and a summary dictionary.

    Parameters:
    ----------
    config : Settings
        An object containing configuration settings for the timeseries description.
    series : Any
        The 1-dimensional timeseries data to be described.
    summary : dict
        A dictionary containing summary information related to the timeseries.

    Returns:
    -------
    Tuple[Settings, Any, dict]
        A tuple containing the updated configuration, processed timeseries data,
        and an updated summary dictionary.

    Raises:
    ------
    NotImplementedError
        This method is not yet implemented.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()
