"""
    Logger function for ydata-profiling reports
"""

import logging

import pandas as pd

from ydata_profiling.utils.common import (
    analytics_features,
    calculate_nrows,
    is_running_in_databricks,
)


class ProfilingLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.INFO):
        """```python
def __init__(self, name: str, level: int = logging.INFO):
    """
    Initializes a new instance of the class.

    Parameters:
    name (str): The name of the logger.
    level (int, optional): The logging level for the logger. Defaults to logging.INFO.

    This constructor calls the superclass initializer with the provided name and level.
    """
    super().__init__(name, level)
```"""
        super().__init__(name, level)

    def info_def_report(self, df, timeseries: bool) -> None:
        """
    Generates and logs a data profiling report based on the characteristics of the provided DataFrame or dataset.

    This function assesses the input data (df) to determine its structure, including the number of rows 
    and columns, and whether it's a Pandas DataFrame, a Spark DataFrame, or None. It also identifies 
    if the data is in a timeseries format. Based on these attributes, it calls the `analytics_features` 
    function to generate a report with the relevant details and logs the information for profiling purposes.

    Parameters:
    ----------
    df : DataFrame or None
        The input data for profiling. It can be a Pandas DataFrame, a Spark DataFrame, or None.
        
    timeseries : bool
        A boolean indicating whether the data is in a timeseries format. 

    Returns:
    -------
    None
        This function does not return a value. It conducts an operation to generate a report and logs 
        profiling information.

    Raises:
    ------
    AttributeError
        If the input DataFrame does not have columns, an AttributeError may be caught, and the number 
        of columns will be set to zero.
    """
        try:
            ncols = len(df.columns)
        except AttributeError:
            ncols = 0

        nrows = calculate_nrows(df)

        if isinstance(df, pd.DataFrame):
            dataframe = "pandas"
            report_type = "regular"
        elif df is None:
            dataframe = "pandas"
            report_type = "compare"
        else:
            dataframe = "spark"
            report_type = "regular"

        dbx = is_running_in_databricks()
        datatype = "timeseries" if timeseries else "tabular"

        analytics_features(
            dataframe=dataframe,
            datatype=datatype,
            report_type=report_type,
            nrows=nrows,
            ncols=ncols,
            dbx=dbx,
        )

        super().info(
            f"[PROFILING] Calculating profile with the following characteristics "
            f"- {dataframe} | {datatype} | {report_type}."
        )
