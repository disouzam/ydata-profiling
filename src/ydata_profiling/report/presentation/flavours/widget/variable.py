from ipywidgets import widgets

from ydata_profiling.report.presentation.core import Variable


class WidgetVariable(Variable):
    def render(self) -> widgets.VBox:
        """```python
def render(self) -> widgets.VBox:
    """
    Renders the top and bottom content into a vertical box layout.

    This method constructs a list of items by rendering the 'top' content 
    from the `self.content` dictionary. If the 'bottom' content is present 
    (not None), it is also rendered and added to the list of items. Finally, 
    the items are organized into a VBox layout using the widgets library.

    Returns:
        widgets.VBox: A VBox widget containing the rendered top and optional 
                      bottom content.
    """
        items = [self.content["top"].render()]
        if self.content["bottom"] is not None:
            items.append(self.content["bottom"].render())

        return widgets.VBox(items)
