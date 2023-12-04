import typing
import pandas as pd


class RawData:
    """A class to represent raw data of a traffic measurement station."""
    def __init__(self):
        self.data_raw: typing.Optional[pd.DataFrame] = None
        pass
