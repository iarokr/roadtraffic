import pandas as pd
import numpy as np
from typing import Sequence
import scipy
import time

from .constants import DEF_AGG_TIME_PER


def aggregate(
    data: pd.DataFrame,
    by_lane: bool = False,
    aggregation_time_period: int = DEF_AGG_TIME_PER,
    aggregation_time_period_unit: str = "min",
) -> pd.DataFrame:
    assert aggregation_time_period_unit in ["min", "sec"], "[LOG]: AssertionError: Wrong aggregation time period unit." # noqa E501
    start_time = time.perf_counter()

    # Copy initial data set to calculate aggregation periods for a selected direction
    df = data.copy(deep=True)
    if aggregation_time_period_unit == "min":
        df["aggregation"] = (df["hour"] * 60 + df["minute"]) / aggregation_time_period
    if aggregation_time_period_unit == "sec":
        df["aggregation"] = (
            df["hour"] * 60 * 60 + df["minute"] * 60 + df["second"]
        ) / aggregation_time_period
    df = df.astype({"aggregation": int})

    # Aggregate flow and speed by time
    if by_lane:
        agg_data = df.groupby(
            ["id", "date", "aggregation", "direction", "lane"], as_index=False
        ).agg(
            period_speed=("speed", scipy.stats.hmean),
            period_flow=("cars", "count"),
            period_cars=("cars", "sum"),
            period_buses=("buses", "sum"),
            period_trucks=("trucks", "sum"),
        )
    else:
        agg_data = df.groupby(
            ["id", "date", "aggregation", "direction"], as_index=False
        ).agg(
            period_speed=("speed", scipy.stats.hmean),
            period_flow=("cars", "count"),
            period_cars=("cars", "sum"),
            period_buses=("buses", "sum"),
            period_trucks=("trucks", "sum"),
        )

    agg_data["flow"] = 60 / aggregation_time_period * agg_data["period_flow"]
    agg_data["cars"] = 60 / aggregation_time_period * agg_data["period_cars"]
    agg_data["buses"] = 60 / aggregation_time_period * agg_data["period_buses"]
    agg_data["trucks"] = 60 / aggregation_time_period * agg_data["period_trucks"]
    agg_data["density"] = agg_data["flow"].div(agg_data["period_speed"].values)
    agg_data["seconds"] = agg_data["aggregation"] * 60 * aggregation_time_period
    agg_data["seconds"] = agg_data["seconds"].astype("float64")
    agg_data["time"] = pd.to_datetime(agg_data["seconds"], unit="s")
    agg_data["time"] = pd.Series([val.strftime("%H:%M") for val in agg_data["time"]])

    end_time = time.perf_counter()

    print(f"Aggregation took {end_time-start_time:.4f} seconds")
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
    size_before = len(agg_data)

    # Getting the max density and flow values to calculate the size of the bag
    max_density = agg_data["density"].max()
    max_flow = agg_data["flow"].max()

    # Calculating the size of the bag
    grid_density_size = max_density / grid_size_x
    grid_flow_size = max_flow / grid_size_y

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
        f"Data bagging took {end_time-start_time:.4f} seconds. Data reduction is {(1 - size_after/size_before)*100.0:.2f}%" # noqa E501
    )

    return bag_data


def representor(
    alpha: Sequence[float], beta: Sequence[float], x: Sequence[float]
) -> Sequence[float]:  # noqa E501
    """
    Parameters
    ----------
    alpha : Sequence[float]
        A numpy array of alpha coefficients
    beta : Sequence[float]
        A numpy array of beta coefficients
    x : Sequence[float]
        A numpy array of input variables
    Calculation of representation function (Kuosmanen, 2008 / Formula 4.1)

    Returns
    -------
    ArrayLike[float]
        The minimum value of g_hat for each x
    """
    alpha_r = alpha.reshape(-1, 1)
    beta_r = beta.reshape(-1, 1)
    x_t = x.reshape(1, -1)
    mult = np.matmul(beta_r, x_t)
    mult_a = alpha_r + mult
    g_hat_min = mult_a.min(axis=0)

    return g_hat_min
