import copy
import json
import warnings
from pathlib import Path
from typing import Any, Optional, Union

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pkg_resources

try:
    from pyspark.sql import DataFrame as sDataFrame
except:  # noqa: E722
    from typing import TypeVar

    sDataFrame = TypeVar("sDataFrame")  # type: ignore


from dataclasses import asdict, is_dataclass

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from typeguard import typechecked
from visions import VisionsTypeset

from ydata_profiling.config import Config, Settings, SparkSettings
from ydata_profiling.expectations_report import ExpectationsReport
from ydata_profiling.model import BaseDescription
from ydata_profiling.model.alerts import AlertType
from ydata_profiling.model.describe import describe as describe_df
from ydata_profiling.model.sample import Sample
from ydata_profiling.model.summarizer import (
    BaseSummarizer,
    PandasProfilingSummarizer,
    format_summary,
    redact_summary,
)
from ydata_profiling.model.typeset import ProfilingTypeSet
from ydata_profiling.report import get_report_structure
from ydata_profiling.report.presentation.core import Root
from ydata_profiling.report.presentation.flavours.html.templates import (
    create_html_assets,
)
from ydata_profiling.serialize_report import SerializeReport
from ydata_profiling.utils.dataframe import hash_dataframe
from ydata_profiling.utils.logger import ProfilingLogger
from ydata_profiling.utils.paths import get_config

logger = ProfilingLogger(name="ReportLogger")


@typechecked
class ProfileReport(SerializeReport, ExpectationsReport):
    """Generate a profile report from a Dataset stored as a pandas `DataFrame`.

    Used as is, it will output its content as an HTML report in a Jupyter notebook.
    """

    _description_set = None
    _report = None
    _html = None
    _widgets = None
    _json = None
    config: Settings

    def __init__(
        self,
        df: Optional[Union[pd.DataFrame, sDataFrame]] = None,
        minimal: bool = False,
        tsmode: bool = False,
        sortby: Optional[str] = None,
        sensitive: bool = False,
        explorative: bool = False,
        sample: Optional[dict] = None,
        config_file: Optional[Union[Path, str]] = None,
        lazy: bool = True,
        typeset: Optional[VisionsTypeset] = None,
        summarizer: Optional[BaseSummarizer] = None,
        config: Optional[Settings] = None,
        type_schema: Optional[dict] = None,
        **kwargs,
    ):
        """Generate a ProfileReport based on a pandas or spark.sql DataFrame

        Config processing order (in case of duplicate entries, entries later in the order are retained):
        - config presets (e.g. `config_file`, `minimal` arguments)
        - config groups (e.g. `explorative` and `sensitive` arguments)
        - custom settings (e.g. `config` argument)
        - custom settings **kwargs (e.g. `title`)

        Args:
            df: a pandas or spark.sql DataFrame
            minimal: minimal mode is a default configuration with minimal computation
            ts_mode: activates time-series analysis for all the numerical variables from the dataset.
            Only available for pd.DataFrame
            sort_by: ignored if ts_mode=False. Order the dataset by a provided column.
            sensitive: hides the values for categorical and text variables for report privacy
            config_file: a config file (.yml), mutually exclusive with `minimal`
            lazy: compute when needed
            sample: optional dict(name="Sample title", caption="Caption", data=pd.DataFrame())
            typeset: optional user typeset to use for type inference
            summarizer: optional user summarizer to generate custom summary output
            type_schema: optional dict containing pairs of `column name`: `type`
            **kwargs: other arguments, for valid arguments, check the default configuration file.
        """

        self.__validate_inputs(df, minimal, tsmode, config_file, lazy)

        if config_file or minimal:
            if not config_file:
                config_file = get_config("config_minimal.yaml")

            report_config = Settings().from_file(config_file)
        elif config is not None:
            report_config = config
        else:
            if isinstance(df, pd.DataFrame):
                report_config = Settings()
            else:
                report_config = SparkSettings()

        groups = [
            (explorative, "explorative"),
            (sensitive, "sensitive"),
        ]

        if any(condition for condition, _ in groups):
            cfg = Settings()
            for condition, key in groups:
                if condition:
                    cfg = cfg.update(Config.get_arg_groups(key))
            report_config = report_config.update(cfg.dict(exclude_defaults=True))

        if len(kwargs) > 0:
            shorthands, kwargs = Config.shorthands(kwargs)
            report_config = report_config.update(
                Settings().update(shorthands).dict(exclude_defaults=True)
            )

        if kwargs:
            report_config = report_config.update(kwargs)

        report_config.vars.timeseries.active = tsmode
        if tsmode and sortby:
            report_config.vars.timeseries.sortby = sortby

        self.df = self.__initialize_dataframe(df, report_config)
        self.config = report_config
        self._df_hash = None
        self._sample = sample
        self._type_schema = type_schema
        self._typeset = typeset
        self._summarizer = summarizer

        if not lazy:
            # Trigger building the report structure
            _ = self.report

    @staticmethod
    def __validate_inputs(
        df: Optional[Union[pd.DataFrame, sDataFrame]],
        minimal: bool,
        tsmode: bool,
        config_file: Optional[Union[Path, str]],
        lazy: bool,
    ) -> None:
        """def __validate_inputs(
    df: Optional[Union[pd.DataFrame, sDataFrame]],
    minimal: bool,
    tsmode: bool,
    config_file: Optional[Union[Path, str]],
    lazy: bool,
) -> None:
    """
    Validates the inputs for the profiling function.

    This method checks the following conditions:
    - If a DataFrame is not provided and lazy profiling is not enabled,
      a ValueError is raised.
    - If a `config_file` is specified, using a minimal profile is not allowed,
      and a ValueError is raised.
    - If the provided DataFrame is a Pandas DataFrame, it verifies that it is
      not empty; otherwise, a ValueError is raised.
    - If the provided DataFrame is a Spark DataFrame and time-series mode is
      enabled, a NotImplementedError is raised.
    - For Spark DataFrames, it checks whether the RDD is empty, raising a
      ValueError if it is.

    Parameters:
    ----------
    df : Optional[Union[pd.DataFrame, sDataFrame]]
        The DataFrame to validate. Can be a Pandas DataFrame or a Spark DataFrame.

    minimal : bool
        Indicates whether to execute in minimal profiling mode.

    tsmode : bool
        Indicates whether to enable time-series analysis.

    config_file : Optional[Union[Path, str]]
        An optional configuration file path that guides the profiling process.

    lazy : bool
        A flag indicating if lazy profiling should be performed.

    Raises:
    ------
    ValueError
        If the DataFrame is None and lazy is False,
        if the DataFrame is empty, or if both `config_file` and `minimal` 
        are set.

    NotImplementedError
        If the time-series mode is enabled while using a Spark DataFrame.
    """
        # Lazy profile cannot be set if no DataFrame is provided
        if df is None and not lazy:
            raise ValueError("Can init a not-lazy ProfileReport with no DataFrame")

        if config_file is not None and minimal:
            raise ValueError(
                "Arguments `config_file` and `minimal` are mutually exclusive."
            )

        # Spark Dataframe validations
        if isinstance(df, pd.DataFrame):
            if df is not None and df.empty:
                raise ValueError(
                    "DataFrame is empty. Please" "provide a non-empty DataFrame."
                )
        else:
            if tsmode:
                raise NotImplementedError(
                    "Time-Series dataset analysis is not yet supported for Spark DataFrames"
                )

            if (
                df is not None and df.rdd.isEmpty()
            ):  # df.isEmpty is only support by 3.3.0 pyspark version
                raise ValueError(
                    "DataFrame is empty. Please" "provide a non-empty DataFrame."
                )

    @staticmethod
    def __initialize_dataframe(
        df: Optional[Union[pd.DataFrame, sDataFrame]], report_config: Settings
    ) -> Optional[Union[pd.DataFrame, sDataFrame]]:
        """def __initialize_dataframe(
    df: Optional[Union[pd.DataFrame, sDataFrame]], report_config: Settings
) -> Optional[Union[pd.DataFrame, sDataFrame]]:
    """
    Initializes a given DataFrame based on the provided report configuration.

    This static method takes a DataFrame or a custom DataFrame type (`sDataFrame`) 
    and prepares it according to specific settings defined in the report configuration. 
    If the DataFrame is valid and contains time series settings, it sorts the DataFrame 
    based on the specified column in the configuration and sets the index accordingly. 
    If no sorting column is specified, it sorts the DataFrame by its index.

    Parameters:
    df (Optional[Union[pd.DataFrame, sDataFrame]]): 
        A pandas DataFrame or a custom DataFrame to initialize. 
        Can be None if no initialization is needed.
    
    report_config (Settings): 
        An object containing configuration settings for the report, 
        including time series specifications.

    Returns:
    Optional[Union[pd.DataFrame, sDataFrame]]: 
        The initialized DataFrame according to the report configurations, 
        or None if the input DataFrame was None.
    """

        logger.info_def_report(
            df=df,
            timeseries=report_config.vars.timeseries.active,
        )

        if (
            df is not None
            and isinstance(df, pd.DataFrame)
            and report_config.vars.timeseries.active
        ):
            if report_config.vars.timeseries.sortby:
                df = df.sort_values(by=report_config.vars.timeseries.sortby)
                df = df.set_index(report_config.vars.timeseries.sortby, drop=False)
                df.index.name = None
            else:
                df = df.sort_index()

        return df

    def invalidate_cache(self, subset: Optional[str] = None) -> None:
        """Invalidate report cache. Useful after changing setting.

        Args:
            subset:
            - "rendering" to invalidate the html, json and widget report rendering
            - "report" to remove the caching of the report structure
            - None (default) to invalidate all caches

        Returns:
            None
        """
        if subset is not None and subset not in ["rendering", "report"]:
            raise ValueError(
                "'subset' parameter should be None, 'rendering' or 'report'"
            )

        if subset is None or subset in ["rendering", "report"]:
            self._widgets = None
            self._json = None
            self._html = None

        if subset is None or subset == "report":
            self._report = None

        if subset is None:
            self._description_set = None

    @property
    def typeset(self) -> Optional[VisionsTypeset]:
        """def typeset(self) -> Optional[VisionsTypeset]:
    """
    Gets the typeset for the current instance. 

    If the typeset has not been created yet, it initializes it using the
    ProfilingTypeSet class, passing the configuration and type schema
    defined in the instance. 

    Returns:
        Optional[VisionsTypeset]: The initialized typeset if it exists,
        otherwise, it will create and return a new instance of 
        ProfilingTypeSet.
    """
    if self._typeset is None:
        self._typeset = ProfilingTypeSet(self.config, self._type_schema)
    return self._typeset"""
        if self._typeset is None:
            self._typeset = ProfilingTypeSet(self.config, self._type_schema)
        return self._typeset

    @property
    def summarizer(self) -> BaseSummarizer:
        """def summarizer(self) -> BaseSummarizer:
    """
    Retrieves the summarizer instance for the current object.

    This property lazily initializes the summarizer if it has not 
    been created yet. The summarizer is an instance of 
    `PandasProfilingSummarizer`, which is initialized with the 
    current object's typeset.

    Returns:
        BaseSummarizer: An instance of the summarizer used for generating 
        summaries of the data.

    Raises:
        None: This property does not raise any exceptions.
    """
    if self._summarizer is None:
        self._summarizer = PandasProfilingSummarizer(self.typeset)
    return self._summarizer"""
        if self._summarizer is None:
            self._summarizer = PandasProfilingSummarizer(self.typeset)
        return self._summarizer

    @property
    def description_set(self) -> BaseDescription:
        """def description_set(self) -> BaseDescription:
    """
    Gets the description set for the current object's data frame. 

    This property lazily computes the description set if it has not been
    previously calculated. It calls the `describe_df` function with the
    current configuration, data frame, summarizer, typeset, and sample to
    generate the description set.

    Returns:
        BaseDescription: The computed description set for the data frame.

    Note:
        The description set will only be computed once and stored for
        subsequent access.
    """
    if self._description_set is None:
        self._description_set = describe_df(
            self.config,
            self.df,
            self.summarizer,
            self.typeset,
            self._sample,
        )
    return self._description_set"""
        if self._description_set is None:
            self._description_set = describe_df(
                self.config,
                self.df,
                self.summarizer,
                self.typeset,
                self._sample,
            )
        return self._description_set

    @property
    def df_hash(self) -> Optional[str]:
        """def df_hash(self) -> Optional[str]:
    """
    Compute and return the hash of the DataFrame.

    This property retrieves the hash of the DataFrame if it has already been computed. 
    If the hash has not been computed yet and the DataFrame is not None, 
    it calculates the hash using the `hash_dataframe` function, stores it, 
    and then returns the computed hash.

    Returns:
        Optional[str]: The hash of the DataFrame if available; otherwise, None.
    """
        if self._df_hash is None and self.df is not None:
            self._df_hash = hash_dataframe(self.df)
        return self._df_hash

    @property
    def report(self) -> Root:
        """def report(self) -> Root:
    """
    Get the report structure.

    This property lazily initializes the report structure by calling 
    `get_report_structure` with the current configuration and description 
    set if it has not been previously set. On subsequent calls, it 
    simply returns the already initialized report structure.

    Returns:
        Root: The report structure.

    Raises:
        None: This property does not raise exceptions.
    """
    if self._report is None:
        self._report = get_report_structure(self.config, self.description_set)
    return self._report"""
        if self._report is None:
            self._report = get_report_structure(self.config, self.description_set)
        return self._report

    @property
    def html(self) -> str:
        """def html(self) -> str:
    """
    Retrieves the HTML representation of the object.

    If the HTML has not been generated yet, this property will invoke
    the `_render_html` method to create the HTML content and store it 
    in the `_html` attribute. Subsequent calls to this property will
    return the cached HTML.

    Returns:
        str: The HTML representation of the object.
    """
        if self._html is None:
            self._html = self._render_html()
        return self._html

    @property
    def json(self) -> str:
        """def json(self) -> str:
    """
    Retrieves the JSON representation of the object. If the JSON has not been 
    previously generated, it will call the `_render_json` method to create it 
    and store it for future access.

    Returns:
        str: The JSON string representing the object.
    """
        if self._json is None:
            self._json = self._render_json()
        return self._json

    @property
    def widgets(self) -> Any:
        """def widgets(self) -> Any:
    """
    Property that retrieves the widgets associated with the report.

    This property checks if the report supports the widgets interface.
    If the report involves comparing multiple descriptions (i.e., the 
    'n' attribute in the description_set's table is a list with 
    more than one element), a RuntimeError is raised, as widgets 
    are not supported for such comparisons. 

    If the widgets have not yet been rendered, they are generated 
    using the _render_widgets() method and cached for future access.

    Returns:
        Any: The rendered widgets associated with the report.
    
    Raises:
        RuntimeError: If the widgets interface is not supported 
        due to multiple descriptions being compared.
    """
        if (
            isinstance(self.description_set.table["n"], list)
            and len(self.description_set.table["n"]) > 1
        ):
            raise RuntimeError(
                "Widgets interface not (yet) supported for comparing reports, please use the HTML rendering."
            )

        if self._widgets is None:
            self._widgets = self._render_widgets()
        return self._widgets

    def get_duplicates(self) -> Optional[pd.DataFrame]:
        """Get duplicate rows and counts based on the configuration

        Returns:
            A DataFrame with the duplicate rows and their counts.
        """
        return self.description_set.duplicates

    def get_sample(self) -> dict:
        """Get head/tail samples based on the configuration

        Returns:
            A dict with the head and tail samples.
        """
        return self.description_set.sample

    def get_description(self) -> BaseDescription:
        """Return the description (a raw statistical summary) of the dataset.

        Returns:
            Dict containing a description for each variable in the DataFrame.
        """
        return self.description_set

    def get_rejected_variables(self) -> set:
        """Get variables that are rejected for analysis (e.g. constant, mixed data types)

        Returns:
            a set of column names that are unsupported
        """
        return {
            alert.column_name
            for alert in self.description_set.alerts
            if alert.alert_type == AlertType.REJECTED
        }

    def to_file(self, output_file: Union[str, Path], silent: bool = True) -> None:
        """Write the report to a file.

        Args:
            output_file: The name or the path of the file to generate including the extension (.html, .json).
            silent: if False, opens the file in the default browser or download it in a Google Colab environment
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pillow_version = pkg_resources.get_distribution("Pillow").version
        version_tuple = tuple(map(int, pillow_version.split(".")))
        if version_tuple < (9, 5, 0):
            warnings.warn(
                "Try running command: 'pip install --upgrade Pillow' to avoid ValueError"
            )

        if not isinstance(output_file, Path):
            output_file = Path(str(output_file))

        if output_file.suffix == ".json":
            data = self.to_json()
        else:
            if not self.config.html.inline:
                self.config.html.assets_path = str(output_file.parent)
                if self.config.html.assets_prefix is None:
                    self.config.html.assets_prefix = str(output_file.stem) + "_assets"
                create_html_assets(self.config, output_file)

            data = self.to_html()

            if output_file.suffix != ".html":
                suffix = output_file.suffix
                output_file = output_file.with_suffix(".html")
                warnings.warn(
                    f"Extension {suffix} not supported. For now we assume .html was intended. "
                    f"To remove this warning, please use .html or .json."
                )

        disable_progress_bar = not self.config.progress_bar
        with tqdm(
            total=1, desc="Export report to file", disable=disable_progress_bar
        ) as pbar:
            output_file.write_text(data, encoding="utf-8")
            pbar.update()

        if not silent:
            try:
                from google.colab import files  # noqa: F401

                files.download(output_file.absolute().as_uri())
            except ModuleNotFoundError:
                import webbrowser

                webbrowser.open_new_tab(output_file.absolute().as_uri())

    def _render_html(self) -> str:
        """
    Renders an HTML report based on the specified configuration and report data.

    This method utilizes the HTMLReport class from the ydata_profiling package 
    to generate an HTML representation of the report. It supports various 
    configurations, such as displaying a navigation bar, using local assets, 
    and applying styling options.

    Args:
        self: The instance of the class invoking this method, which contains 
        the report data and configuration options.

    Returns:
        str: The rendered HTML content of the report.

    Notes:
        - Progress bar is displayed if the configuration permits.
        - The HTML output can be minified based on the user's settings, which 
        removes empty spaces and comments to optimize the file size.
    """
        from ydata_profiling.report.presentation.flavours import HTMLReport

        report = self.report

        with tqdm(
            total=1, desc="Render HTML", disable=not self.config.progress_bar
        ) as pbar:
            html = HTMLReport(copy.deepcopy(report)).render(
                nav=self.config.html.navbar_show,
                offline=self.config.html.use_local_assets,
                inline=self.config.html.inline,
                assets_prefix=self.config.html.assets_prefix,
                primary_color=self.config.html.style.primary_colors[0],
                logo=self.config.html.style.logo,
                theme=self.config.html.style.theme,
                title=self.description_set.analysis.title,
                date=self.description_set.analysis.date_start,
                version=self.description_set.package["ydata_profiling_version"],
            )

            if self.config.html.minify_html:
                from htmlmin.main import minify

                html = minify(html, remove_all_empty_space=True, remove_comments=True)
            pbar.update()
        return html

    def _render_widgets(self) -> Any:
        """
    Renders the widgets for the report using the WidgetReport class.

    This method creates a progress bar to provide feedback during the widget rendering process.
    The rendering is based on a deep copy of the report to ensure that the original data remains
    unchanged.

    Returns:
        Any: The rendered widgets as generated by the WidgetReport.

    Note:
        The progress bar is disabled based on the configuration settings, and it will leave
        a final status on completion if enabled.
    """
        from ydata_profiling.report.presentation.flavours import WidgetReport

        report = self.report

        with tqdm(
            total=1,
            desc="Render widgets",
            disable=not self.config.progress_bar,
            leave=False,
        ) as pbar:
            widgets = WidgetReport(copy.deepcopy(report)).render()
            pbar.update()
        return widgets

    def _render_json(self) -> str:
        """
    Renders the object's description as a JSON string.

    This method converts various data types, including dataclasses, dictionaries,
    lists, sets, Pandas Series, Pandas DataFrames, and NumPy arrays into a JSON
    compatible format. The resulting JSON string is indented for better readability.

    The conversion process is handled by the nested function `encode_it`, which recursively
    encodes the input into JSON-serializable formats. Special handling is provided for
    specific data types such as dataclasses, Pandas objects, and NumPy arrays.

    The progress of the rendering process is displayed using a progress bar, unless
    disabled in the configuration.

    Returns:
        str: The rendered description in JSON format.

    Notes:
        - This method is part of a class and relies on `self.description_set` 
          and `self.config` to function properly.
        - The JSON output may contain redacted information based on the provided configuration.
    """
        def encode_it(o: Any) -> Any:
            if is_dataclass(o):
                o = asdict(o)
            if isinstance(o, dict):
                return {encode_it(k): encode_it(v) for k, v in o.items()}
            else:
                if isinstance(o, (bool, int, float, str)):
                    return o
                elif isinstance(o, list):
                    return [encode_it(v) for v in o]
                elif isinstance(o, set):
                    return {encode_it(v) for v in o}
                elif isinstance(o, pd.Series):
                    return encode_it(o.to_list())
                elif isinstance(o, pd.DataFrame):
                    return encode_it(o.to_dict(orient="records"))
                elif isinstance(o, np.ndarray):
                    return encode_it(o.tolist())
                elif isinstance(o, Sample):
                    return encode_it(o.dict())
                elif isinstance(o, np.generic):
                    return o.item()
                else:
                    return str(o)

        description = self.description_set

        with tqdm(
            total=1, desc="Render JSON", disable=not self.config.progress_bar
        ) as pbar:
            description_dict = format_summary(description)
            description_dict = encode_it(description_dict)
            description_dict = redact_summary(description_dict, self.config)

            data = json.dumps(description_dict, indent=4)
            pbar.update()
        return data

    def to_html(self) -> str:
        """Generate and return complete template as lengthy string
            for using with frameworks.

        Returns:
            Profiling report html including wrapper.

        """
        return self.html

    def to_json(self) -> str:
        """Represent the ProfileReport as a JSON string

        Returns:
            JSON string
        """

        return self.json

    def to_notebook_iframe(self) -> None:
        """Used to output the HTML representation to a Jupyter notebook.
        When config.notebook.iframe.attribute is "src", this function creates a temporary HTML file
        in `./tmp/profile_[hash].html` and returns an Iframe pointing to that contents.
        When config.notebook.iframe.attribute is "srcdoc", the same HTML is injected in the "srcdoc" attribute of
        the Iframe.

        Notes:
            This constructions solves problems with conflicting stylesheets and navigation links.
        """
        from IPython.display import display

        from ydata_profiling.report.presentation.flavours.widget.notebook import (
            get_notebook_iframe,
        )

        # Ignore warning: https://github.com/ipython/ipython/pull/11350/files
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            display(get_notebook_iframe(self.config, self))

    def to_widgets(self) -> None:
        """The ipython notebook widgets user interface."""
        try:
            from google.colab import files  # noqa: F401

            warnings.warn(
                "Ipywidgets is not yet fully supported on Google Colab (https://github.com/googlecolab/colabtools/issues/60)."
                "As an alternative, you can use the HTML report. See the documentation for more information."
            )
        except ModuleNotFoundError:
            pass

        from IPython.display import display

        display(self.widgets)

    def _repr_html_(self) -> None:
        """The ipython notebook widgets user interface gets called by the jupyter notebook."""
        self.to_notebook_iframe()

    def __repr__(self) -> str:
        """Override so that Jupyter Notebook does not print the object."""
        return ""

    def compare(
        self, other: "ProfileReport", config: Optional[Settings] = None
    ) -> "ProfileReport":
        """Compare this report with another ProfileReport
        Alias for:
        ```
        ydata_profiling.compare([report1, report2], config=config)
        ```
        See `ydata_profiling.compare` for details.

        Args:
            other: the ProfileReport to compare to
            config: the settings object for the merged ProfileReport. If `None`, uses the caller's config

        Returns:
            Comparison ProfileReport
        """
        from ydata_profiling.compare_reports import compare

        return compare([self, other], config if config is not None else self.config)
