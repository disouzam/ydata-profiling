import datetime
import imghdr
import os
import warnings
from functools import partial, wraps
from typing import Callable, Sequence, Set
from urllib.parse import urlparse

import pandas as pd
import visions
from multimethod import multimethod
from pandas.api import types as pdt
from visions.backends.pandas.series_utils import series_not_empty
from visions.relations import IdentityRelation, InferenceRelation, TypeRelation

from ydata_profiling.config import Settings
from ydata_profiling.model.typeset_relations import (
    numeric_is_category,
    series_is_string,
    string_is_bool,
    string_is_category,
    string_is_datetime,
    string_is_numeric,
    string_to_bool,
    string_to_datetime,
    string_to_numeric,
    to_bool,
    to_category,
)

pandas_has_string_dtype_flag = hasattr(pdt, "is_string_dtype")


def series_handle_nulls(fn: Callable[..., bool]) -> Callable[..., bool]:
    """Decorator for nullable series"""

    @wraps(fn)
    def inner(series: pd.Series, state: dict, *args, **kwargs) -> bool:
        """
    Inner function that checks for NaN values in a given pandas Series and processes
    the Series accordingly before passing it to the provided function.

    This function updates the 'state' dictionary by adding a key 'hasnans' that indicates 
    whether the input Series contains any NaN values. If NaN values are present, they are 
    dropped from the Series. If the resulting Series is empty after dropping NaNs, the 
    function returns False. Otherwise, it calls the provided function 'fn' with the 
    cleaned Series and the current state, along with any additional positional or keyword 
    arguments.

    Parameters:
        series (pd.Series): The input pandas Series to be processed.
        state (dict): A dictionary that maintains the state information across calls.
        *args: Variable length argument list for additional parameters to be passed to fn.
        **kwargs: Arbitrary keyword arguments to be passed to fn.

    Returns:
        bool: Returns False if the Series is empty after dropping NaNs; 
              otherwise, it returns the result of the function fn.
    """
        if "hasnans" not in state:
            state["hasnans"] = series.hasnans

        if state["hasnans"]:
            series = series.dropna()
            if series.empty:
                return False

        return fn(series, state, *args, **kwargs)

    return inner


def typeset_types(config: Settings) -> Set[visions.VisionsBaseType]:
    """Define types based on the config"""

    class Unsupported(visions.Generic):
        """Base type. All other types have relationship with this type."""

        pass

    class Numeric(visions.VisionsBaseType):
        """Type for all numeric (float, int) columns.

        Can be transformed from
        - Unsupported
        - String

        Examples
        --------
        >>> s = pd.Series([1, 2, 5, 3, 8, 9])
        >>> s in Numeric
        True

        >>> s = pd.Series([.34, 2.9, 55, 3.14, 89, 91])
        >>> s in Numeric
        True
        """

        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [
                IdentityRelation(Unsupported),
                InferenceRelation(
                    Text,
                    relationship=lambda x, y: partial(string_is_numeric, k=config)(
                        x, y
                    ),
                    transformer=string_to_numeric,
                ),
            ]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            return pdt.is_numeric_dtype(series) and not pdt.is_bool_dtype(series)

    class Text(visions.VisionsBaseType):
        """Type for plaintext columns.
        Like name, note, string identifier, residence etc.

        Examples
        --------
        >>> s = pd.Series(["AX01", "BC32", "AC00"])
        >>> s in Categorical
        True

        >>> s = pd.Series([1, 2, 3, 4])
        >>> s in Categorical
        False
        """

        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [
                IdentityRelation(Unsupported),
            ]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            return (
                not isinstance(series.dtype, pd.CategoricalDtype)
                and pdt.is_string_dtype(series)
                and series_is_string(series, state)
            )

    class DateTime(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [
                IdentityRelation(Unsupported),
                InferenceRelation(
                    Text,
                    relationship=lambda x, y: partial(string_is_datetime)(x, y),
                    transformer=string_to_datetime,
                ),
            ]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            is_datetime = pdt.is_datetime64_any_dtype(series)
            if is_datetime:
                return True
            has_builtin_datetime = (
                series.dropna()
                .apply(type)
                .isin([datetime.date, datetime.datetime])
                .all()
            )
            return has_builtin_datetime

    class Categorical(visions.VisionsBaseType):
        """Type for categorical columns.
        Categorical columns in pandas categorical format
        and columns in string format with small count of unique values.

        Can be transformed from:
            - Unsupported
            - Numeric
            - String

        Examples
        --------
        >>> s = pd.Series(["male", "female", "female", "male"], dtype="category")
        >>> s in Categorical
        True

        >>> s = pd.Series(["male", "female"])
        >>> s in Categorical
        False

        >>> s = pd.Series(["male", "female", "female", "male"])
        >>> s in Categorical
        True
        """

        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [
                IdentityRelation(Unsupported),
                InferenceRelation(
                    Numeric,
                    relationship=lambda x, y: partial(numeric_is_category, k=config)(
                        x, y
                    ),
                    transformer=to_category,
                ),
                InferenceRelation(
                    Text,
                    relationship=lambda x, y: partial(string_is_category, k=config)(
                        x, y
                    ),
                    transformer=to_category,
                ),
            ]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            is_valid_dtype = isinstance(
                series.dtype, pd.CategoricalDtype
            ) and not pdt.is_bool_dtype(series)
            if is_valid_dtype:
                return True
            return False

    class Boolean(visions.VisionsBaseType):
        """Type for boolean columns."""

        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            # Numeric [0, 1] goes via Categorical with distinct_count_without_nan <= 2
            mapping = config.vars.bool.mappings

            return [
                IdentityRelation(Unsupported),
                InferenceRelation(
                    Text,
                    relationship=lambda x, y: partial(string_is_bool, k=mapping)(x, y),
                    transformer=lambda s, st: to_bool(
                        partial(string_to_bool, k=mapping)(s, st)
                    ),
                ),
            ]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            if pdt.is_object_dtype(series):
                try:
                    return series.isin({True, False}).all()
                except:  # noqa: E722
                    return False

            return pdt.is_bool_dtype(series)

    class URL(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [IdentityRelation(Text)]

        @staticmethod
        @multimethod
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            # TODO: use coercion utils
            try:
                url_gen = (urlparse(x) for x in series)
                return all(x.netloc and x.scheme for x in url_gen)  # noqa: TC300
            except AttributeError:
                return False

    class Path(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [IdentityRelation(Text)]

        @staticmethod
        @multimethod
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            # TODO: use coercion utils
            try:
                return all(os.path.isabs(p) for p in series)
            except TypeError:
                return False

    class File(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [IdentityRelation(Path)]

        @staticmethod
        @multimethod
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            return all(os.path.exists(p) for p in series)

    class Image(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [IdentityRelation(File)]

        @staticmethod
        @multimethod
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            return all(imghdr.what(p) for p in series)

    class TimeSeries(visions.VisionsBaseType):
        @staticmethod
        def get_relations() -> Sequence[TypeRelation]:
            """def get_relations() -> Sequence[TypeRelation]:
    """
    Retrieves a list of relational types.

    This static method returns a sequence of relations, currently returning
    a single relation of type IdentityRelation, parameterized with the 
    Numeric type.

    Returns:
        Sequence[TypeRelation]: A sequence containing the defined relations.
    """
    return [IdentityRelation(Numeric)]"""
            return [IdentityRelation(Numeric)]

        @staticmethod
        @multimethod
        @series_not_empty
        @series_handle_nulls
        def contains_op(series: pd.Series, state: dict) -> bool:
            """
    Determines if the provided pandas Series is both numeric (excluding boolean types)
    and time-dependent based on autocorrelation analysis.

    This function checks whether the input Series meets two conditions:
    1. It is a numeric type and not a boolean type.
    2. It exhibits time-dependence, as determined by calculating
       the autocorrelation at specified lags and comparing the 
       values against a predefined threshold.

    The autocorrelation is computed for each lag specified in the configuration.
    If any of the computed autocorrelations exceed the defined threshold, 
    the function concludes that the Series is time-dependent.

    Args:
        series (pd.Series): The pandas Series to be evaluated.
        state (dict): A dictionary that may be used to maintain or pass state information.

    Returns:
        bool: True if the Series is numeric (non-boolean) and time-dependent, False otherwise.
    """
            def is_timedependent(series: pd.Series) -> bool:
                autocorrelation_threshold = config.vars.timeseries.autocorrelation
                lags = config.vars.timeseries.lags
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    for lag in lags:
                        autcorr = series.autocorr(lag=lag)
                        if autcorr >= autocorrelation_threshold:
                            return True

                return False

            is_numeric = pdt.is_numeric_dtype(series) and not pdt.is_bool_dtype(series)
            return is_numeric and is_timedependent(series)

    types = {Unsupported, Boolean, Numeric, Text, Categorical, DateTime}
    if config.vars.path.active:
        types.add(Path)
        if config.vars.file.active:
            types.add(File)
            if config.vars.image.active:
                types.add(Image)

    if config.vars.url.active:
        types.add(URL)

    if config.vars.timeseries.active:
        types.add(TimeSeries)

    return types


class ProfilingTypeSet(visions.VisionsTypeset):
    def __init__(self, config: Settings, type_schema: dict = None):
        """
    Initializes an instance of the class with a given configuration and type schema.

    Args:
        config (Settings): An instance of Settings that contains the configuration for the class.
        type_schema (dict, optional): A dictionary representing the type schema. Defaults to an empty dictionary if not provided.

    Raises:
        UserWarning: Suppressed warning for user-related issues during initialization.

    This constructor retrieves the types based on the provided configuration and 
    initializes the superclass with these types, while ignoring any UserWarnings 
    that may arise during the process. It also sets up the type schema using the
    provided dictionary or initializes it to an empty dictionary if not specified.
    """
    self.config = config

    types = typeset_types(config)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        super().__init__(types)

    self.type_schema = self._init_type_schema(type_schema or {})"""
        self.config = config

        types = typeset_types(config)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            super().__init__(types)

        self.type_schema = self._init_type_schema(type_schema or {})

    def _init_type_schema(self, type_schema: dict) -> dict:
        """
    Initializes the type schema by transforming each value in the provided 
    dictionary using the _get_type method.

    Args:
        type_schema (dict): A dictionary representing the type schema, 
                            where keys are type names and values are the 
                            corresponding type definitions.

    Returns:
        dict: A new dictionary with the same keys as the input, but with values 
              transformed by calling _get_type on each original value.
    """
    return {k: self._get_type(v) for k, v in type_schema.items()}"""
        return {k: self._get_type(v) for k, v in type_schema.items()}

    def _get_type(self, type_name: str) -> visions.VisionsBaseType:
        """
    Retrieve a type from the collection of types by its name.

    This method searches for a type in the `self.types` collection that matches
    the provided `type_name`, ignoring case. If a match is found, the type is returned.
    If no matching type is found, a ValueError is raised.

    Args:
        type_name (str): The name of the type to retrieve.

    Returns:
        visions.VisionsBaseType: The matching type object.

    Raises:
        ValueError: If no type with the specified name is found in the collection.

    Example:
        >>> type_instance = self._get_type('SomeTypeName')
    """
        for t in self.types:
            if t.__name__.lower() == type_name.lower():
                return t
        raise ValueError(f"Type [{type_name}] not found.")
