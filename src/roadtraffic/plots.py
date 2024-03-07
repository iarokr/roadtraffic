import matplotlib.pyplot as plt
import seaborn as sns

from .funcs import day_to_date
from ..fintraffic import TrafficMeasurementStation


class Plotter:
    """
    Plotting class.
    """

    @staticmethod
    def plot_timeline_agg(
        tms: TrafficMeasurementStation,
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


def _plot_against_time(
    tms: TrafficMeasurementStation,
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
    fig, ax = plt.subplots(1, 3, sharex="col", figsize=(15, 8), constrained_layout=True)

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
            sns.scatterplot(data=tms.agg.data, x="time", y="flow", hue="lane", ax=ax[0])
            sns.scatterplot(
                data=tms.agg.data, x="time", y="speed", hue="lane", ax=ax[1]
            )
            sns.scatterplot(
                data=tms.agg.data, x="time", y="density", hue="lane", ax=ax[2]
            )
        else:
            sns.scatterplot(data=tms.agg.data, x="time", y="flow", ax=ax[0])
            sns.scatterplot(data=tms.agg.data, x="time", y="speed", ax=ax[1])
            sns.scatterplot(data=tms.agg.data, x="time", y="density", ax=ax[2])
    elif plot_type == "line":
        if tms.agg.aggregation_by_lane:
            sns.lineplot(data=tms.agg.data, x="time", y="flow", hue="lane", ax=ax[0])
            sns.lineplot(data=tms.agg.data, x="time", y="speed", hue="lane", ax=ax[1])
            sns.lineplot(data=tms.agg.data, x="time", y="density", hue="lane", ax=ax[2])
        else:
            sns.lineplot(data=tms.agg.data, x="time", y="flow", ax=ax[0])
            sns.lineplot(data=tms.agg.data, x="time", y="speed", ax=ax[1])
            sns.lineplot(data=tms.agg.data, x="time", y="density", ax=ax[2])
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

    # Setting titles
    ax[0].set_title(f"Flow [veh/h+{lane_append}]")
    ax[1].set_title("Speed [km/h]")
    ax[2].set_title(f"Density [veh/km+{lane_append}]")

    # formatting time axis
    plt.gca().xaxis.set_major_locator(
        plt.MaxNLocator(
            nbins=tms.raw.cleaning_params["hour_to"]
            + 1
            - tms.raw.cleaning_params["hour_from"]
        )
    )
    plt.gcf().autofmt_xdate()

    return fig, ax
