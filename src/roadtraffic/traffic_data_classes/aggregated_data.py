import typing

from numpy.typing import ArrayLike
import pandas as pd

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
        self.aggregation_time_period: str = "min"
        self.models: models.ModelResults = models.ModelResults()
        self.quantiles: list[float] = []
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
                        quantile=q,
                        penalty=penalty,
                        eta=eta,
                        email=email,
                    )
                else:
                    model = models._cqr(
                        x=self._density, y=self._flow, quantile=q, email=email
                    )
                self.models._add_model(model, q, penalty, eta)

        elif model_type == "mean":
            if penalty is not None:
                model = models._pcnls(
                    x=self._density,
                    y=self._flow,
                    penalty=penalty,
                    eta=eta,
                    email=email,
                )
            else:
                model = models._cnls(x=self._density, y=self._flow, email=email)
            self.models._add_model(model, "mean", penalty, eta)
        pass


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
