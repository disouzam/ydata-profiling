from IPython.display import display
from ipywidgets import Output, widgets

from ydata_profiling.report.presentation.core.correlation_table import CorrelationTable


class WidgetCorrelationTable(CorrelationTable):
    def render(self) -> widgets.VBox:
        """
    Renders a VBox widget containing a title and a correlation matrix.

    This method creates a VBox layout that includes an HTML widget for the title 
    and an Output widget that displays the correlation matrix contained 
    in the object's content. The correlation matrix is displayed when 
    this method is called.

    Returns:
        widgets.VBox: A VBox containing the title and correlation matrix 
        displayed as an output widget.
    """
    out = Output()
    with out:
        display(self.content["correlation_matrix"])

    name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
    return widgets.VBox([name, out])"""
        out = Output()
        with out:
            display(self.content["correlation_matrix"])

        name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
        return widgets.VBox([name, out])
