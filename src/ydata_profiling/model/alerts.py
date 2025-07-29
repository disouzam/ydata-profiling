"""Logic for alerting the user on possibly problematic patterns in the data (e.g. high number of zeros , constant
values, high correlations)."""

from enum import Enum, auto, unique
from typing import Dict, List, Optional, Set

import numpy as np
import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.correlations import perform_check_correlation
from ydata_profiling.utils.styles import get_alert_styles


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


@unique
class AlertType(Enum):
    """Alert types"""

    CONSTANT = auto()
    """This variable has a constant value."""

    ZEROS = auto()
    """This variable contains zeros."""

    HIGH_CORRELATION = auto()
    """This variable is highly correlated."""

    HIGH_CARDINALITY = auto()
    """This variable has a high cardinality."""

    UNSUPPORTED = auto()
    """This variable is unsupported."""

    DUPLICATES = auto()
    """This variable contains duplicates."""

    SKEWED = auto()
    """This variable is highly skewed."""

    IMBALANCE = auto()
    """This variable is imbalanced."""

    MISSING = auto()
    """This variable contains missing values."""

    INFINITE = auto()
    """This variable contains infinite values."""

    TYPE_DATE = auto()
    """This variable is likely a datetime, but treated as categorical."""

    UNIQUE = auto()
    """This variable has unique values."""

    CONSTANT_LENGTH = auto()
    """This variable has a constant length."""

    REJECTED = auto()
    """Variables are rejected if we do not want to consider them for further analysis."""

    UNIFORM = auto()
    """The variable is uniformly distributed."""

    NON_STATIONARY = auto()
    """The variable is a non-stationary series."""

    SEASONAL = auto()
    """The variable is a seasonal time series."""

    EMPTY = auto()
    """The DataFrame is empty."""


class Alert:
    """An alert object (type, values, column)."""

    _anchor_id: Optional[str] = None

    def __init__(
        self,
        alert_type: AlertType,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        fields: Optional[Set] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        self.fields = fields or set()
        self.alert_type = alert_type
        self.values = values or {}
        self.column_name = column_name
        self._is_empty = is_empty
        self._styles = get_alert_styles()

    @property
    def alert_type_name(self) -> str:
        """def alert_type_name(self) -> str:
    """
    Get the formatted name of the alert type.

    This property retrieves the name of the alert type, replaces underscores 
    with spaces, and capitalizes the first letter of the resulting string.

    Returns:
        str: A capitalized string representing the alert type name 
              with underscores replaced by spaces.
    """
    return self.alert_type.name.replace("_", " ").capitalize()"""
        return self.alert_type.name.replace("_", " ").capitalize()

    @property
    def anchor_id(self) -> Optional[str]:
        """def anchor_id(self) -> Optional[str]:
    """
    Gets the anchor ID for the current instance.

    If the anchor ID has not been previously set, it generates a new anchor ID
    based on the hash of the column name. The anchor ID is cached for future
    accesses.

    Returns:
        Optional[str]: The anchor ID as a string, or None if it cannot be generated.
    """
    if self._anchor_id is None:
        self._anchor_id = str(hash(self.column_name))
    return self._anchor_id"""
        if self._anchor_id is None:
            self._anchor_id = str(hash(self.column_name))
        return self._anchor_id

    def fmt(self) -> str:
        """
    Renders a badge HTML element with the appropriate styling and tooltip based on the alert type.

    The function determines the background style for the badge based on the alert type and, if the 
    alert type is HIGH_CORRELATION, includes additional tooltip information that indicates the 
    correlation and number of associated fields.

    Returns:
        str: An HTML string representing a badge with the alert type name and optional tooltip.
        
    Attributes:
        self.alert_type (AlertType): The type of alert, which influences the badge style and tooltip.
        self.alert_type_name (str): The display name of the alert type to be shown on the badge.
        self.values (dict or None): Optional additional data that may include correlation information
                                    when the alert type is HIGH_CORRELATION.
    """
        # TODO: render in template
        style = self._styles.get(self.alert_type.name.lower(), "secondary")
        hint = ""

        if self.alert_type == AlertType.HIGH_CORRELATION and self.values is not None:
            num = len(self.values["fields"])
            title = ", ".join(self.values["fields"])
            corr = self.values["corr"]
            hint = f'data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="This variable has a high {corr} correlation with {num} fields: {title}"'

        return (
            f'<span class="badge text-bg-{style}" {hint}>{self.alert_type_name}</span>'
        )

    def _get_description(self) -> str:
        """Return a human level description of the alert.

        Returns:
            str: alert description
        """
        alert_type = self.alert_type.name
        column = self.column_name
        return f"[{alert_type}] alert on column {column}"

    def __repr__(self):
        """```python
def __repr__(self):
    """
    Return a string representation of the object.

    This method calls the `_get_description()` method to obtain a descriptive
    string representing the current state of the object. It is intended to provide
    an informative output for debugging and logging purposes.

    Returns:
        str: A string description of the object.
    """
    return self._get_description()"""
        return self._get_description()


class ConstantLengthAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.CONSTANT_LENGTH,
            values=values,
            column_name=column_name,
            fields={"composition_min_length", "composition_max_length"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] has a constant length"


class ConstantAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.CONSTANT,
            values=values,
            column_name=column_name,
            fields={"n_distinct"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] has a constant value"


class DuplicatesAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.DUPLICATES,
            values=values,
            column_name=column_name,
            fields={"n_duplicates"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            return f"Dataset has {self.values['n_duplicates']} ({fmt_percent(self.values['p_duplicates'])}) duplicate rows"
        else:
            return "Dataset has duplicated values"


class EmptyAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.EMPTY,
            values=values,
            column_name=column_name,
            fields={"n"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return "Dataset is empty"


class HighCardinalityAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.HIGH_CARDINALITY,
            values=values,
            column_name=column_name,
            fields={"n_distinct"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            return f"[{self.column_name}] has {self.values['n_distinct']:} ({fmt_percent(self.values['p_distinct'])}) distinct values"
        else:
            return f"[{self.column_name}] has a high cardinality"


class HighCorrelationAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.HIGH_CORRELATION,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            description = f"[{self.column_name}] is highly {self.values['corr']} correlated with [{self.values['fields'][0]}]"
            if len(self.values["fields"]) > 1:
                description += f" and {len(self.values['fields']) - 1} other fields"
        else:
            return (
                f"[{self.column_name}] has a high correlation with one or more colums"
            )
        return description


class ImbalanceAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.IMBALANCE,
            values=values,
            column_name=column_name,
            fields={"imbalance"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        description = f"[{self.column_name}] is highly imbalanced"
        if self.values is not None:
            return description + f" ({self.values['imbalance']})"
        else:
            return description


class InfiniteAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.INFINITE,
            values=values,
            column_name=column_name,
            fields={"p_infinite", "n_infinite"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            return f"[{self.column_name}] has {self.values['n_infinite']} ({fmt_percent(self.values['p_infinite'])}) infinite values"
        else:
            return f"[{self.column_name}] has infinite values"


class MissingAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.MISSING,
            values=values,
            column_name=column_name,
            fields={"p_missing", "n_missing"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            return f"[{self.column_name}] {self.values['n_missing']} ({fmt_percent(self.values['p_missing'])}) missing values"
        else:
            return f"[{self.column_name}] has missing values"


class NonStationaryAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.NON_STATIONARY,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] is non stationary"


class SeasonalAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.SEASONAL,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] is seasonal"


class SkewedAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.SKEWED,
            values=values,
            column_name=column_name,
            fields={"skewness"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        description = f"[{self.column_name}] is highly skewed"
        if self.values is not None:
            return description + f"(\u03b31 = {self.values['skewness']})"
        else:
            return description


class TypeDateAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.TYPE_DATE,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] only contains datetime values, but is categorical. Consider applying `pd.to_datetime()`"


class UniformAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.UNIFORM,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] is uniformly distributed"


class UniqueAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.UNIQUE,
            values=values,
            column_name=column_name,
            fields={"n_distinct", "p_distinct", "n_unique", "p_unique"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] has unique values"


class UnsupportedAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.UNSUPPORTED,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] is an unsupported type, check if it needs cleaning or further analysis"


class ZerosAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.ZEROS,
            values=values,
            column_name=column_name,
            fields={"n_zeros", "p_zeros"},
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        if self.values is not None:
            return f"[{self.column_name}] has {self.values['n_zeros']} ({fmt_percent(self.values['p_zeros'])}) zeros"
        else:
            return f"[{self.column_name}] has predominantly zeros"


class RejectedAlert(Alert):
    def __init__(
        self,
        values: Optional[Dict] = None,
        column_name: Optional[str] = None,
        is_empty: bool = False,
    ):
        """self,
    values: Optional[Dict] = None,
    column_name: Optional[str] = None,
    is_empty: bool = False,
):
    """
    Initializes an instance of the class with the provided parameters.

    Parameters:
    ----------
    values : Optional[Dict], optional
        A dictionary containing values associated with the instance. Defaults to None.
        
    column_name : Optional[str], optional
        The name of the column associated with the values. Defaults to None.
        
    is_empty : bool, optional
        A flag indicating whether the values are considered empty. Defaults to False.

    This constructor also initializes the superclass with the alert type set to 
    AlertType.REJECTED along with the provided values, column_name, and is_empty 
    parameters.
    """
        super().__init__(
            alert_type=AlertType.REJECTED,
            values=values,
            column_name=column_name,
            is_empty=is_empty,
        )

    def _get_description(self) -> str:
        """
    Generate a description indicating that the specified column was rejected.

    Returns:
        str: A formatted string that includes the name of the column
              indicating its rejection status.
    """
    return f"[{self.column_name}] was rejected"""
        return f"[{self.column_name}] was rejected"


def check_table_alerts(table: dict) -> List[Alert]:
    """Checks the overall dataset for alerts.

    Args:
        table: Overall dataset statistics.

    Returns:
        A list of alerts.
    """
    alerts: List[Alert] = []
    if alert_value(table.get("n_duplicates", np.nan)):
        alerts.append(
            DuplicatesAlert(
                values=table,
            )
        )
    if table["n"] == 0:
        alerts.append(
            EmptyAlert(
                values=table,
            )
        )
    return alerts


def numeric_alerts(config: Settings, summary: dict) -> List[Alert]:
    """
    Generate a list of alerts based on the provided summary statistics and configuration settings.

    This function evaluates the skewness, presence of infinite values, 
    and the occurrence of zeros in the summary. It also checks the p-value 
    of the chi-squared statistic to determine if a uniform alert should be raised.

    Args:
        config (Settings): The configuration settings that define alert thresholds 
                           and parameters.
        summary (dict): A dictionary containing summary statistics which must include 
                        'skewness', 'p_infinite', 'p_zeros', and optionally 
                        'chi_squared'.

    Returns:
        List[Alert]: A list of alerts that were triggered based on the summary statistics.
                      Possible alerts include SkewedAlert, InfiniteAlert, ZerosAlert, 
                      and UniformAlert.
                      
    Raises:
        KeyError: If expected keys are missing in the summary dictionary.
    """
    alerts: List[Alert] = []

    # Skewness
    if skewness_alert(summary["skewness"], config.vars.num.skewness_threshold):
        alerts.append(SkewedAlert(summary))

    # Infinite values
    if alert_value(summary["p_infinite"]):
        alerts.append(InfiniteAlert(summary))

    # Zeros
    if alert_value(summary["p_zeros"]):
        alerts.append(ZerosAlert(summary))

    if (
        "chi_squared" in summary
        and summary["chi_squared"]["pvalue"] > config.vars.num.chi_squared_threshold
    ):
        alerts.append(UniformAlert())

    return alerts


def timeseries_alerts(config: Settings, summary: dict) -> List[Alert]:
    """
    Generates a list of alerts based on the provided configuration 
    and summary of time series data.

    This function checks the summary for characteristics of the time series 
    data and appends appropriate alerts to the list based on the following criteria:
    - If the time series is non-stationary, a NonStationaryAlert is added.
    - If the time series has seasonality, a SeasonalAlert is added.

    Additionally, it retrieves numeric alerts using a separate function.

    Args:
        config (Settings): Configuration settings for generating alerts.
        summary (dict): A dictionary containing summary statistics and attributes
                        about the time series, such as whether it is stationary 
                        or seasonal.

    Returns:
        List[Alert]: A list of Alert objects that represent the generated alerts 
                      based on the time series analysis.
    """
    alerts: List[Alert] = numeric_alerts(config, summary)

    if not summary["stationary"]:
        alerts.append(NonStationaryAlert())

    if summary["seasonal"]:
        alerts.append(SeasonalAlert())

    return alerts


def categorical_alerts(config: Settings, summary: dict) -> List[Alert]:
    """
    Generates a list of alerts based on the categorical data summary and the provided configuration settings.

    This function evaluates various criteria from the statistical summary of categorical data 
    and generates alerts accordingly. The following conditions trigger specific alerts:
    
    - High cardinality: If the number of distinct values exceeds a specified threshold.
    - Chi-squared test: If the p-value for the chi-squared test indicates non-uniformity.
    - Date warning: If there is a warning about date types in the summary.
    - Constant length: If the length of categorical values is constant.
    - Imbalance: If the imbalance metric exceeds a defined threshold.

    Args:
        config (Settings): The configuration settings object that contains thresholds for 
                           various alerts.
        summary (dict): A dictionary containing the statistical summary of the categorical data, 
                        which includes keys like 'n_distinct', 'chi_squared', 'date_warning', 
                        'composition', 'min_length', 'max_length', and 'imbalance'.

    Returns:
        List[Alert]: A list of generated alerts corresponding to the conditions met in the 
                     summary.
    """
    alerts: List[Alert] = []

    # High cardinality
    if summary.get("n_distinct", np.nan) > config.vars.cat.cardinality_threshold:
        alerts.append(HighCardinalityAlert(summary))

    if (
        "chi_squared" in summary
        and summary["chi_squared"]["pvalue"] > config.vars.cat.chi_squared_threshold
    ):
        alerts.append(UniformAlert())

    if summary.get("date_warning"):
        alerts.append(TypeDateAlert())

    # Constant length
    if "composition" in summary and summary["min_length"] == summary["max_length"]:
        alerts.append(ConstantLengthAlert())

    # Imbalance
    if (
        "imbalance" in summary
        and summary["imbalance"] > config.vars.cat.imbalance_threshold
    ):
        alerts.append(ImbalanceAlert(summary))
    return alerts"""
    alerts: List[Alert] = []

    # High cardinality
    if summary.get("n_distinct", np.nan) > config.vars.cat.cardinality_threshold:
        alerts.append(HighCardinalityAlert(summary))

    if (
        "chi_squared" in summary
        and summary["chi_squared"]["pvalue"] > config.vars.cat.chi_squared_threshold
    ):
        alerts.append(UniformAlert())

    if summary.get("date_warning"):
        alerts.append(TypeDateAlert())

    # Constant length
    if "composition" in summary and summary["min_length"] == summary["max_length"]:
        alerts.append(ConstantLengthAlert())

    # Imbalance
    if (
        "imbalance" in summary
        and summary["imbalance"] > config.vars.cat.imbalance_threshold
    ):
        alerts.append(ImbalanceAlert(summary))
    return alerts


def boolean_alerts(config: Settings, summary: dict) -> List[Alert]:
    """
    Generates a list of alerts based on the provided summary and configuration settings.

    Args:
        config (Settings): An object containing configuration settings, including a threshold for imbalance.
        summary (dict): A dictionary containing summary data, which may include the "imbalance" key.

    Returns:
        List[Alert]: A list of generated alerts. An ImbalanceAlert will be added to the list
        if the "imbalance" key is present in the summary and its value exceeds the specified threshold
        in the configuration.

    Example:
        >>> config = Settings(vars={'bool': {'imbalance_threshold': 10}})
        >>> summary = {'imbalance': 15}
        >>> alerts = boolean_alerts(config, summary)
        >>> len(alerts)
        1
    """
    alerts: List[Alert] = []

    if (
        "imbalance" in summary
        and summary["imbalance"] > config.vars.bool.imbalance_threshold
    ):
        alerts.append(ImbalanceAlert())
    return alerts"""
    alerts: List[Alert] = []

    if (
        "imbalance" in summary
        and summary["imbalance"] > config.vars.bool.imbalance_threshold
    ):
        alerts.append(ImbalanceAlert())
    return alerts


def generic_alerts(summary: dict) -> List[Alert]:
    """```python
def generic_alerts(summary: dict) -> List[Alert]:
    """
    Generate a list of alerts based on the provided summary.

    This function analyzes the given summary dictionary to determine if any alerts should be generated.
    Currently, it checks for missing values using the `p_missing` key in the summary. If the alert value 
    for `p_missing` is triggered, a `MissingAlert` instance is added to the alerts list.

    Args:
        summary (dict): A dictionary containing summary data which may include various keys, 
                        with at least a 'p_missing' key to check for missing alerts.

    Returns:
        List[Alert]: A list of generated alerts, which may include instances of 
                      `MissingAlert` if any missing values are detected.
    """
    alerts: List[Alert] = []

    # Missing
    if alert_value(summary["p_missing"]):
        alerts.append(MissingAlert())

    return alerts


def supported_alerts(summary: dict) -> List[Alert]:
    """
    Generate a list of alerts based on the provided summary statistics.

    This function analyzes the summary dictionary to determine the types of alerts 
    that are applicable. It checks for two conditions:
    
    1. If the number of distinct values is equal to the total count, a UniqueAlert 
       is appended to the alerts list.
    2. If there is only one distinct value, a ConstantAlert is created with the 
       summary information and appended to the alerts list.

    Parameters:
    -----------
    summary : dict
        A dictionary containing summary statistics, including keys such as 
        'n_distinct' and 'n'.

    Returns:
    --------
    List[Alert]
        A list of alerts indicating the detected issues based on the summary 
        statistics. The alerts include UniqueAlert and ConstantAlert instances.
    """
    alerts: List[Alert] = []

    if summary.get("n_distinct", np.nan) == summary["n"]:
        alerts.append(UniqueAlert())
    if summary.get("n_distinct", np.nan) == 1:
        alerts.append(ConstantAlert(summary))
    return alerts


def unsupported_alerts() -> List[Alert]:
    """
    Generates a list of unsupported alerts.

    This function returns a list containing instances of unsupported alerts,
    specifically `UnsupportedAlert` and `RejectedAlert`. These alerts represent
    situations where certain conditions are not met, indicating that the user
    should be aware of unsupported actions or data.

    Returns:
        List[Alert]: A list of alert objects, including UnsupportedAlert and RejectedAlert.
    """
    alerts: List[Alert] = [
        UnsupportedAlert(),
        RejectedAlert(),
    ]
    return alerts


def check_variable_alerts(config: Settings, col: str, description: dict) -> List[Alert]:
    """Checks individual variables for alerts.

    Args:
        col: The column name that is checked.
        description: The series description.

    Returns:
        A list of alerts.
    """
    alerts: List[Alert] = []

    alerts += generic_alerts(description)

    if description["type"] == "Unsupported":
        alerts += unsupported_alerts()
    else:
        alerts += supported_alerts(description)

        if description["type"] == "Categorical":
            alerts += categorical_alerts(config, description)
        if description["type"] == "Numeric":
            alerts += numeric_alerts(config, description)
        if description["type"] == "TimeSeries":
            alerts += timeseries_alerts(config, description)
        if description["type"] == "Boolean":
            alerts += boolean_alerts(config, description)

    for idx in range(len(alerts)):
        alerts[idx].column_name = col
        alerts[idx].values = description
    return alerts


def check_correlation_alerts(config: Settings, correlations: dict) -> List[Alert]:
    """
    Check for high correlation alerts based on the provided configuration settings and correlation matrices.

    This function evaluates given correlation data against specified thresholds and configuration settings
    to determine if any high correlation alerts should be created. Alerts are generated for columns that 
    exceed the defined correlation threshold, indicating potential multicollinearity issues.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class that contains configuration options, 
        including thresholds for high correlations.
        
    correlations : dict
        A dictionary where keys are correlation identifiers and values are 
        correlation matrices to be evaluated.

    Returns:
    -------
    List[Alert]
        A list of HighCorrelationAlert instances for any columns that have 
        exceeded the configured correlation thresholds. If no high 
        correlations are detected, returns an empty list.

    Example:
    --------
    >>> config = Settings(...)
    >>> correlations = {...}
    >>> alerts = check_correlation_alerts(config, correlations)
    """
    alerts: List[Alert] = []

    correlations_consolidated = {}
    for corr, matrix in correlations.items():
        if config.correlations[corr].warn_high_correlations:
            threshold = config.correlations[corr].threshold
            correlated_mapping = perform_check_correlation(matrix, threshold)
            for col, fields in correlated_mapping.items():
                set(fields).update(set(correlated_mapping.get(col, [])))
                correlations_consolidated[col] = fields

    if len(correlations_consolidated) > 0:
        for col, fields in correlations_consolidated.items():
            alerts.append(
                HighCorrelationAlert(
                    column_name=col,
                    values={"corr": "overall", "fields": fields},
                )
            )
    return alerts


def get_alerts(
    config: Settings, table_stats: dict, series_description: dict, correlations: dict
) -> List[Alert]:
    """config: Settings, table_stats: dict, series_description: dict, correlations: dict
) -> List[Alert]:
    """
    Retrieve a list of alerts based on the provided configuration, table statistics, 
    series descriptions, and correlations.

    This function checks for three types of alerts: 
    - Alerts related to the overall table statistics.
    - Alerts associated with individual variables based on their descriptions.
    - Alerts concerning the correlations between variables.

    The resulting list of alerts is sorted by the alert type.

    Args:
        config (Settings): The configuration settings used to determine alert thresholds.
        table_stats (dict): A dictionary containing statistics for the tables to be checked.
        series_description (dict): A dictionary mapping variable names to their descriptions.
        correlations (dict): A dictionary containing correlation data between variables.

    Returns:
        List[Alert]: A sorted list of alerts generated based on the input parameters.
    """
    alerts: List[Alert] = check_table_alerts(table_stats)
    for col, description in series_description.items():
        alerts += check_variable_alerts(config, col, description)
    alerts += check_correlation_alerts(config, correlations)
    alerts.sort(key=lambda alert: str(alert.alert_type))
    return alerts


def alert_value(value: float) -> bool:
    """
    Check if the provided value is valid for alerting.

    This function checks if the given value is not NaN (Not a Number) 
    and is greater than 0.01. It returns True if both conditions are met, 
    indicating that the value is suitable for alerting.

    Args:
        value (float): The value to be checked.

    Returns:
        bool: True if the value is not NaN and greater than 0.01, 
              otherwise False.
    """
    return not pd.isna(value) and value > 0.01


def skewness_alert(v: float, threshold: int) -> bool:
    """```python
def skewness_alert(v: float, threshold: int) -> bool:
    """
    Check if the skewness value exceeds the defined thresholds.

    This function evaluates whether the provided skewness value
    `v` is not NaN and falls outside the range defined by the 
    positive and negative thresholds. It returns True if the
    skewness is either less than the negative threshold or
    greater than the positive threshold, indicating a significant
    skewness alert.

    Parameters:
    v (float): The skewness value to be evaluated.
    threshold (int): The threshold value for the skewness.

    Returns:
    bool: True if the skewness is outside the defined thresholds,
          False otherwise.
    """
    return not pd.isna(v) and (v < (-1 * threshold) or v > threshold)"""
    return not pd.isna(v) and (v < (-1 * threshold) or v > threshold)


def type_date_alert(series: pd.Series) -> bool:
    """```python
def type_date_alert(series: pd.Series) -> bool:
    """
    Checks if all values in a pandas Series can be parsed as dates.

    This function attempts to parse each value in the provided Series using the 
    dateutil.parser's `parse` function. If at least one value cannot be parsed 
    as a date, the function returns False. If all values are successfully 
    parsed, it returns True.

    Parameters:
    series (pd.Series): A pandas Series containing values to be checked.

    Returns:
    bool: True if all values in the Series can be parsed as dates, False otherwise.
    
    Exceptions:
    If a ParserError is encountered during parsing, the function will catch 
    the exception and return False.
    """
    from dateutil.parser import ParserError, parse

    try:
        series.apply(parse)
    except ParserError:
        return False
    else:
        return True
