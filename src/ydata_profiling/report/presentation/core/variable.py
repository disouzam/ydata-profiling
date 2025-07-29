from typing import Any, Callable, Optional

from ydata_profiling.report.presentation.core.item_renderer import ItemRenderer
from ydata_profiling.report.presentation.core.renderable import Renderable


class Variable(ItemRenderer):
    def __init__(
        self,
        top: Renderable,
        bottom: Optional[Renderable] = None,
        ignore: bool = False,
        **kwargs,
    ):
        """```python
def __init__(
    self,
    top: Renderable,
    bottom: Optional[Renderable] = None,
    ignore: bool = False,
    **kwargs,
):
    """
    Initializes a new instance of the class.

    Parameters:
    ----------
    top : Renderable
        The top part of the variable. This is a required parameter.
        
    bottom : Optional[Renderable], optional
        The bottom part of the variable. This parameter is optional and defaults to None.
        
    ignore : bool, optional
        A flag indicating whether to ignore certain conditions. Defaults to False.
        
    **kwargs : keyword arguments
        Additional keyword arguments to be passed to the superclass initialization.

    """
        super().__init__(
            "variable", {"top": top, "bottom": bottom, "ignore": ignore}, **kwargs
        )

    def __str__(self):
        """```python
def __str__(self):
    """
    Returns a string representation of the object.

    The string representation includes the 'top' and 'bottom' content from 
    the object's 'content' attribute. Each line in the 'top' and 'bottom' 
    content is indented for better readability. The output format is as follows:

    - Variable
      - top: {top_content}
      - bottom: {bottom_content}

    where {top_content} and {bottom_content} are the indented string 
    representations of the respective contents. 

    Returns:
        str: A formatted string representing the contents of the object.
    """
    top_text = str(self.content["top"]).replace("\n", "\n\t")
    bottom_text = str(self.content["bottom"]).replace("\n", "\n\t")

    text = "Variable\n"
    text += f"- top: {top_text}"
    text += f"- bottom: {bottom_text}"
    return text"""
        top_text = str(self.content["top"]).replace("\n", "\n\t")
        bottom_text = str(self.content["bottom"]).replace("\n", "\n\t")

        text = "Variable\n"
        text += f"- top: {top_text}"
        text += f"- bottom: {bottom_text}"
        return text

    def __repr__(self):
        """
    Return a string representation of the Variable instance.

    This method is intended to provide a concise representation of the object,
    which can be useful for debugging and logging purposes. The output will be
    a simple string indicating the type of the object.

    Returns:
        str: A string representation of the Variable instance.
    """
    return "Variable"""
        return "Variable"

    def render(self) -> Any:
        """```python
def render(self) -> Any:
    """
    Render a representation of the object.

    This method must be implemented by subclasses. It is intended to
    provide a specific rendering logic for the object. 

    Raises:
        NotImplementedError: If the method is not implemented in a
        subclass.
    
    Returns:
        Any: The rendered representation of the object.
    """
    raise NotImplementedError()"""
        raise NotImplementedError()

    @classmethod
    def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
        """def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
    """
    Converts the given object to an instance of the specified class.

    This method modifies the object's class to be the class from which 
    this method is called. Additionally, it checks the 'content' attribute
    of the object for 'top' and 'bottom' keys. If these keys exist and 
    their corresponding values are not None, a provided callable is invoked
    with these values.

    Parameters:
    cls: The class to convert the object to.
    obj (Renderable): The object to be converted.
    flv (Callable): A callable to be applied to the 'top' and 'bottom' 
                    values if they exist in the object's content.

    Returns:
    None
    """
        obj.__class__ = cls
        if "top" in obj.content and obj.content["top"] is not None:
            flv(obj.content["top"])
        if "bottom" in obj.content and obj.content["bottom"] is not None:
            flv(obj.content["bottom"])
