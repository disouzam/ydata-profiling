from ydata_profiling.report.presentation.core import VariableInfo
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLVariableInfo(VariableInfo):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders an HTML template with the given content.

    This method utilizes the 'variable_info.html' template and fills it 
    with content from the instance's 'self.content' attribute. The content 
    is passed as keyword arguments to the template renderer.

    Returns:
        str: The rendered HTML as a string.
    """
    return templates.template("variable_info.html").render(**self.content)"""
        return templates.template("variable_info.html").render(**self.content)
