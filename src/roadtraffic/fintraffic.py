import typing

import numpy as np
import pandas as pd

from .traffic_data_classes.aggregated_data import AggregatedData
from .traffic_data_classes.bagged_data import BaggedData
from .traffic_data_classes.raw_data import RawData
from .traffic_data_classes.rolling_data import RollingData
from .utils import load, process
from .utils.constants import (
    DEF_AGG_TIME_PER,
    DEF_NUM_BAGS_DENSITY,
    DEF_NUM_BAGS_FLOW,
    LANES,
    TMS_LIST,
    DEF_ROLLING_WINDOW_INTERVAL,
    DEF_ROLLING_WINDOW_INTERVAL_UNIT,
    DEF_ROLLING_GAP_INTERVAL,
    DEF_ROLLING_GAP_INTERVAL_UNIT,
)


class TrafficMeasurementStation:
    class _Raw(RawData):
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

            cleaning_params["direction"] = direction

            if self.tms_id in TMS_LIST:
                lanes = LANES[self.tms_id][direction]
                cleaning_params["lanes"] = lanes
            else:
                try:
                    lanes = cleaning_params["lanes"]
                except KeyError:
                    lanes = None
                    cleaning_params["lanes"] = lanes

            try:
                delete_if_faulty = cleaning_params["delete_if_faulty"]
            except KeyError:
                delete_if_faulty = True
                cleaning_params["delete_if_faulty"] = delete_if_faulty

            try:
                hour_from = cleaning_params["hour_from"]
            except KeyError:
                hour_from = 0
                cleaning_params["hour_from"] = hour_from

            try:
                hour_to = cleaning_params["hour_to"]
            except KeyError:
                hour_to = 23
                cleaning_params["hour_to"] = hour_to

            try:
                assign_date = cleaning_params["assign_date"]
            except KeyError:
                assign_date = True
                cleaning_params["assign_date"] = assign_date

            try:
                calculate_vehicles = cleaning_params["calculate_vehicles"]
            except KeyError:
                calculate_vehicles = True
                cleaning_params["calculate_vehicles"] = calculate_vehicles

            self.cleaning_params = cleaning_params

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

    class _Aggregated(AggregatedData):
        """A class to represent aggregated data of a traffic measurement station."""

        def __init__(self):
            super().__init__()
            pass

    class _Bagged(BaggedData):
        """A class to represent bagged data of a traffic measurement station."""

        def __init__(self):
            super().__init__()
            pass

    class _Rolling(RollingData):
        """A class to represent rolling data of a traffic measurement station."""

        def __init__(self):
            super().__init__()
            pass

    def __init__(self, tms_id: int, days_list: list[tuple[int, int]]):
        self.tms_id: int = tms_id
        self.days_list: list[tuple[int, int]] = days_list

        self.raw = TrafficMeasurementStation._Raw(self.tms_id, self.days_list)
        self.agg = TrafficMeasurementStation._Aggregated()
        self.bag = TrafficMeasurementStation._Bagged()
        self.roll = TrafficMeasurementStation._Rolling()
        pass

    def raw_to_agg(
        self,
        aggregation_time_period: int = DEF_AGG_TIME_PER,
        aggregation_time_period_unit: str = "min",
        by_lane: bool = False,
    ) -> None:
        """Convert raw data to aggregated data.

        Parameters
        ----------
        aggregation_time_period : int
            Aggregation time period value, by default DEF_AGG_TIME_PER
        aggregation_time_period_unit : str
            Aggregation time period unit, either "min" or "sec", by default "min"
        by_lane : bool
            Whether to aggregate by lane (by_lane=True) or by road direction (by_lane=False), by default False

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
            by_lane=by_lane,
        )
        self.agg.aggregation_time_period = aggregation_time_period
        self.agg.aggregation_time_period_unit = aggregation_time_period_unit
        self.agg.aggregation_by_lane = by_lane

        _density = self.agg.data["density"].to_numpy().T
        _flow = self.agg.data["flow"].to_numpy().T
        _speed = self.agg.data["speed"].to_numpy().T
        _data_array = (np.stack([_density, _flow, _speed], axis=0)).T
        _data_array = _data_array[np.argsort(_data_array[:, 0])].T
        self.agg._density = _data_array[0]
        self.agg._flow = _data_array[1]
        self.agg._speed = _data_array[2]

        pass

    def raw_to_roll(
        self,
        window_interval: int = DEF_ROLLING_WINDOW_INTERVAL,
        window_interval_unit: str = DEF_ROLLING_WINDOW_INTERVAL_UNIT,
        gap_interval: int = DEF_ROLLING_GAP_INTERVAL,
        gap_interval_unit: str = DEF_ROLLING_GAP_INTERVAL_UNIT,
        by_lane: bool = False,
    ) -> None:
        """
        Create a rolling window representation of the data.

        Parameters
        ----------
        window_interval: int
            Size of the window in `window_interval_unit` units, by default DEF_ROLLING_WINDOW_INTERVAL
        window_interval_unit: str
            Unit of the window size, either 'min' or 'sec', by default DEF_ROLLING_WINDOW_INTERVAL_UNIT
        gap_interval: int
            Size of the gap between window intervals in `window_interval_unit` units, by default DEF_ROLLING_GAP_INTERVAL
        gap_interval_unit:
            Unit of the gap size, either 'min' or 'sec', by default DEF_ROLLING_GAP_INTERVAL_UNIT
        by_lane: bool
            Whether to create rollings by lane (by_lane=True) or by road direction (by_lane=False), by default False

        Returns
        -------
        pd.DataFrame
            A rolling window representation of the data

        Raises
        ------
        AssertionError
            If raw.data_processed does not exist.
        """
        assert (
            self.raw.data_processed is not None
        ), "[LOG] AssertionError: clean the data first."
        assert window_interval_unit in [
            "min",
            "sec",
        ], "[LOG] AssertionError: window_interval_unit must be either 'min' or 'sec'."
        assert gap_interval_unit in [
            "min",
            "sec",
        ], "[LOG] AssertionError: gap_interval_unit must be either 'min' or 'sec'."
        assert (
            window_interval > 0
        ), "[LOG] AssertionError: window_interval must be greater than 0."
        assert (
            gap_interval > 0
        ), "[LOG] AssertionError: gap_interval must be greater than 0."

        rolling_df = process.rolling_window(
            self.raw.data_processed,
            hour_from=self.raw.cleaning_params["hour_from"],
            hour_to=self.raw.cleaning_params["hour_to"],
            window_interval=window_interval,
            gap_interval=gap_interval,
            window_interval_unit=window_interval_unit,
            gap_interval_unit=gap_interval_unit,
            by_lane=by_lane,
        )

        # update rolling data
        if self.roll.data is None:
            self.roll.data = {}

        add = "road"
        if by_lane:
            add = "lane"

        self.roll.data[
            f"{window_interval}{window_interval_unit}_{gap_interval}{gap_interval_unit}_{add}"
        ] = rolling_df

        pass

    def agg_to_bag(
        self,
        num_bags_density: int = DEF_NUM_BAGS_DENSITY,
        num_bags_flow: int = DEF_NUM_BAGS_FLOW,
        context: typing.Optional[str] = None,
    ) -> None:
        """Convert aggregated data to bagged data.

        Parameters
        ----------
        num_bags_density : int
            Number of bags for density to be used in the bagging procedure, by default DEF_NUM_BAGS_DENSITY
        num_bags_flow : int
            Number of bags for flow to be used in the bagging procedure, by default DEF_NUM_BAGS_FLOW
        context : typing.Optional[str], optional
            Column name to group the data by, by default None

        Raises
        ------
        AssertionError
            If aggregated data is not aggregated.
        """
        assert self.agg.data is not None, "[LOG] AssertionError: aggregate data first."
        assert (
            num_bags_flow > 0
        ), "[LOG] AssertionError: num_bags_flow must be greater than 0."
        assert (
            num_bags_density > 0
        ), "[LOG] AssertionError: num_bags_density must be greater than 0."

        if context is not None:
            assert (
                context in self.agg.data.columns
            ), "[LOG] AssertionError: context must be a column in the data."

        self.bag.data = process.bagging(
            self.agg.data,
            grid_size_x=num_bags_density,
            grid_size_y=num_bags_flow,
            group_by=context,
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
        self.bag.context = context

        pass
