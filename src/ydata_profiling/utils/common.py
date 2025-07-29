"""Common util functions (e.g. missing in Python)."""

import collections.abc
import contextlib
import os
import platform
import subprocess
import zipfile
from datetime import datetime, timedelta

# Monkeypatch bug in imagehdr
from imghdr import tests
from pathlib import Path
from typing import Mapping

import pandas as pd
import requests

from ydata_profiling.version import __version__


def update(d: dict, u: Mapping) -> dict:
    """Recursively update a dict.

    Args:
        d: Dictionary to update.
        u: Dictionary with values to use.

    Returns:
        The merged dictionary.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def _copy(self, target):
    """Monkeypatch for pathlib

    Args:
        self:
        target:

    Returns:

    """
    import shutil

    assert self.is_file()
    shutil.copy(str(self), target)


Path.copy = _copy  # type: ignore


def extract_zip(outfile, effective_path):
    """
    Extracts the contents of a zip file to the specified directory.

    This function takes a zip file and extracts all its contents to the 
    given path. If the provided zip file is invalid, a ValueError 
    is raised.

    Parameters:
    outfile (str): The path to the zip file that needs to be extracted.
    effective_path (str): The directory where the contents of the zip 
                          file will be extracted to.

    Raises:
    ValueError: If the zip file is invalid or cannot be opened.
    """
    try:
        with zipfile.ZipFile(outfile) as z:
            z.extractall(effective_path)
    except zipfile.BadZipFile as e:
        raise ValueError("Bad zip file") from e"""
    try:
        with zipfile.ZipFile(outfile) as z:
            z.extractall(effective_path)
    except zipfile.BadZipFile as e:
        raise ValueError("Bad zip file") from e


def test_jpeg1(h, f):
    """JPEG data in JFIF format"""
    if b"JFIF" in h[:23]:
        return "jpeg"


JPEG_MARK = (
    b"\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06"
    b"\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f"
)


def test_jpeg2(h, f):
    """JPEG with small header"""
    if len(h) >= 32 and h[5] == 67 and h[:32] == JPEG_MARK:
        return "jpeg"


def test_jpeg3(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[6:10] in (b"JFIF", b"Exif") or h[:2] == b"\xff\xd8":
        return "jpeg"


tests.append(test_jpeg1)
tests.append(test_jpeg2)
tests.append(test_jpeg3)


def convert_timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert a Unix timestamp to a datetime object.

    This function takes an integer Unix timestamp as input and converts it to a 
    corresponding datetime object. If the timestamp is non-negative, it returns 
    the datetime representing the local time for the given timestamp. If the 
    timestamp is negative, it returns a datetime object that occurs before the 
    epoch (January 1, 1970) by the number of seconds specified by the timestamp.

    Args:
        timestamp (int): The Unix timestamp to convert.

    Returns:
        datetime: The corresponding datetime object.

    Examples:
        >>> convert_timestamp_to_datetime(1609459200)
        datetime.datetime(2021, 1, 1, 0, 0)

        >>> convert_timestamp_to_datetime(-100000)
        datetime.datetime(1969, 12, 31, 23, 46, 40)
    """
    if timestamp >= 0:
        return datetime.fromtimestamp(timestamp)
    else:
        return datetime(1970, 1, 1) + timedelta(seconds=int(timestamp))


def analytics_features(
    dataframe: str, datatype: str, report_type: str, ncols: int, nrows: int, dbx: str
) -> None:
    """dataframe: str, datatype: str, report_type: str, ncols: int, nrows: int, dbx: str
) -> None:
    """
    Sends analytics data to a specified endpoint regarding the profiling
    of a dataframe.

    This function constructs a request message that includes details such
    as the package version, Python version, report type, dataframe metadata,
    operating system, GPU presence, and other parameters. The information
    is then sent as a GET request to the YData Profiling endpoint.

    Parameters:
    -----------
    dataframe : str
        The name of the dataframe being analyzed.

    datatype : str
        The type of data contained within the dataframe (e.g., numerical,
        categorical).

    report_type : str
        The type of report to be generated (e.g., summary, detailed).

    ncols : int
        The number of columns in the dataframe.

    nrows : int
        The number of rows in the dataframe.

    dbx : str
        The database connection string or identifier.

    Returns:
    --------
    None
        This function does not return any value. It only transmits data to
        the analytics endpoint.

    Raises:
    -------
    Exception
        If an error occurs during the request or while checking for GPU
        presence, it is suppressed and does not stop the execution.

    Notes:
    ------
    The function will not send analytics if the environment variable
    "YDATA_PROFILING_NO_ANALYTICS" is set, or if the package version is 
    in development mode ("0.0.dev0").
    """
    endpoint = "https://packages.ydata.ai/ydata-profiling?"
    package_version = __version__

    if (
        bool(os.getenv("YDATA_PROFILING_NO_ANALYTICS")) is not True
        and package_version != "0.0.dev0"
    ):
        try:
            subprocess.check_output("nvidia-smi")
            gpu_present = True
        except Exception:
            gpu_present = False

        python_version = ".".join(platform.python_version().split(".")[:2])

        with contextlib.suppress(Exception):
            request_message = (
                f"{endpoint}version={package_version}"
                f"&python_version={python_version}"
                f"&report_type={report_type}"
                f"&dataframe={dataframe}"
                f"&ncols={ncols}"
                f"&nrows={nrows}"
                f"&datatype={datatype}"
                f"&os={platform.system()}"
                f"&gpu={str(gpu_present)}"
                f"&dbx={dbx}"
            )

            requests.get(request_message)


def is_running_in_databricks():
    """
    Check if the current environment is Databricks.

    This function inspects the environment variables to determine
    whether the code is being executed within a Databricks runtime.
    If the Databricks runtime version is found in the environment,
    it returns the version as a string. Otherwise, it returns a 
    boolean string indicating whether the Databricks runtime 
    variable was found.

    Returns:
        str: The Databricks runtime version if running in Databricks,
             otherwise "False" if the runtime variable is not found,
             or "True" if the variable is found but the version is not.
    """
    mask = "DATABRICKS_RUNTIME_VERSION" in os.environ
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        return os.environ["DATABRICKS_RUNTIME_VERSION"]
    else:
        return str(mask)


def calculate_nrows(df):
    """
    Calculates the approx. number of rows spark dataframes

    Returns: int, approximate number of rows
    """
    if isinstance(df, pd.DataFrame):
        if df is not None:
            nrows = len(df)
        else:
            nrows = 0
    else:
        try:
            n_partitions = df.rdd.getNumPartitions()

            nrows = (
                df.rdd.mapPartitionsWithIndex(
                    lambda idx, partition: [sum(1 for _ in partition)]
                    if idx == 0
                    else [0]
                ).collect()[0]
                * n_partitions
            )
        except Exception:
            nrows = 0

    return nrows
