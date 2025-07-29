import pandas as pd

from ydata_profiling.report.presentation.core.duplicate import Duplicate
from ydata_profiling.report.presentation.flavours.html import templates


def to_html(df: pd.DataFrame) -> str:
    """
    Convert a pandas DataFrame to an HTML table representation.

    This function takes a DataFrame as input and converts it into an HTML table format. 
    If the DataFrame is empty, it adds a message indicating that the dataset 
    does not contain any duplicate rows.

    Parameters:
    df (pd.DataFrame): The DataFrame to be converted to HTML.

    Returns:
    str: An HTML string representation of the DataFrame.
    
    Notes:
    The resulting HTML table will have the classes "duplicate", "table", and "table-striped" applied to it.
    """
    html = df.to_html(
        classes="duplicate table table-striped",
    )
    if df.empty:
        html = html.replace(
            "<tbody>",
            f"<tbody><tr><td colspan={len(df.columns) + 1}>Dataset does not contain duplicate rows.</td></tr>",
        )
    return html


class HTMLDuplicate(Duplicate):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders the HTML template for the duplicate content.

    This method generates the HTML representation of the duplicate content 
    stored in the instance variable `self.content`. It uses the `to_html` 
    function to convert the duplicate content into HTML format, which is 
    then passed to the specified HTML template ("duplicate.html"). 

    Returns:
        str: The rendered HTML as a string.
    """
        duplicate_html = to_html(self.content["duplicate"])
        return templates.template("duplicate.html").render(
            **self.content, duplicate_html=duplicate_html
        )
