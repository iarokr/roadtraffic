# URL to the source of traffic data in Finland
URL_FINTRAFFIC = (
    "https://tie-test.digitraffic.fi/api/tms/history/raw/lamraw_TMS_YY_DD.csv"
)
"""
URL to access raw data from traffic measurement stations, \
installed on the roads in Finland.

Source: `Finntraffic <https://www.fintraffic.fi/en>`_ \
/ `Digitraffic <https://www.digitraffic.fi/en/>`_ under \
`CC 4.0 BY <https://creativecommons.org/licenses/by/4.0/>`_ license.
"""

# Source: `Finntraffic <https://www.fintraffic.fi/en>`_ \
#    `Digitraffic <https://www.digitraffic.fi/en/>`_
#
# Standardized column names for files containing traffic data from Finland

DEF_COL_NAMES_FINTRAFFIC = [
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

DEF_AGG_TIME_PER = 5
"""
Default aggregation time period.
"""

DEF_TAU_LIST = [0.5]
"""
Default list of quantiles to be estimated.
"""

DEF_FILENAME = "lamraw_TMS_YY_DD_bz2.pkl"
"""
Default filename to load processed traffic data from local file. \
Processing is done with :func:`~roadtraffic.utils.load.read_report`
"""

DEF_FILENAME_U = "lamraw_TMS_YY_DD_bz2_u.pkl"
"""
Default filename to load raw data from local file.
"""
