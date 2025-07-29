from ydata_profiling.report.presentation.core import HTML


class HTMLHTML(HTML):
    def render(self) -> str:
        """
    Render the HTML content.

    This method retrieves the HTML content from the object's `content` attribute.

    Returns:
        str: The HTML content as a string.
    """
    return self.content["html"]"""
        return self.content["html"]
