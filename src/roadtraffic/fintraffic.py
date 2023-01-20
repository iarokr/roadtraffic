# Import dependencies
from pystoned import wCQER
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import enum
import numpy as np
from sklearn.linear_model import LinearRegression
import math

from roadtraffic.utils import load, process, constant

DEFAULT_TAU_LIST = [0.5]


class Representations(enum.Enum):
    agg = 1
    bag = 2
    bag_w = 3


class FintrafficTMS:
    """
    This is a class to represent a Traffic Measurement Station (TMS) in Finland. \
    The data is loaded using Digitraffic service. \
    The class uses the raw data available from Digitraffic. \
    The authors of the package cannot influence the availability of data.\
    Fintraffic / digitraffic.fi is licensed under CC 4.0 BY license.

    Parameters
    ----------
    tms_id : int
        The identity number of a traffic measurement station (TMS). \
        Meta-data about TMS is available `here <https://www.digitraffic.fi/en/road-traffic/#current-data-from-tms-stations>`_.
    days_list : list
        A list of days in the format `[[year1, day1], [year2, day2],...]`
    direction : int
        low direction of interest. Marked as 1 or 2. Check the TMS meta-data to get the necessary direction.
    hour_from : int, optional
        Hour from which the data is loaded, by default 6
    hour_to : int, optional
        Hour until which the data is loaded (this our is not inclued), by default 20
    delete_if_faulty : bool, optional
        If `True`, observations with the `1` value for the column `if_faulty` will be deleted, by default True
    path_name : str, optional
        If specified, reads data from the `path_name` folder from a locally saved bz2-compressed .pkl file. \
        Both processed "lamraw_TMS_YY_DD_bz2.pkl" and unprocessed "lamraw_TMS_YY_DD_bz2_u.pkl" files can be read, by default None
    """  # noqa E501

    def __init__(
        self,
        tms_id: int,
        days_list: list,
        direction: int,
        tau_list: list = DEFAULT_TAU_LIST,
        hour_from: int = 6,
        hour_to: int = 20,
        path_name: str = None,
    ):
        self.tms_id = tms_id
        self.path_name = path_name

        # Date and time information
        self.days_list = days_list
        self.hour_from = hour_from
        self.hour_to = hour_to

        # Vehicle positioning
        self.direction = direction

        # Quantiles to model
        self.tau_list = tau_list

    def load_raw_data(self):
        self.raw_data = load.read_several_reports(
            tms_id=self.tms_id,
            year_day_list=self.days_list,
            direction=self.direction,
            path_name=self.path_name,
        )

    def aggregate_road(self, aggregation_time_period: int = constant.DEF_AGG_TIME_PER):
        self.agg_data = process.aggregate_road(
            data=self.raw_data,
            direction=self.direction,
            aggregation_time_period=aggregation_time_period,
        )
        self.agg_time_period = aggregation_time_period
        self.agg_flow = self.agg_data["flow"]
        self.agg_density = self.agg_data["density"]

    def aggregate_lane(self, aggregation_time_period: int = constant.DEF_AGG_TIME_PER):
        self.agg_data = process.aggregate_lane(
            data=self.raw_data,
            direction=self.direction,
            aggregation_time_period=aggregation_time_period,
        )
        self.agg_time_period = aggregation_time_period
        self.agg_flow = self.agg_data["flow"]
        self.agg_density = self.agg_data["density"]

    def bagging(self, gridsize_x: int = 70, gridsize_y: int = 400):
        self.bag_data = process.bagging(self.agg_data, gridsize_x, gridsize_y)
        self.gridsize_x = gridsize_x
        self.gridsize_y = gridsize_y
        self.bag_density = self.bag_data["centroid_density"]
        self.bag_flow = self.bag_data["centroid_flow"]
        self.weight = self.bag_data["weight"]

    def weighted_model(self, tau_list: list = None, email: str = None):
        self.bagged_model = {}
        self.time_weighted = {}
        if tau_list is None:
            tau_list = self.tau_list
        for tau in tau_list:
            start_time = time.perf_counter()
            model = wCQER.wCQR(
                y=self.bag_data.centroid_flow,
                x=self.bag_data.centroid_density,
                w=self.weight,
                tau=tau,
            )
            model.__model__.beta.setlb(None)
            if email is not None:
                model.optimize(email)
            else:
                model.optimize()
            self.bagged_model[tau] = model
            end_time = time.perf_counter()
            self.time_weighted[tau] = end_time - start_time

    def get_params_weighted_model(self, tau):
        self.weighted_model_params = []

    def plot_data(self, representation: Representations):
        if isinstance(representation, Representations):
            plt.clf()
            figure(figsize=(7, 7), dpi=300)

            if representation == Representations.agg:
                plt.scatter(
                    self.agg_density,
                    self.agg_flow,
                    marker="x",
                    c="black",
                    label="Aggregated data",
                )
            elif representation == Representations.bag:
                plt.scatter(
                    self.bag_density,
                    self.bag_flow,
                    marker="x",
                    c="black",
                    label="Bagged data",
                )
            elif representation == Representations.bag_w:
                plt.scatter(
                    self.bag_density,
                    self.bag_flow,
                    marker="o",
                    c="black",
                    s=self.weight * 10000,
                    label="Bagged data with weighted representation",
                )

            plt.xlabel("Density [veh/km]")
            plt.ylabel("Flow [veh/h]")
            plt.legend()
        else:
            raise Exception(f"Representation {representation} does not exist")

    def plot_model(self, data_representation: Representations):
        if isinstance(data_representation, Representations):
            plt.clf()
            figure(figsize=(7, 7), dpi=300)

            if data_representation == Representations.agg:
                plt.scatter(
                    self.agg_density,
                    self.agg_flow,
                    marker="x",
                    c="black",
                    label="Aggregated data",
                )
            elif data_representation == Representations.bag:
                plt.scatter(
                    self.bag_density,
                    self.bag_flow,
                    marker="x",
                    c="black",
                    label="Bagged data",
                )
            elif data_representation == Representations.bag_w:
                plt.scatter(
                    self.bag_density,
                    self.bag_flow,
                    marker="o",
                    c="black",
                    s=self.weight * 10000,
                    label="Bagged data with weighted representation",
                )

            cmap = plt.get_cmap("plasma")
            slicedCM = cmap(np.linspace(0, 1, len(self.bagged_model)))
            color_index = 0
            for tau in self.tau_list:
                model = self.bagged_model[tau]
                x = np.array(model.x).flatten()
                y = np.array(model.y).T
                yhat = np.array(model.get_frontier()).T

                data = (np.stack([x, y, yhat])).T

                # sort
                data = data[np.argsort(data[:, 0])].T
                x, y, f = data[0], data[1], data[2]
                plt.plot(
                    x,
                    f,
                    c=slicedCM[color_index],
                    label="tau=" + str(tau),
                )
                color_index += 1

            plt.xlabel("Density [veh/km]")
            plt.ylabel("Flow [veh/h]")
            plt.legend()
        else:
            raise Exception(f"Representation {data_representation} does not exist")

    def make_model(
        self,
        aggregation_time_period: int = constant.DEF_AGG_TIME_PER,
        gridsize_x: int = 70,
        gridsize_y: int = 400,
        tau_list: list = None,
        email: str = None,
    ):
        if tau_list is None:
            tau_list = self.tau_list
        self.load_raw_data()
        self.aggregate_road(aggregation_time_period=aggregation_time_period)
        self.bagging(gridsize_x=gridsize_x, gridsize_y=gridsize_y)
        self.weighted_model(tau_list=tau_list, email=email)

    def derv_model(
        self,
        free_flow_speed,
        graph: bool = False,
    ):
        data = self.agg_data[["density", "flow"]].to_numpy()
        data = np.append(data, [[1, 1]], axis=0)
        capacity = np.max(data[:, 1])
        y_ff = data[:, 0] * free_flow_speed
        critical_density = capacity / free_flow_speed
        y_cap = np.full_like(y_ff, capacity)
        iqr = np.subtract(*np.percentile(data[:, 1], [75, 25]))
        data_cong = data[data[:, 0] > critical_density]
        data_cong = np.sort(data_cong, axis=0)
        maxlen = round(len(data_cong[:, 0]), -1)
        last_dist = len(data_cong[:, 0]) - maxlen
        new = np.array([[critical_density, capacity]])
        for i in range(0, maxlen, 10):
            if i == maxlen:
                ddd = data_cong[i : i + last_dist, :]  # noqa: E203
            else:
                ddd = data_cong[i : i + 10, :]  # noqa: E203
            xxx = np.mean(ddd[:, 0])
            q75 = np.percentile(ddd[:, 1], 75)
            yy = ddd[:, 1] - q75 - 1.5 * iqr
            yy = yy[yy <= 0]
            yyy = ddd[np.argmax(yy), 1]
            new = np.append(new, [[xxx, yyy]], axis=0)

        lm = LinearRegression(fit_intercept=False)

        # center data on x_0, y_0
        y2 = new[:, 1] - capacity
        x2 = new[:, 0] - critical_density

        # fit model
        lm.fit(x2.reshape(-1, 1), y2)

        # predict line
        preds = lm.predict(x2.reshape(-1, 1))
        pred_act = preds + capacity
        jam_density = capacity / abs(lm.coef_[0]) + critical_density
        new = np.append(new, [[jam_density, 0.0]], axis=0)
        pred_act = np.append(pred_act, [0.0], axis=0)

        if graph is True:
            plt.clf()
            plt.figure(figsize=(5, 5), dpi=300)
            plt.scatter(data[:, 0], data[:, 1], color="black", marker="x")
            plt.plot(data[:, 0], y_ff, color="r")
            plt.plot(data[:, 0], y_cap, color="r")
            plt.plot(new[:, 0], pred_act, color="r")
            plt.ylim([0, 5000])
            plt.show()
        x_uncon = data[data[:, 0] <= critical_density][:, 0]
        x_uncon = x_uncon[:-1]
        y_pred_uncon = x_uncon * free_flow_speed
        y_uncon = data[data[:, 0] <= critical_density][:, 1]
        y_uncon = y_uncon[:-1]
        se_uncon = np.sum(np.power((y_pred_uncon - y_uncon), 2))
        x_con = data[data[:, 0] > critical_density][:, 0]
        y_con = data[data[:, 0] > critical_density][:, 1]
        y_pred_con = lm.coef_[0] * (x_con - critical_density) + capacity
        se_con = np.sum(np.power((y_pred_con - y_con), 2))
        rmse = math.sqrt((se_con + se_uncon) / (len(y_con) + len(y_uncon)))
        ae_con = np.sum(np.abs(y_pred_con - y_con))
        mae = ae_con / (len(y_con) + len(y_uncon))

        self.derv_params = [
            free_flow_speed,
            critical_density,
            capacity,
            abs(lm.coef_[0]),
            jam_density,
            rmse,
            mae,
        ]

    def do_research(
        self, free_flow_speed, days_list_ny, agg=0
    ):  # agg = 0 - road, agg = 1 - lane
        self.load_raw_data()
        if agg == 0:
            self.aggregate_road(5)
        elif agg == 1:
            self.aggregate_lane(5)
        self.bagging()
        self.derv_model(free_flow_speed)
        self.weighted_model()

        tmsy = FintrafficTMS(
            tms_id=self.tms_id,
            days_list=days_list_ny,
            direction=self.direction,
            tau_list=self.tau_list,
            path_name=self.path_name,
        )
        tmsy.load_raw_data()
        if agg == 0:
            tmsy.aggregate_road(self.agg_time_period)
        elif agg == 1:
            tmsy.aggregate_lane(self.agg_time_period)
        tmsy.bagging()

        agg_data_y = tmsy.agg_data[["density", "flow"]].to_numpy()
        agg_data_y_con = agg_data_y[agg_data_y[:, 0] > self.derv_params[1]]
        agg_data_y_uncon = agg_data_y[agg_data_y[:, 0] <= self.derv_params[1]]
        agg_data_y_uncon = np.c_[
            agg_data_y_uncon, np.array(self.derv_params[0] * agg_data_y_uncon[:, 0])
        ]
        agg_data_y_con = np.c_[
            agg_data_y_con,
            np.array(
                (-1)
                * self.derv_params[3]
                * (agg_data_y_con[:, 0] - self.derv_params[1])
                + self.derv_params[2]
            ),
        ]
        agg_data_y_merged = np.r_[agg_data_y_con, agg_data_y_uncon]
        agg_data_y_merged = np.r_[
            agg_data_y_merged,
            np.array([[self.derv_params[1], self.derv_params[2], self.derv_params[2]]]),
        ]
        agg_data_y_merged = agg_data_y_merged[np.argsort(agg_data_y_merged[:, 0])]
        rep_list = []
        for x in np.nditer(agg_data_y_merged[:, 0]):
            representor = process.representor(
                self.bagged_model[self.tau_list[0]].get_alpha().flatten(),
                self.bagged_model[self.tau_list[0]].get_beta().flatten(),
                x,
            )
            rep_list.append(representor)
        agg_data_y_merged = np.c_[agg_data_y_merged, np.array(rep_list)]

        rmse_derv_new = math.sqrt(
            np.sum(np.power(agg_data_y_merged[:, 2] - agg_data_y_merged[:, 1], 2))
            / len(agg_data_y_merged[:, 2])
        )
        rmse_weigh_new = math.sqrt(
            np.sum(np.power(agg_data_y_merged[:, 3] - agg_data_y_merged[:, 1], 2))
            / len(agg_data_y_merged[:, 3])
        )

        mae_derv_new = np.sum(
            np.abs(agg_data_y_merged[:, 2] - agg_data_y_merged[:, 1])
        ) / len(agg_data_y_merged[:, 2])

        mae_weigh_new = np.sum(
            np.abs(agg_data_y_merged[:, 3] - agg_data_y_merged[:, 1])
        ) / len(agg_data_y_merged[:, 3])

        # for old data
        agg_data_y_old = self.agg_data[["density", "flow"]].to_numpy()
        agg_data_y_con_old = agg_data_y_old[agg_data_y_old[:, 0] > self.derv_params[1]]
        agg_data_y_uncon_old = agg_data_y_old[
            agg_data_y_old[:, 0] <= self.derv_params[1]
        ]
        agg_data_y_uncon_old = np.c_[
            agg_data_y_uncon_old,
            np.array(self.derv_params[0] * agg_data_y_uncon_old[:, 0]),
        ]
        agg_data_y_con_old = np.c_[
            agg_data_y_con_old,
            np.array(
                (-1)
                * self.derv_params[3]
                * (agg_data_y_con_old[:, 0] - self.derv_params[1])
                + self.derv_params[2]
            ),
        ]
        agg_data_y_merged_old = np.r_[agg_data_y_con_old, agg_data_y_uncon_old]
        agg_data_y_merged_old = np.r_[
            agg_data_y_merged_old,
            np.array([[self.derv_params[1], self.derv_params[2], self.derv_params[2]]]),
        ]
        agg_data_y_merged_old = agg_data_y_merged_old[
            np.argsort(agg_data_y_merged_old[:, 0])
        ]
        rep_list_old = []
        for x in np.nditer(agg_data_y_merged_old[:, 0]):
            representor_old = process.representor(
                self.bagged_model[self.tau_list[0]].get_alpha().flatten(),
                self.bagged_model[self.tau_list[0]].get_beta().flatten(),
                x,
            )
            rep_list_old.append(representor_old)
        agg_data_y_merged_old = np.c_[agg_data_y_merged_old, np.array(rep_list_old)]

        rmse_derv_old = math.sqrt(
            np.sum(
                np.power(agg_data_y_merged_old[:, 2] - agg_data_y_merged_old[:, 1], 2)
            )
            / len(agg_data_y_merged_old[:, 2])
        )
        rmse_weigh_old = math.sqrt(
            np.sum(
                np.power(agg_data_y_merged_old[:, 3] - agg_data_y_merged_old[:, 1], 2)
            )
            / len(agg_data_y_merged_old[:, 3])
        )

        mae_derv_old = np.sum(
            np.abs(agg_data_y_merged_old[:, 2] - agg_data_y_merged_old[:, 1])
        ) / len(agg_data_y_merged_old[:, 2])

        mae_weigh_old = np.sum(
            np.abs(agg_data_y_merged_old[:, 3] - agg_data_y_merged_old[:, 1])
        ) / len(agg_data_y_merged_old[:, 3])

        err_list = [
            rmse_derv_old,
            rmse_weigh_old,
            mae_derv_old,
            mae_weigh_old,
            rmse_derv_new,
            rmse_weigh_new,
            mae_derv_new,
            mae_weigh_new,
        ]
        return agg_data_y_merged_old, agg_data_y_merged, err_list
