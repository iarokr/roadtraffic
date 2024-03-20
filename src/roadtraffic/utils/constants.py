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

TMS_LIST: list[int] = [
    10,
    11,
    103,
    117,
    109,
    116,
    118,
    126,
    145,
    146,
    147,
    148,
    149,
    205,
    227,
    230,
    231,
    233,
    234,
    235,
    237,
    238,
    239,
    240,
    249,
    251,
    252,
    257,
    401,
    431,
    435,
    436,
    438,
    449,
    450,
    451,
    452,
    455,
    457,
    458,
    460,
    462,
    463,
    471,
]
"""
List of the most used traffic measurement stations.
"""


LANES: dict = {
    10: {1: [1, 2, 3], 2: [4, 5, 6]},
    11: {1: [1, 2], 2: [3, 4]},
    103: {1: [1, 2], 2: [3, 4, 5]},
    109: {1: [1, 2], 2: [3, 4]},
    116: {1: [1, 2, 3], 2: [4, 5, 6]},
    117: {1: [1, 2], 2: [3, 4, 5]},
    118: {1: [1, 2, 3, 4, 5], 2: [6, 7, 8]},
    126: {1: [1, 2, 3], 2: [4, 5, 6]},
    145: {1: [1, 2, 3], 2: [4, 5, 6, 7]},
    146: {1: [1, 2, 3], 2: [4, 5, 6]},
    147: {1: [1, 2, 3, 4], 2: [5, 6, 7, 8]},
    148: {1: [1, 2], 2: [3, 4]},
    149: {1: [1, 2], 2: [3, 4]},
    205: {1: [1, 2], 2: [3, 4]},
    227: {1: [1, 2], 2: [3, 4]},
    230: {1: [1], 2: [2]},
    231: {1: [1], 2: [2]},
    233: {1: [1, 2], 2: [3, 4]},
    234: {1: [1, 2], 2: [3, 4, 5]},
    235: {1: [1, 2], 2: [3, 4]},
    237: {1: [1, 2, 3], 2: [4, 5, 6]},
    238: {1: [1, 2], 2: [3, 4, 5]},
    239: {1: [1, 2], 2: [3, 4]},
    240: {1: [1, 2], 2: [3, 4]},
    249: {1: [1, 2], 2: [3, 4]},
    251: {1: [1], 2: [2]},
    252: {1: [1], 2: [2]},
    257: {1: [1, 2], 2: [3, 4]},
    401: {1: [1, 2], 2: [3, 4]},
    431: {1: [1], 2: [2]},
    435: {1: [1, 2], 2: [3, 4]},
    436: {1: [1], 2: [2]},
    438: {1: [1, 2], 2: [3, 4]},
    449: {1: [1, 2], 2: [3, 4]},
    450: {1: [1, 2], 2: [3, 4]},
    451: {1: [1], 2: [2]},
    452: {1: [1, 2, 3], 2: [4, 5, 6]},
    455: {1: [1, 2], 2: [3, 4]},
    457: {1: [1, 2], 2: [3, 4]},
    458: {1: [1, 2], 2: [3, 4]},
    460: {1: [1, 2], 2: [3, 4]},
    462: {1: [1, 2], 2: [3, 4]},
    463: {1: [1, 2], 2: [3, 4]},
    471: {1: [1, 2], 2: [3, 4]},
}
"""
Dictionary of the most used traffic measurement stations and their lanes.
"""

FREE_FLOW_SPEED: dict = {
    10: {1: 70, 2: 70},
    11: {1: 60, 2: 60},
    103: {1: 80, 2: 100},
    109: {1: 100, 2: 100},
    116: {1: 60, 2: 60},
    117: {1: 80, 2: 60},
    118: {1: 60, 2: 60},
    126: {1: 80, 2: 80},
    145: {1: 80, 2: 80},
    146: {1: 80, 2: 80},
    147: {1: 80, 2: 80},
    148: {1: 80, 2: 80},
    149: {1: 80, 2: 80},
    205: {1: 100, 2: 100},
    227: {1: 120, 2: 120},
    230: {1: 60, 2: 60},
    231: {1: 80, 2: 80},
    233: {1: 100, 2: 100},
    234: {1: 100, 2: 100},
    235: {1: 80, 2: 80},
    237: {1: 80, 2: 80},
    238: {1: 100, 2: 100},
    239: {1: 120, 2: 120},
    240: {1: 120, 2: 120},
    249: {1: 100, 2: 100},
    251: {1: 60, 2: 60},
    252: {1: 80, 2: 80},
    257: {1: 50, 2: 50},
    401: {1: 100, 2: 100},
    431: {1: 80, 2: 80},
    435: {1: 100, 2: 100},
    436: {1: 60, 2: 60},
    438: {1: 70, 2: 60},
    449: {1: 100, 2: 100},
    450: {1: 100, 2: 100},
    451: {1: 80, 2: 80},
    452: {1: 60, 2: 60},
    455: {1: 70, 2: 70},
    457: {1: 70, 2: 70},
    458: {1: 70, 2: 70},
    460: {1: 100, 2: 100},
    462: {1: 100, 2: 100},
    463: {1: 100, 2: 100},
    471: {1: 100, 2: 100},
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
