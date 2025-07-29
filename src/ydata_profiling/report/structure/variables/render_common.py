from ydata_profiling.config import Settings
from ydata_profiling.report.presentation.frequency_table_utils import (
    extreme_obs_table,
    freq_table,
)


def render_common(config: Settings, summary: dict) -> dict:
    """
    Renders common template variables for frequency and extreme observation tables.

    This function generates a dictionary of template variables based on the provided 
    configuration settings and a summary dictionary. It constructs frequency tables 
    and tables of extreme observations (both first and last) to be used in rendering 
    templates.

    Parameters:
    ----------
    config : Settings
        An object containing configuration settings, including the number of extreme 
        observations to display and the maximum number of rows for the frequency table.
        
    summary : dict
        A dictionary containing summary statistics, which includes:
        - "value_counts_without_nan": The frequency counts without NaN values.
        - "n": The total number of observations.
        - "value_counts_index_sorted": The frequency counts sorted by index.
        
    Returns:
    -------
    dict
        A dictionary containing:
        - "freq_table_rows": A formatted frequency table with a maximum of 
          `n_freq_table_max` rows.
        - "firstn_expanded": A formatted table of the first `n_extreme_obs` 
          extreme observations.
        - "lastn_expanded": A formatted table of the last `n_extreme_obs` 
          extreme observations.
    """
    n_extreme_obs = config.n_extreme_obs
    n_freq_table_max = config.n_freq_table_max

    template_variables = {
        # TODO: with nan
        "freq_table_rows": freq_table(
            freqtable=summary["value_counts_without_nan"],
            n=summary["n"],
            max_number_to_print=n_freq_table_max,
        ),
        "firstn_expanded": extreme_obs_table(
            freqtable=summary["value_counts_index_sorted"],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
        "lastn_expanded": extreme_obs_table(
            freqtable=summary["value_counts_index_sorted"][::-1],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
    }

    return template_variables"""
    n_extreme_obs = config.n_extreme_obs
    n_freq_table_max = config.n_freq_table_max

    template_variables = {
        # TODO: with nan
        "freq_table_rows": freq_table(
            freqtable=summary["value_counts_without_nan"],
            n=summary["n"],
            max_number_to_print=n_freq_table_max,
        ),
        "firstn_expanded": extreme_obs_table(
            freqtable=summary["value_counts_index_sorted"],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
        "lastn_expanded": extreme_obs_table(
            freqtable=summary["value_counts_index_sorted"][::-1],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
    }

    return template_variables
