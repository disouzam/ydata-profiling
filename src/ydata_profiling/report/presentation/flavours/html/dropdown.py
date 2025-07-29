from ydata_profiling.report.presentation.core import Dropdown
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLDropdown(Dropdown):
    def render(self) -> str:
        """
    Renders a dropdown HTML template using the provided content.

    This method utilizes the 'dropdown.html' template and fills it with 
    the content stored in the instance's `content` attribute.

    Returns:
        str: The rendered HTML as a string.
    """
    return templates.template("dropdown.html").render(**self.content)"""
        return templates.template("dropdown.html").render(**self.content)
