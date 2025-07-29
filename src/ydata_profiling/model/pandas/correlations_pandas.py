"""Correlations between variables."""
import itertools
import warnings
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy import stats

from ydata_profiling.config import Settings
from ydata_profiling.model.correlations import (
    Auto,
    Cramers,
    Kendall,
    Pearson,
    PhiK,
    Spearman,
)
from ydata_profiling.model.pandas.discretize_pandas import (
    DiscretizationType,
    Discretizer,
)


@Spearman.compute.register(Settings, pd.DataFrame, dict)
def pandas_spearman_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Spearman correlation matrix for numeric columns in the given DataFrame.

    This function takes a configuration object, a pandas DataFrame, and a summary dictionary
    as inputs. It selects only the numeric columns from the DataFrame and computes the Spearman
    correlation matrix using the `corr` method.

    Parameters:
    ----------
    config : Settings
        Configuration settings for the computation.
    df : pd.DataFrame
        The input DataFrame containing the data for which the Spearman correlation is to be calculated.
    summary : dict
        A dictionary to store any relevant summary information (currently not used in the computation).

    Returns:
    -------
    Optional[pd.DataFrame]
        A DataFrame containing the Spearman correlation coefficients between the numeric columns.
        Returns None if there are no numeric columns in the input DataFrame.
    """
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="spearman")


@Pearson.compute.register(Settings, pd.DataFrame, dict)
def pandas_pearson_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Pearson correlation coefficient for numerical columns in the given DataFrame.

    This function selects only the numerical columns from the provided DataFrame and calculates 
    the Pearson correlation matrix among them. The result is a DataFrame containing the correlation 
    coefficients.

    Args:
        config (Settings): Configuration settings for the computation.
        df (pd.DataFrame): The input DataFrame containing numerical data.
        summary (dict): A dictionary to hold summary statistics or additional information.

    Returns:
        Optional[pd.DataFrame]: A DataFrame representing the Pearson correlation matrix, 
        or None if no numerical data is present in the input DataFrame.
    """
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="pearson")


@Kendall.compute.register(Settings, pd.DataFrame, dict)
def pandas_kendall_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Kendall correlation coefficient for numerical columns in a given DataFrame.

    This function selects only the numerical columns from the provided DataFrame and 
    computes the Kendall correlation matrix. The resulting correlation matrix is returned 
    as a new DataFrame.

    Parameters:
    ----------
    config : Settings
        Configuration settings to guide the computation process.
    df : pd.DataFrame
        A pandas DataFrame from which numerical columns will be selected.
    summary : dict
        A dictionary for storing metadata or summary statistics related to the computation.

    Returns:
    -------
    Optional[pd.DataFrame]
        A DataFrame containing the Kendall correlation coefficients 
        between the numerical columns of the input DataFrame. 
        Returns None if there are no numerical columns to compute correlation.

    Note:
    -----
    Ensure that the input DataFrame contains at least one numerical column 
    to generate a valid correlation matrix. If there are no numerical columns, 
    None will be returned.
    """
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="kendall")


def _cramers_corrected_stat(confusion_matrix: pd.DataFrame, correction: bool) -> float:
    """Calculate the Cramer's V corrected stat for two variables.

    Args:
        confusion_matrix: Crosstab between two variables.
        correction: Should the correction be applied?

    Returns:
        The Cramer's V corrected stat for the two variables.
    """
    # handles empty crosstab
    if confusion_matrix.empty:
        return 0

    chi2 = stats.chi2_contingency(confusion_matrix, correction=correction)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r = confusion_matrix.shape[0]
    k = confusion_matrix.shape[1] if len(confusion_matrix.shape) > 1 else 1

    # Deal with NaNs later on
    with np.errstate(divide="ignore", invalid="ignore"):
        phi2corr = max(0.0, phi2 - ((k - 1.0) * (r - 1.0)) / (n - 1.0))
        rcorr = r - ((r - 1.0) ** 2.0) / (n - 1.0)
        kcorr = k - ((k - 1.0) ** 2.0) / (n - 1.0)
        rkcorr = min((kcorr - 1.0), (rcorr - 1.0))
        if rkcorr == 0.0:
            corr = 1.0
        else:
            corr = np.sqrt(phi2corr / rkcorr)
    return corr


def _pairwise_spearman(col_1: pd.Series, col_2: pd.Series) -> float:
    """
    Calculate the Spearman correlation coefficient between two pandas Series.

    This function computes the Spearman rank correlation coefficient,
    which measures the strength and direction of the association between 
    two ranked variables. It is a non-parametric measure and is suitable 
    for assessing the correlation of ordinal data.

    Parameters:
    col_1 (pd.Series): The first pandas Series to compare.
    col_2 (pd.Series): The second pandas Series to compare.

    Returns:
    float: The Spearman correlation coefficient between the two Series,
           ranging from -1 (perfect negative correlation) to 1 (perfect positive correlation).
           A coefficient of 0 indicates no correlation.
    """
    return col_1.corr(col_2, method="spearman")


def _pairwise_cramers(col_1: pd.Series, col_2: pd.Series) -> float:
    """
    Calculate the Cramér's V statistic between two categorical variables.

    This function computes the Cramér's V statistic using a contingency table generated 
    from the two input categorical variables, col_1 and col_2. It applies a correction 
    to the statistic for better accuracy in statistical inference.

    Parameters:
    col_1 (pd.Series): The first categorical variable as a Pandas Series.
    col_2 (pd.Series): The second categorical variable as a Pandas Series.

    Returns:
    float: The Cramér's V statistic, a measure of association between the two variables, 
           ranging from 0 (no association) to 1 (perfect association).
    """
    return _cramers_corrected_stat(pd.crosstab(col_1, col_2), correction=True)"""
    return _cramers_corrected_stat(pd.crosstab(col_1, col_2), correction=True)


@Cramers.compute.register(Settings, pd.DataFrame, dict)
def pandas_cramers_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Cramér's V correlation matrix for categorical and boolean variables in a given DataFrame.

    This function identifies categorical variables based on their distinct value counts as specified 
    in the provided configuration and computes the Cramér's V statistic for each pair of selected variables. 
    The resulting correlation matrix indicates the strength of association between pairs of categorical variables. 
    If there are less than two categorical variables that meet the distinct value criteria, the function returns None.

    Parameters:
    ----------
    config : Settings
        The configuration settings containing the maximum number of distinct values allowed for categorical variables.
    df : pd.DataFrame
        The input DataFrame containing the data from which to compute the correlation matrix.
    summary : dict
        A dictionary summarizing the variable types and distinct counts, used to filter the categorical variables.

    Returns:
    -------
    Optional[pd.DataFrame]
        A DataFrame representing the Cramér's V correlation matrix for the identified categorical variables, 
        or None if fewer than two categorical variables are identified.

    Notes:
    -----
    - The function ensures that the variable names are stored in a list since index and column names in Pandas 
      must not be sets starting from version 1.5.
    - The diagonal of the correlation matrix is filled with 1.0, representing perfect correlation of each variable 
      with itself.
    - Cramér's V statistic is calculated using a corrected method for pairs of variables, and NaN values are 
      assigned in cases where a confusion matrix is empty.

    Example:
    --------
    >>> config = Settings(categorical_maximum_correlation_distinct=10)
    >>> df = pd.DataFrame({'A': ['a', 'b', 'a'], 'B': ['x', 'y', 'x'], 'C': [1, 2, 1]})
    >>> summary = {'A': {'type': 'Categorical', 'n_distinct': 2}, 
    ...           'B': {'type': 'Categorical', 'n_distinct': 2},
    ...           'C': {'type': 'Numeric', 'n_distinct': 2}}
    >>> correlation_matrix = pandas_cramers_compute(config, df, summary)
    """
    threshold = config.categorical_maximum_correlation_distinct

    # `index` and `columns` must not be a set since Pandas 1.5,
    # so convert it to a list. The order of the list is arbitrary.
    categoricals = list(
        {
            key
            for key, value in summary.items()
            if value["type"] in {"Categorical", "Boolean"}
            and 1 < value["n_distinct"] <= threshold
        }
    )

    if len(categoricals) <= 1:
        return None

    categoricals = sorted(categoricals)
    matrix = np.zeros((len(categoricals), len(categoricals)))
    np.fill_diagonal(matrix, 1.0)
    correlation_matrix = pd.DataFrame(
        matrix,
        index=categoricals,
        columns=categoricals,
    )

    for name1, name2 in itertools.combinations(categoricals, 2):
        confusion_matrix = pd.crosstab(df[name1], df[name2])
        if confusion_matrix.empty:
            correlation_matrix.loc[name2, name1] = np.nan
        else:
            correlation_matrix.loc[name2, name1] = _cramers_corrected_stat(
                confusion_matrix, correction=True
            )
        correlation_matrix.loc[name1, name2] = correlation_matrix.loc[name2, name1]
    return correlation_matrix


@PhiK.compute.register(Settings, pd.DataFrame, dict)
def pandas_phik_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Compute the correlation matrix for a given DataFrame using the PhiK method.

    This function selects numeric and categorical columns from the DataFrame 
    based on the provided summary and configuration settings. It computes 
    the PhiK correlation matrix for these selected columns and returns it 
    as a DataFrame. If there are not enough columns to compute the correlation, 
    the function returns None.

    Parameters:
    ----------
    config : Settings
        A configuration object containing settings for the computation.
    
    df : pd.DataFrame
        The input DataFrame for which the correlation matrix is to be computed.
    
    summary : dict
        A dictionary providing metadata about the columns in the DataFrame, 
        including types and distinct value counts.

    Returns:
    -------
    Optional[pd.DataFrame]
        A DataFrame containing the PhiK correlation matrix, or None if there 
        are not enough valid columns to compute the correlation.

    Notes:
    -----
    - DateTime columns are currently excluded from the correlation calculation.
    - The function uses the `phik` library to compute the correlation matrix.
    """
    df_cols_dict = {i: list(df.columns).index(i) for i in df.columns}

    intcols = {
        key
        for key, value in summary.items()
        # DateTime currently excluded
        # In some use cases, it makes sense to convert it to interval
        # See https://github.com/KaveIO/PhiK/issues/7
        if value["type"] == "Numeric" and 1 < value["n_distinct"]
    }

    selcols = {
        key
        for key, value in summary.items()
        if value["type"] != "Unsupported"
        and 1 < value["n_distinct"] <= config.categorical_maximum_correlation_distinct
    }
    selcols = selcols.union(intcols)
    selected_cols = sorted(selcols, key=lambda i: df_cols_dict[i])

    if len(selected_cols) <= 1:
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from phik import phik_matrix

        correlation = phik_matrix(df[selected_cols], interval_cols=list(intcols))

    return correlation


@Auto.compute.register(Settings, pd.DataFrame, dict)
def pandas_auto_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes a correlation matrix for the given DataFrame based on specified 
    numerical and categorical columns. The function performs discretization 
    on the numerical columns and evaluates the correlation between all 
    pairs of tested columns using appropriate statistical methods. 

    Parameters:
    ----------
    config : Settings
        Configuration settings containing parameters for correlation computations.
    df : pd.DataFrame
        The input DataFrame containing the data to analyze.
    summary : dict
        A summary dictionary containing metadata about the columns of the DataFrame, 
        including their types and the number of distinct values.

    Returns:
    -------
    Optional[pd.DataFrame]
        A DataFrame representing the correlation matrix of the tested columns, 
        or None if there are insufficient columns to compute correlations.
    """

    # Function implementation...
```"""
    threshold = config.categorical_maximum_correlation_distinct
    numerical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Numeric", "TimeSeries"} and value["n_distinct"] > 1
    ]
    categorical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Categorical", "Boolean"}
        and 1 < value["n_distinct"] <= threshold
    ]

    if len(numerical_columns + categorical_columns) <= 1:
        return None

    df_discretized = Discretizer(
        DiscretizationType.UNIFORM, n_bins=config.correlations["auto"].n_bins
    ).discretize_dataframe(df)
    columns_tested = sorted(numerical_columns + categorical_columns)

    correlation_matrix = pd.DataFrame(
        np.ones((len(columns_tested), len(columns_tested))),
        index=columns_tested,
        columns=columns_tested,
    )
    for col_1_name, col_2_name in itertools.combinations(columns_tested, 2):

        method = (
            _pairwise_spearman
            if any(elem in categorical_columns for elem in [col_1_name, col_2_name])
            is False
            else _pairwise_cramers
        )

        def f(col_name: str, method: Callable) -> pd.Series:
            return (
                df_discretized
                if col_name in numerical_columns and method is _pairwise_cramers
                else df
            )

        score = method(
            f(col_1_name, method)[col_1_name], f(col_2_name, method)[col_2_name]
        )
        (
            correlation_matrix.loc[col_1_name, col_2_name],
            correlation_matrix.loc[col_2_name, col_1_name],
        ) = (score, score)

    return correlation_matrix
