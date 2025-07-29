from ipywidgets import widgets

from ydata_profiling.report.presentation.core import VariableInfo
from ydata_profiling.report.presentation.flavours.html import templates


class WidgetVariableInfo(VariableInfo):
    def render(self) -> widgets.HTML:
        """
    Renders an HTML widget using a template and the content of the instance.

    This method retrieves the HTML content from a template file called
    "variable_info.html" and fills it with the instance's content 
    using keyword arguments. It returns an HTML widget that can be
    displayed in a Jupyter notebook or similar environment.

    Returns:
        widgets.HTML: An HTML widget containing the rendered content.
    """
    return widgets.HTML(
        templates.template("variable_info.html").render(**self.content)
    )"""
        return widgets.HTML(
            templates.template("variable_info.html").render(**self.content)
        )
