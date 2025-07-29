from dataclasses import asdict
from typing import Any, Callable, Dict, List, Type, Union

import numpy as np
import pandas as pd
from visions import VisionsBaseType, VisionsTypeset

from ydata_profiling.config import Settings
from ydata_profiling.model import BaseDescription
from ydata_profiling.model.handler import Handler
from ydata_profiling.model.summary_algorithms import (
    describe_boolean_1d,
    describe_categorical_1d,
    describe_counts,
    describe_date_1d,
    describe_file_1d,
    describe_generic,
    describe_image_1d,
    describe_numeric_1d,
    describe_path_1d,
    describe_supported,
    describe_text_1d,
    describe_timeseries_1d,
    describe_url_1d,
)


class BaseSummarizer(Handler):
    """A base summarizer

    Can be used to define custom summarizations
    """

    def summarize(
        self, config: Settings, series: pd.Series, dtype: Type[VisionsBaseType]
    ) -> dict:
        """

        Returns:
            object:
        """
        _, _, summary = self.handle(str(dtype), config, series, {"type": str(dtype)})
        return summary


class PandasProfilingSummarizer(BaseSummarizer):
    """The default YData Profiling summarizer"""

    def __init__(self, typeset: VisionsTypeset, *args, **kwargs):
        """
    Initializes the class with a summary map and a typeset.

    This constructor defines a mapping of data types to their respective 
    description functions, which are used to summarize the characteristics 
    of different data types. The available categories include Unsupported, 
    Numeric, DateTime, Text, Categorical, Boolean, URL, Path, File, Image, 
    and TimeSeries.

    Parameters:
    -----------
    typeset : VisionsTypeset
        An instance of VisionsTypeset that specifies the type of data being processed.

    *args : variable length argument list
        Additional positional arguments to be passed to the superclass initializer.

    **kwargs : variable length keyword arguments
        Additional keyword arguments to be passed to the superclass initializer.

    Summary Map:
    -------------
    - "Unsupported": Functions to describe unsupported types.
    - "Numeric": Function to describe numeric 1D data.
    - "DateTime": Function to describe date 1D data.
    - "Text": Function to describe text 1D data.
    - "Categorical": Function to describe categorical 1D data.
    - "Boolean": Function to describe boolean 1D data.
    - "URL": Function to describe URL 1D data.
    - "Path": Function to describe path 1D data.
    - "File": Function to describe file 1D data.
    - "Image": Function to describe image 1D data.
    - "TimeSeries": Function to describe time series 1D data.

    This constructor calls the initializer of the superclass with the 
    summary map, typeset, and any additional arguments provided.
    """
        summary_map: Dict[str, List[Callable]] = {
            "Unsupported": [
                describe_counts,
                describe_generic,
                describe_supported,
            ],
            "Numeric": [
                describe_numeric_1d,
            ],
            "DateTime": [
                describe_date_1d,
            ],
            "Text": [
                describe_text_1d,
            ],
            "Categorical": [
                describe_categorical_1d,
            ],
            "Boolean": [
                describe_boolean_1d,
            ],
            "URL": [
                describe_url_1d,
            ],
            "Path": [
                describe_path_1d,
            ],
            "File": [
                describe_file_1d,
            ],
            "Image": [
                describe_image_1d,
            ],
            "TimeSeries": [
                describe_timeseries_1d,
            ],
        }
        super().__init__(summary_map, typeset, *args, **kwargs)


def format_summary(summary: Union[BaseDescription, dict]) -> dict:
    """Prepare summary for export to json file.

    Args:
        summary (Union[BaseDescription, dict]): summary to export

    Returns:
        dict: summary as dict
    """

    def fmt(v: Any) -> Any:
        """
    Recursively formats the input value `v`.

    This function checks the type of the input value and processes it accordingly:
    - If `v` is a dictionary, it applies the `fmt` function to each key-value pair recursively, returning a new dictionary with formatted values.
    - If `v` is a pandas Series, it converts the Series to a dictionary and applies the `fmt` function to that dictionary.
    - If `v` is a tuple containing exactly two numpy arrays, it returns a dictionary with keys 'counts' and 'bin_edges', where 'counts' corresponds to the first array and 'bin_edges' corresponds to the second array, both converted to lists.
    - For all other types, it simply returns the value as is.

    Parameters:
    ----------
    v : Any
        The input value to be formatted. It can be a dictionary, pandas Series, a tuple of numpy arrays, or any other type.

    Returns:
    -------
    Any
        The formatted value based on the type of the input.
    """
        if isinstance(v, dict):
            return {k: fmt(va) for k, va in v.items()}
        else:
            if isinstance(v, pd.Series):
                return fmt(v.to_dict())
            elif (
                isinstance(v, tuple)
                and len(v) == 2
                and all(isinstance(x, np.ndarray) for x in v)
            ):
                return {"counts": v[0].tolist(), "bin_edges": v[1].tolist()}
            else:
                return v

    if isinstance(summary, BaseDescription):
        summary = asdict(summary)

    summary = {k: fmt(v) for k, v in summary.items()}
    return summary


def _redact_column(column: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact sensitive information in specific fields of a given dictionary.

    This function processes the input dictionary to redact certain keys and values 
    based on predefined criteria. Specifically, it transforms the contents of the 
    specified fields by replacing their keys or values with a redacted format 
    (i.e., "REDACTED_{i}" where {i} is an index). 

    The following fields are targeted for key redaction:
    - "block_alias_char_counts"
    - "block_alias_values"
    - "category_alias_char_counts"
    - "category_alias_values"
    - "character_counts"
    - "script_char_counts"
    - "value_counts_index_sorted"
    - "value_counts_without_nan"
    - "word_counts"

    The following field is targeted for value redaction:
    - "first_rows"

    If the target fields contain dictionaries as values, the function will apply
    redaction on the keys or values of those dictionaries accordingly.

    Args:
        column (Dict[str, Any]): A dictionary representing a column of data, 
                                  which may contain sensitive information.

    Returns:
        Dict[str, Any]: A new dictionary with sensitive information redacted 
                         based on the specified rules.
    """
    def redact_key(data: Dict[str, Any]) -> Dict[str, Any]:
        return {f"REDACTED_{i}": v for i, (_, v) in enumerate(data.items())}

    def redact_value(data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: f"REDACTED_{i}" for i, (k, _) in enumerate(data.items())}

    keys_to_redact = [
        "block_alias_char_counts",
        "block_alias_values",
        "category_alias_char_counts",
        "category_alias_values",
        "character_counts",
        "script_char_counts",
        "value_counts_index_sorted",
        "value_counts_without_nan",
        "word_counts",
    ]

    values_to_redact = ["first_rows"]

    for field in keys_to_redact:
        if field not in column:
            continue
        is_dict = (isinstance(v, dict) for v in column[field].values())
        if any(is_dict):
            column[field] = {k: redact_key(v) for k, v in column[field].items()}
        else:
            column[field] = redact_key(column[field])

    for field in values_to_redact:
        if field not in column:
            continue
        is_dict = (isinstance(v, dict) for v in column[field].values())
        if any(is_dict):
            column[field] = {k: redact_value(v) for k, v in column[field].items()}
        else:
            column[field] = redact_value(column[field])

    return column


def redact_summary(summary: dict, config: Settings) -> dict:
    """Redact summary to export to json file.

    Args:
        summary (dict): summary to redact

    Returns:
        dict: redacted summary
    """
    for _, col in summary["variables"].items():
        if (config.vars.cat.redact and col["type"] == "Categorical") or (
            config.vars.text.redact and col["type"] == "Text"
        ):
            col = _redact_column(col)

    return summary
