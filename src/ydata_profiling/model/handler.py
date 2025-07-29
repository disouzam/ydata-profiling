from functools import reduce
from typing import Any, Callable, Dict, List, Sequence

import networkx as nx
from visions import VisionsTypeset


def compose(functions: Sequence[Callable]) -> Callable:
    """
    Compose a sequence of functions
    :param functions: sequence of functions
    :return: combined functions, e.g. [f(x), g(x)] -> g(f(x))
    """

    def func(f: Callable, g: Callable) -> Callable:
        """
    Applies a function `f` conditionally based on the result of another function `g`.

    This higher-order function takes two callable arguments, `f` and `g`. It returns a new function 
    that applies `g` to the given arguments. If the result of `g` is a boolean, it directly applies 
    `f` to the same arguments. If the result of `g` is not a boolean, it applies `f` to the result 
    obtained from `g`.

    Parameters:
    f (Callable): A callable that will be applied based on the result of g.
    g (Callable): A callable whose result determines how f is applied.

    Returns:
    Callable: A new function that encapsulates the described conditional logic between f and g.

    Example:
    >>> def multiply_by_two(x):
    ...     return x * 2
    >>> def is_positive(x):
    ...     return x > 0
    >>> combined_func = func(multiply_by_two, is_positive)
    >>> combined_func(3)  # Returns 6 (since is_positive(3) is True)
    >>> combined_func(-3) # Returns -6 (since is_positive(-3) is False, it computes f(is_positive(-3)))
    """
    def func2(*x) -> Any:
        res = g(*x)
        if type(res) == bool:
            return f(*x)
        else:
            return f(*res)

    return func2"""
        def func2(*x) -> Any:
            res = g(*x)
            if type(res) == bool:
                return f(*x)
            else:
                return f(*res)

        return func2

    return reduce(func, reversed(functions), lambda *x: x)


class Handler:
    """A generic handler

    Allows any custom mapping between data types and functions
    """

    def __init__(
        self,
        mapping: Dict[str, List[Callable]],
        typeset: VisionsTypeset,
        *args,
        **kwargs
    ):
        """self,
    mapping: Dict[str, List[Callable]],
    typeset: VisionsTypeset,
    *args,
    **kwargs
):
    """
    Initializes an instance of the class.

    Parameters:
    mapping (Dict[str, List[Callable]]): A dictionary that maps strings to lists of callable objects.
    typeset (VisionsTypeset): An instance of VisionsTypeset that defines the typeset for the instance.
    *args: Variable length argument list for additional parameters.
    **kwargs: Variable length keyword arguments for additional configuration.

    This constructor also calls the private method _complete_dag() to complete the directed acyclic graph setup.
    """
        self.mapping = mapping
        self.typeset = typeset

        self._complete_dag()

    def _complete_dag(self) -> None:
        """
    Completes the directed acyclic graph (DAG) by updating the mapping of 
    types in the typeset's base graph. It processes the types in topological 
    order, combining the mappings of source and target types.

    This method uses a line graph representation of the base graph to 
    determine the order in which the types should be processed. It assumes 
    that the mapping attribute contains the necessary initial mappings 
    for the types.

    Returns:
        None: This method does not return a value, but modifies the 
        instance's mapping attribute in place.
    """
        for from_type, to_type in nx.topological_sort(
            nx.line_graph(self.typeset.base_graph)
        ):
            self.mapping[str(to_type)] = (
                self.mapping[str(from_type)] + self.mapping[str(to_type)]
            )

    def handle(self, dtype: str, *args, **kwargs) -> dict:
        """

        Returns:
            object:
        """
        funcs = self.mapping.get(dtype, [])
        op = compose(funcs)
        return op(*args)


def get_render_map() -> Dict[str, Callable]:
    """
    Generate a mapping of data types to their corresponding rendering functions.

    This function creates and returns a dictionary where the keys are 
    string representations of various data types and the values are 
    the corresponding rendering functions from the `ydata_profiling.report.structure.variables` module. 
    The supported data types include:

    - Boolean
    - Numeric
    - Complex
    - Text
    - DateTime
    - Categorical
    - URL
    - Path
    - File
    - Image
    - Unsupported
    - TimeSeries

    Returns:
        Dict[str, Callable]: A dictionary mapping data type names to their respective rendering functions.
    """
    import ydata_profiling.report.structure.variables as render_algorithms

    render_map = {
        "Boolean": render_algorithms.render_boolean,
        "Numeric": render_algorithms.render_real,
        "Complex": render_algorithms.render_complex,
        "Text": render_algorithms.render_text,
        "DateTime": render_algorithms.render_date,
        "Categorical": render_algorithms.render_categorical,
        "URL": render_algorithms.render_url,
        "Path": render_algorithms.render_path,
        "File": render_algorithms.render_file,
        "Image": render_algorithms.render_image,
        "Unsupported": render_algorithms.render_generic,
        "TimeSeries": render_algorithms.render_timeseries,
    }

    return render_map
