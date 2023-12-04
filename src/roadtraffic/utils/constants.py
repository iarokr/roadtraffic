from typing import Union, Any

URL_FINTRAFFIC: str = (
    "https://tie.digitraffic.fi/api/tms/v1/history/raw/lamraw_TMS_YY_DD.csv"
)
"""
URL to access raw data from traffic measurement stations, \
installed on the roads in Finland.

Source: `Finntraffic <https://www.fintraffic.fi/en>`_ \
/ `Digitraffic <https://www.digitraffic.fi/en/>`_ under \
`CC 4.0 BY <https://creativecommons.org/licenses/by/4.0/>`_ license.
"""

DEF_COL_NAMES_FINTRAFFIC: list[Union[str, Any]] = [
    "id",
    "year",
    "day",
    "hour",
    "minute",
    "second",
    "hund_second",
    "length",
    "lane",
    "direction",
    "vehicle",
    "speed",
    "faulty",
    "total_time",
    "time_interval",
    "queue_start",
]
"""
Standardized column names for files containing traffic data from Finland.
"""

DEF_AGG_TIME_PER: int = 5
"""
Default aggregation time period.
"""

DEF_TAU_LIST: list[float] = [0.5]
"""
Default list of quantiles to be estimated.
"""

DEF_FILENAME: str = "lamraw_TMS_YY_DD_bz2.pkl"
"""
Default filename to load processed traffic data from local file. \
Processing is done with :func:`~roadtraffic.utils.load.read_report`
"""

DEF_FILENAME_U: str = "lamraw_TMS_YY_DD_bz2_u.pkl"
"""
Default filename to load raw data from local file.
"""

DEF_NUM_BAGS_DENSITY: int = 70
"""
Default number of bags for density to be used in the bagging procedure.
"""

DEF_NUM_BAGS_FLOW: int = 400
"""
Default number of bags for flow to be used in the bagging procedure.
"""
