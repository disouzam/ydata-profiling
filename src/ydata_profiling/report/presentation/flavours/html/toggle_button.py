from ydata_profiling.report.presentation.core import ToggleButton
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLToggleButton(ToggleButton):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders a toggle button template.

    This method utilizes the specified template, "toggle_button.html", 
    and populates it with the content provided in the instance's 
    `self.content` dictionary. It returns the rendered HTML as a string.

    Returns:
        str: The rendered HTML of the toggle button template.
    """
    return templates.template("toggle_button.html").render(**self.content)"""
        return templates.template("toggle_button.html").render(**self.content)
