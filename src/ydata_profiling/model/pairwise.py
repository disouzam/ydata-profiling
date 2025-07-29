from typing import Any, List, Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.visualisation.plot import scatter_pairwise


def get_scatter_tasks(
    config: Settings, continuous_variables: list
) -> List[Tuple[Any, Any]]:
    """config: Settings, continuous_variables: list
) -> List[Tuple[Any, Any]]:
    """
    Generate a list of scatter tasks based on the given configuration and continuous variables.

    A scatter task is defined as a pair (target, continuous variable). If the configuration does not allow 
    for continuous interactions or if there are no specified targets, it uses the continuous variables for 
    generating the tasks.

    Args:
        config (Settings): The configuration settings that determine the behavior of task generation.
        continuous_variables (list): A list of continuous variable names to be used in scatter tasks.

    Returns:
        List[Tuple[Any, Any]]: A list of tuples representing scatter tasks, where each tuple consists 
        of a target and a continuous variable. If no tasks can be generated, an empty list is returned.
    """
    if not config.interactions.continuous:
        return []

    targets = config.interactions.targets
    if len(targets) == 0:
        targets = continuous_variables

    tasks = [(x, y) for y in continuous_variables for x in targets]
    return tasks


def get_scatter_plot(
    config: Settings, df: pd.DataFrame, x: Any, y: Any, continuous_variables: list
) -> str:
    """```python
def get_scatter_plot(
    config: Settings, df: pd.DataFrame, x: Any, y: Any, continuous_variables: list
) -> str:
    """
    Generates a scatter plot for the given x and y variables if they are continuous.

    This function takes a DataFrame and checks if the specified x variable 
    is in the list of continuous variables. If y is the same as x, it creates 
    a temporary DataFrame with only the x variable. Otherwise, it includes both 
    x and y variables in the temporary DataFrame. It then calls the `scatter_pairwise` 
    function to generate the scatter plot.

    Parameters:
    - config (Settings): Configuration settings for the plot.
    - df (pd.DataFrame): The DataFrame containing the data.
    - x (Any): The variable to be plotted on the x-axis.
    - y (Any): The variable to be plotted on the y-axis.
    - continuous_variables (list): A list of variables that are considered continuous.

    Returns:
    - str: The result of the `scatter_pairwise` function call, or an empty string 
           if x is not a continuous variable.
    """
    if x in continuous_variables:
        if y == x:
            df_temp = df[[x]].dropna()
        else:
            df_temp = df[[x, y]].dropna()
        return scatter_pairwise(config, df_temp[x], df_temp[y], x, y)
    else:
        return ""
