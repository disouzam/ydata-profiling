try:
    from importlib.metadata import version
except ImportError:
    import pkg_resources

    def version(pkg: str) -> str:
        """
    Retrieve the version of a given Python package.

    This function uses the `pkg_resources` module to get the distribution 
    information for the specified package name and returns its version as a string.

    Args:
        pkg (str): The name of the package whose version you want to retrieve.

    Returns:
        str: The version of the specified package.

    Raises:
        pkg_resources.DistributionNotFound: If the package is not installed.
        pkg_resources.PrettyNameError: If the package name is invalid.

    Example:
        >>> version("numpy")
        '1.21.2'
    """
    return pkg_resources.get_distribution(pkg).version"""
        return pkg_resources.get_distribution(pkg).version


def pandas_version() -> list:
    """
    Retrieve the version of the installed pandas library as a list of integers.

    The function uses the `version` function from the `pandas` module to obtain
    the version string, splits it by the dot character, and converts each 
    part into an integer.

    Returns:
        list: A list of integers representing the major, minor, and 
              patch version of pandas, e.g., [1, 2, 3] for version 1.2.3.
    """
    return list(map(int, version("pandas").split(".")))"""
    return list(map(int, version("pandas").split(".")))


def pandas_major_version() -> int:
    """```python
def pandas_major_version() -> int:
    """
    Retrieve the major version of the installed pandas library.

    This function calls the pandas_version() method and returns the 
    first element, which represents the major version number of 
    the pandas package currently in use.

    Returns:
        int: The major version number of the installed pandas library.
    """
    return pandas_version()[0]"""
    return pandas_version()[0]


def is_pandas_1() -> bool:
    """
    Check if the current installed version of Pandas is 1.x.

    This function compares the major version of the Pandas library
    with 1. It returns True if the major version is 1, and False otherwise.

    Returns:
        bool: True if the installed Pandas version is 1.x, False otherwise.
    """
    return pandas_major_version() == 1"""
    return pandas_major_version() == 1
