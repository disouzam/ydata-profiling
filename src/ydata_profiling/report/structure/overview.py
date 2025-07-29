from datetime import datetime
from typing import Any, List
from urllib.parse import quote

from ydata_profiling.config import Settings
from ydata_profiling.model import BaseDescription
from ydata_profiling.model.alerts import AlertType
from ydata_profiling.model.description import TimeIndexAnalysis
from ydata_profiling.report.formatters import (
    fmt,
    fmt_bytesize,
    fmt_number,
    fmt_numeric,
    fmt_percent,
    fmt_timespan,
    fmt_timespan_timedelta,
    list_args,
)
from ydata_profiling.report.presentation.core import Alerts, Container
from ydata_profiling.report.presentation.core import Image as ImageWidget
from ydata_profiling.report.presentation.core import Table
from ydata_profiling.report.presentation.core.renderable import Renderable
from ydata_profiling.visualisation.plot import plot_overview_timeseries


def get_dataset_overview(config: Settings, summary: BaseDescription) -> Renderable:
    """
    Generate an overview of the dataset statistics and variable types.

    This function creates tables that summarize key metrics about the dataset,
    including the number of variables, number of observations, missing cells,
    duplicate rows, and memory usage, if applicable. It then returns a container
    that holds these tables formatted for rendering.

    Args:
        config (Settings): The configuration settings that determine how 
                           the output should be styled.
        summary (BaseDescription): An object containing the summary statistics 
                                   of the dataset, including counts of variables,
                                   observations, missing values, and variable types.

    Returns:
        Renderable: A Container object that contains the dataset statistics and 
                    variable types formatted as tables.
    """
    table_metrics = [
        {
            "name": "Number of variables",
            "value": fmt_number(summary.table["n_var"]),
        },
        {
            "name": "Number of observations",
            "value": fmt_number(summary.table["n"]),
        },
        {
            "name": "Missing cells",
            "value": fmt_number(summary.table["n_cells_missing"]),
        },
        {
            "name": "Missing cells (%)",
            "value": fmt_percent(summary.table["p_cells_missing"]),
        },
    ]
    if "n_duplicates" in summary.table:
        table_metrics.extend(
            [
                {
                    "name": "Duplicate rows",
                    "value": fmt_number(summary.table["n_duplicates"]),
                },
                {
                    "name": "Duplicate rows (%)",
                    "value": fmt_percent(summary.table["p_duplicates"]),
                },
            ]
        )
    if "memory_size" in summary.table:
        table_metrics.extend(
            [
                {
                    "name": "Total size in memory",
                    "value": fmt_bytesize(summary.table["memory_size"]),
                },
                {
                    "name": "Average record size in memory",
                    "value": fmt_bytesize(summary.table["record_size"]),
                },
            ]
        )

    dataset_info = Table(
        table_metrics, name="Dataset statistics", style=config.html.style
    )

    dataset_types = Table(
        [
            {
                "name": str(type_name),
                "value": fmt_numeric(count, precision=config.report.precision),
            }
            for type_name, count in summary.table["types"].items()
        ],
        name="Variable types",
        style=config.html.style,
    )

    return Container(
        [dataset_info, dataset_types],
        anchor_id="dataset_overview",
        name="Overview",
        sequence_type="grid",
    )


def get_dataset_schema(config: Settings, metadata: dict) -> Container:
    """
    Generates a schema for the dataset based on the provided metadata.

    This function constructs a representation of the dataset's metadata including 
    description, creator, author, URL, and copyright information. The metadata 
    must contain relevant keys as described below, and the function formats 
    this information into a structured output suitable for display.

    Args:
        config (Settings): The configuration settings that determine the style 
                           of the generated output.
        metadata (dict): A dictionary containing metadata about the dataset. 
                         The expected keys include:
                         - 'description': A brief description of the dataset.
                         - 'creator': The entity that created the dataset.
                         - 'author': The individual or organization that authored the dataset.
                         - 'url': A URL linking to the dataset source or information.
                         - 'copyright_holder': The holder of the copyright for the dataset.
                         - 'copyright_year': The year of copyright.

    Returns:
        Container: A container object holding a structured table representation 
                   of the dataset metadata.
    
    The output includes a table with the following information:
        - Name and value pairs for 'description', 'creator', and 'author' where applicable.
        - A clickable hyperlink for the 'url' if provided.
        - Copyright information formatted with the holder's name and year if available.

    Note:
        If 'copyright_year' is not provided but 'copyright_holder' is, 
        the year will not be included in the output.
    """
    about_dataset = []
    for key in ["description", "creator", "author"]:
        if key in metadata and len(metadata[key]) > 0:
            about_dataset.append(
                {"name": key.capitalize(), "value": fmt(metadata[key])}
            )

    if "url" in metadata:
        about_dataset.append(
            {
                "name": "URL",
                "value": f'<a href="{metadata["url"]}">{metadata["url"]}</a>',
            }
        )

    if "copyright_holder" in metadata and len(metadata["copyright_holder"]) > 0:
        if "copyright_year" not in metadata:
            about_dataset.append(
                {
                    "name": "Copyright",
                    "value": fmt(f"(c) {metadata['copyright_holder']}"),
                }
            )
        else:
            about_dataset.append(
                {
                    "name": "Copyright",
                    "value": fmt(
                        f"(c) {metadata['copyright_holder']} {metadata['copyright_year']}"
                    ),
                }
            )

    return Container(
        [
            Table(
                about_dataset,
                name="Dataset",
                anchor_id="metadata_dataset",
                style=config.html.style,
            )
        ],
        name="Dataset",
        anchor_id="dataset",
        sequence_type="grid",
    )


def get_dataset_reproduction(config: Settings, summary: BaseDescription) -> Renderable:
    """Dataset reproduction part of the report

    Args:
        config: settings object
        summary: the dataset summary.

    Returns:
        A renderable object
    """

    version = summary.package["ydata_profiling_version"]
    config_file = summary.package["ydata_profiling_config"]
    date_start = summary.analysis.date_start
    date_end = summary.analysis.date_end
    duration = summary.analysis.duration

    @list_args
    def fmt_version(version: str) -> str:
        """
    Formats a version string into an HTML anchor tag linking to the ydata-profiling GitHub repository.

    Args:
        version (str): The version of the ydata-profiling package.

    Returns:
        str: An HTML string that contains an anchor tag with the version information.
    
    Example:
        >>> fmt_version("1.0.0")
        '<a href="https://github.com/ydataai/ydata-profiling">ydata-profiling v1.0.0</a>'
    """
        return f'<a href="https://github.com/ydataai/ydata-profiling">ydata-profiling v{version}</a>'

    @list_args
    def fmt_config(config: str) -> str:
        """
    Generates an HTML anchor element that allows for downloading a given configuration string as a JSON file.

    The function takes a configuration string, encodes it in a data URL format, 
    and generates an anchor link with the appropriate attributes for initiating a 
    download when clicked.

    Args:
        config (str): The configuration string that will be included in the downloaded JSON file.

    Returns:
        str: An HTML anchor element as a string. The link allows users to download the 
              configuration string as 'config.json'.
    """
    return f'<a download="config.json" href="data:text/plain;charset=utf-8,{quote(config)}">config.json</a>'"""
        return f'<a download="config.json" href="data:text/plain;charset=utf-8,{quote(config)}">config.json</a>'

    reproduction_table = Table(
        [
            {"name": "Analysis started", "value": fmt(date_start)},
            {"name": "Analysis finished", "value": fmt(date_end)},
            {"name": "Duration", "value": fmt_timespan(duration)},
            {"name": "Software version", "value": fmt_version(version)},
            {"name": "Download configuration", "value": fmt_config(config_file)},
        ],
        name="Reproduction",
        anchor_id="overview_reproduction",
        style=config.html.style,
    )

    return Container(
        [reproduction_table],
        name="Reproduction",
        anchor_id="reproduction",
        sequence_type="grid",
    )


def get_dataset_column_definitions(config: Settings, definitions: dict) -> Container:
    """Generate an overview section for the variable description

    Args:
        config: settings object
        definitions: the variable descriptions.

    Returns:
        A container object
    """

    variable_descriptions = [
        Table(
            [
                {"name": column, "value": fmt(value)}
                for column, value in definitions.items()
            ],
            name="Variable descriptions",
            anchor_id="variable_definition_table",
            style=config.html.style,
        )
    ]

    return Container(
        variable_descriptions,
        name="Variables",
        anchor_id="variable_descriptions",
        sequence_type="grid",
    )


def get_dataset_alerts(config: Settings, alerts: list) -> Alerts:
    """Obtain the alerts for the report

    Args:
        config: settings object
        alerts: list of alerts

    Returns:
        Alerts renderable object
    """
    # add up alerts from multiple reports
    if isinstance(alerts, tuple):
        count = 0

        # Initialize
        combined_alerts = {
            f"{alert.alert_type}_{alert.column_name}": [
                None for _ in range(len(alerts))
            ]
            for report_alerts in alerts
            for alert in report_alerts
        }

        for report_idx, report_alerts in enumerate(alerts):
            for alert in report_alerts:
                combined_alerts[f"{alert.alert_type}_{alert.column_name}"][
                    report_idx
                ] = alert

            count += len(
                [
                    alert
                    for alert in report_alerts
                    if alert.alert_type != AlertType.REJECTED
                ]
            )

        return Alerts(
            alerts=combined_alerts,
            name=f"Alerts ({count})",
            anchor_id="alerts",
            style=config.html.style,
        )

    count = len([alert for alert in alerts if alert.alert_type != AlertType.REJECTED])
    return Alerts(
        alerts=alerts,
        name=f"Alerts ({count})",
        anchor_id="alerts",
        style=config.html.style,
    )


def get_timeseries_items(config: Settings, summary: BaseDescription) -> Container:
    """
    Generates a container with a summary of time series statistics and associated visualizations.

    This function retrieves time series data, calculates various statistics including
    the number of series, their lengths, starting and ending points, and the period. 
    It formats these statistics into a table, and also provides visual representations
    of the time series data in the form of images. The images are created at a specified
    DPI and can be displayed in different scales.

    Args:
        config (Settings): Configuration settings that define plotting and styling parameters.
        summary (BaseDescription): A summary object containing the time index analysis and related variables.

    Returns:
        Container: A container object that holds the table of time series statistics and 
        visualizations of the time series data.
    
    Raises:
        AssertionError: If the time_index_analysis attribute of summary is not an instance of TimeIndexAnalysis.
    """
    @list_args
    def fmt_tsindex_limit(limit: Any) -> str:
        if isinstance(limit, datetime):
            return limit.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return fmt_number(limit)

    assert isinstance(summary.time_index_analysis, TimeIndexAnalysis)
    table_stats = [
        {
            "name": "Number of series",
            "value": fmt_number(summary.time_index_analysis.n_series),
        },
        {
            "name": "Time series length",
            "value": fmt_number(summary.time_index_analysis.length),
        },
        {
            "name": "Starting point",
            "value": fmt_tsindex_limit(summary.time_index_analysis.start),
        },
        {
            "name": "Ending point",
            "value": fmt_tsindex_limit(summary.time_index_analysis.end),
        },
        {
            "name": "Period",
            "value": fmt_timespan_timedelta(summary.time_index_analysis.period),
        },
    ]

    ts_info = Table(table_stats, name="Timeseries statistics", style=config.html.style)

    dpi_bak = config.plot.dpi
    config.plot.dpi = 300
    timeseries = ImageWidget(
        plot_overview_timeseries(config, summary.variables),
        image_format=config.plot.image_format,
        alt="ts_plot",
        name="Original",
        anchor_id="ts_plot_overview",
    )
    timeseries_scaled = ImageWidget(
        plot_overview_timeseries(config, summary.variables, scale=True),
        image_format=config.plot.image_format,
        alt="ts_plot_scaled",
        name="Scaled",
        anchor_id="ts_plot_scaled_overview",
    )
    config.plot.dpi = dpi_bak
    ts_tab = Container(
        [timeseries, timeseries_scaled],
        anchor_id="ts_plot_overview",
        name="",
        sequence_type="tabs",
    )

    return Container(
        [ts_info, ts_tab],
        anchor_id="timeseries_overview",
        name="Time Series",
        sequence_type="grid",
    )


def get_dataset_items(config: Settings, summary: BaseDescription, alerts: list) -> list:
    """Returns the dataset overview (at the top of the report)

    Args:
        config: settings object
        summary: the calculated summary
        alerts: the alerts

    Returns:
        A list with components for the dataset overview (overview, reproduction, alerts)
    """

    items: List[Renderable] = [get_dataset_overview(config, summary)]

    metadata = {key: config.dataset.dict()[key] for key in config.dataset.dict().keys()}

    if len(metadata) > 0 and any(len(value) > 0 for value in metadata.values()):
        items.append(get_dataset_schema(config, metadata))

    column_details = {
        key: config.variables.descriptions[key]
        for key in config.variables.descriptions.keys()
    }

    if len(column_details) > 0:
        items.append(get_dataset_column_definitions(config, column_details))

    if summary.time_index_analysis:
        items.append(get_timeseries_items(config, summary))

    if alerts:
        items.append(get_dataset_alerts(config, alerts))

    items.append(get_dataset_reproduction(config, summary))

    return items
