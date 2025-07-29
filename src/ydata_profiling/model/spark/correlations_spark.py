"""Correlations between variables."""
from typing import Optional

import pandas as pd
import phik
import pyspark
from packaging import version
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation
from pyspark.sql import DataFrame
from pyspark.sql.functions import PandasUDFType, lit, pandas_udf
from pyspark.sql.types import ArrayType, DoubleType, StructField, StructType

from ydata_profiling.config import Settings
from ydata_profiling.model.correlations import Cramers, Kendall, Pearson, PhiK, Spearman

SPARK_CORRELATION_PEARSON = "pearson"
SPARK_CORRELATION_SPEARMAN = "spearman"


@Spearman.compute.register(Settings, DataFrame, dict)
def spark_spearman_compute(
    config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Spearman correlation matrix for a given DataFrame using Spark.

    This function retrieves the numerical columns of the provided DataFrame
    and utilizes Spark's native capabilities to compute the Spearman correlation.
    It returns the resulting correlation matrix as a Pandas DataFrame.

    Args:
        config (Settings): Configuration object containing settings for the computation.
        df (DataFrame): The input Spark DataFrame for which the Spearman correlation 
                        matrix is to be computed.
        summary (dict): A dictionary that may contain summary statistics or additional
                        information relevant to the computation.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame representing the Spearman correlation 
                                 matrix, indexed by numerical column names. Returns None 
                                 if the computation fails or if there are no numerical columns.
    """
    # Get the numerical cols for index and column names
    # Spark only computes Spearman natively for the above dtypes
    matrix, num_cols = _compute_spark_corr_natively(
        df, summary, corr_type=SPARK_CORRELATION_SPEARMAN
    )
    return pd.DataFrame(matrix, index=num_cols, columns=num_cols)


@Pearson.compute.register(Settings, DataFrame, dict)
def spark_pearson_compute(
    config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Pearson correlation coefficient for the numerical columns in the provided DataFrame 
    using Spark's native computation capabilities.

    This function registers the computation with the Pearson module and is particularly designed 
    to handle DataFrames with numerical data types supported by Spark for Pearson correlation.

    Args:
        config (Settings): The configuration settings used for the computation.
        df (DataFrame): The input Spark DataFrame containing the data for correlation analysis.
        summary (dict): A summary dictionary that may contain additional information relevant to the computation.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing the Pearson correlation matrix with 
        numerical column names as both index and columns. If the computation cannot be performed, 
        returns None.
    """

    # Get the numerical cols for index and column names
    # Spark only computes Pearson natively for the above dtypes
    matrix, num_cols = _compute_spark_corr_natively(
        df, summary, corr_type=SPARK_CORRELATION_PEARSON
    )
    return pd.DataFrame(matrix, index=num_cols, columns=num_cols)


def _compute_spark_corr_natively(
    df: DataFrame, summary: dict, corr_type: str
) -> ArrayType:
    """
    This function exists as pearson and spearman correlation computations have the
    exact same workflow. The syntax is Correlation.corr(dataframe, method="pearson" OR "spearman"),
    and Correlation is from pyspark.ml.stat
    """
    variables = {column: description["type"] for column, description in summary.items()}
    interval_columns = [
        column for column, type_name in variables.items() if type_name == "Numeric"
    ]
    df = df.select(*interval_columns)

    # convert to vector column first
    vector_col = "corr_features"

    assembler_args = {"inputCols": df.columns, "outputCol": vector_col}

    # As handleInvalid was only implemented in spark 2.4.0, we use it only if pyspark version >= 2.4.0
    if version.parse(pyspark.__version__) >= version.parse("2.4.0"):
        assembler_args["handleInvalid"] = "skip"

    assembler = VectorAssembler(**assembler_args)
    df_vector = assembler.transform(df).select(vector_col)

    # get correlation matrix
    matrix = (
        Correlation.corr(df_vector, vector_col, method=corr_type).head()[0].toArray()
    )
    return matrix, interval_columns


@Kendall.compute.register(Settings, DataFrame, dict)
def spark_kendall_compute(
    config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the Kendall correlation based on the provided configuration and input data.

    This function is registered with the Kendall computation framework and is expected
    to implement the logic for calculating Kendall coefficients from a given DataFrame.

    Args:
        config (Settings): A configuration object containing settings required for the computation.
        df (DataFrame): A Pandas DataFrame containing the data on which the Kendall correlation
                        is to be computed.
        summary (dict): A dictionary to store summarized results or metadata related to the
                        computation.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing the results of the Kendall
                                  computation, or None if the computation cannot be performed.

    Raises:
        NotImplementedError: This function is a placeholder and should be implemented
                             to provide the actual computation logic.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@Cramers.compute.register(Settings, DataFrame, dict)
def spark_cramers_compute(
    config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes Cramér's V statistic for categorical feature analysis in a Spark DataFrame.

    This function is registered with the computation framework and is expected to
    perform the calculation of Cramér's V based on the input configuration and 
    data provided. It currently raises a NotImplementedError, indicating that 
    the implementation is pending.

    Args:
        config (Settings): The settings for the computation, which may include 
                           parameters such as significance level, categories 
                           to analyze, etc.
        df (DataFrame): A Spark DataFrame containing the categorical data 
                        for which Cramér's V needs to be computed.
        summary (dict): A dictionary that may hold summary statistics or 
                        additional context for the computation.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing Cramér's V results, 
                                or None if the computation is not yet implemented.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@PhiK.compute.register(Settings, DataFrame, dict)
def spark_phi_k_compute(
    config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """config: Settings, df: DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    """
    Computes the PhiK correlation matrix for a given DataFrame using Spark.

    This function leverages a pandas User Defined Function (UDF) to calculate 
    the PhiK correlations between supported numeric columns and selected 
    categorical columns. It only considers columns with a certain number 
    of distinct values, as defined in the provided configuration.

    Args:
        config (Settings): An object containing configuration settings such as 
                           the maximum number of distinct values for categorical 
                           columns to be considered in the correlation calculation.
        df (DataFrame): A Spark DataFrame containing the data for which 
                        correlations will be computed.
        summary (dict): A dictionary providing metadata about the DataFrame's columns, 
                        including their types and number of distinct values.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing the PhiK correlation 
                                 matrix, or None if there are not enough columns 
                                 to compute correlations.
    """

    threshold = config.categorical_maximum_correlation_distinct
    intcols = {
        key
        for key, value in summary.items()
        # DateTime currently excluded
        # In some use cases, it makes sense to convert it to interval
        # See https://github.com/KaveIO/PhiK/issues/7
        if value["type"] == "Numeric" and 1 < value["n_distinct"]
    }

    supportedcols = {
        key
        for key, value in summary.items()
        if value["type"] != "Unsupported" and 1 < value["n_distinct"] <= threshold
    }
    selcols = list(supportedcols.union(intcols))

    if len(selcols) <= 1:
        return None

    # pandas mapped udf works only with a groupby, we force the groupby to operate on all columns at once
    # by giving one value to all columns
    groupby_df = df.select(selcols).withColumn("groupby", lit(1))

    # generate output schema for pandas_udf
    output_schema_components = []
    for column in selcols:
        output_schema_components.append(StructField(column, DoubleType(), True))
    output_schema = StructType(output_schema_components)

    # create the pandas grouped map function to do vectorized kendall within spark itself
    @pandas_udf(output_schema, PandasUDFType.GROUPED_MAP)
    def spark_phik(pdf: pd.DataFrame) -> pd.DataFrame:
        correlation = phik.phik_matrix(df=pdf, interval_cols=list(intcols))
        return correlation

    # return the appropriate dataframe (similar to pandas_df.corr results)
    if len(groupby_df.head(1)) > 0:
        # perform correlation in spark, and get the results back in pandas
        df = pd.DataFrame(
            groupby_df.groupby("groupby").apply(spark_phik).toPandas().values,
            columns=selcols,
            index=selcols,
        )
    else:
        df = pd.DataFrame()

    return df
