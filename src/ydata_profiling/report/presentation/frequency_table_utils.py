from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd


def _frequency_table(
    freqtable: pd.Series, n: int, max_number_to_print: int
) -> List[Dict[str, Any]]:
    """freqtable: pd.Series, n: int, max_number_to_print: int
) -> List[Dict[str, Any]]:
    """
    Generates a frequency table summary from a given frequency series.

    This function computes a summary of the frequency distribution, including 
    the counts, percentages, and widths of the specified number of top labels, 
    as well as additional entries for other values and missing values if applicable.

    Parameters:
    freqtable (pd.Series): A pandas Series containing frequency counts for each category.
    n (int): The total number of observations being analyzed.
    max_number_to_print (int): The maximum number of top categories to include in the output.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains:
        - 'label': The name of the category or a descriptor (e.g., "Other values", "(Missing)").
        - 'width': The relative width of the bar representing this category in a visualization (scaled from 0 to 1).
        - 'count': The absolute count of observations for this category.
        - 'percentage': The percentage of the total observations represented by this category.
        - 'n': The total number of observations (n).
        - 'extra_class': A string for additional CSS class names for styling purposes (e.g., "other" or "missing").

    Returns an empty list if the frequency table is empty or if the maximum frequency is zero.

    Note:
    - The function adjusts `max_number_to_print` if it exceeds the total number of categories.
    - Frequencies for categories beyond the top `max_number_to_print` are aggregated into "Other values".
    - Missing values are included as a separate category if applicable.
    """
    # TODO: replace '' by '(Empty)' ?

    if max_number_to_print > n:
        max_number_to_print = n

    if max_number_to_print < len(freqtable):
        freq_other = np.sum(freqtable.iloc[max_number_to_print:])
        min_freq = freqtable.values[max_number_to_print]
    else:
        freq_other = 0
        min_freq = 0

    freq_missing = n - np.sum(freqtable)
    # No values
    if len(freqtable) == 0:
        return []

    max_freq = max(freqtable.values[0], freq_other, freq_missing)

    # TODO: Correctly sort missing and other
    # No values
    if max_freq == 0:
        return []

    rows = []
    for label, freq in freqtable.iloc[0:max_number_to_print].items():
        rows.append(
            {
                "label": label,
                "width": freq / max_freq,
                "count": freq,
                "percentage": float(freq) / n,
                "n": n,
                "extra_class": "",
            }
        )

    if freq_other > min_freq:
        other_count = str(freqtable.count() - max_number_to_print)
        rows.append(
            {
                "label": f"Other values ({other_count})",
                "width": freq_other / max_freq,
                "count": freq_other,
                # Hack for tables with combined...
                "percentage": min(float(freq_other) / n, 1.0),
                "n": n,
                "extra_class": "other",
            }
        )

    if freq_missing > min_freq:
        rows.append(
            {
                "label": "(Missing)",
                "width": freq_missing / max_freq,
                "count": freq_missing,
                "percentage": float(freq_missing) / n,
                "n": n,
                "extra_class": "missing",
            }
        )

    return rows


def freq_table(
    freqtable: Union[pd.Series, List[pd.Series]],
    n: Union[int, List[int]],
    max_number_to_print: int,
) -> Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
    """Render the rows for a frequency table (value, count).

    Args:
      freqtable: The frequency table.
      n: The total number of values.
      max_number_to_print: The maximum number of observations to print.

    Returns:
        The rows of the frequency table.
    """

    if isinstance(freqtable, list) and isinstance(n, list):
        return [
            _frequency_table(v, n2, max_number_to_print) for v, n2 in zip(freqtable, n)
        ]
    else:
        return [_frequency_table(freqtable, n, max_number_to_print)]  # type: ignore


def _extreme_obs_table(
    freqtable: pd.Series, number_to_print: int, n: int
) -> List[Dict[str, Any]]:
    """freqtable: pd.Series, number_to_print: int, n: int
) -> List[Dict[str, Any]]:
    """
    Generate a table of extreme observations from a frequency table.

    This function takes a frequency table (as a Pandas Series) and produces
    a list of dictionaries containing details of the top observations based
    on their frequency. Each dictionary in the list includes the label, width,
    count, and percentage of the observations relative to the total count.

    Parameters:
        freqtable (pd.Series): A Pandas Series representing the frequency table
            where the index is the labels and the values are the counts.
        number_to_print (int): The number of top occurrences to include in the 
            output table.
        n (int): The total count of observations used to calculate percentages.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing an
            extreme observation with the following keys:
            - 'label': The label of the observation.
            - 'width': The width of the observation, scaled relative to the 
              maximum frequency (0 if max frequency is 0).
            - 'count': The count of occurrences of the observation.
            - 'percentage': The proportion of the total count that this 
              observation represents.
            - 'extra_class': A placeholder for any additional class information
              (currently set as an empty string).
            - 'n': The total number of observations used for percentage calculation.
    """
    obs_to_print = freqtable.iloc[:number_to_print]
    max_freq = obs_to_print.max()

    rows = [
        {
            "label": label,
            "width": freq / max_freq if max_freq != 0 else 0,
            "count": freq,
            "percentage": float(freq) / n,
            "extra_class": "",
            "n": n,
        }
        for label, freq in obs_to_print.items()
    ]

    return rows


def extreme_obs_table(
    freqtable: Union[pd.Series, List[pd.Series]],
    number_to_print: int,
    n: Union[int, List[int]],
) -> List[List[Dict[str, Any]]]:
    """Similar to the frequency table, for extreme observations.

    Args:
      freqtable: The (sorted) frequency table.
      number_to_print: The number of observations to print.
      n: The total number of observations.

    Returns:
        The HTML rendering of the extreme observation table.
    """
    if isinstance(freqtable, list) and isinstance(n, list):
        return [
            _extreme_obs_table(v, number_to_print, n1) for v, n1 in zip(freqtable, n)
        ]

    return [_extreme_obs_table(freqtable, number_to_print, n)]  # type: ignore
