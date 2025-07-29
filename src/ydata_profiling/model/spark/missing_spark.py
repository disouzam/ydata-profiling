from typing import Any, List, Optional

import numpy as np
from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.missing import missing_bar, missing_heatmap, missing_matrix
from ydata_profiling.visualisation.missing import (
    plot_missing_bar,
    plot_missing_heatmap,
    plot_missing_matrix,
)


class MissingnoBarSparkPatch:
    """
    Technical Debt :
    This is a monkey patching object that allows usage of the library missingno as is for spark dataframes.
    This is because missingno library's bar function always applies a isnull().sum() on dataframes in the visualisation
    function, instead of allowing just values counts as an entry point. Thus, in order to calculate the
    missing values dataframe in spark, we compute it first, then wrap it in this MissingnoBarSparkPatch object which
    will be unwrapped by missingno and return the pre-computed value counts.
    The best fix to this currently terrible patch is to submit a PR to missingno to separate preprocessing function
    (compute value counts from df) and visualisation functions such that we can call the visualisation directly.
    Unfortunately, the missingno library people have not really responded to our issues on gitlab.
    See https://github.com/ResidentMario/missingno/issues/119.
    We could also fork the missingno library and implement some of the code in our database, but that feels
    like bad practice as well.
    """

    def __init__(
        self, df: DataFrame, columns: List[str] = None, original_df_size: int = None
    ):
        """self, df: DataFrame, columns: List[str] = None, original_df_size: int = None
):
    """
    Initializes an instance of the class.

    Parameters:
    df (DataFrame): The DataFrame to be used for the instance.
    columns (List[str], optional): A list of column names to be considered. Defaults to None.
    original_df_size (int, optional): The original size of the DataFrame before any modifications. Defaults to None.
    
    Attributes:
    df (DataFrame): The DataFrame stored in the instance.
    columns (List[str]): The list of column names.
    original_df_size (int): The original size of the DataFrame.
    """
        self.df = df
        self.columns = columns
        self.original_df_size = original_df_size

    def isnull(self) -> Any:
        """
        This patches the .isnull().sum() function called by missingno library
        """
        return self  # return self to patch .sum() function

    def sum(self) -> DataFrame:
        """
        This patches the .sum() function called by missingno library
        """
        return self.df  # return unwrapped dataframe

    def __len__(self) -> Optional[int]:
        """
        This patches the len(df) function called by missingno library
        """
        return self.original_df_size


@missing_bar.register
def spark_missing_bar(config: Settings, df: DataFrame) -> str:
    """
    Generate a bar plot depicting the count of missing values in each column of a Spark DataFrame.

    This function processes the input DataFrame to count the number of null or NaN values in each column.
    It returns the result as a string that presumably represents the plot or its file path.

    Parameters:
    ----------
    config : Settings
        An object containing configuration settings that may influence the plot generation.
    
    df : DataFrame
        A Spark DataFrame for which the missing values will be analyzed.

    Returns:
    -------
    str
        A string representing the result of the plot generation, which may be the file path or the plot data itself.

    Notes:
    -----
    - The implementation includes a FIXME comment indicating that this function should be refactored to handle 
      univariate analyses in the future.
    - The function relies on the external `plot_missing_bar` function to create the visualization of the missing data.
    """
    import pyspark.sql.functions as F

    # FIXME: move to univariate
    data_nan_counts = (
        df.agg(
            *[F.count(F.when(F.isnull(c) | F.isnan(c), c)).alias(c) for c in df.columns]
        )
        .toPandas()
        .squeeze(axis="index")
    )

    return plot_missing_bar(
        config, notnull_counts=data_nan_counts, columns=df.columns, nrows=df.count()
    )


@missing_matrix.register
def spark_missing_matrix(config: Settings, df: DataFrame) -> str:
    """def spark_missing_matrix(config: Settings, df: DataFrame) -> str:
    """
    Generates a missing value matrix visualization for a Spark DataFrame.

    This function creates a missing value plot using the provided configuration and Spark DataFrame.
    It utilizes a patched version of the MissingnoBarSpark to handle Spark DataFrames effectively.

    Args:
        config (Settings): Configuration settings for the plot, including visualization options.
        df (DataFrame): The Spark DataFrame for which the missing value matrix is to be generated.

    Returns:
        str: A string representation of the plot, which can be used for further processing or display.

    Notes:
        The function counts the original size of the DataFrame and uses this information for visualization.
    """
    df = MissingnoBarSparkPatch(df, columns=df.columns, original_df_size=df.count())
    return plot_missing_matrix(
        config,
        columns=df.columns,
        notnull=df.notnull().values,
        nrows=len(df),
    )"""
    df = MissingnoBarSparkPatch(df, columns=df.columns, original_df_size=df.count())
    return plot_missing_matrix(
        config,
        columns=df.columns,
        notnull=df.notnull().values,
        nrows=len(df),
    )


@missing_heatmap.register
def spark_missing_heatmap(config: Settings, df: DataFrame) -> str:
    """
    Generate a heatmap showing the correlation of missing values in the given DataFrame.

    This function processes the input DataFrame by removing columns that are either 
    completely filled or completely empty and then calculates the correlation matrix 
    for the missing values. It creates a masked heatmap of the correlation matrix, 
    where only the lower triangle is shown.

    Parameters:
    - config (Settings): Configuration settings required for plotting the heatmap.
    - df (DataFrame): The input DataFrame to analyze for missing values.

    Returns:
    - str: A string representation of the generated heatmap, which may contain 
           information about the output path or other relevant details.
    """
    df = MissingnoBarSparkPatch(df, columns=df.columns, original_df_size=df.count())

    # Remove completely filled or completely empty variables.
    columns = [i for i, n in enumerate(np.var(df.isnull(), axis="rows")) if n > 0]
    df = df.iloc[:, columns]

    # Create and mask the correlation matrix. Construct the base heatmap.
    corr_mat = df.isnull().corr()
    mask = np.zeros_like(corr_mat)
    mask[np.triu_indices_from(mask)] = True
    return plot_missing_heatmap(
        config, corr_mat=corr_mat, mask=mask, columns=list(df.columns)
    )
