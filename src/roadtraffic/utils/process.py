# import dependencies

import pandas as pd
import numpy as np
import time
import scipy
from typing import Sequence

from . import constant


def aggregate_road(
    data: pd.DataFrame,
    direction: int,
    aggregation_time_period: int = constant.DEF_AGG_TIME_PER,
) -> pd.DataFrame:
    """
    Function, that aggregates the collected data and calculates space-mean speed, \
    flow and density. Space-mean speed is calculated as harmonic average of speeds.

    Parameters
    ----------
    data : pd.DataFrame
        Collected data
    direction : int
        Direction of the road in interest, usually 1 or 2. Check the description of \
        Traffic Measurement Station
    aggregation_time_period : int, optional
        Aggregation time period in minutes, by default constant.DEF_AGG_TIME_PER

    Returns
    -------
    pd.DataFrame
        Aggregated data set
    """
    start_time = time.perf_counter()

    # Initialize resulting DataFrame
    agg_data = pd.DataFrame()

    # Copy initial data set to calculate aggregation periods for a slected direction
    df = data[data["direction"] == direction]
    df["aggregation"] = (df["hour"] * 60 + df["minute"]) / aggregation_time_period
    df = df.astype({"aggregation": int})

    # Aggregate flow and speed by time
    agg_data = df.groupby(
        ["id", "date", "aggregation", "direction"], as_index=False
    ).agg(
        smspeed=("speed", scipy.stats.hmean),
        minute_flow=("cars", "count"),
        minute_cars=("cars", "sum"),
        minute_buses=("buses", "sum"),
        minute_trucks=("trucks", "sum"),
    )

    agg_data["flow"] = 60 / aggregation_time_period * agg_data["minute_flow"]
    agg_data["cars"] = 60 / aggregation_time_period * agg_data["minute_cars"]
    agg_data["buses"] = 60 / aggregation_time_period * agg_data["minute_buses"]
    agg_data["trucks"] = 60 / aggregation_time_period * agg_data["minute_trucks"]
    agg_data["density"] = agg_data["flow"].div(agg_data["smspeed"].values)
    agg_data["seconds"] = agg_data["aggregation"] * 60 * aggregation_time_period
    agg_data["seconds"] = agg_data["seconds"].astype("float64")
    agg_data["time"] = pd.to_datetime(agg_data["seconds"], unit="s")
    agg_data["time"] = pd.Series([val.strftime("%H:%M") for val in agg_data["time"]])

    end_time = time.perf_counter()
    print(f"Aggregation took {end_time-start_time:0.4f} seconds")
    return agg_data


def aggregate_lane(
    data: pd.DataFrame,
    direction: int,
    aggregation_time_period: int = constant.DEF_AGG_TIME_PER,
) -> pd.DataFrame:
    """
    Function, that aggregates the collected data by lane and calculates \
    space-mean speed, flow and density. \
    Space-mean speed is calculated as harmonic average of speeds.

    Parameters
    ----------
    data : pd.DataFrame
        Collected data
    direction : int
        Direction of the road in interest, usually 1 or 2. Check the description of \
        Traffic Measurement Station
    aggregation_time_period : int, optional
        Aggregation time period in minutes, by default constant.DEF_AGG_TIME_PER

    Returns
    -------
    pd.DataFrame
        Aggregated data set
    """
    start_time = time.perf_counter()

    # Initialize resulting DataFrame
    agg_data = pd.DataFrame()

    # Copy initial data set to calculate aggregation periods for a slected direction
    df = data[data["direction"] == direction]
    df["aggregation"] = (df["hour"] * 60 + df["minute"]) / aggregation_time_period
    df = df.astype({"aggregation": int})

    # Aggregate flow and speed by time
    agg_data = df.groupby(
        ["id", "date", "aggregation", "direction", "lane"], as_index=False
    ).agg(
        smspeed=("speed", scipy.stats.hmean),
        minute_flow=("cars", "count"),
        minute_cars=("cars", "sum"),
        minute_buses=("buses", "sum"),
        minute_trucks=("trucks", "sum"),
    )

    agg_data["flow"] = 60 / aggregation_time_period * agg_data["minute_flow"]
    agg_data["cars"] = 60 / aggregation_time_period * agg_data["minute_cars"]
    agg_data["buses"] = 60 / aggregation_time_period * agg_data["minute_buses"]
    agg_data["trucks"] = 60 / aggregation_time_period * agg_data["minute_trucks"]
    agg_data["density"] = agg_data["flow"].div(agg_data["smspeed"].values)
    agg_data["seconds"] = agg_data["aggregation"] * 60 * aggregation_time_period
    agg_data["seconds"] = agg_data["seconds"].astype("float64")
    agg_data["time"] = pd.to_datetime(agg_data["seconds"], unit="s")
    agg_data["time"] = pd.Series([val.strftime("%H:%M") for val in agg_data["time"]])

    end_time = time.perf_counter()
    print(f"Aggregation took {end_time-start_time:0.4f} seconds")
    return agg_data


def bagging(
    agg_data: pd.DataFrame, grid_size_x: int = 70, grid_size_y: int = 400
) -> pd.DataFrame:
    """
    This function is used to reduce computational complexity for \
    convex non-parametric modeling. It merges similar data points \
    into centroid ones, which further will be used for estimation.
    Parameters
    ----------
    agg_data : pd.DataFrame
        Aggregated dataframe
    grid_size_x : int, optional
        Number of bags for x-axis, by default 70
    grid_size_y : int, optional
        Number of bags for y-axis, by default 400

    Returns
    -------
    pd.DataFrame
        pd.DataFrame with bagged data
    """
    start_time = time.perf_counter()

    # Initilize the final data set
    bag_data = pd.DataFrame()
    size_before = len(agg_data)

    # Getting the max density and flow values to calculcate the size of the bag
    maxDensity = agg_data["density"].max()
    maxFlow = agg_data["flow"].max()

    # Calclulating the size of the bag
    grid_density_size = maxDensity / grid_size_x
    grid_flow_size = maxFlow / grid_size_y

    # Assigning the bag number for density and
    agg_data["grid_density"] = agg_data["density"] / grid_density_size
    agg_data["grid_flow"] = agg_data["flow"] / grid_flow_size
    agg_data = agg_data.astype({"grid_density": int, "grid_flow": int})

    # Calculating the centroid and the weight of each bag
    bag_data = agg_data.groupby(
        ["id", "direction", "grid_density", "grid_flow"], as_index=False
    ).agg(
        bag_size=("id", "count"),
        sum_flow=("flow", "sum"),
        sum_density=("density", "sum"),
    )
    bag_data["centroid_flow"] = bag_data["sum_flow"].div(bag_data["bag_size"])
    bag_data["centroid_density"] = bag_data["sum_density"].div(bag_data["bag_size"])
    bag_data["weight"] = bag_data["bag_size"].div(len(agg_data))
    size_after = len(bag_data)

    end_time = time.perf_counter()
    print(
        f"Data bagging took {end_time-start_time:0.4f} seconds. Data reduction is \
        {(1 - size_after/size_before)*100.0:0.2f}%"
    )

    return bag_data


def representor(
    alpha: Sequence[float], beta: Sequence[float], x: Sequence[float]
) -> Sequence[float]:  # noqa E501
    """
    Parameters
    ----------
    alpha : Sequence[float]
        np.array of alpha coefficients
    beta : Sequence[float]
        np.array of beta coefficients
    x : Sequence[float]
        np.array of input variables
    Calculation of representation function (Kuosmanen, 2008 / Formula 4.1)

    Returns
    -------
    Sequence[float]
        The minimum value g_hat for the each x
    """
    alpha_r = alpha.reshape(-1, 1)
    beta_r = beta.reshape(-1, 1)
    x_t = x.reshape(1, -1)
    mult = np.matmul(beta_r, x_t)
    mult_a = alpha_r + mult
    g_hat_min = mult_a.min(axis=0)

    return g_hat_min
