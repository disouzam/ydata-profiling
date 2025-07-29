import numpy as np
import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.missing import missing_bar, missing_heatmap, missing_matrix
from ydata_profiling.visualisation.missing import (
    plot_missing_bar,
    plot_missing_heatmap,
    plot_missing_matrix,
)


@missing_bar.register
def pandas_missing_bar(config: Settings, df: pd.DataFrame) -> str:
    """def pandas_missing_bar(config: Settings, df: pd.DataFrame) -> str:
    """
    Generate a missing value bar plot for a given DataFrame.

    This function calculates the count of non-null values in each column of the provided
    DataFrame, then creates a bar plot visualizing the number of missing values per column.

    Args:
        config (Settings): Configuration settings used for plot customization.
        df (pd.DataFrame): The DataFrame from which to compute and visualize missing values.

    Returns:
        str: A string representation of the plot or a file path to the saved plot image.
    """
    notnull_counts = len(df) - df.isnull().sum()
    return plot_missing_bar(
        config,
        notnull_counts=notnull_counts,
        nrows=len(df),
        columns=list(df.columns),
    )"""
    notnull_counts = len(df) - df.isnull().sum()
    return plot_missing_bar(
        config,
        notnull_counts=notnull_counts,
        nrows=len(df),
        columns=list(df.columns),
    )


@missing_matrix.register
def pandas_missing_matrix(config: Settings, df: pd.DataFrame) -> str:
    """def pandas_missing_matrix(config: Settings, df: pd.DataFrame) -> str:
    """
    Generates a missing matrix plot for the given DataFrame.

    This function utilizes the `plot_missing_matrix` function to visualize the 
    missing values in the DataFrame. It constructs a matrix where each cell 
    indicates whether the corresponding value is missing or not.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class containing configuration settings for 
        the missing matrix plot.
    
    df : pd.DataFrame
        A pandas DataFrame for which the missing values are to be analyzed.
    
    Returns:
    -------
    str
        A string representation of the generated missing matrix plot. 
    """
    return plot_missing_matrix(
        config,
        columns=list(df.columns),
        notnull=df.notnull().values,
        nrows=len(df),
    )"""
    return plot_missing_matrix(
        config,
        columns=list(df.columns),
        notnull=df.notnull().values,
        nrows=len(df),
    )


@missing_heatmap.register
def pandas_missing_heatmap(config: Settings, df: pd.DataFrame) -> str:
    """
    Generates a heatmap to visualize missing values in a DataFrame.

    This function first removes any columns from the DataFrame that are completely filled or completely empty.
    It then computes the correlation matrix of the remaining columns based on their missing values 
    and generates a masked heatmap to visualize these correlations.

    Args:
        config (Settings): Configuration settings for the heatmap generation.
        df (pd.DataFrame): The input DataFrame from which to visualize missing values.

    Returns:
        str: The resulting heatmap as a string or a rendering identifier.

    Notes:
        - The function utilizes the plot_missing_heatmap function for the actual heatmap generation.
        - Ensure that the DataFrame passed does not contain too many missing values to avoid misleading correlations.
    """
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
