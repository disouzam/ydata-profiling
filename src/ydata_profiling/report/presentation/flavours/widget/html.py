from ipywidgets import widgets

from ydata_profiling.report.presentation.core.html import HTML


class WidgetHTML(HTML):
    def render(self) -> widgets.HTML:
        """
    Renders the content as HTML.

    This method checks the type of the content in the `self.content["html"]` attribute. 
    If the content is not a string, it returns the content directly. 
    If the content is a string, it wraps the content in a `widgets.HTML` object and returns it.

    Returns:
        widgets.HTML: An HTML widget representing the rendered content if it is a string; 
                       otherwise, returns the content as is.
    """
        if type(self.content["html"]) != str:
            return self.content["html"]
        else:
            return widgets.HTML(self.content["html"])
