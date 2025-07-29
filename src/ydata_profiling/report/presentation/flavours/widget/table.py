from typing import Any, Dict, List

from ipywidgets import GridspecLayout, VBox, widgets

from ydata_profiling.report.formatters import fmt_color
from ydata_profiling.report.presentation.core.table import Table


def get_table(items: List[Dict[str, Any]]) -> GridspecLayout:
    """
    Creates a table layout displaying the names and values of items.

    Args:
        items (List[Dict[str, Any]]): A list of dictionaries where each dictionary
                                        contains the following keys:
                                        - 'name': A string representing the name of the item.
                                        - 'value': A string representing the value of the item.
                                        - 'alert': An optional boolean indicating if the item
                                                   should be highlighted (default is False).

    Returns:
        GridspecLayout: A layout object containing the formatted names and values
                        arranged in a table format. If an item has an 'alert' key set to True,
                        its name and value will be displayed in an error color.
    """
    table = GridspecLayout(len(items), 2)
    for row_id, item in enumerate(items):
        name = item["name"]
        value = item["value"]
        if "alert" in item and item["alert"]:
            name = fmt_color(name, "var(--jp-error-color1)")
            value = fmt_color(value, "var(--jp-error-color1)")

        table[row_id, 0] = widgets.HTML(name)
        table[row_id, 1] = widgets.HTML(value)

    return table


class WidgetTable(Table):
    def render(self) -> VBox:
        """
    Renders a VBox containing a table and an optional caption.

    This method constructs a vertical box (VBox) widget that includes a table generated
    from the provided rows in the content and an optional caption. If a caption is present
    in the content, it is displayed in italicized text below the table.

    Returns:
        VBox: A VBox object containing the table and the caption (if any).

    Example:
        vbox = self.render()
    """
        items = [get_table(self.content["rows"])]
        if self.content["caption"] is not None:
            items.append(widgets.HTML(f'<em>{self.content["caption"]}</em>'))

        return VBox(items)
