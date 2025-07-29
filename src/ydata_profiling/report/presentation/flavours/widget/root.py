from ipywidgets import widgets

from ydata_profiling.report.presentation.core.root import Root


class WidgetRoot(Root):
    def render(self, **kwargs) -> widgets.VBox:
        """
    Renders the content of the widget as a VBox.

    This method creates a VBox layout containing the rendered body 
    and footer of the widget. It uses the `render` method of both 
    the body and footer contents to display them in a vertical stack.

    Args:
        **kwargs: Additional keyword arguments that may be passed to 
        the render function (currently unused in this implementation).

    Returns:
        widgets.VBox: A VBox containing the rendered body and footer.
    """
    return widgets.VBox(
        [self.content["body"].render(), self.content["footer"].render()]
    )"""
        return widgets.VBox(
            [self.content["body"].render(), self.content["footer"].render()]
        )
