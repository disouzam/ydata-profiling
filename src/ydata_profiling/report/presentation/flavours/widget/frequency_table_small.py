from typing import List

from ipywidgets import widgets

from ydata_profiling.report.presentation.core.frequency_table_small import (
    FrequencyTableSmall,
)


class WidgetFrequencyTableSmall(FrequencyTableSmall):
    def render(self) -> widgets.VBox:
        """```python
def render(self) -> widgets.VBox:
    """
    Renders the content as a VBox widget.

    This method utilizes the `frequency_table_nb` function to generate 
    a frequency table from the rows contained in the `content` attribute. 
    The resulting frequency table is returned as a VBox widget.

    Returns:
        widgets.VBox: A VBox widget containing the rendered frequency table.
    """
    return frequency_table_nb(self.content["rows"])"""
        return frequency_table_nb(self.content["rows"])


def frequency_table_nb(rows: List[List[dict]]) -> widgets.VBox:
    """
    Generates a frequency table represented as a vertical box of progress bars, 
    based on the provided data.

    Each entry in the frequency table displays a progress bar that represents the count 
    of occurrences for various labels. The appearance of the progress bar is determined 
    by the "extra_class" attribute of the data, categorizing the count into three styles: 
    "missing", "other", or default.

    Args:
        rows (List[List[dict]]): A list of lists containing dictionaries with the following keys:
            - "extra_class": A string indicating the category of the count ("missing", "other", etc.).
            - "count": An integer representing the count of occurrences.
            - "n": An integer indicating the maximum value for the progress bar.
            - "label": A string to describe the progress bar in the UI.

    Returns:
        widgets.VBox: A VBox widget containing HBox widgets for each frequency representation. 
                       Each HBox includes a progress bar and a label displaying the count.
    """
    items = []

    fq_rows = rows[0]
    for row in fq_rows:
        if row["extra_class"] == "missing":
            items.append(
                widgets.HBox(
                    [
                        widgets.FloatProgress(
                            value=row["count"],
                            min=0,
                            max=row["n"],
                            description=str(row["label"]),
                            bar_style="danger",
                        ),
                        widgets.Label(str(row["count"])),
                    ]
                )
            )
        elif row["extra_class"] == "other":
            items.append(
                widgets.HBox(
                    [
                        widgets.FloatProgress(
                            value=row["count"],
                            min=0,
                            max=row["n"],
                            description=str(row["label"]),
                            bar_style="info",
                        ),
                        widgets.Label(str(row["count"])),
                    ]
                )
            )
        else:
            items.append(
                widgets.HBox(
                    [
                        widgets.FloatProgress(
                            value=row["count"],
                            min=0,
                            max=row["n"],
                            description=str(row["label"]),
                            bar_style="",
                        ),
                        widgets.Label(str(row["count"])),
                    ]
                )
            )

    return widgets.VBox(items)
