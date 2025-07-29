from typing import Any

from multimethod import multimethod

from ydata_profiling.config import Settings


@multimethod
def get_table_stats(config: Settings, df: Any, variable_stats: dict) -> dict:
    """```python
"""
Get statistics for a given DataFrame based on the provided configuration.

This function is a multimethod that computes and returns statistical information 
about the specified DataFrame. The actual implementation should be provided by 
subclasses or specific method overloads for different data types or configurations.

Parameters:
    config (Settings): An instance of the Settings class containing configuration 
                       options for calculating the statistics.
    df (Any): The DataFrame for which statistics are to be computed. 
              It can be of any type compatible with the statistics 
              being calculated.
    variable_stats (dict): A dictionary containing variable-specific statistics 
                           and configurations to be used in the computation.

Returns:
    dict: A dictionary containing computed statistics for the DataFrame.
           The structure and contents of the returned dictionary depend on 
           the implementation of the method.

Raises:
    NotImplementedError: If the method is not implemented in the subclass 
                         or specific overload.
"""
    raise NotImplementedError()
