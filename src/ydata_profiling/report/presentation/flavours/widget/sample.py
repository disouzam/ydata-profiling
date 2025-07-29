from IPython.display import display
from ipywidgets import Output, widgets

from ydata_profiling.report.presentation.core.sample import Sample


class WidgetSample(Sample):
    def render(self) -> widgets.VBox:
        """```python
def render(self) -> widgets.VBox:
    """
    Renders a vertical box widget containing the sample content and its name.

    This method creates a custom widget layout using a VBox layout from the 
    `widgets` module. It first initializes an output widget to display the 
    content labeled as 'sample' from the object's content dictionary. 
    Additionally, it creates an HTML widget to display the name from the 
    content dictionary. Finally, it combines both widgets into a VBox and 
    returns it.

    Returns:
        widgets.VBox: A VBox containing the formatted name and the output 
        of the sample content.
    """
    out = Output()
    with out:
        display(self.content["sample"])

    name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
    return widgets.VBox([name, out])"""
        out = Output()
        with out:
            display(self.content["sample"])

        name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
        return widgets.VBox([name, out])
