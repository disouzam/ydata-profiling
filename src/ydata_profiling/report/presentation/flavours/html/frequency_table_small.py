from ydata_profiling.report.presentation.core import FrequencyTableSmall
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLFrequencyTableSmall(FrequencyTableSmall):
    def render(self) -> str:
        """
    Renders an HTML representation of a frequency table using the provided content.

    This method constructs an HTML string by iterating over the rows defined in 
    the object's content attribute. It uses a template to generate the HTML 
    for each row, while excluding the 'rows' key from the parameters passed 
    to the template.

    Returns:
        str: The generated HTML string representing the frequency table.

    Example:
        html_output = self.render()
    """
        html = ""
        kwargs = self.content.copy()
        del kwargs["rows"]

        for idx, rows in enumerate(self.content["rows"]):
            html += templates.template("frequency_table_small.html").render(
                rows=rows, idx=idx, **kwargs
            )
        return html
