from typing import List

from ipywidgets import widgets

from ydata_profiling.report.presentation.core.container import Container
from ydata_profiling.report.presentation.core.renderable import Renderable


def get_name(item: Renderable) -> str:
    """
    Retrieves the name of a given Renderable item.

    This function checks if the item has a 'name' attribute. If it does, 
    it returns the value of this attribute. Otherwise, it returns the 
    'anchor_id' attribute of the item.

    Parameters:
    item (Renderable): The Renderable item from which to retrieve the name.

    Returns:
    str: The name of the item if it exists, otherwise the anchor_id.
    """
    if hasattr(item, "name"):
        return item.name
    else:
        return item.anchor_id


def get_tabs(items: List[Renderable]) -> widgets.Tab:
    """
    Creates a Tab widget containing rendered items.

    This function accepts a list of Renderable items, renders each item,
    and organizes them into a Tab widget with corresponding titles.

    Args:
        items (List[Renderable]): A list of Renderable objects to be added as tabs.

    Returns:
        widgets.Tab: A Tab widget containing the rendered items as its children,
                     with each tab titled according to the name obtained from 
                     the Renderable objects.

    Example:
        >>> tab_widget = get_tabs([item1, item2, item3])
    """
    children = []
    titles = []
    for item in items:
        children.append(item.render())
        titles.append(get_name(item))

    tab = widgets.Tab()
    tab.children = children
    for id, title in enumerate(titles):
        tab.set_title(id, title)
    return tab


def get_list(items: List[Renderable]) -> widgets.VBox:
    """
    Generates a vertical box widget containing rendered items.

    Args:
        items (List[Renderable]): A list of Renderable objects to be rendered.

    Returns:
        widgets.VBox: A VBox widget containing the rendered outputs of the provided items.
    """
    return widgets.VBox([item.render() for item in items])


def get_named_list(items: List[Renderable]) -> widgets.VBox:
    """
    Creates a vertical box (VBox) containing items with their respective names rendered in HTML.

    Each item in the input list is wrapped in a VBox, where the name of the item is displayed 
    in bold using HTML, followed by the rendered representation of the item.

    Parameters:
        items (List[Renderable]): A list of Renderable items to be displayed.

    Returns:
        widgets.VBox: A VBox widget containing the named items.
    """
    return widgets.VBox(
        [
            widgets.VBox(
                [widgets.HTML(f"<strong>{get_name(item)}</strong>"), item.render()]
            )
            for item in items
        ]
    )"""
    return widgets.VBox(
        [
            widgets.VBox(
                [widgets.HTML(f"<strong>{get_name(item)}</strong>"), item.render()]
            )
            for item in items
        ]
    )


def get_row(items: List[Renderable]) -> widgets.GridBox:
    """
    Creates a GridBox layout containing the specified Renderable items.

    The function arranges the items into a grid layout based on the number of items provided. 
    It supports layouts for 1 to 4 items and raises a ValueError for any other number of items.

    Parameters:
    items (List[Renderable]): A list of Renderable items to be displayed in the grid.

    Returns:
    widgets.GridBox: A GridBox widget containing the rendered items arranged in the specified layout.

    Raises:
    ValueError: If the number of items exceeds 4, as the layout is undefined for 
                more than 4 columns.
    
    Example:
    >>> get_row([item1, item2])  # Returns a GridBox with 2 items, each occupying 50% width.
    """
    if len(items) == 1:
        layout = widgets.Layout(width="100%", grid_template_columns="100%")
    elif len(items) == 2:
        layout = widgets.Layout(width="100%", grid_template_columns="50% 50%")
    elif len(items) == 3:
        layout = widgets.Layout(width="100%", grid_template_columns="25% 25% 50%")
    elif len(items) == 4:
        layout = widgets.Layout(width="100%", grid_template_columns="25% 25% 25% 25%")
    else:
        raise ValueError("Layout undefined for this number of columns")

    return widgets.GridBox([item.render() for item in items], layout=layout)


def get_batch_grid(
    items: List[Renderable], batch_size: int, titles: bool, subtitles: bool
) -> widgets.GridBox:
    """items: List[Renderable], batch_size: int, titles: bool, subtitles: bool
) -> widgets.GridBox:
    """
    Create a grid layout of renderable items.

    This function generates a GridBox containing items arranged in a grid format, 
    based on the specified batch size. It provides an option to include titles 
    or subtitles for each item.

    Parameters:
    ----------
    items : List[Renderable]
        A list of renderable items to be displayed in the grid.
        
    batch_size : int
        The number of items to display per row in the grid.
        
    titles : bool
        Flag to indicate if item names should be displayed as titles (h4).
        
    subtitles : bool
        Flag to indicate if item names should be displayed as subtitles (h5).

    Returns:
    -------
    widgets.GridBox
        A GridBox widget containing the organized renderable items.

    Notes:
    -----
    The function utilizes the `widgets` module to create an interactive grid layout. 
    The layout adjusts based on the specified `batch_size`, and the display style 
    of each item (either with titles, subtitles, or without) is controlled by the 
    corresponding boolean parameters.
    """
    layout = widgets.Layout(
        width="100%",
        grid_template_columns=" ".join([f"{int(100 / batch_size)}%"] * batch_size),
    )
    out = []
    for item in items:
        if subtitles:
            out.append(
                widgets.VBox(
                    [widgets.HTML(f"<h5><em>{ item.name }</em></h5>"), item.render()]
                )
            )
        elif titles:
            out.append(
                widgets.VBox([widgets.HTML(f"<h4>{ item.name }</h4>"), item.render()])
            )
        else:
            out.append(item.render())

    return widgets.GridBox(out, layout=layout)


def get_accordion(items: List[Renderable]) -> widgets.Accordion:
    """
    Create an accordion widget containing rendered items.

    This function takes a list of renderable items, renders each item, and 
    creates an Accordion widget where the titles are derived from the names 
    of the items. Each rendered item is added as a child to the Accordion.

    Parameters:
    -----------
    items : List[Renderable]
        A list of items that implement the Renderable interface and have a 
        corresponding name. Each item will be rendered and displayed in the 
        accordion.

    Returns:
    --------
    widgets.Accordion
        An Accordion widget populated with the rendered items and their 
        respective titles.

    Example:
    ---------
    >>> items = [Item1(), Item2()]  # Assuming Item1 and Item2 are Renderable objects
    >>> accordion = get_accordion(items)
    >>> display(accordion)  # Displays the accordion widget with Item1 and Item2
    """
    children = []
    titles = []
    for item in items:
        children.append(item.render())
        titles.append(get_name(item))

    accordion = widgets.Accordion(children=children)
    for id, title in enumerate(titles):
        accordion.set_title(id, title)

    return accordion


class WidgetContainer(Container):
    def render(self) -> widgets.Widget:
        """
    Render a widget based on the specified sequence type.

    This method creates a widget from the content provided in the instance's 
    `content` attribute, which is expected to be a dictionary containing
    an 'items' key. The type of widget rendered depends on the value of
    the `sequence_type` attribute.

    The following sequence types are supported:
    
    - "list": Renders a simple list widget.
    - "named_list": Renders a named list widget.
    - "tabs", "sections", or "select": Renders a tabbed interface widget.
    - "accordion": Renders an accordion widget.
    - "grid": Renders a grid widget.
    - "batch_grid": Renders a batch grid widget, with additional options for
      titles and subtitles.

    Raises:
        ValueError: If the `sequence_type` is not recognized.

    Returns:
        widgets.Widget: The rendered widget based on the specified sequence type.
    """
        if self.sequence_type == "list":
            widget = get_list(self.content["items"])
        elif self.sequence_type == "named_list":
            widget = get_named_list(self.content["items"])
        elif self.sequence_type in ["tabs", "sections", "select"]:
            widget = get_tabs(self.content["items"])
        elif self.sequence_type == "accordion":
            widget = get_accordion(self.content["items"])
        elif self.sequence_type == "grid":
            widget = get_row(self.content["items"])
        elif self.sequence_type == "batch_grid":
            widget = get_batch_grid(
                self.content["items"],
                self.content["batch_size"],
                self.content.get("titles", True),
                self.content.get("subtitles", False),
            )
        else:
            raise ValueError("widget type not understood", self.sequence_type)

        return widget
