"""Compute statistical description of datasets."""

from typing import Any

from multimethod import multimethod
from tqdm import tqdm
from visions import VisionsTypeset

from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer


@multimethod
def describe_1d(
    config: Settings,
    series: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
) -> dict:
    """config: Settings,
    series: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
) -> dict:
    """
    Describe a one-dimensional data series using a specified summarizer and configuration.

    This function is intended to be implemented in a multi-method context. It takes a set of parameters 
    that includes configuration settings, the data series to be described, a summarizer to process 
    the data, and a typeset for visual representation.

    Parameters:
    ----------
    config : Settings
        An instance of the Settings class containing configuration options for data description.
    series : Any
        The one-dimensional data series to be analyzed, can be of any type (e.g., list, numpy array, etc.).
    summarizer : BaseSummarizer
        An instance of a summarizer that defines how to summarize the data series.
    typeset : VisionsTypeset
        An instance of VisionsTypeset used to format the output for visual representation.

    Returns:
    -------
    dict
        A dictionary containing the results of the description and summarization of the data series.

    Raises:
    ------
    NotImplementedError
        This method should be implemented in subclasses or specific use cases.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def get_series_descriptions(
    config: Settings,
    df: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
    pbar: tqdm,
) -> dict:
    """config: Settings,
    df: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
    pbar: tqdm,
) -> dict:
    """
    Retrieves descriptions for a series of data based on the provided configuration and summarizer.

    This function is intended to be implemented in a subclass, as it currently raises a 
    NotImplementedError. The method is designed to process the given DataFrame (`df`) 
    and utilize the specified `summarizer` to generate meaningful descriptions. 

    Parameters:
        config (Settings): The configuration settings used to guide the description retrieval process.
        df (Any): The input DataFrame containing the data for which descriptions are to be generated.
        summarizer (BaseSummarizer): An instance of a summarizer that provides methods to summarize
                                      the data in the DataFrame.
        typeset (VisionsTypeset): An instance that defines the type system used for handling 
                                   various data types within the DataFrame.
        pbar (tqdm): A tqdm progress bar instance for tracking the progress of the description 
                      generation process.

    Returns:
        dict: A dictionary containing the generated descriptions for the series of data 
              processed.

    Raises:
        NotImplementedError: This method must be implemented in a subclass.
    """
    raise NotImplementedError()
