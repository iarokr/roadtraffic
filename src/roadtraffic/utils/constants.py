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

TMS_LIST: list[int] = [10, 11, 109, 116, 118, 126, 145, 146, 147, 148, 149]
"""
List of the most used traffic measurement stations.
"""


LANES: dict = {
    10: {1: [1, 2, 3], 2: [4, 5, 6]},
    11: {1: [1, 2], 2: [3, 4]},
    109: {1: [1, 2], 2: [3, 4]},
    116: {1: [1, 2, 3], 2: [4, 5, 6]},
    118: {1: [1, 2, 3, 4, 5], 2: [6, 7, 8]},
    126: {1: [1, 2, 3], 2: [4, 5, 6]},
    145: {1: [1, 2, 3], 2: [4, 5, 6, 7]},
    146: {1: [1, 2, 3], 2: [4, 5, 6]},
    147: {1: [1, 2, 3, 4], 2: [5, 6, 7, 8]},
    148: {1: [1, 2], 2: [3, 4]},
    149: {1: [1, 2], 2: [3, 4]},
}
"""
Dictionary of the most used traffic measurement stations and their lanes.
"""

FREE_FLOW_SPEED: dict = {
    10: {1: 70, 2: 70},
    11: {1: 60, 2: 60},
    109: {1: 100, 2: 100},
    116: {1: 60, 2: 60},
    118: {1: 60, 2: 60},
    126: {1: 80, 2: 80},
    145: {1: 80, 2: 80},
    146: {1: 80, 2: 80},
    147: {1: 80, 2: 80},
    148: {1: 80, 2: 80},
    149: {1: 80, 2: 80},
}
"""
Dictionary of the most used traffic measurement stations and their \
free flow speeds.
"""

DEF_ROLLING_WINDOW_INTERVAL: int = 5
"""
Default rolling window interval.
"""

DEF_ROLLING_WINDOW_INTERVAL_UNIT: str = "min"
"""
Default rolling window interval unit.
"""

DEF_ROLLING_GAP_INTERVAL: int = 15
"""
Default rolling gap interval.
"""

DEF_ROLLING_GAP_INTERVAL_UNIT: str = "sec"
"""
Default rolling gap interval unit.
"""
