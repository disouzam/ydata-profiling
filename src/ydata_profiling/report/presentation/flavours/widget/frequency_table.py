from typing import List, Tuple

from ipywidgets import GridspecLayout, VBox, widgets

from ydata_profiling.report.presentation.core.frequency_table import FrequencyTable


def get_table(
    items: List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]
) -> VBox:
    """items: List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]
) -> VBox:
    """
    Creates a vertical box (VBox) layout containing a table of items.

    Each item is represented as a tuple consisting of:
        - A label (widgets.Label): The label to be displayed.
        - A progress bar (widgets.FloatProgress): The progress indicator.
        - A count label (widgets.Label): The count associated with the item.

    The function organizes the provided items into a grid layout (GridspecLayout),
    where each row corresponds to an item and holds the label, progress bar, and count.

    Args:
        items (List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]): 
            A list of tuples, each containing a label, a progress bar, and a count label.

    Returns:
        VBox: A VBox containing the table of items arranged in rows.
    """
    table = GridspecLayout(len(items), 3)
    for row_id, (label, progress, count) in enumerate(items):
        table[row_id, 0] = label
        table[row_id, 1] = progress
        table[row_id, 2] = count

    return VBox([table])


class WidgetFrequencyTable(FrequencyTable):
    def render(self) -> VBox:
        """
    Renders a table of progress bars based on the provided content.

    The function processes the 'rows' data from the 'content' attribute and creates a list of items,
    where each item consists of a label, a progress bar, and a count label. The appearance of the progress
    bar is customized based on the 'extra_class' attribute of each row, allowing for different styles 
    such as 'danger', 'info', or a default style.

    Returns:
        VBox: A VBox containing the rendered table with progress bars.

    The `rows` data structure is expected to be a list of dictionaries, where each dictionary contains:
        - 'label': A string representing the label associated with the progress bar.
        - 'count': A float representing the current value of the progress bar.
        - 'n': A float representing the maximum value for the progress bar.
        - 'extra_class': A string used to determine the style of the progress bar (e.g., 'missing', 'other').
    """
    items = []

    rows = self.content["rows"][0]
    for row in rows:
        if row["extra_class"] == "missing":
            items.append(
                (
                    widgets.Label(str(row["label"])),
                    widgets.FloatProgress(
                        value=row["count"], min=0, max=row["n"], bar_style="danger"
                    ),
                    widgets.Label(str(row["count"])),
                )
            )
        elif row["extra_class"] == "other":
            items.append(
                (
                    widgets.Label(str(row["label"])),
                    widgets.FloatProgress(
                        value=row["count"], min=0, max=row["n"], bar_style="info"
                    ),
                    widgets.Label(str(row["count"])),
                )
            )
        else:
            items.append(
                (
                    widgets.Label(str(row["label"])),
                    widgets.FloatProgress(
                        value=row["count"], min=0, max=row["n"], bar_style=""
                    ),
                    widgets.Label(str(row["count"])),
                )
            )

    return get_table(items)"""
        items = []

        rows = self.content["rows"][0]
        for row in rows:
            if row["extra_class"] == "missing":
                items.append(
                    (
                        widgets.Label(str(row["label"])),
                        widgets.FloatProgress(
                            value=row["count"], min=0, max=row["n"], bar_style="danger"
                        ),
                        widgets.Label(str(row["count"])),
                    )
                )
            elif row["extra_class"] == "other":
                items.append(
                    (
                        widgets.Label(str(row["label"])),
                        widgets.FloatProgress(
                            value=row["count"], min=0, max=row["n"], bar_style="info"
                        ),
                        widgets.Label(str(row["count"])),
                    )
                )
            else:
                items.append(
                    (
                        widgets.Label(str(row["label"])),
                        widgets.FloatProgress(
                            value=row["count"], min=0, max=row["n"], bar_style=""
                        ),
                        widgets.Label(str(row["count"])),
                    )
                )

        return get_table(items)
