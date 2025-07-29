from ydata_profiling.report.presentation.core.correlation_table import CorrelationTable
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLCorrelationTable(CorrelationTable):
    def render(self) -> str:
        """
    Renders an HTML representation of a correlation matrix.

    This method generates an HTML table of the correlation matrix 
    stored in the instance's content. It formats the correlation values 
    to three decimal places and applies specified CSS classes for styling.

    Returns:
        str: The rendered HTML output for the correlation matrix table 
             embedded in a specified template.
    """
    correlation_matrix_html = self.content["correlation_matrix"].to_html(
        classes="correlation-table table table-striped",
        float_format="{:.3f}".format,
    )
    return templates.template("correlation_table.html").render(
        **self.content, correlation_matrix_html=correlation_matrix_html
    )"""
        correlation_matrix_html = self.content["correlation_matrix"].to_html(
            classes="correlation-table table table-striped",
            float_format="{:.3f}".format,
        )
        return templates.template("correlation_table.html").render(
            **self.content, correlation_matrix_html=correlation_matrix_html
        )
