import typing

from numpy.typing import ArrayLike
import pandas as pd

from ..utils import models


class BaggedData:
    """A class to represent bagged data of a traffic measurement station."""

    def __init__(self):
        self.data: typing.Optional[pd.DataFrame] = None
        self._flow: typing.Optional[ArrayLike] = None
        self._density: typing.Optional[ArrayLike] = None
        self._weight: typing.Optional[ArrayLike] = None
        self.bag_size_flow: typing.Optional[int] = None
        self.bag_size_density: typing.Optional[int] = None

        self.models: models.ModelResults = models.ModelResults()
        self.quantiles: list[float] = []
        pass

    def estimate_model(
        self,
        model_type: str,
        quantiles: typing.Optional[list[float]] = None,
        penalty: typing.Optional[str] = None,
        eta: typing.Optional[float] = None,
        email: str = None,
    ) -> None:
        """ Estimates a convex nonparametric least squares (CNLS) or convex quantile regression (CQR) model for
            bagged data.

        Parameters
        ----------
        model_type : str
            Type of the model to be estimated. Takes value `'quantile'` for the convex quantile regression (wCQR)
            model or `'mean'` for the convex nonparametric least squares (wCNLS) model
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
        ], "[LOG] AssertionError: Model type must be 'quantile' or 'mean'."
        assert self.data is not None, "[LOG] AssertionError: No data is available"
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
                    model = models._pwcqr(
                        x=self._density,
                        y=self._flow,
                        weight=self._weight,
                        quantile=q,
                        penalty=penalty,
                        eta=eta,
                        email=email,
                    )
                else:
                    model = models._wcqr(
                        x=self._density, y=self._flow, weight=self._weight, quantile=q, email=email
                    )
                self.models._add_model(model, q, penalty, eta)

        elif model_type == "mean":
            if penalty is not None:
                model = models._pwcnls(
                    x=self._density,
                    y=self._flow,
                    weight=self._weight,
                    penalty=penalty,
                    eta=eta,
                    email=email,
                )
            else:
                model = models._wcnls(x=self._density, y=self._flow, weight=self._weight, email=email)
            self.models._add_model(model, "mean", penalty, eta)
        pass
