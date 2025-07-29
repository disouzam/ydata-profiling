"""Correlations between variables."""
import warnings
from typing import Dict, List, Optional, Sized

import numpy as np
import pandas as pd
from multimethod import multimethod

from ydata_profiling.config import Settings

try:
    from pandas.core.base import DataError
except ImportError:
    from pandas.errors import DataError


class Correlation:
    @staticmethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class Auto(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class Spearman(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class Pearson(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class Kendall(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class Cramers(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


class PhiK(Correlation):
    @staticmethod
    @multimethod
    def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
        """@multimethod
def compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]:
    """
    Computes a result based on the provided configuration, data frame, and summary.

    This is a static method that utilizes multiple dispatch to provide varying implementations
    depending on the input types. The method is expected to be overridden in derived classes.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options for the computation.
    
    df : Sized
        A data structure that implements the Sized interface, typically representing the data to be processed.
    
    summary : dict
        A dictionary containing summary information relevant to the computation.

    Returns:
    -------
    Optional[Sized]
        Returns a Sized object as the result of the computation or None if no result is applicable.

    Raises:
    ------
    NotImplementedError
        This exception is raised if the method is called without an overriding implementation.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()


def warn_correlation(correlation_name: str, error: str) -> None:
    """
    Emits a warning when an attempt to calculate a specified correlation fails.

    This function generates a warning message indicating that the calculation 
    of a correlation with the given name has failed. It also provides instructions 
    on how to suppress this warning by disabling the calculation and suggests 
    reporting the issue if it is problematic.

    Parameters:
    ----------
    correlation_name : str
        The name of the correlation that failed to be calculated.
    
    error : str
        The error message associated with the failure of the correlation calculation.

    Returns:
    -------
    None
    """
    warnings.warn(
        f"""There was an attempt to calculate the {correlation_name} correlation, but this failed.
To hide this warning, disable the calculation
(using `df.profile_report(correlations={{\"{correlation_name}\": {{\"calculate\": False}}}})`
If this is problematic for your use case, please report this as an issue:
https://github.com/ydataai/ydata-profiling/issues
(include the error message: '{error}')"""
    )


def calculate_correlation(
    config: Settings, df: Sized, correlation_name: str, summary: dict
) -> Optional[Sized]:
    """Calculate the correlation coefficients between variables for the correlation types selected in the config
    (auto, pearson, spearman, kendall, phi_k, cramers).

    Args:
        config: report Settings object
        df: The DataFrame with variables.
        correlation_name:
        summary: summary dictionary

    Returns:
        The correlation matrices for the given correlation measures. Return None if correlation is empty.
    """
    correlation_measures = {
        "auto": Auto,
        "pearson": Pearson,
        "spearman": Spearman,
        "kendall": Kendall,
        "cramers": Cramers,
        "phi_k": PhiK,
    }

    correlation = None
    try:
        correlation = correlation_measures[correlation_name].compute(
            config, df, summary
        )
    except (ValueError, AssertionError, TypeError, DataError, IndexError) as e:
        warn_correlation(correlation_name, str(e))

    if correlation is not None and len(correlation) <= 0:
        correlation = None

    return correlation


def perform_check_correlation(
    correlation_matrix: pd.DataFrame, threshold: float
) -> Dict[str, List[str]]:
    """Check whether selected variables are highly correlated values in the correlation matrix.

    Args:
        correlation_matrix: The correlation matrix for the DataFrame.
        threshold:.

    Returns:
        The variables that are highly correlated.
    """

    cols = correlation_matrix.columns
    bool_index = abs(correlation_matrix.values) >= threshold
    np.fill_diagonal(bool_index, False)
    return {
        col: cols[bool_index[i]].values.tolist()
        for i, col in enumerate(cols)
        if any(bool_index[i])
    }


def get_active_correlations(config: Settings) -> List[str]:
    """
    Retrieves a list of active correlation names from the given configuration.

    This function iterates over the correlation settings in the provided
    `config` object and collects the names of correlations that are set 
    to be calculated (i.e., where `calculate` is True).

    Args:
        config (Settings): An instance of the Settings class containing 
                           correlation configurations.

    Returns:
        List[str]: A list of names of correlations that are active 
                   (those marked for calculation).
    """
    correlation_names = [
        correlation_name
        for correlation_name in config.correlations.keys()
        if config.correlations[correlation_name].calculate
    ]
    return correlation_names
