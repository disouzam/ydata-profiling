from ydata_profiling.report.presentation.core import Variable
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLVariable(Variable):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders the HTML template with the provided content.

    This method utilizes a template engine to generate an HTML string by 
    rendering a specified template file ('variable.html') with the 
    attributes contained in the 'content' attribute of the instance.

    Returns:
        str: The rendered HTML as a string.
    """
    return templates.template("variable.html").render(**self.content)"""
        return templates.template("variable.html").render(**self.content)
