from ydata_profiling.report.presentation.core.table import Table
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLTable(Table):
    def render(self) -> str:
        """
    Renders an HTML table using the provided content.

    This method utilizes a template engine to generate an HTML representation 
    of a table, sourcing the data from the instance's `content` attribute.

    Returns:
        str: The rendered HTML string of the table.
    """
    return templates.template("table.html").render(**self.content)"""
        return templates.template("table.html").render(**self.content)
