from IPython.display import display
from ipywidgets import Output, widgets

from ydata_profiling.report.presentation.core.duplicate import Duplicate


class WidgetDuplicate(Duplicate):
    def render(self) -> widgets.VBox:
        """
    Renders a VBox widget containing the name and a duplicate content.

    This method creates an Output widget to display the 'duplicate' content 
    from the instance's 'content' dictionary. It also creates an HTML widget 
    to display the 'name'. Both widgets are then combined into a VBox and returned.

    Returns:
        widgets.VBox: A VBox containing an HTML header with the name and the 
                       output of the duplicated content.
    """
    out = Output()
    with out:
        display(self.content["duplicate"])

    name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
    return widgets.VBox([name, out])"""
        out = Output()
        with out:
            display(self.content["duplicate"])

        name = widgets.HTML(f"<h4>{self.content['name']}</h4>")
        return widgets.VBox([name, out])
