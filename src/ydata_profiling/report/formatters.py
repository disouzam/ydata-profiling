"""Formatters are mappings from object(s) to a string."""
import decimal
import math
import re
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from markupsafe import escape


def list_args(func: Callable) -> Callable:
    """Extend the function to allow taking a list as the first argument, and apply the function on each of the elements.

    Args:
        func: the function to extend

    Returns:
        The extended function
    """

    def inner(arg: Any, *args: Any, **kwargs: Any) -> Any:
        """
    Applies a function to the given argument(s). If the argument is a list,
    the function is applied to each element in the list. Otherwise, the function 
    is applied directly to the argument.

    Parameters:
    arg (Any): The input argument which can be a single value or a list of values.
    *args (Any): Additional positional arguments to be passed to the function.
    **kwargs (Any): Additional keyword arguments to be passed to the function.

    Returns:
    Any: A list of results if the input argument is a list; otherwise, 
         returns the result of applying the function to the input argument.
    """
        if isinstance(arg, list):
            return [func(v, *args, **kwargs) for v in arg]

        return func(arg, *args, **kwargs)

    return inner


@list_args
def fmt_color(text: str, color: str) -> str:
    """Format a string in a certain color (`<span>`).

    Args:
      text: The text to format.
      color: Any valid CSS color.

    Returns:
        A `<span>` that contains the colored text.
    """
    return f'<span style="color:{color}">{text}</span>'


@list_args
def fmt_class(text: str, cls: str) -> str:
    """Format a string in a certain class (`<span>`).

    Args:
      text: The text to format.
      cls: The name of the class.

    Returns:
        A `<span>` with a class added.
    """
    return f'<span class="{cls}">{text}</span>'


@list_args
def fmt_bytesize(num: float, suffix: str = "B") -> str:
    """Change a number of bytes in a human-readable format.

    Args:
      num: number to format
      suffix: (Default value = 'B')

    Returns:
      The value formatted in human readable format (e.g. KiB).
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


@list_args
def fmt_percent(value: float, edge_cases: bool = True) -> str:
    """Format a ratio as a percentage.

    Args:
        edge_cases: Check for edge cases?
        value: The ratio.

    Returns:
        The percentage with 1 point precision.
    """
    if edge_cases and round(value, 3) == 0 and value > 0:
        return "< 0.1%"
    if edge_cases and round(value, 3) == 1 and value < 1:
        return "> 99.9%"

    return f"{value*100:2.1f}%"


@list_args
def fmt_timespan(num_seconds: Any, detailed: bool = False, max_units: int = 3) -> str:
    """
    Format a duration specified in seconds into a human-readable string.

    This function takes a time duration given in seconds and converts it into a more understandable format 
    using appropriate units such as seconds, minutes, hours, etc. It can provide a detailed output or a shorter 
    version depending on the parameters provided.

    Args:
        num_seconds (Any): The time duration to be formatted. This can be an integer, float, or a timedelta object.
        detailed (bool, optional): If set to True, the output will include smaller time units (e.g., seconds and milliseconds). 
                                   If False, only the largest relevant units will be included. Defaults to False.
        max_units (int, optional): The maximum number of different units to include in the output. 
                                   This parameter only applies when 'detailed' is False. Defaults to 3.

    Returns:
        str: A human-readable string representing the formatted time duration.

    Example:
        >>> fmt_timespan(3661)
        '1 hour and 1 minute'
        >>> fmt_timespan(59)
        '59 seconds'
        >>> fmt_timespan(120, detailed=True)
        '2 minutes'
    
    Note:
        The function uses units from nanoseconds to years, and properly handles pluralization.
    """
    # From the `humanfriendly` module (without additional dependency)
    # https://github.com/xolox/python-humanfriendly/
    # Author: Peter Odding <peter@peterodding.com>
    # URL: https://humanfriendly.readthedocs.io

    time_units: List[Dict[str, Any]] = [
        {
            "divider": 1e-9,
            "singular": "nanosecond",
            "plural": "nanoseconds",
            "abbreviations": ["ns"],
        },
        {
            "divider": 1e-6,
            "singular": "microsecond",
            "plural": "microseconds",
            "abbreviations": ["us"],
        },
        {
            "divider": 1e-3,
            "singular": "millisecond",
            "plural": "milliseconds",
            "abbreviations": ["ms"],
        },
        {
            "divider": 1,
            "singular": "second",
            "plural": "seconds",
            "abbreviations": ["s", "sec", "secs"],
        },
        {
            "divider": 60,
            "singular": "minute",
            "plural": "minutes",
            "abbreviations": ["m", "min", "mins"],
        },
        {
            "divider": 60 * 60,
            "singular": "hour",
            "plural": "hours",
            "abbreviations": ["h"],
        },
        {
            "divider": 60 * 60 * 24,
            "singular": "day",
            "plural": "days",
            "abbreviations": ["d"],
        },
        {
            "divider": 60 * 60 * 24 * 7,
            "singular": "week",
            "plural": "weeks",
            "abbreviations": ["w"],
        },
        {
            "divider": 60 * 60 * 24 * 7 * 52,
            "singular": "year",
            "plural": "years",
            "abbreviations": ["y"],
        },
    ]

    def round_number(count: Any, keep_width: bool = False) -> str:
        text = f"{float(count):.2f}"
        if not keep_width:
            text = re.sub("0+$", "", text)
            text = re.sub(r"\.$", "", text)
        return text

    def coerce_seconds(value: Union[timedelta, int, float]) -> float:
        if isinstance(value, timedelta):
            return value.total_seconds()
        return float(value)

    def concatenate(items: List[str]) -> str:
        items = list(items)
        if len(items) > 1:
            return ", ".join(items[:-1]) + " and " + items[-1]
        elif items:
            return items[0]
        else:
            return ""

    def pluralize(count: Any, singular: str, plural: Optional[str] = None) -> str:
        if not plural:
            plural = singular + "s"
        return f"{count} {singular if math.floor(float(count)) == 1 else plural}"

    num_seconds = coerce_seconds(num_seconds)
    if num_seconds < 60 and not detailed:
        # Fast path.
        return pluralize(round_number(num_seconds), "second")
    else:
        # Slow path.
        result = []
        num_seconds = decimal.Decimal(str(num_seconds))
        relevant_units = list(reversed(time_units[0 if detailed else 3 :]))
        for unit in relevant_units:
            # Extract the unit count from the remaining time.
            divider = decimal.Decimal(str(unit["divider"]))
            count = num_seconds / divider
            num_seconds %= divider
            # Round the unit count appropriately.
            if unit != relevant_units[-1]:
                # Integer rounding for all but the smallest unit.
                count = int(count)
            else:
                # Floating point rounding for the smallest unit.
                count = round_number(count)
            # Only include relevant units in the result.
            if count not in (0, "0"):
                result.append(pluralize(count, unit["singular"], unit["plural"]))
        if len(result) == 1:
            # A single count/unit combination.
            return result[0]
        else:
            if not detailed:
                # Remove `insignificant' data from the formatted timespan.
                result = result[:max_units]
            # Format the timespan in a readable way.
            return concatenate(result)


@list_args
def fmt_timespan_timedelta(
    delta: Any, detailed: bool = False, max_units: int = 3, precision: int = 10
) -> str:
    """delta: Any, detailed: bool = False, max_units: int = 3, precision: int = 10
) -> str:
    """
    Formats a given time delta (pd.Timedelta) or numeric value into a human-readable string representation.

    Parameters:
    ----------
    delta : Any
        The time delta value, which can be a pandas Timedelta object or a numeric value (e.g., int or float).
    detailed : bool, optional
        If True, the function provides a more detailed format for the output. Default is False.
    max_units : int, optional
        The maximum number of time units to include in the output. Default is 3.
    precision : int, optional
        The number of decimal places to include for numeric values. Default is 10.

    Returns:
    -------
    str
        A string representation of the time delta formatted according to the specified parameters. 
        If the input is not a pd.Timedelta, it returns a formatted numeric string.
    
    Notes:
    -----
    The function first checks if the input 'delta' is a pd.Timedelta instance. If so, it calculates the total
    number of seconds and formats it accordingly. If not, it falls back to formatting the numeric value using
    the specified precision.
    """
    if isinstance(delta, pd.Timedelta):
        num_seconds = delta.total_seconds()
        if delta.microseconds > 0:
            num_seconds += delta.microseconds * 1e-6
        if delta.nanoseconds > 0:
            num_seconds += delta.nanoseconds * 1e-9
        return fmt_timespan(num_seconds, detailed, max_units)
    else:
        return fmt_numeric(delta, precision)


@list_args
def fmt_numeric(value: float, precision: int = 10) -> str:
    """Format any numeric value.

    Args:
        value: The numeric value to format.
        precision: The numeric precision

    Returns:
        The numeric value with the given precision.
    """
    fmtted = f"{{:.{precision}g}}".format(value)
    for v in ["e+", "e-"]:
        if v in fmtted:
            sign = "-" if v in "e-" else ""
            fmtted = fmtted.replace(v, " × 10<sup>") + "</sup>"
            fmtted = fmtted.replace("<sup>0", "<sup>")
            fmtted = fmtted.replace("<sup>", f"<sup>{sign}")

    return fmtted


@list_args
def fmt_number(value: int) -> str:
    """Format any numeric value.

    Args:
        value: The numeric value to format.

    Returns:
        The numeric value with the given precision.
    """
    return f"{value:n}"


@list_args
def fmt_array(value: np.ndarray, threshold: Any = np.nan) -> str:
    """Format numpy arrays.

    Args:
        value: Array to format.
        threshold: Threshold at which to show ellipsis

    Returns:
        The string representation of the numpy array.
    """
    with np.printoptions(threshold=3, edgeitems=threshold):
        return_value = str(value)

    return return_value


@list_args
def fmt(value: Any) -> str:
    """Format any value.

    Args:
        value: The value to format.

    Returns:
        The numeric formatting if the value is float or int, the string formatting otherwise.
    """
    if type(value) in [float, int]:
        return fmt_numeric(value)
    else:
        return str(escape(value))


@list_args
def fmt_monotonic(value: int) -> str:
    """
    Format a monotonicity descriptor based on the given integer value.

    The function translates an integer input into a descriptive string
    that indicates the type of monotonicity represented by the value. 
    The mapping is as follows:
    
    - 2: "Strictly increasing"
    - 1: "Increasing"
    - 0: "Not monotonic"
    - -1: "Decreasing"
    - -2: "Strictly decreasing"

    Parameters:
    value (int): An integer representing the type of monotonicity. It must 
                 be in the range of -2 to 2.

    Returns:
    str: A string description of the monotonicity corresponding to the input value.

    Raises:
    ValueError: If the input value is not an integer within the range of -2 to 2.
    """
    if value == 2:
        return "Strictly increasing"
    elif value == 1:
        return "Increasing"
    elif value == 0:
        return "Not monotonic"
    elif value == -1:
        return "Decreasing"
    elif value == -2:
        return "Strictly decreasing"
    else:
        raise ValueError("Value should be integer ranging from -2 to 2.")"""
    if value == 2:
        return "Strictly increasing"
    elif value == 1:
        return "Increasing"
    elif value == 0:
        return "Not monotonic"
    elif value == -1:
        return "Decreasing"
    elif value == -2:
        return "Strictly decreasing"
    else:
        raise ValueError("Value should be integer ranging from -2 to 2.")


def help(title: str, url: Optional[str] = None) -> str:
    """Creat help badge

    Args:
        title: help text
        url: url to open in new tab (optional)

    Returns:
        HTML formatted help badge
    """
    if url is not None:
        return f'<a href="{url}"><span class="badge text-bg-secondary float-end" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="{title}">?</span></a>'
    else:
        return f'<span class="badge text-bg-secondary float-end" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="{title}">?</span>'


@list_args
def fmt_badge(value: str) -> str:
    """
    Format a string by replacing occurrences of numbers enclosed in parentheses with HTML 
    span elements styled as badges.

    This function searches for patterns in the input string that match the 
    regex pattern `(\d+)` contained within parentheses. Each match is replaced 
    with a span element that has the class "badge text-bg-secondary align-text-top" 
    and contains the matched number.

    Args:
        value (str): The input string that may contain numbers in parentheses.

    Returns:
        str: The formatted string with numbers in parentheses replaced by styled 
        badge elements.
    
    Example:
        >>> fmt_badge("This is a test (5) and another test (10).")
        'This is a test <span class="badge text-bg-secondary align-text-top">5</span> and another test <span class="badge text-bg-secondary align-text-top">10</span>.'
    """
    return re.sub(
        r"\((\d+)\)",
        r'<span class="badge text-bg-secondary align-text-top">\1</span>',
        value,
    )
