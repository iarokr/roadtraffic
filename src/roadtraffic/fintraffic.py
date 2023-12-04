import typing
import pandas as pd
import numpy as np

from .traffic_data_classes.bagged_data import BaggedData

from .traffic_data_classes.raw_data import RawData
from .traffic_data_classes.aggregated_data import AggregatedData
from .utils import load, process
from .utils.constants import DEF_AGG_TIME_PER, DEF_NUM_BAGS_DENSITY, DEF_NUM_BAGS_FLOW


class TrafficMeasurementStation:
    class Raw(RawData):
        """A class to represent raw data of a traffic measurement station.

        Attributes
        ----------
        tms_id : int
            Traffic measurement station ID, learn more at \
            `Digitraffic <https://www.digitraffic.fi/en/road-traffic/lam/>`_

        days_list : list[tuple[int, int]]
            List of tuples containing year and ordinal day of the year

        data_raw : typing.Optional[pd.DataFrame]
            Raw data of the traffic measurement station

        data_processed : typing.Optional[pd.DataFrame]
            Processed data of the traffic measurement station

        cleaning_params : typing.Optional[dict]
            Parameters used for cleaning the data
        """

        def __init__(self, tms_id: int, days_list: list[tuple[int, int]]):
            super().__init__()
            self.tms_id: int = tms_id
            self.days_list: list[tuple[int, int]] = days_list

            self.data_raw: typing.Optional[pd.DataFrame] = None
            self.data_processed: typing.Optional[pd.DataFrame] = None
            self.cleaning_params: typing.Optional[dict] = None
            pass

        def load(
            self,
            load_path: typing.Optional[str] = None,
            save: bool = False,
            save_path: typing.Optional[str] = None,
            sort: bool = True,
        ) -> None:
            """Load data from local storage or from the Internet.

            Parameters
            ----------
            load_path : typing.Optional[str], optional
                Path to load data from local storage, by default None
            save : bool, optional
                Whether to save the loaded data to local storage, by default False
            save_path : typing.Optional[str], optional
                Path to save the loaded data to local storage, by default None
            sort : bool, optional
                Whether to sort the loaded data by `total_time`, by default True
            """
            self.data_raw = load.read_many_reports(
                self.tms_id,
                self.days_list,
                save=save,
                save_path=save_path,
                sort_total_time=sort,
                load_path=load_path,
            )
            pass

        def clean(self, direction: int, **cleaning_params) -> None:
            """Clean the loaded data.

            Parameters
            ----------
            direction : int
                Direction of the traffic for a given traffic measurement station.
                It is either 1 or 2. Check the direction of a traffic measurement station at
                `Finntraffic <https://liikennetilanne.fintraffic.fi/kartta/>`_
            cleaning_params : dict
                Parameters for cleaning the data, check :func:`~roadtraffic.utils.load.process_data`
            """
            assert (
                self.data_raw is not None
            ), "[LOG] AssertionError: load the data first."
            assert direction in [
                1,
                2,
            ], "[LOG] AssertionError: direction must be either 1 or 2."
            self.cleaning_params = cleaning_params

            try:
                lanes = cleaning_params["lanes"]
            except KeyError:
                lanes = None

            try:
                delete_if_faulty = cleaning_params["delete_if_faulty"]
            except KeyError:
                delete_if_faulty = True

            try:
                hour_from = cleaning_params["hour_from"]
            except KeyError:
                hour_from = 0

            try:
                hour_to = cleaning_params["hour_to"]
            except KeyError:
                hour_to = 23

            try:
                assign_date = cleaning_params["assign_date"]
            except KeyError:
                assign_date = True

            try:
                calculate_vehicles = cleaning_params["calculate_vehicles"]
            except KeyError:
                calculate_vehicles = True

            self.data_processed = load.process_data(
                self.data_raw,
                direction=direction,
                lanes=lanes,
                delete_if_faulty=delete_if_faulty,
                hour_from=hour_from,
                hour_to=hour_to,
                assign_date=assign_date,
                calculate_vehicles=calculate_vehicles,
            )
        pass

    class Aggregated(AggregatedData):
        """A class to represent aggregated data of a traffic measurement station."""

        def __init__(self):
            super().__init__()
            pass

    class Bagged(BaggedData):
        """A class to represent bagged data of a traffic measurement station."""

        def __init__(self):
            super().__init__()
            pass

    def __init__(self, tms_id: int, days_list: list[tuple[int, int]]):
        self.tms_id: int = tms_id
        self.days_list: list[tuple[int, int]] = days_list

        self.raw = TrafficMeasurementStation.Raw(self.tms_id, self.days_list)
        self.agg = TrafficMeasurementStation.Aggregated()
        self.bag = TrafficMeasurementStation.Bagged()
        pass

    def raw_to_agg(
        self,
        aggregation_time_period: int = DEF_AGG_TIME_PER,
        aggregation_time_period_unit: str = "min",
    ) -> None:
        """Convert raw data to aggregated data.

        Parameters
        ----------
        aggregation_time_period : int
            Aggregation time period value, by default DEF_AGG_TIME_PER
        aggregation_time_period_unit : str
            Aggregation time period unit, either "min" or "sec", by default "min"

        Raises
        ------
        AssertionError
            If raw data is not cleaned.
        """
        assert (
            self.raw.data_processed is not None
        ), "[LOG] AssertionError: clean raw data first."
        self.agg.data = process.aggregate(
            self.raw.data_processed,
            aggregation_time_period=aggregation_time_period,
            aggregation_time_period_unit=aggregation_time_period_unit,
        )
        self.agg.aggregation_time_period = aggregation_time_period
        self.agg.aggregation_time_period_unit = aggregation_time_period_unit

        _density = self.agg.data["density"].to_numpy().T
        _flow = self.agg.data["flow"].to_numpy().T
        _speed = self.agg.data["period_speed"].to_numpy().T
        _data_array = (np.stack([_density, _flow, _speed], axis=0)).T
        _data_array = _data_array[np.argsort(_data_array[:, 0])].T
        self.agg._density = _data_array[0]
        self.agg._flow = _data_array[1]
        self.agg._speed = _data_array[2]

        pass

    def agg_to_bag(
        self,
        num_bags_density: int = DEF_NUM_BAGS_DENSITY,
        num_bags_flow: int = DEF_NUM_BAGS_FLOW,
    ) -> None:
        """Convert aggregated data to bagged data.

        Parameters
        ----------
        num_bags_density : int
            Number of bags for density to be used in the bagging procedure, by default DEF_NUM_BAGS_DENSITY
        num_bags_flow : int
            Number of bags for flow to be used in the bagging procedure, by default DEF_NUM_BAGS_FLOW

        Raises
        ------
        AssertionError
            If aggregated data is not aggregated.
        """
        assert (
            self.agg.data is not None
        ), "[LOG] AssertionError: aggregate data first."

        self.bag.data = process.bagging(
            self.agg.data, grid_size_x=num_bags_density, grid_size_y=num_bags_flow
        )
        self.bag.bag_size_flow = num_bags_flow
        self.bag.bag_size_density = num_bags_density

        _density = self.bag.data["centroid_density"].to_numpy().T
        _flow = self.bag.data["centroid_flow"].to_numpy().T
        _weight = self.bag.data["weight"].to_numpy().T
        _data_array = (np.stack([_density, _flow, _weight], axis=0)).T
        _data_array = _data_array[np.argsort(_data_array[:, 0])].T
        self.bag._density = _data_array[0]
        self.bag._flow = _data_array[1]
        self.bag._weight = _data_array[2]

        pass
