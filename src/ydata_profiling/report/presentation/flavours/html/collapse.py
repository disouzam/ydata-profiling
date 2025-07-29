from ydata_profiling.report.presentation.core import Collapse
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLCollapse(Collapse):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders the content using the specified HTML template.

    This function utilizes the 'collapse.html' template and passes the
    content of the instance as keyword arguments to the template renderer.

    Returns:
        str: The rendered HTML as a string.
    """
    return templates.template("collapse.html").render(**self.content)"""
        return templates.template("collapse.html").render(**self.content)
