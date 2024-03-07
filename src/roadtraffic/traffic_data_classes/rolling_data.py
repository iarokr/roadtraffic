import typing

import pandas as pd


class RollingData:
    """A class to represent rolling data of a traffic measurement station.

    Attributes:
    -----------
    data : typing.Optional[dict[str, pd.DataFrame]]
        Dictionary with dataframes with rolling data of the traffic measurement station.
        Keys are in the form of "5min_15sec_lane", where the first part is the window interval,
        the second part is the gap interval
        and the last one is whether the rolling windows were created by lane or by road.
    """

    def __init__(self):
        self.data: typing.Optional[dict[str, pd.DataFrame]] = None
        pass
