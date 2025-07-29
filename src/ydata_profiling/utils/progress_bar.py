from functools import wraps
from typing import Any, Callable

from tqdm import tqdm


def progress(fn: Callable, bar: tqdm, message: str) -> Callable:
    """
    Decorator function that wraps a callable and updates a progress bar with a message
    after execution of the original function.

    Args:
        fn (Callable): The function to be decorated.
        bar (tqdm): A tqdm progress bar instance that will be updated.
        message (str): A message to be displayed alongside the progress bar.

    Returns:
        Callable: A new function that, when called, executes the original function and
                   updates the progress bar with the provided message.
    """
    @wraps(fn)
    def inner(*args, **kwargs) -> Any:
        bar.set_postfix_str(message)
        ret = fn(*args, **kwargs)
        bar.update()
        return ret

    return inner"""
    @wraps(fn)
    def inner(*args, **kwargs) -> Any:
        bar.set_postfix_str(message)
        ret = fn(*args, **kwargs)
        bar.update()
        return ret

    return inner
