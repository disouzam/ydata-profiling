from enum import Enum
from typing import List

import numpy as np
import pandas as pd


class DiscretizationType(Enum):
    UNIFORM = "uniform"
    QUANTILE = "quantile"


class Discretizer:
    """
    A class which enables the discretization of a pandas dataframe.
    Perform this action when you want to convert a continuous variable
    into a categorical variable.

    Attributes:

    method (DiscretizationType): this attribute controls how the buckets
    of your discretization are formed. A uniform discretization type forms
    the bins to be of equal width whereas a quantile discretization type
    forms the bins to be of equal size.

    n_bins (int): number of bins
    reset_index (bool): instruction to reset the index of
                        the dataframe after the discretization
    """

    def __init__(
        self, method: DiscretizationType, n_bins: int = 10, reset_index: bool = False
    ) -> None:
        """self, method: DiscretizationType, n_bins: int = 10, reset_index: bool = False
) -> None:
    """
    Initializes an instance of the class with the specified discretization method, number of bins, 
    and a flag to reset the index.

    Parameters:
    -----------
    method : DiscretizationType
        The method used for discretization. This should be an instance of DiscretizationType.
        
    n_bins : int, optional
        The number of bins to be used in the discretization process. Default is 10.

    reset_index : bool, optional
        A flag indicating whether to reset the index after discretization. Default is False.

    Returns:
    --------
    None
    """
        self.discretization_type = method
        self.n_bins = n_bins
        self.reset_index = reset_index

    def discretize_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """_summary_

        Args:
            dataframe (pd.DataFrame): pandas dataframe

        Returns:
            pd.DataFrame: discretized dataframe
        """

        discretized_df = dataframe.copy()
        all_columns = dataframe.columns
        num_columns = self._get_numerical_columns(dataframe)
        for column in num_columns:
            discretized_df.loc[:, column] = self._discretize_column(
                discretized_df[column]
            )

        discretized_df = discretized_df[all_columns]
        return (
            discretized_df.reset_index(drop=True)
            if self.reset_index
            else discretized_df
        )

    def _discretize_column(self, column: pd.Series) -> pd.Series:
        """
    Discretizes a given pandas Series based on the specified discretization type.

    Depending on the `discretization_type` attribute, this function will apply
    either quantile or uniform discretization to the input column.

    Parameters:
    ----------
    column : pd.Series
        A pandas Series object containing the data to be discretized.

    Returns:
    -------
    pd.Series
        A pandas Series containing the discretized values.

    Raises:
    ------
    NotImplementedError
        If the `discretization_type` is not set to a recognized value.

    Notes:
    -----
    This is an internal method and should not be called directly outside of 
    the class context.

    Example:
    --------
    >>> discretized_column = self._discretize_column(raw_column)
    """
    if self.discretization_type == DiscretizationType.QUANTILE:
        return self._descritize_quantile(column)

    elif self.discretization_type == DiscretizationType.UNIFORM:
        return self._descritize_uniform(column)"""
        if self.discretization_type == DiscretizationType.QUANTILE:
            return self._descritize_quantile(column)

        elif self.discretization_type == DiscretizationType.UNIFORM:
            return self._descritize_uniform(column)

    def _descritize_quantile(self, column: pd.Series) -> pd.Series:
        """```python
def _descritize_quantile(self, column: pd.Series) -> pd.Series:
    """
    Discretizes a given pandas Series into quantiles.

    This method divides the values in the specified column into `n_bins` quantiles 
    using the pandas `qcut` function. The output is a Series of integer labels 
    corresponding to the quantile each value belongs to. 

    Parameters:
    ----------
    column : pd.Series
        A pandas Series containing the numeric data to be discretized.

    Returns:
    -------
    pd.Series
        A Series of integers representing the bin labels for each value in the input column.
        The labels range from 0 to n_bins-1, where each integer corresponds to a quantile interval.
    
    Notes:
    -----
    The `duplicates="drop"` parameter is used to handle cases where there are duplicate bin edges 
    by automatically dropping the redundant edges.
    """
    return pd.qcut(
        column, q=self.n_bins, labels=False, retbins=False, duplicates="drop"
    ).values
```"""
        return pd.qcut(
            column, q=self.n_bins, labels=False, retbins=False, duplicates="drop"
        ).values

    def _descritize_uniform(self, column: pd.Series) -> pd.Series:
        """```python
def _descritize_uniform(self, column: pd.Series) -> pd.Series:
    """
    Discretizes a continuous variable into uniform bins.

    This function takes a pandas Series as input and divides its values into 
    a specified number of uniform bins. It returns the bin labels as integers, 
    where each integer represents the corresponding bin index.

    Parameters:
    ----------
    column : pd.Series
        A pandas Series containing the continuous variable to be discretized.

    Returns:
    -------
    pd.Series
        A pandas Series containing the bin indices for each value in the input column.
    
    Notes:
    -----
    The number of bins is specified by the `self.n_bins` attribute. 
    If there are duplicate bin edges, they are dropped.
    """
    return pd.cut(
        column, bins=self.n_bins, labels=False, retbins=True, duplicates="drop"
    )[0].values"""
        return pd.cut(
            column, bins=self.n_bins, labels=False, retbins=True, duplicates="drop"
        )[0].values

    def _get_numerical_columns(self, dataframe: pd.DataFrame) -> List[str]:
        """
    Retrieves the names of numerical columns from the given DataFrame.

    This method uses the DataFrame's data type selection capabilities
    to filter and return the column names that have numerical data types.

    Args:
        dataframe (pd.DataFrame): A pandas DataFrame from which to extract
                                   numerical column names.

    Returns:
        List[str]: A list of column names that contain numerical data types.
    """
        return dataframe.select_dtypes(include=np.number).columns.tolist()
