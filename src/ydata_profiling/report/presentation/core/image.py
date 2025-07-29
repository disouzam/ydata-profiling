from typing import Any, Optional

from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.core.item_renderer import ItemRenderer


class Image(ItemRenderer):
    def __init__(
        self,
        image: str,
        image_format: ImageType,
        alt: str,
        caption: Optional[str] = None,
        **kwargs,
    ):
        """```python
def __init__(
    self,
    image: str,
    image_format: ImageType,
    alt: str,
    caption: Optional[str] = None,
    **kwargs,
):
    """
    Initializes an instance of the class.

    Args:
        image (str): The path or URL of the image. Must not be None.
        image_format (ImageType): The format of the image (e.g., JPEG, PNG).
        alt (str): Alternative text for the image, used for accessibility.
        caption (Optional[str]): Caption for the image. Defaults to None.
        **kwargs: Additional keyword arguments.

    Raises:
        ValueError: If the image parameter is None.

    """
        if image is None:
            raise ValueError(f"Image may not be None (alt={alt}, caption={caption})")

        super().__init__(
            "image",
            {
                "image": image,
                "image_format": image_format,
                "alt": alt,
                "caption": caption,
            },
            **kwargs,
        )

    def __repr__(self) -> str:
        """
    Return a string representation of the Image object.

    This method provides a concise description of the Image instance
    when it is printed or represented in the console, returning the 
    string "Image". 

    Returns:
        str: A string that indicates the type of the object.
    """
    return "Image"""
        return "Image"

    def render(self) -> Any:
        """```python
def render(self) -> Any:
    """
    Render the output for the current object.

    This method is intended to be overridden by subclasses. It 
    should implement the logic for rendering the specific 
    representation of the object. Calling this method without 
    overriding will raise a NotImplementedError.

    Returns:
        Any: The rendered output of the object.
    
    Raises:
        NotImplementedError: If the method is not overridden in a subclass.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()
