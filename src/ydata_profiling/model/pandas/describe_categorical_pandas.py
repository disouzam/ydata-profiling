import contextlib
import string
from collections import Counter
from typing import List, Tuple

import numpy as np
import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.pandas.imbalance_pandas import column_imbalance_score
from ydata_profiling.model.pandas.utils_pandas import weighted_median
from ydata_profiling.model.summary_algorithms import (
    chi_square,
    describe_categorical_1d,
    histogram_compute,
    series_handle_nulls,
    series_hashable,
)


def get_character_counts_vc(vc: pd.Series) -> pd.Series:
    """
    Count the occurrences of each character in a pandas Series.

    This function takes a pandas Series where the index represents some categories 
    and the values are strings. It will count the occurrences of each character 
    in the non-empty strings of the Series, returning a new Series with characters 
    as the index and their respective counts as values. The results are sorted 
    in descending order of occurrences.

    Parameters:
    vc (pd.Series): A pandas Series where the index represents categories 
                    and the values are strings to be processed.

    Returns:
    pd.Series: A Series containing characters as the index and their counts 
                as values, sorted in descending order. Empty strings are excluded 
                from the results. If there are no characters present, an empty 
                Series will be returned.

    Example:
    >>> s = pd.Series(['apple', 'banana', 'apple', ''])
    >>> get_character_counts_vc(s)
    a    5
    p    2
    b    2
    n    2
    l    1
    ```"""
    series = pd.Series(vc.index, index=vc)
    characters = series[series != ""].apply(list)
    characters = characters.explode()

    counts = pd.Series(characters.index, index=characters).dropna()
    if len(counts) > 0:
        counts = counts.groupby(level=0, sort=False).sum()
        counts = counts.sort_values(ascending=False)
        # FIXME: correct in split, below should be zero: print(counts.loc[''])
        counts = counts[counts.index.str.len() > 0]
    return counts


def get_character_counts(series: pd.Series) -> Counter:
    """Function to return the character counts

    Args:
        series: the Series to process

    Returns:
        A dict with character counts
    """
    return Counter(series.str.cat())


def counter_to_series(counter: Counter) -> pd.Series:
    """```python
def counter_to_series(counter: Counter) -> pd.Series:
    """
    Convert a Counter object to a Pandas Series.

    This function takes a Counter object as input and returns a Pandas Series
    where the index consists of the unique items from the Counter and the 
    values correspond to their counts. If the Counter is empty, an empty Series
    is returned.

    Parameters:
    counter (Counter): A Counter object containing elements as keys and their counts as values.

    Returns:
    pd.Series: A Pandas Series with the items from the Counter as the index
               and their corresponding counts as the values. If the Counter is empty,
               an empty Series with dtype=object is returned.

    Examples:
    >>> from collections import Counter
    >>> counter = Counter(['a', 'b', 'a', 'c'])
    >>> counter_to_series(counter)
    a    2
    b    1
    c    1
    dtype: int64

    >>> empty_counter = Counter()
    >>> counter_to_series(empty_counter)
    Series([], dtype=object)
    """
    if not counter:
        return pd.Series([], dtype=object)

    counter_as_tuples = counter.most_common()
    items, counts = zip(*counter_as_tuples)
    return pd.Series(counts, index=items)


def unicode_summary_vc(vc: pd.Series) -> dict:
    """
    Generate a summary of Unicode character distributions for a given pandas Series.

    This function takes a Series of Unicode characters and calculates various statistics 
    related to their Unicode properties. It provides detailed information on distinct 
    characters, their counts, categories, blocks, and scripts.

    Args:
        vc (pd.Series): A pandas Series containing Unicode characters.

    Returns:
        dict: A dictionary summarizing the following information:
            - n_characters_distinct (int): The number of distinct characters.
            - n_characters (int): The total number of characters.
            - character_counts (pd.Series): A Series with counts of each character.
            - category_alias_values (dict): A dictionary mapping characters to their long category names.
            - block_alias_values (dict): A dictionary mapping characters to their block abbreviations.
            - block_alias_counts (pd.Series): Series counting characters by their block aliases.
            - n_block_alias (int): The number of unique block aliases.
            - block_alias_char_counts (dict): A dictionary of character counts categorized by block aliases.
            - script_counts (pd.Series): Series counting characters by their scripts.
            - n_scripts (int): The number of unique scripts.
            - script_char_counts (dict): A dictionary of character counts categorized by scripts.
            - category_alias_counts (pd.Series): Series counting characters by their category aliases.
            - n_category (int): The number of unique category aliases.
            - category_alias_char_counts (dict): A dictionary of character counts categorized by category aliases.

    Notes:
        If the `tangled_up_in_unicode` package is not available, the function falls back to using
        built-in Unicode data and provides basic information through a character handler.
    """
    try:
        from tangled_up_in_unicode import (  # type: ignore
            block,
            block_abbr,
            category,
            category_long,
            script,
        )
    except ImportError:
        from unicodedata import category as _category  # pylint: disable=import-error

        category = _category  # type: ignore
        char_handler = lambda char: "(unknown)"  # noqa: E731
        block = char_handler
        block_abbr = char_handler
        category_long = char_handler
        script = char_handler

    # Unicode Character Summaries (category and script name)
    character_counts = get_character_counts_vc(vc)

    character_counts_series = character_counts
    summary = {
        "n_characters_distinct": len(character_counts_series),
        "n_characters": np.sum(character_counts_series.values),
        "character_counts": character_counts_series,
    }

    char_to_block = {key: block(key) for key in character_counts.keys()}
    char_to_category_short = {key: category(key) for key in character_counts.keys()}
    char_to_script = {key: script(key) for key in character_counts.keys()}

    summary.update(
        {
            "category_alias_values": {
                key: category_long(value)
                for key, value in char_to_category_short.items()
            },
            "block_alias_values": {
                key: block_abbr(value) for key, value in char_to_block.items()
            },
        }
    )

    # Retrieve original distribution
    block_alias_counts: Counter = Counter()
    per_block_char_counts: dict = {
        k: Counter() for k in summary["block_alias_values"].values()
    }
    for char, n_char in character_counts.items():
        block_name = summary["block_alias_values"][char]
        block_alias_counts[block_name] += n_char
        per_block_char_counts[block_name][char] = n_char
    summary["block_alias_counts"] = counter_to_series(block_alias_counts)
    summary["n_block_alias"] = len(summary["block_alias_counts"])
    summary["block_alias_char_counts"] = {
        k: counter_to_series(v) for k, v in per_block_char_counts.items()
    }

    script_counts: Counter = Counter()
    per_script_char_counts: dict = {k: Counter() for k in char_to_script.values()}
    for char, n_char in character_counts.items():
        script_name = char_to_script[char]
        script_counts[script_name] += n_char
        per_script_char_counts[script_name][char] = n_char
    summary["script_counts"] = counter_to_series(script_counts)
    summary["n_scripts"] = len(summary["script_counts"])
    summary["script_char_counts"] = {
        k: counter_to_series(v) for k, v in per_script_char_counts.items()
    }

    category_alias_counts: Counter = Counter()
    per_category_alias_char_counts: dict = {
        k: Counter() for k in summary["category_alias_values"].values()
    }
    for char, n_char in character_counts.items():
        category_alias_name = summary["category_alias_values"][char]
        category_alias_counts[category_alias_name] += n_char
        per_category_alias_char_counts[category_alias_name][char] += n_char
    summary["category_alias_counts"] = counter_to_series(category_alias_counts)
    if len(summary["category_alias_counts"]) > 0:
        summary["category_alias_counts"].index = summary[
            "category_alias_counts"
        ].index.str.replace("_", " ")
    summary["n_category"] = len(summary["category_alias_counts"])
    summary["category_alias_char_counts"] = {
        k: counter_to_series(v) for k, v in per_category_alias_char_counts.items()
    }

    with contextlib.suppress(AttributeError):
        summary["category_alias_counts"].index = summary[
            "category_alias_counts"
        ].index.str.replace("_", " ")

    return summary


def word_summary_vc(vc: pd.Series, stop_words: List[str] = []) -> dict:
    """Count the number of occurrences of each individual word across
    all lines of the data Series, then sort from the word with the most
    occurrences to the word with the least occurrences. If a list of
    stop words is given, they will be ignored.

    Args:
        vc: Series containing all unique categories as index and their
            frequency as value. Sorted from the most frequent down.
        stop_words: List of stop words to ignore, empty by default.

    Returns:
        A dict containing the results as a Series with unique words as
        index and the computed frequency as value
    """
    # TODO: configurable lowercase/punctuation etc.
    # TODO: remove punctuation in words

    series = pd.Series(vc.index, index=vc)
    word_lists = series.str.lower().str.split()
    words = word_lists.explode().str.strip(string.punctuation + string.whitespace)
    word_counts = pd.Series(words.index, index=words)
    # fix for pandas 1.0.5
    word_counts = word_counts[word_counts.index.notnull()]
    word_counts = word_counts.groupby(level=0, sort=False).sum()
    word_counts = word_counts.sort_values(ascending=False)

    # Remove stop words
    if len(stop_words) > 0:
        stop_words = [x.lower() for x in stop_words]
        word_counts = word_counts.loc[~word_counts.index.isin(stop_words)]

    return {"word_counts": word_counts} if not word_counts.empty else {}


def length_summary_vc(vc: pd.Series) -> dict:
    """
    Generate a summary of the lengths of the values in a pandas Series.

    This function takes a pandas Series as input and calculates statistics regarding 
    the lengths of the string representations of its values. It returns a dictionary 
    containing the maximum length, mean length, median length, minimum length, 
    and a histogram of the lengths.

    Parameters:
    vc (pd.Series): A pandas Series containing the values for which string lengths 
                    are to be analyzed.

    Returns:
    dict: A dictionary containing the following key-value pairs:
        - "max_length": The maximum length of the string representations.
        - "mean_length": The mean length of the string representations (weighted average).
        - "median_length": The median length of the string representations (weighted).
        - "min_length": The minimum length of the string representations.
        - "length_histogram": A pandas Series representing the frequency of each length.

    Notes:
    - The function handles empty input gracefully by returning NaN for mean and median 
      lengths if no values are present in the input Series.
    - The `weighted_median` function is expected to be defined elsewhere in the code.

    Raises:
    ValueError: If the input is not a pandas Series.
    """
    series = pd.Series(vc.index, index=vc)
    length = series.str.len()
    length_counts = pd.Series(length.index, index=length)
    length_counts = length_counts.groupby(level=0, sort=False).sum()
    length_counts = length_counts.sort_values(ascending=False)

    summary = {
        "max_length": np.max(length_counts.index),
        "mean_length": np.average(length_counts.index, weights=length_counts.values)
        if not length_counts.empty
        else np.nan,
        "median_length": weighted_median(
            length_counts.index.values, weights=length_counts.values
        )
        if not length_counts.empty
        else np.nan,
        "min_length": np.min(length_counts.index),
        "length_histogram": length_counts,
    }

    return summary


@describe_categorical_1d.register
@series_hashable
@series_handle_nulls
def pandas_describe_categorical_1d(
    config: Settings, series: pd.Series, summary: dict
) -> Tuple[Settings, pd.Series, dict]:
    """Describe a categorical series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    # Make sure we deal with strings (Issue #100)
    series = series.astype(str)

    # Only run if at least 1 non-missing value
    value_counts = summary["value_counts_without_nan"]
    value_counts.index = value_counts.index.astype(str)

    summary["imbalance"] = column_imbalance_score(value_counts, len(value_counts))

    redact = config.vars.cat.redact
    if not redact:
        summary.update({"first_rows": series.head(5)})

    chi_squared_threshold = config.vars.num.chi_squared_threshold
    if chi_squared_threshold > 0.0:
        summary["chi_squared"] = chi_square(histogram=value_counts.values)

    if config.vars.cat.length:
        summary.update(length_summary_vc(value_counts))
        summary.update(
            histogram_compute(
                config,
                summary["length_histogram"].index.values,
                len(summary["length_histogram"]),
                name="histogram_length",
                weights=summary["length_histogram"].values,
            )
        )

    if config.vars.cat.characters:
        summary.update(unicode_summary_vc(value_counts))

    if config.vars.cat.words:
        summary.update(word_summary_vc(value_counts, config.vars.cat.stop_words))

    return config, series, summary
