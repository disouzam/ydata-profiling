from ydata_profiling.config import Settings
from ydata_profiling.report.formatters import fmt, fmt_bytesize, fmt_percent
from ydata_profiling.report.presentation.core import (
    HTML,
    Container,
    Table,
    VariableInfo,
)


def render_generic(config: Settings, summary: dict) -> dict:
    """
    Render a generic overview of variable information and summary statistics.

    This function generates a structured representation of variable details and its associated summary statistics
    in a defined format. It constructs a VariableInfo object to encapsulate key details about the variable, and 
    a Table object to display summary statistics like missing values and memory size.

    Parameters:
        config (Settings): Configuration settings containing styles for HTML rendering.
        summary (dict): A dictionary containing statistical information about the variable, which includes:
            - "varid" (str): The identifier of the variable.
            - "alerts" (list): A list of alerts associated with the variable.
            - "cast_type" (str or None): The expected data type of the variable; "Unsupported" if not available.
            - "varname" (str): The name of the variable.
            - "description" (str): A brief description of the variable.
            - "n_missing" (int): The number of missing entries.
            - "p_missing" (float): The percentage of missing entries.
            - "memory_size" (int): The memory size occupied by the variable.
            - "alert_fields" (list): A list of fields that trigger alerts.

    Returns:
        dict: A dictionary containing:
            - "top": A Container object that includes the VariableInfo and Table.
            - "bottom": Always returns None, reserved for future use.

    Example:
        >>> config = Settings(html=HTMLStyle(...))
        >>> summary = {
        ...     "varid": "v1",
        ...     "alerts": [],
        ...     "cast_type": "int",
        ...     "varname": "Variable 1",
        ...     "description": "This is the first variable.",
        ...     "n_missing": 5,
        ...     "p_missing": 0.1,
        ...     "memory_size": 2048,
        ...     "alert_fields": ["n_missing"]
        ... }
        >>> result = render_generic(config, summary)
    """
    info = VariableInfo(
        anchor_id=summary["varid"],
        alerts=summary["alerts"],
        var_type=summary["cast_type"] or "Unsupported",
        var_name=summary["varname"],
        description=summary["description"],
        style=config.html.style,
    )

    table = Table(
        [
            {
                "name": "Missing",
                "value": fmt(summary["n_missing"]),
                "alert": "n_missing" in summary["alert_fields"],
            },
            {
                "name": "Missing (%)",
                "value": fmt_percent(summary["p_missing"]),
                "alert": "p_missing" in summary["alert_fields"],
            },
            {
                "name": "Memory size",
                "value": fmt_bytesize(summary["memory_size"]),
                "alert": False,
            },
        ],
        style=config.html.style,
    )

    return {
        "top": Container([info, table, HTML("")], sequence_type="grid"),
        "bottom": None,
    }
