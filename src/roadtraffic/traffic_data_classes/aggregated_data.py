import typing

import pandas as pd
from numpy.typing import ArrayLike

from ..utils import models, constants


# from ..utils import plot


class AggregatedData:
    """A class to represent aggregated data of a traffic measurement station.

    Attributes:
    -----------
    data : typing.Optional[pd.DataFrame]
        Aggregated data of the traffic measurement station.
    aggregation_time_period : int
        Aggregation time period value, by default DEF_AGG_TIME_PER
    aggregation_time_period_unit : str
        Aggregation time period unit, either "min" or "sec", by default "min"
    models : models.ModelResults
        Estimated models for the aggregated data.
    quantiles : list[float]
        List of quantiles for which the models were estimated.

    Methods:
    --------
    estimate_model(model_type: str, quantiles: list = None, penalty: str = None, eta: float = None, email: str = None) -> None
        Estimates a convex nonparametric least squares (CNLS) or convex quantile regression (CQR) model for the\\
        aggregated data.
    plot(quantiles=None, figure_name=None) -> None
        Plot estimated quantiles of the fundamental diagram.
    """  # noqa E501

    def __init__(self):
        self.data: typing.Optional[pd.DataFrame] = None
        self._flow: typing.Optional[ArrayLike] = None
        self._speed: typing.Optional[ArrayLike] = None
        self._density: typing.Optional[ArrayLike] = None
        self.aggregation_time_period: int = constants.DEF_AGG_TIME_PER
        self.aggregation_time_period_unit: str = "min"
        self.aggregation_by_lane: bool = False
        self.models: models.ModelResults = models.ModelResults()
        self.quantiles: list[float] = []
        self.context: typing.Optional[str] = None
        pass

    # def load_csv(
    #    self,
    #    path: str,
    #    separator: str = ",",
    #    column_names: list[str] = None,
    #    aggregation_time: int = 5,
    # ) -> None:
    #    """Load aggregated data from a csv file.

    #    Parameters
    #    ----------
    #    path : str
    #        Path to the file to be loaded.
    #    separator : str, optional
    #        Separator used in the file, by default ","
    #    column_names : list[str], optional
    #        Names of columns in the file. Make sure to include "density" and "flow" columns,
    #        by default ["density", "flow"]
    #    aggregation_time : int, optional
    #        Aggregation time period used in the file, by default 5

    #    Raises
    #    ------
    #    FileNotFoundError
    #        File was not found on the given `path`.
    #    """
    #    if column_names is None:
    #        column_names = ["density", "flow"]

    #    path = pathlib.Path(path)

    #    if not path.exists():
    #        raise FileNotFoundError(f"[LOG] File {path} does not exist.")
    #    else:
    #        assert "density" in column_names, "Column names must contain 'density'."
    #        assert "flow" in column_names, "Column names must contain 'flow'."

    #        self.data = pd.read_csv(path, header=0, sep=separator, names=column_names)
    #        self._flow = self.data["flow"].to_numpy()
    #        self._density = self.data["density"].to_numpy()
    #        self.aggregation_time = aggregation_time
    #    pass

    def estimate_model(
        self,
        model_type: str,
        quantiles: typing.Optional[list[float]] = None,
        penalty: typing.Optional[str] = None,
        eta: typing.Optional[float] = None,
        context: typing.Optional[str] = None,
        email: str = None,
    ) -> None:
        """ Estimates a convex nonparametric least squares (CNLS) or convex quantile regression (CQR) model for the\\
            aggregated data.

        Parameters
        ----------
        model_type : str
            Type of the model to be estimated. Takes value `'quantile'` for the convex quantile regression (CQR)
            model or `'mean'` for the convex nonparametric least squares (CNLS) model
        quantiles : list[float]
            Quantiles to be estimated for the `model_type=quantile`
        penalty : str, optional
            Type of penalty to be used in the model. Takes values `penalty=None` (no penalty), `penalty='l1'` (L1 norm),
            `penalty='l2'` (L2 norm), or `penalty='l3'` (Lipschitz norm), by default None
        eta : float, optional
            Value of the tuning parameter if `penalty` is in `['l1', 'l2', 'l3']`, by default None
        context : str, optional
            Contextual variable, by default None
        email : str, optional
            For external optimization on the NEOS server, by default None

        Raises
        ------
        AssertionError
            Model type must be "quantile" or "mean".
            Quantiles must be a non-empty list.
            Quantiles must be between 0 and 1.
            Data must be loaded first.
            Data contains more than 3000 observations. Apply bagging first.
        """
        # if quantiles is None:
        #    quantiles = [0.5]

        assert model_type in [
            "quantile",
            "mean",
        ], "[LOG] AssertionError:Model type must be 'quantile' or 'mean'."
        assert self.data is not None, "[LOG] AssertionError: No data is available"
        assert (
            len(self._flow) <= 3000
        ), "[LOG] AssertionError:Data contains more than 3000 observations. Apply bagging first."
        if penalty is not None:
            assert penalty in [
                "l1",
                "l2",
                "l3",
            ], "[LOG] AssertionError:Penalty must be None, 'l1', 'l2' or 'l3'."
            assert (
                eta is not None
            ), "[LOG] AssertionError: eta must be specified if penalty is selected."

        if context is not None:
            z = self.data[context]
            assert (
                context in self.data.columns
            ), "[LOG] AssertionError: Context must be a column in the data."
        else:
            z = None

        if model_type == "quantile":
            assert (
                len(quantiles) > 0
            ), "[LOG] AssertionError: Quantiles must be a non-empty list."
            assert all(
                [0 < q < 1 for q in quantiles]
            ), "[LOG] AssertionError: Quantiles must be between 0 and 1."

            [self.quantiles.append(x) for x in quantiles if x not in self.quantiles]
            self.quantiles.sort()

            for q in quantiles:
                if penalty is not None:
                    model = models._pcqr(
                        x=self._density,
                        y=self._flow,
                        z=z,
                        quantile=q,
                        penalty=penalty,
                        eta=eta,
                        email=email,
                    )
                else:
                    model = models._cqr(
                        x=self._density, y=self._flow, z=z, quantile=q, email=email
                    )
                self.models._add_model(model, q, penalty, eta, context)

        elif model_type == "mean":
            if penalty is not None:
                model = models._pcnls(
                    x=self._density,
                    y=self._flow,
                    z=z,
                    penalty=penalty,
                    eta=eta,
                    email=email,
                )
            else:
                model = models._cnls(x=self._density, y=self._flow, z=z, email=email)
            self.models._add_model(model, "mean", penalty, eta, context)
        pass

    def create_contextual_variable(
        self,
        speed_limit: typing.Optional[float] = None,
        density_limit: typing.Optional[float] = None,
    ) -> None:
        """Create a contextual variable for the aggregated data.
        If `speed_limit` is provided, the contextual variable will be `contextual_speed` and will be equal to 1 if
        `speed` is below the `speed_limit` and 0 otherwise.
        If `density_limit` is provided, the contextual variable
        will be `contextual_density` and will be equal to 1 if `density` is above the `density_limit` and 0 otherwise.
        Only one contextual variable can be created at a time.

        Parameters
        ----------
        speed_limit : float, optional
            Speed limit value, by default None
        density_limit : float, optional
            Density limit value, by default None

        Raises
        ------
        AssertionError
            Speed limit and density limit cannot be provided at the same time.
        """
        if speed_limit is not None and density_limit is not None:
            raise AssertionError(
                "[LOG] AssertionError: Speed limit and density limit cannot be provided at the same time."
            )

        assert self.data is not None, "[LOG] AssertionError: No data is available"

        if speed_limit is not None:
            self.data["contextual_speed"] = (self.data["speed"] <= speed_limit).astype(
                int
            )
            self.context = "contextual_speed"
        elif density_limit is not None:
            self.data["contextual_density"] = (
                self.data["density"] >= density_limit
            ).astype(int)
            self.context = "contextual_density"
        return None


#    def plot(self, quantiles=None, figure_name=None) -> None:
#        """
#        Plot estimated quantiles of the fundamental diagram.
#        Parameters
#        ----------
#        quantiles : list[float] or None, optional
#            List of quantiles to be plotted. If `None`, all estimated quantiles will be plotted, by default None
#        figure_name : str or None, optional
#            Name of the figure is specified when the figure is intended to be saved, by default None
#        """
#        plot.plot(
#            self, representation="agg", quantiles=quantiles, figure_name=figure_name
#        )
#        pass
