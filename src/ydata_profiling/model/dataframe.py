from typing import Any

from multimethod import multimethod

from ydata_profiling.config import Settings


@multimethod
def check_dataframe(df: Any) -> None:
    """
    Validates the provided DataFrame.

    This function serves as a placeholder for multimethods 
    that will implement specific DataFrame validation logic 
    based on the type of the DataFrame provided. 

    Parameters:
    df (Any): The DataFrame to be validated. The exact type 
              expected will depend on the specific 
              implementation of the multimethod.

    Raises:
    NotImplementedError: This is a base implementation and 
                         should be overridden by subclasses 
                         to provide actual validation logic.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


@multimethod
def preprocess(config: Settings, df: Any) -> Any:
    """
    Preprocesses the given DataFrame based on the provided configuration settings.

    This function serves as a placeholder for data preprocessing tasks. It takes a 
    configuration object of type `Settings` and a DataFrame (df) as input and returns 
    the DataFrame as is by default. The actual preprocessing logic can be implemented 
    in specific cases based on the configuration.

    Parameters:
    ----------
    config : Settings
        An object containing configuration settings that may influence the preprocessing.
    
    df : Any
        The DataFrame or data structure to be preprocessed.

    Returns:
    -------
    Any
        The preprocessed DataFrame (or an equivalent data structure), which defaults 
        to the input DataFrame if no processing is applied.
    """
    return df"""
    return df
