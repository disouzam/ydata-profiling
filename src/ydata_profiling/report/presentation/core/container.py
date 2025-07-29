from typing import Any, Callable, Optional, Sequence

from ydata_profiling.report.presentation.core.renderable import Renderable


class Container(Renderable):
    def __init__(
        self,
        items: Sequence[Renderable],
        sequence_type: str,
        nested: bool = False,
        name: Optional[str] = None,
        anchor_id: Optional[str] = None,
        classes: Optional[str] = None,
        **kwargs,
    ):
        """self,
    items: Sequence[Renderable],
    sequence_type: str,
    nested: bool = False,
    name: Optional[str] = None,
    anchor_id: Optional[str] = None,
    classes: Optional[str] = None,
    **kwargs,
):
    """
    Initializes a new instance of the class.

    Args:
        items (Sequence[Renderable]): A sequence of renderable items to be processed.
        sequence_type (str): A string indicating the type of the sequence (e.g., 'ordered', 'unordered').
        nested (bool, optional): Indicates whether the items are nested. Defaults to False.
        name (Optional[str], optional): The name of the instance. Defaults to None.
        anchor_id (Optional[str], optional): An optional anchor ID for reference. Defaults to None.
        classes (Optional[str], optional): Optional CSS classes to apply to the instance. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the superclass initializer.

    This constructor initializes the base class with the provided arguments, 
    sets the sequence_type attribute, and prepares any additional context 
    specified through keyword arguments.
    """
        args = {"items": items, "nested": nested}
        args.update(**kwargs)
        super().__init__(args, name, anchor_id, classes)
        self.sequence_type = sequence_type

    def __str__(self) -> str:
        """
    Returns a string representation of the container.

    The string includes the designation 'Container' followed by a list of items 
    present in the container. Each item is prefixed with its index in the list.

    If the container contains items, they will be formatted with a new line 
    for each item, and any newline characters within the item's string 
    representation will be preceded by a tab to maintain readability.

    Returns:
        str: A formatted string representing the contents of the container.
    """
        text = "Container\n"
        if "items" in self.content:
            for id, item in enumerate(self.content["items"]):
                name = str(item).replace("\n", "\n\t")
                text += f"- {id}: {name}\n"
        return text

    def __repr__(self) -> str:
        """
    Return a string representation of the Container instance.

    The string representation includes the name of the container if it is 
    present in the content attribute. If the name is available, 
    it returns a formatted string containing the name. Otherwise, 
    it returns a generic representation.

    Returns:
        str: A string representation of the Container, 
             either in the form "Container(name=<name>)" 
             or "Container" if the name is not defined.
    """
        if "name" in self.content:
            name = self.content["name"]
            return f"Container(name={name})"
        else:
            return "Container"

    def render(self) -> Any:
        """```python
def render(self) -> Any:
    """
    Render the output for the current instance.

    This method should be implemented by subclasses to provide
    the specific rendering logic. Since this is a base method,
    calling it directly will raise a NotImplementedError.

    Returns:
        Any: The rendered output, the type will depend on the 
        specific implementation in the derived classes.

    Raises:
        NotImplementedError: If called directly from the base class
        without an overriding implementation.
    """
    raise NotImplementedError()
```"""
        raise NotImplementedError()

    @classmethod
    def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
        """```python
@classmethod
def convert_to_class(cls, obj: Renderable, flv: Callable) -> None:
    """
    Converts the class of the given object to the specified class.

    This method changes the class of the provided object to the class
    represented by `cls`. If the object's content contains an "items"
    key, it applies the given callable function `flv` to each item
    in the list of items.

    Parameters:
        cls: The class to which the object will be converted.
        obj (Renderable): The object whose class is being changed.
        flv (Callable): A callable function that will be applied to 
                        each item in the object's content, if present.

    Returns:
        None: This method does not return any value.

    Raises:
        TypeError: If `obj` is not an instance of `Renderable`.
    """
        obj.__class__ = cls
        if "items" in obj.content:
            for item in obj.content["items"]:
                flv(item)
