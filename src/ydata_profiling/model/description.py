from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from pandas import Timedelta


@dataclass
class BaseAnalysis:
    """Description of base analysis module of report.
    Overall info about report.

    Attributes
        title (str): Title of report.
        date_start (Union[datetime, List[datetime]]): Start of generating description.
        date_end (Union[datetime, List[datetime]]): End of generating description.
    """

    title: str
    date_start: Union[datetime, List[datetime]]
    date_end: Union[datetime, List[datetime]]

    def __init__(self, title: str, date_start: datetime, date_end: datetime) -> None:
        """self,
    n_series: int,
    length: int,
    start: Any,
    end: Any,
    period: float,
    frequency: Optional[str] = None,
) -> None:
    """
    Initializes a new instance of the class.

    Parameters:
    n_series (int): The number of time series to be generated or handled.
    length (int): The length of each time series.
    start (Any): The starting point of the time series, can be of various types (e.g., date, integer).
    end (Any): The ending point of the time series, can be of various types (e.g., date, integer).
    period (float): The period of the time series, specified as a float value.
    frequency (Optional[str]): The frequency of the time series (e.g., 'daily', 'monthly'). If not provided, defaults to None.

    Returns:
    None: This initializer does not return a value.
    """
        self.title = title
        self.date_start = date_start
        self.date_end = date_end

    @property
    def duration(self) -> Union[timedelta, List[timedelta]]:
        """def duration(self) -> Union[timedelta, List[timedelta]]:
    """
    Calculates the duration between start and end dates.

    Depending on the types of `date_start` and `date_end`, this property 
    returns the duration as follows:

    - If both `date_start` and `date_end` are instances of `datetime`, 
      it returns a single `timedelta` object representing the difference 
      between `date_end` and `date_start`.
    
    - If both `date_start` and `date_end` are lists of `datetime` objects, 
      it returns a list of `timedelta` objects, each representing the 
      duration between the corresponding start and end dates from the lists.

    Raises:
        TypeError: If `date_start` and `date_end` are not both `datetime` 
        or both lists of `datetime` objects.

    Returns:
        Union[timedelta, List[timedelta]]: The calculated duration(s).
    """
        if isinstance(self.date_start, datetime) and isinstance(
            self.date_end, datetime
        ):
            return self.date_end - self.date_start
        if isinstance(self.date_start, list) and isinstance(self.date_end, list):
            return [
                self.date_end[i] - self.date_start[i]
                for i in range(len(self.date_start))
            ]
        else:
            raise TypeError()


@dataclass
class TimeIndexAnalysis:
    """Description of timeseries index analysis module of report.

    Attributes:
        n_series (Union[int, List[int]): Number of time series identified in the dataset.
        length (Union[int, List[int]): Number of data points in the time series.
        start (Any): Starting point of the time series.
        end (Any): Ending point of the time series.
        period (Union[float, List[float]): Average interval between data points in the time series.
        frequency (Union[Optional[str], List[Optional[str]]): A string alias given to useful common time series frequencies, e.g. H - hours.
    """

    n_series: Union[int, List[int]]
    length: Union[int, List[int]]
    start: Any
    end: Any
    period: Union[float, List[float], Timedelta, List[Timedelta]]
    frequency: Union[Optional[str], List[Optional[str]]]

    def __init__(
        self,
        n_series: int,
        length: int,
        start: Any,
        end: Any,
        period: float,
        frequency: Optional[str] = None,
    ) -> None:
        """self,
    n_series: int,
    length: int,
    start: Any,
    end: Any,
    period: float,
    frequency: Optional[str] = None,
) -> None:
    """
    Initializes a new instance of the class.

    Parameters:
    n_series (int): The number of time series to be generated or handled.
    length (int): The length of each time series.
    start (Any): The starting point of the time series, can be of various types (e.g., date, integer).
    end (Any): The ending point of the time series, can be of various types (e.g., date, integer).
    period (float): The period of the time series, specified as a float value.
    frequency (Optional[str]): The frequency of the time series (e.g., 'daily', 'monthly'). If not provided, defaults to None.

    Returns:
    None: This initializer does not return a value.
    """
        self.n_series = n_series
        self.length = length
        self.start = start
        self.end = end
        self.period = period
        self.frequency = frequency


@dataclass
class BaseDescription:
    """Description of DataFrame.

    Attributes:
        analysis (BaseAnalysis): Base info about report. Title, start time and end time of description generating.
        time_index_analysis (Optional[TimeIndexAnalysis]): Description of timeseries index analysis module of report.
        table (Any): DataFrame statistic. Base information about DataFrame.
        variables (Dict[str, Any]): Description of variables (columns) of DataFrame. Key is column name, value is description dictionary.
        scatter (Any): Pairwise scatter for all variables. Plot interactions between variables.
        correlations (Dict[str, Any]): Prepare correlation matrix for DataFrame
        missing (Dict[str, Any]): Describe missing values.
        alerts (Any): Take alerts from all modules (variables, scatter, correlations), and group them.
        package (Dict[str, Any]): Contains version of ydata-profiling and config.
        sample (Any): Sample of data.
        duplicates (Any): Description of duplicates.
    """

    analysis: BaseAnalysis
    time_index_analysis: Optional[TimeIndexAnalysis]
    table: Any
    variables: Dict[str, Any]
    scatter: Any
    correlations: Dict[str, Any]
    missing: Dict[str, Any]
    alerts: Any
    package: Dict[str, Any]
    sample: Any
    duplicates: Any
