import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

from . import fintraffic
from .utils.funcs import day_to_date


class Plotter:
    """
    Plotting class.
    """

    @staticmethod
    def timeline(
        tms: fintraffic.TrafficMeasurementStation,
        plot_type: str = "scatter",
    ) -> (plt.Figure, plt.Axes):
        """
        Plot main traffic characteristics (flow, density, speed) from aggregated data against time.
        Parameters
        ----------
        tms: roadtraffic.fintraffic.TrafficMeasurementStation
            Traffic Measurement Station object.
        plot_type: str
            Type of plot to be used. Possible values: "scatter", "line", by default "scatter".

        Returns
        -------
        fig: matplotlib.figure.Figure
            Figure object.
        ax: matplotlib.axes.Axes
            Axes object.

        Raises
        ------
        ValueError
            If plot_type is not "scatter" or "line".
        """
        return _plot_against_time(tms, plot_type)

    @staticmethod
    def fundamental(
        tms: fintraffic.TrafficMeasurementStation,
        x: str = "density",
        y: str = "flow",
        data_type: str = "agg",
    ) -> (plt.Figure, plt.Axes):
        """
        Plot fundamental diagram.
        Parameters
        ----------
        tms: roadtraffic.fintraffic.TrafficMeasurementStation
            Traffic Measurement Station object.
        x: str
            x-axis variable. Possible values: "density", "speed", by default "density".
        y: str
            y-axis variable. Possible values: "flow", "speed", by default "flow".
        data_type: str
            Type of data to be used. Possible values: "agg", "bag", "bag_sized", by default "agg".

        Returns
        -------
        fig: matplotlib.figure.Figure
            Figure object.
        ax: matplotlib.axes.Axes
            Axes object.

        Raises
        ------
        ValueError
            If x or y is not "density", "flow" or "speed".
        ValueError
            If data_type is not "agg", "bag" or "bag_sized".
        """
        return _plot_fundamental_diagram(tms, x, y, data_type)


def _plot_against_time(
    tms: fintraffic.TrafficMeasurementStation,
    plot_type: str = "scatter",
) -> (plt.Figure, plt.Axes):
    """
    Plot main traffic characteristics against time.
    Parameters
    ----------
    tms: roadtraffic.fintraffic.TrafficMeasurementStation
        Traffic Measurement Station object.
    plot_type: str
        Type of plot to be used. Possible values: "scatter", "line", by default "scatter".

    Returns
    -------
    fig: matplotlib.figure.Figure
        Figure object.
    ax: matplotlib.axes.Axes
        Axes object.

    Raises
    ------
    ValueError
        If plot_type is not "scatter" or "line".
    """
    sns.color_palette("Set2")

    fig, ax = plt.subplots(3, 1, sharex="col", figsize=(8, 18))

    lane_append = "" if not tms.agg.aggregation_by_lane else "/lane"

    # Setting title
    day_string = ""
    if len(tms.days_list) == 1:
        day_string = f"{day_to_date(tms.days_list[0][0], tms.days_list[0][1])}"
    else:
        day_string = f"{day_to_date(tms.days_list[0][0], tms.days_list[0][1])} - {day_to_date(tms.days_list[-1][0], tms.days_list[-1][1])}"  # noqa E501
    fig.suptitle(
        f"TMS {tms.tms_id} on {day_string}, {tms.agg.aggregation_time_period} {tms.agg.aggregation_time_period_unit} intervals"
    )  # noqa E501

    # Plotting
    if plot_type == "scatter":
        if tms.agg.aggregation_by_lane:
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="flow",
                hue="lane",
                ax=ax[0],
                palette="Set2",
            )
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="period_speed",
                hue="lane",
                ax=ax[1],
                palette="Set2",
            )
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="density",
                hue="lane",
                ax=ax[2],
                palette="Set2",
            )
        else:
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="flow",
                ax=ax[0],
                palette="Set2",
            )
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="period_speed",
                ax=ax[1],
                palette="Set2",
            )
            sns.scatterplot(
                data=tms.agg.data,
                x="time",
                y="density",
                ax=ax[2],
                palette="Set2",
            )
    elif plot_type == "line":
        if tms.agg.aggregation_by_lane:
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="flow",
                hue="lane",
                ax=ax[0],
                palette="Set2",
            )
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="period_speed",
                hue="lane",
                ax=ax[1],
                palette="Set2",
            )
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="density",
                hue="lane",
                ax=ax[2],
                palette="Set2",
            )
        else:
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="flow",
                ax=ax[0],
                palette="Set2",
            )
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="period_speed",
                ax=ax[1],
                palette="Set2",
            )
            sns.lineplot(
                data=tms.agg.data,
                x="time",
                y="density",
                ax=ax[2],
                palette="Set2",
            )
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

    # Setting titles
    ax[0].set_title(f"Flow [veh/h{lane_append}]")
    ax[0].set_ylabel(f"flow [veh/h{lane_append}]")

    ax[1].set_title("Speed [km/h]")
    ax[1].set_ylabel("Speed [km/h]")

    ax[2].set_title(f"Density [veh/km{lane_append}]")
    ax[2].set_ylabel(f"Density [veh/km{lane_append}]")

    # formatting time axis
    plt.gca().xaxis.set_major_locator(
        plt.MaxNLocator(
            nbins=tms.raw.cleaning_params["hour_to"]
            + 2
            - tms.raw.cleaning_params["hour_from"]
        )
    )
    plt.gcf().autofmt_xdate()

    # formatting y_axis
    if tms.agg.aggregation_by_lane:
        ax[0].yaxis.set_major_locator(ticker.MultipleLocator(500))
        ax[0].yaxis.set_minor_locator(ticker.MultipleLocator(100))
        ax[0].set_ylim(0, 3000)

        ax[1].yaxis.set_major_locator(ticker.MultipleLocator(20))
        ax[1].yaxis.set_minor_locator(ticker.MultipleLocator(5))
        ax[1].set_ylim(0, 120)

        ax[2].yaxis.set_major_locator(ticker.MultipleLocator(20))
        ax[2].yaxis.set_minor_locator(ticker.MultipleLocator(5))
        ax[2].set_ylim(0, 80)

    else:
        ax[0].yaxis.set_major_locator(ticker.MultipleLocator(1000))
        ax[0].yaxis.set_minor_locator(ticker.MultipleLocator(250))
        ax[0].set_ylim(0, 9000)

        ax[1].yaxis.set_major_locator(ticker.MultipleLocator(20))
        ax[1].yaxis.set_minor_locator(ticker.MultipleLocator(5))
        ax[1].set_ylim(0, 120)

        ax[2].yaxis.set_major_locator(ticker.MultipleLocator(50))
        ax[2].yaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax[2].set_ylim(0, 300)

    return fig, ax


def _plot_fundamental_diagram(
    tms: fintraffic.TrafficMeasurementStation,
    x: str = "density",
    y: str = "flow",
    data_type: str = "agg",
) -> (plt.Figure, plt.Axes):
    assert x in [
        "density",
        "speed",
        "flow",
    ], "[LOG] AssertionError: x must be either density, speed or flow."  # noqa E501
    assert y in [
        "density",
        "speed",
        "flow",
    ], "[LOG] AssertionError: y must be either density, speed or flow."  # noqa E501
    assert data_type in [
        "agg",
        "bag",
        "bag_sized",
    ], "[LOG] AssertionError: data_type must be either agg, bag or bag_sized."  # noqa E501

    if x == "speed":
        x = "period_speed"
    if y == "speed":
        y = "period_speed"

    data = pd.DataFrame()
    marker_size = 1

    if data_type == "agg":
        data = tms.agg.data
    elif data_type == "bag":
        data = tms.bag.data
    elif data_type == "bag_sized":
        data = tms.bag.data
        marker_size = tms.bag.data["weight"] * 1000

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    fig.suptitle(
        f"TMS {tms.tms_id}, {tms.agg.aggregation_time_period} {tms.agg.aggregation_time_period_unit} intervals"
    )  # noqa E501

    sns.scatterplot(
        data=data,
        x=x,
        y=y,
        hue="lane" if tms.agg.aggregation_by_lane and data_type == "agg" else None,
        ax=ax,
        palette="Set2" if tms.agg.aggregation_by_lane and data_type == "agg" else None,
        size=marker_size,
    )

    return fig, ax
