# import dependencies
import typing
import time
from dataclasses import dataclass

import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
from pystoned import CNLS, pCNLS, wCNLS, pwCNLS, CQER, pCQER, wCQER, pwCQER
from pystoned.constant import RTS_VRS, FUN_PROD, CET_ADDI


@dataclass
class ModelResults:
    """A class to represent estimated for the aggregated data.

    Methods:
    --------
    get_models() -> dict
        Get the dictionary where all the models are stored. The model object is a pystoned model object. Not recommended
        to use this to extract the estimated model parameters. Use the other methods instead.
    get_frontier(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> ArrayLike
        Get the array with the estimated values of the piecewise-linear function.
    get_coefficients(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> ArrayLike
        Get the array with the estimated coefficients of the piecewise-linear function.
    get_number_of_segments(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> int
        Get the number of segments in the estimated piecewise-linear function.
    get_estimate(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> pd.DataFrame
        Get all the data for estimated fundamental diagram. Original density, flow and speed values, estimated flow
        and speed values.
    get_problem_status(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> int
        Get the status of the optimization problem.
    """  # noqa E501

    def __init__(self):
        self._models = dict()
        pass

    def _add_model(
        self,
        model: typing.Union[
            CNLS.CNLS,
            pCNLS.pCNLS,
            wCNLS.wCNLS,
            pwCNLS.pwCNLS,
            CQER.CQR,
            pCQER.pCQR,
            wCQER.wCQR,
            pwCQER.pwCQR,
        ],
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str],
        eta: typing.Union[None, float],
    ):
        self._models[quantile, penalty, eta] = model
        pass

    def __getitem__(self, item):
        if (item == "mean") or (0 < item < 1):
            try:
                return self._models[item, None, None]
            except KeyError:
                raise KeyError("Model with the specified parameters was not estimated.")
        elif (type(item) is tuple) and (len(item) == 3):
            try:
                return self._models[item]
            except KeyError:
                raise KeyError("Model with the specified parameters was not estimated.")
        else:
            raise KeyError("Model with the specified parameters was not estimated.")
        pass

    def get_models(self):
        """
        Get the dictionary where all the models are stored. The model object is a pystoned model object. Not recommended
        to use this to extract the estimated model parameters. Use the other methods instead.
        """
        return self._models

    def get_frontier(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
    ) -> ArrayLike:
        """
        Get the array with the estimated values of the piecewise-linear function.
        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
            Value of the penalty parameter, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        ArrayLike
            Array with the estimated function values.
        """
        assert (
            quantile,
            penalty,
            eta,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return self._models[quantile, penalty, eta].get_frontier()

    def get_coefficients(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
    ) -> ArrayLike:
        """
        Get the array with the estimated coefficients of the piecewise-linear function.

        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
            Value of the penalty parameter, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        ArrayLike
            Array with the estimated coefficients, alpha and beta.
        """
        assert (
            quantile,
            penalty,
            eta,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        alpha = self._models[quantile, penalty, eta].get_alpha()
        beta = self._models[quantile, penalty, eta].get_beta().flatten()
        # join alpha in beta into one array
        coefficients = (np.stack([alpha, beta], axis=0)).T
        return coefficients

    def get_number_of_segments(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
    ) -> int:
        """
        Get the number of segments in the estimated piecewise-linear function.
        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
            Value of the penalty parameter, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        int
            Number of segments in the estimated piecewise-linear function.
        """
        assert (
            quantile,
            penalty,
            eta,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return len(self._models[quantile, penalty, eta].get_alpha())

    def get_estimate(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
    ) -> pd.DataFrame:
        """Get all the data for estimated fundamental diagram. Original density, flow and speed values, estimated flow
        and speed values.
        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
            Value of the penalty parameter, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        estimate : pd.DataFrame
            Estimated fundamental diagram values.
        """
        assert (
            quantile,
            penalty,
            eta,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        x = np.array(self._models[quantile, penalty, eta].x).flatten().T
        y = np.array(self._models[quantile, penalty, eta].y).T
        y_hat = np.array(self._models[quantile, penalty, eta].get_frontier()).T
        data = (np.stack([x, y, y_hat], axis=0)).T
        data = data[np.argsort(data[:, 0])].T

        x, y, f = data[0], data[1], data[2]
        speed = y / x
        speed_hat = y_hat / x

        estimate = pd.DataFrame(
            {
                "density": x,
                "flow": y,
                "flow_estimate": f,
                "speed": speed,
                "speed_estimate": speed_hat,
            }
        )
        return estimate

    def get_problem_status(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
    ) -> int:
        """Get the status of the optimization problem.

        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
            Value of the penalty parameter, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        int
            Status of the optimization problem.

        """
        assert (
            quantile,
            penalty,
            eta,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return self._models[quantile, penalty, eta].get_status()


# Estimate CNLS model
def _cnls(x: ArrayLike, y: ArrayLike, email: str) -> CNLS.CNLS:
    start_time = time.perf_counter()
    print("[LOG] Estimating the CNLS model...")
    model = CNLS.CNLS(y=y, x=x, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS)
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] CNLS model was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate pCNLS model
def _pcnls(
    x: ArrayLike, y: ArrayLike, penalty: str, eta: float, email: str
) -> pCNLS.pCNLS:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the CNLS model with {penalty} penalty (eta={eta})...")
    model = pCNLS.pCNLS(
        y=y, x=x, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS, penalty=int(penalty[-1]), eta=eta
    )
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] CNLS model with {penalty} penalty (eta={eta}) was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate wCNLS model
def _wcnls(x: ArrayLike, y: ArrayLike, weight: ArrayLike, email: str) -> wCNLS.wCNLS:
    start_time = time.perf_counter()
    print("[LOG] Estimating the weighted CNLS model...")
    model = wCNLS.wCNLS(y=y, x=x, w=weight, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS)
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] weighted CNLS model was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate pwCNLS model
def _pwcnls(
    x: ArrayLike, y: ArrayLike, weight: ArrayLike, penalty: str, eta: float, email: str
) -> pwCNLS.pwCNLS:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the weighted CNLS model with {penalty} penalty and eta={eta}..."
    )
    model = pwCNLS.pwCNLS(
        y=y,
        x=x,
        w=weight,
        fun=FUN_PROD,
        cet=CET_ADDI,
        rts=RTS_VRS,
        penalty=int(penalty[-1]),
        eta=eta,
    )
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] weighted CNLS model with {penalty} penalty (eta={eta}) was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate CQR model
def _cqr(x: ArrayLike, y: ArrayLike, quantile: float, email: str) -> CQER.CQR:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the CQR model for quantile={quantile}...")
    model = CQER.CQR(y=y, x=x, tau=quantile, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS)
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] CQR model for quantile={quantile} was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate pCQR model
def _pcqr(
    x: ArrayLike, y: ArrayLike, quantile: float, penalty: str, eta: float, email: str
) -> pCQER.pCQR:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the CQR model for quantile={quantile} with {penalty} penalty (eta={eta})..."
    )
    model = pCQER.pCQR(
        y=y,
        x=x,
        tau=quantile,
        fun=FUN_PROD,
        cet=CET_ADDI,
        rts=RTS_VRS,
        penalty=int(penalty[-1]),
        eta=eta,
    )
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] CQR model for quantile={quantile} with {penalty} penalty (eta={eta}) was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate wCQR model
def _wcqr(
    x: ArrayLike, y: ArrayLike, weight: ArrayLike, quantile: float, email: str
) -> wCQER.wCQR:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the weighted CQR model for quantile={quantile}...")
    model = wCQER.wCQR(
        y=y, x=x, w=weight, tau=quantile, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS
    )
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] weighted CQR model for quantile={quantile} was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate pwCQR model
def _pwcqr(
    x: ArrayLike,
    y: ArrayLike,
    weight: ArrayLike,
    quantile: float,
    penalty: str,
    eta: float,
    email: str,
) -> pwCQER.pwCQR:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the weighted CQR model for quantile={quantile} with {penalty} penalty (eta={eta})..."
    )
    model = pwCQER.pwCQR(
        y=y,
        x=x,
        w=weight,
        tau=quantile,
        fun=FUN_PROD,
        cet=CET_ADDI,
        rts=RTS_VRS,
        penalty=int(penalty[-1]),
        eta=eta,
    )
    model.__model__.beta.setlb(None)
    if email is not None:
        model.optimize(email)
    else:
        model.optimize()
    end_time = time.perf_counter()
    print(
        f"[LOG] weighted CQR model for quantile={quantile} with {penalty} penalty (eta={eta}) was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model
