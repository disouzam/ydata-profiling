from typing import Any, Dict

from ydata_profiling.config import Settings
from ydata_profiling.report.formatters import fmt, fmt_bytesize, fmt_percent
from ydata_profiling.report.presentation.core import (
    Container,
    Image,
    Table,
    VariableInfo,
)
from ydata_profiling.visualisation.plot import histogram, mini_histogram


def render_date(config: Settings, summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renders a date summary for visualization based on the provided configuration and summary data.

    This function takes in configuration settings and a summary dictionary containing date-related statistics,
    and generates a structured template with various components including variable information, tables of statistics,
    and histograms.

    Args:
        config (Settings): Configuration settings that include styling and image formatting options.
        summary (Dict[str, Any]): A dictionary containing summary information including:
            - varid (str): The variable identifier.
            - varname (str): The name of the variable.
            - alerts (list): A list of alerts associated with the variable.
            - description (str): A description of the variable.
            - n_distinct (int): Count of distinct values.
            - p_distinct (float): Percentage of distinct values.
            - n_missing (int): Count of missing values.
            - p_missing (float): Percentage of missing values.
            - memory_size (int): Size in bytes of the variable's data.
            - min (datetime): The minimum date value.
            - max (datetime): The maximum date value.
            - n_invalid_dates (int): Count of invalid date entries.
            - p_invalid_dates (float): Percentage of invalid dates.
            - histogram (list or tuple): Data for histogram generation.

    Returns:
        Dict[str, Any]: A dictionary containing template variables for rendering the date summary, including:
            - top (Container): A container with variable information, summary tables, and a mini histogram.
            - bottom (Container): A container with the main histogram of date data.
    """
    varid = summary["varid"]
    template_variables = {}

    image_format = config.plot.image_format

    # Top
    info = VariableInfo(
        summary["varid"],
        summary["varname"],
        "Date",
        summary["alerts"],
        summary["description"],
        style=config.html.style,
    )

    table1 = Table(
        [
            {
                "name": "Distinct",
                "value": fmt(summary["n_distinct"]),
                "alert": False,
            },
            {
                "name": "Distinct (%)",
                "value": fmt_percent(summary["p_distinct"]),
                "alert": False,
            },
            {
                "name": "Missing",
                "value": fmt(summary["n_missing"]),
                "alert": False,
            },
            {
                "name": "Missing (%)",
                "value": fmt_percent(summary["p_missing"]),
                "alert": False,
            },
            {
                "name": "Memory size",
                "value": fmt_bytesize(summary["memory_size"]),
                "alert": False,
            },
        ],
        style=config.html.style,
    )

    table2 = Table(
        [
            {"name": "Minimum", "value": fmt(summary["min"]), "alert": False},
            {"name": "Maximum", "value": fmt(summary["max"]), "alert": False},
            {
                "name": "Invalid dates",
                "value": fmt(summary["n_invalid_dates"]),
                "alert": False,
            },
            {
                "name": "Invalid dates (%)",
                "value": fmt_percent(summary["p_invalid_dates"]),
                "alert": False,
            },
        ],
        style=config.html.style,
    )

    if isinstance(summary["histogram"], list):
        mini_histo = Image(
            mini_histogram(
                config,
                [x[0] for x in summary["histogram"]],
                [x[1] for x in summary["histogram"]],
                date=True,
            ),
            image_format=image_format,
            alt="Mini histogram",
        )
    else:
        mini_histo = Image(
            mini_histogram(
                config, summary["histogram"][0], summary["histogram"][1], date=True
            ),
            image_format=image_format,
            alt="Mini histogram",
        )

    template_variables["top"] = Container(
        [info, table1, table2, mini_histo], sequence_type="grid"
    )

    if isinstance(summary["histogram"], list):
        hist_data = histogram(
            config,
            [x[0] for x in summary["histogram"]],
            [x[1] for x in summary["histogram"]],
            date=True,
        )
    else:
        hist_data = histogram(
            config, summary["histogram"][0], summary["histogram"][1], date=True
        )

    # Bottom
    n_bins = len(summary["histogram"][1]) - 1 if summary["histogram"] else 0
    bottom = Container(
        [
            Image(
                hist_data,
                image_format=image_format,
                alt="Histogram",
                caption=f"<strong>Histogram with fixed size bins</strong> (bins={n_bins})",
                name="Histogram",
                anchor_id=f"{varid}histogram",
            )
        ],
        sequence_type="tabs",
        anchor_id=summary["varid"],
    )

    template_variables["bottom"] = bottom

    return template_variables
