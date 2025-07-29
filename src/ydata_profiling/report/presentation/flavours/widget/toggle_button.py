from ipywidgets import widgets

from ydata_profiling.report.presentation.core import ToggleButton


class WidgetToggleButton(ToggleButton):
    def render(self) -> widgets.HBox:
        """
    Renders a horizontal box container with a toggle button.

    The toggle button is created using the description provided in the
    'content' attribute of the class instance. The layout of the toggle
    button and the containing box is configured to align items to the
    end and to display them in a column format, ensuring the width 
    spans the full width of the parent container.

    Returns:
        widgets.HBox: A horizontal box widget containing the toggle button.
    """
        toggle = widgets.ToggleButton(description=self.content["text"])
        toggle.layout.width = "fit-content"

        toggle_box = widgets.HBox([toggle])
        toggle_box.layout.align_items = "flex-end"
        toggle_box.layout.display = "flex"
        toggle_box.layout.flex_flow = "column"
        toggle_box.layout.width = "100%"

        return toggle_box
