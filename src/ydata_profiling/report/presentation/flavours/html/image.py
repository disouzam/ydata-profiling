from ydata_profiling.report.presentation.core import Image
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLImage(Image):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders the content into an HTML template.

    This method utilizes the specified HTML template ("diagram.html") 
    and renders it with the content provided in the instance's 
    'content' attribute. The content is unpacked as keyword arguments 
    into the template.

    Returns:
        str: The rendered HTML as a string.
    """
    return templates.template("diagram.html").render(**self.content)"""
        return templates.template("diagram.html").render(**self.content)
