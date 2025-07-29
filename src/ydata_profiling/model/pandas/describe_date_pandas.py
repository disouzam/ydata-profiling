from typing import Tuple

import numpy as np
import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    chi_square,
    describe_date_1d,
    histogram_compute,
    series_handle_nulls,
    series_hashable,
)
from ydata_profiling.model.typeset_relations import is_pandas_1


def to_datetime(series: pd.Series) -> pd.Series:
    """
    Convert a pandas Series to a datetime format.

    This function takes a pandas Series as input and attempts to convert its elements 
    to datetime objects. The conversion method depends on the version of pandas being used. 
    If the pandas version is 1.x or higher, it uses the default behavior of `pd.to_datetime`.
    For earlier versions, it uses the "mixed" format for conversion, while still handling errors 
    by coercing invalid values to NaT (Not a Time).

    Parameters:
    series (pd.Series): A pandas Series containing date/time information to be converted.

    Returns:
    pd.Series: A pandas Series with the elements converted to datetime objects, 
               or NaT for invalid entries.

    Raises:
    ValueError: If the input is not a pandas Series.
    """
    if is_pandas_1():
        return pd.to_datetime(series, errors="coerce")
    return pd.to_datetime(series, format="mixed", errors="coerce")


@describe_date_1d.register
@series_hashable
@series_handle_nulls
def pandas_describe_date_1d(
    config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """Describe a date series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """
    og_series = series.dropna()
    series = to_datetime(og_series)
    invalid_values = og_series[series.isna()]

    series = series.dropna()

    if summary["value_counts_without_nan"].empty:
        values = series.values
        summary.update(
            {
                "min": pd.NaT,
                "max": pd.NaT,
                "range": 0,
            }
        )
    else:
        summary.update(
            {
                "min": pd.Timestamp.to_pydatetime(series.min()),
                "max": pd.Timestamp.to_pydatetime(series.max()),
            }
        )

        summary["range"] = summary["max"] - summary["min"]

        values = series.values.astype(np.int64) // 10**9

    if config.vars.num.chi_squared_threshold > 0.0:
        summary["chi_squared"] = chi_square(values)

    summary.update(histogram_compute(config, values, series.nunique()))
    summary.update(
        {
            "invalid_dates": invalid_values.nunique(),
            "n_invalid_dates": len(invalid_values),
            "p_invalid_dates": len(invalid_values) / summary["n"],
        }
    )
    return config, values, summary
