from ydata_profiling.config import Settings
from ydata_profiling.report.formatters import fmt, fmt_numeric
from ydata_profiling.report.presentation.core import Container, FrequencyTable, Table
from ydata_profiling.report.presentation.frequency_table_utils import freq_table
from ydata_profiling.report.structure.variables.render_categorical import (
    render_categorical,
)


def render_path(config: Settings, summary: dict) -> dict:
    """
    Renders the path information and generates template variables for the report.

    This function takes a configuration object and a summary dictionary,
    processing frequency tables and creating an overview of path-related 
    information. It returns a dictionary of template variables that can 
    be used for rendering the final output.

    Parameters:
    ----------
    config : Settings
        An object containing configuration settings, including maximum number 
        of frequency table entries and formatting styles.
    
    summary : dict
        A dictionary containing summary statistics of the paths, including:
        - varid (str): Variable identifier.
        - n (int): Total number of entries.
        - common_prefix (str): The common prefix for the paths.
        - n_stem_unique (int): Count of unique stems.
        - n_name_unique (int): Count of unique names.
        - n_suffix_unique (int): Count of unique extensions.
        - n_parent_unique (int): Count of unique parent directories.
        - n_anchor_unique (int): Count of unique anchors.
        Each of these statistics is used to construct frequency tables and 
        overview sections in the report.

    Returns:
    -------
    dict
        A dictionary containing various template variables, including frequency 
        tables and overall path summaries, formatted for report generation.
    """
    varid = summary["varid"]
    n_freq_table_max = config.n_freq_table_max
    redact = config.vars.cat.redact

    template_variables = render_categorical(config, summary)

    keys = ["name", "parent", "suffix", "stem", "anchor"]
    for path_part in keys:
        template_variables[f"freqtable_{path_part}"] = freq_table(
            freqtable=summary[f"{path_part}_counts"],
            n=summary["n"],
            max_number_to_print=n_freq_table_max,
        )

    # Top
    template_variables["top"].content["items"][0].content["var_type"] = "Path"

    # Bottom
    path_overview_tab = Container(
        [
            Table(
                [
                    {
                        "name": "Common prefix",
                        "value": fmt(summary["common_prefix"]),
                        "alert": False,
                    },
                    {
                        "name": "Unique stems",
                        "value": fmt_numeric(
                            summary["n_stem_unique"], precision=config.report.precision
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique names",
                        "value": fmt_numeric(
                            summary["n_name_unique"], precision=config.report.precision
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique extensions",
                        "value": fmt_numeric(
                            summary["n_suffix_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique directories",
                        "value": fmt_numeric(
                            summary["n_parent_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique anchors",
                        "value": fmt_numeric(
                            summary["n_anchor_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                ],
                style=config.html.style,
            )
        ],
        anchor_id=f"{varid}tbl",
        name="Overview",
        sequence_type="list",
    )

    path_items = [
        path_overview_tab,
        FrequencyTable(
            template_variables["freq_table_rows"],
            name="Full",
            anchor_id=f"{varid}full_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_stem"],
            name="Stem",
            anchor_id=f"{varid}stem_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_name"],
            name="Name",
            anchor_id=f"{varid}name_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_suffix"],
            name="Extension",
            anchor_id=f"{varid}suffix_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_parent"],
            name="Parent",
            anchor_id=f"{varid}parent_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_anchor"],
            name="Anchor",
            anchor_id=f"{varid}anchor_frequency",
            redact=redact,
        ),
    ]

    path_tab = Container(
        path_items,
        name="Path",
        sequence_type="tabs",
        anchor_id=f"{varid}path",
    )

    template_variables["bottom"].content["items"].append(path_tab)

    return template_variables
