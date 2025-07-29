from ydata_profiling.report.presentation.core.sample import Sample
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLSample(Sample):
    def render(self) -> str:
        """
    Renders an HTML template with the provided content.

    This method generates HTML from a specific sample content using 
    the 'to_html' method, applying the classes "sample", "table", and 
    "table-striped" to the generated HTML. It then renders the final 
    HTML template "sample.html" with the complete content, including 
    the generated sample HTML.

    Returns:
        str: The rendered HTML content as a string.
    """
        sample_html = self.content["sample"].to_html(
            classes="sample table table-striped"
        )
        return templates.template("sample.html").render(
            **self.content, sample_html=sample_html
        )
