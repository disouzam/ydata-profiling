from ydata_profiling.report.presentation.core import FrequencyTable
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLFrequencyTable(FrequencyTable):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders an HTML representation of the content based on its structure.

    This method checks if the first element of the 'rows' in the content is a list.
    If it is a list, the method iterates over each row and renders a frequency table
    for each one, accumulating the results into a single HTML string. If the first 
    element is not a list, it renders a single frequency table using the entire content.

    Returns:
        str: The rendered HTML as a string.

    Raises:
        KeyError: If 'rows' key does not exist in 'self.content'.
        Exception: If rendering the template fails.
    """
        if isinstance(self.content["rows"][0], list):
            html = ""

            kwargs = self.content.copy()
            del kwargs["rows"]
            for idx, rows in enumerate(self.content["rows"]):
                html += templates.template("frequency_table.html").render(
                    rows=rows, idx=idx, **kwargs
                )
            return html
        else:
            return templates.template("frequency_table.html").render(
                **self.content, idx=0
            )
