from typing import List, Optional, TypeVar

from multimethod import multimethod
from pydantic.v1 import BaseModel

from ydata_profiling.config import Settings

T = TypeVar("T")  # type: ignore


class Sample(BaseModel):
    id: str
    data: T  # type: ignore
    name: str
    caption: Optional[str] = None


@multimethod
def get_sample(config: Settings, df: T) -> List[Sample]:
    """
    Retrieves a sample based on the given settings and dataframe.

    This function is intended to be implemented in subclasses or 
    specific use cases. It raises a NotImplementedError if called 
    directly.

    Args:
        config (Settings): The settings configuration to guide the 
                           sampling process.
        df (T): The input dataframe from which samples will be drawn.

    Returns:
        List[Sample]: A list of sampled data points.

    Raises:
        NotImplementedError: When called directly without an implementation.
    """
    raise NotImplementedError()"""
    raise NotImplementedError()


def get_custom_sample(sample: dict) -> List[Sample]:
    """
    Generates a list containing a custom Sample object based on the provided input dictionary.

    This function checks if the keys 'name' and 'caption' are present in the input dictionary 
    (sample). If not, it assigns them a value of None. It then creates a Sample object using 
    the data from the provided dictionary and returns it as a single-item list.

    Parameters:
    sample (dict): A dictionary containing at least the 'data' key, with optional 'name' 
                   and 'caption' keys.

    Returns:
    List[Sample]: A list containing a single Sample object created from the input dictionary. 
                   The Sample will have an id of 'custom'.
    """
    if "name" not in sample:
        sample["name"] = None
    if "caption" not in sample:
        sample["caption"] = None

    samples = [
        Sample(
            id="custom",
            data=sample["data"],
            name=sample["name"],
            caption=sample["caption"],
        )
    ]
    return samples
