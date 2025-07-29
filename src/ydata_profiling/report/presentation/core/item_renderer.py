from abc import ABC
from typing import Optional

from ydata_profiling.report.presentation.core.renderable import Renderable


class ItemRenderer(Renderable, ABC):
    def __init__(
        self,
        item_type: str,
        content: dict,
        name: Optional[str] = None,
        anchor_id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """self,
    item_type: str,
    content: dict,
    name: Optional[str] = None,
    anchor_id: Optional[str] = None,
    classes: Optional[str] = None,
):
    """
    Initializes an instance of the class.

    Parameters:
    - item_type (str): The type of the item being created.
    - content (dict): A dictionary containing the content associated with the item.
    - name (Optional[str]): An optional name for the item. Defaults to None.
    - anchor_id (Optional[str]): An optional anchor ID for the item. Defaults to None.
    - classes (Optional[str]): An optional string of CSS classes for styling. Defaults to None.

    This constructor calls the parent class's initializer with the given content, name, 
    anchor_id, and classes while setting the item_type for the instance.
    """
    super().__init__(content, name, anchor_id, classes)
    self.item_type = item_type"""
        super().__init__(content, name, anchor_id, classes)
        self.item_type = item_type
