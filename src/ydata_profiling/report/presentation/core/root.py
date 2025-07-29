from typing import Any, Callable

from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.item_renderer import ItemRenderer
from ydata_profiling.report.presentation.core.renderable import Renderable


class Root(ItemRenderer):
    """
    Wrapper for the report.
    """

    def __init__(
        self, name: str, body: Renderable, footer: Renderable, style: Style, **kwargs
    ):
        """self, name: str, body: Renderable, footer: Renderable, style: Style, **kwargs
):
    """
    Initializes a report object with a specified name, body, footer, and style.

    Args:
        name (str): The name of the report.
        body (Renderable): The content to be displayed in the body of the report.
        footer (Renderable): The content to be displayed in the footer of the report.
        style (Style): The style configuration for the report presentation.
        **kwargs: Additional keyword arguments that may be passed to the parent class.

    This constructor calls the parent class with a specified type "report"
    and a dictionary containing the body, footer, and style for proper 
    rendering of the report.
    """
        super().__init__(
            "report",
            {"body": body, "footer": footer, "style": style},
            name=name,
            **kwargs
        )

    def __repr__(self) -> str:
        """```python
def __repr__(self) -> str:
    """
    Returns a string representation of the object.

    This method returns the string "Root", indicating the 
    representation of the root object.

    Returns:
        str: A string representation of the object, specifically "Root".
    """
    return "Root"""
        return "Root"

    def render(self, **kwargs) -> Any:
        """```python
def render(self, **kwargs) -> Any:
    """
    Renders the output based on the provided keyword arguments.

    This method is intended to be overridden in subclasses. It raises
    a NotImplementedError if called directly on the base class.

    Args:
        **kwargs: Arbitrary keyword arguments passed to the render method.

    Returns:
        Any: The output of the render operation, the specific type is
        determined by subclasses.

    Raises:
        NotImplementedError: If the method is not implemented in a subclass.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()

    @classmethod
    def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
        """def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
    """
    Converts the given object to an instance of the class.

    This method modifies the __class__ attribute of the provided object 
    to the class from which this method is called. It also applies the 
    provided callable function `flv` to the 'body' and 'footer' if they 
    exist in the object's content.

    Args:
        cls: The class to which the object will be converted.
        obj (Renderable): The object to be converted to the class type.
        flv (Callable): A function to be applied to the object's content, 
                        specifically to 'body' and 'footer' if present.

    Returns:
        None: This method modifies the object in place and does not return 
              a value.
    """
        obj.__class__ = cls
        if "body" in obj.content:
            flv(obj.content["body"])
        if "footer" in obj.content:
            flv(obj.content["footer"])
