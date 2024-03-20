# import dependencies
import time
import typing
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from pystoned import CNLS, pCNLS, wCNLS, pwCNLS, CQER, pCQER, wCQER, pwCQER
from pystoned.constant import RTS_VRS, FUN_PROD, CET_ADDI
from scipy.stats import t


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
    get_context_estimate(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None) -> float
        Get the estimated coefficient for the context variable.
    ttest_context(quantile: typing.Union[str, float], penalty: typing.Union[None, str] = None, eta: typing.Union[None, float] = None, alpha: float = 0.05) -> (float, float)
        Perform the t-test on the contextual variable of the estimated model.
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
        context: typing.Union[None, str],
    ):
        self._models[quantile, penalty, eta, context] = model
        pass

    def __getitem__(self, item):
        if (len(item) == 1) and ((item == "mean") or (0 < item < 1)):
            try:
                return self._models[item, None, None, None]
            except KeyError:
                raise KeyError(f"Model with the parameters {item} was not estimated.")
        elif (type(item) is tuple) and (len(item) == 3):
            try:
                return self._models[item + None]
            except KeyError:
                raise KeyError(f"Model with the parameters {item} was not estimated.")
        elif (type(item) is tuple) and (len(item) == 4):
            try:
                return self._models[item]
            except KeyError:
                raise KeyError(f"Model with the parameters {item} was not estimated.")
        else:
            raise KeyError(f"Model with the parameters {item} was not estimated.")
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
        context: typing.Union[None, str] = None,
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
        context : str or None, optional
            Contextual variable, by default None

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
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return self._models[quantile, penalty, eta, context].get_frontier()

    def get_coefficients(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
        context: typing.Union[None, str] = None,
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
        context : str or None, optional
            Contextual variable, by default None

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
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        alpha = self._models[quantile, penalty, eta, context].get_alpha()
        beta = self._models[quantile, penalty, eta, context].get_beta().flatten()
        # join alpha in beta into one array
        coefficients = (np.stack([alpha, beta], axis=0)).T
        return coefficients

    def get_number_of_segments(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
        context: typing.Union[None, str] = None,
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
        context : str or None, optional
            Contextual variable, by default None

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
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return len(self._models[quantile, penalty, eta, context].get_alpha())

    def get_estimate(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
        context: typing.Union[None, str] = None,
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
        context : str or None, optional
            Contextual variable, by default None

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
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        x = np.array(self._models[quantile, penalty, eta, context].x).flatten().T
        y = np.array(self._models[quantile, penalty, eta, context].y).T
        y_hat = np.array(self._models[quantile, penalty, eta, context].get_frontier()).T
        z = None
        z_coef = None
        if context is not None:
            z = np.array(self._models[quantile, penalty, eta, context].z).flatten()
            z_coef = np.full_like(
                x, self._models[quantile, penalty, eta, context].get_lamda()[0]
            )
            data = (np.stack([x, y, z, y_hat, z_coef], axis=0)).T
            data = data[np.argsort(data[:, 0])].T
            x, y, z, f, z_coef = data[0], data[1], data[2], data[3], data[4]
        else:
            data = (np.stack([x, y, y_hat], axis=0)).T
            data = data[np.argsort(data[:, 0])].T
            x, y, f = data[0], data[1], data[2]
        speed = y / x
        speed_hat = y_hat / x

        if context is not None:
            estimate = pd.DataFrame(
                {
                    "density": x,
                    "flow": y,
                    "context": z,
                    "context_estimate": z_coef,
                    "flow_estimate": f,
                    "speed": speed,
                    "speed_estimate": speed_hat,
                }
            )
        else:
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
        context: typing.Union[None, str] = None,
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
        context : str or None, optional
            Contextual variable, by default None

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
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return self._models[quantile, penalty, eta, context].get_status()

    def get_context_estimate(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
        context: typing.Union[None, str] = None,
    ) -> float:
        """Get the estimated coefficient for the context variable.

        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
           Value of the penalty parameter, by default None
        context : str or None, optional
            Contextual variable, by default None

        Raises
        ------
        AssertionError
            Model with the specified parameters is not estimated.

        Returns
        -------
        (float, float)
            t-statistic and p-value for the t-test.
        """
        assert (
            quantile,
            penalty,
            eta,
            context,
        ) in self._models.keys(), (
            "Model with the specified parameters is not estimated."
        )
        return self._models[quantile, penalty, eta, context].get_lamda()[0]

    def ttest_context(
        self,
        quantile: typing.Union[str, float],
        penalty: typing.Union[None, str] = None,
        eta: typing.Union[None, float] = None,
        context: typing.Union[None, str] = None,
        alpha: float = 0.05,
    ) -> (float, float):
        """Perform the t-test on the contextual variable of the estimated model.

        Parameters
        ----------
        Parameters
        ----------
        quantile : str or float
            Quantile of the estimated model.
        penalty : str or None, optional
            Penalty type of the estimated model, by default None
        eta : float or None, optional
           Value of the penalty parameter, by default None
        context : str or None, optional
            Contextual variable, by default None
        alpha : float, optional
            Significance level, by default 0.05

        Returns
        -------
        (float, float)
            t-statistic and p-value for the t-test.
        """
        return _ttest(self._models[quantile, penalty, eta, context], alpha)


# Estimate CNLS model
def _cnls(
    x: ArrayLike,
    y: ArrayLike,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> CNLS.CNLS:
    start_time = time.perf_counter()
    print("[LOG] Estimating the CNLS model...")
    model = CNLS.CNLS(y=y, x=x, z=z, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS)
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
    x: ArrayLike,
    y: ArrayLike,
    penalty: str,
    eta: float,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> pCNLS.pCNLS:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the CNLS model with {penalty} penalty (eta={eta})...")
    model = pCNLS.pCNLS(
        y=y,
        x=x,
        z=z,
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
        f"[LOG] CNLS model with {penalty} penalty (eta={eta}) was estimated in {end_time - start_time:.4f} seconds."  # noqa E501
    )
    return model


# Estimate wCNLS model
def _wcnls(
    x: ArrayLike,
    y: ArrayLike,
    weight: ArrayLike,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> wCNLS.wCNLS:
    start_time = time.perf_counter()
    print("[LOG] Estimating the weighted CNLS model...")
    model = wCNLS.wCNLS(
        y=y, x=x, w=weight, z=z, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS
    )
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
    x: ArrayLike,
    y: ArrayLike,
    weight: ArrayLike,
    penalty: str,
    eta: float,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> pwCNLS.pwCNLS:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the weighted CNLS model with {penalty} penalty and eta={eta}..."
    )
    model = pwCNLS.pwCNLS(
        y=y,
        x=x,
        w=weight,
        z=z,
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
def _cqr(
    x: ArrayLike,
    y: ArrayLike,
    quantile: float,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> CQER.CQR:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the CQR model for quantile={quantile}...")
    model = CQER.CQR(
        y=y, x=x, z=z, tau=quantile, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS
    )
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
    x: ArrayLike,
    y: ArrayLike,
    quantile: float,
    penalty: str,
    eta: float,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> pCQER.pCQR:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the CQR model for quantile={quantile} with {penalty} penalty (eta={eta})..."
    )
    model = pCQER.pCQR(
        y=y,
        x=x,
        z=z,
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
    x: ArrayLike,
    y: ArrayLike,
    weight: ArrayLike,
    quantile: float,
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> wCQER.wCQR:
    start_time = time.perf_counter()
    print(f"[LOG] Estimating the weighted CQR model for quantile={quantile}...")
    model = wCQER.wCQR(
        y=y, x=x, w=weight, z=z, tau=quantile, fun=FUN_PROD, cet=CET_ADDI, rts=RTS_VRS
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
    z: typing.Optional[ArrayLike] = None,
    email: typing.Optional[str] = None,
) -> pwCQER.pwCQR:
    start_time = time.perf_counter()
    print(
        f"[LOG] Estimating the weighted CQR model for quantile={quantile} with {penalty} penalty (eta={eta})..."
    )
    model = pwCQER.pwCQR(
        y=y,
        x=x,
        w=weight,
        z=z,
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


def _ttest(
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
    alpha: float = 0.05,
) -> (float, float):
    """
    Perform the t-test on the contextual variable of the estimated model.

    Parameters
    ----------
    model: typing.Union[
            CNLS.CNLS,
            pCNLS.pCNLS,
            wCNLS.wCNLS,
            pwCNLS.pwCNLS,
            CQER.CQR,
            pCQER.pCQR,
            wCQER.wCQR,
            pwCQER.pwCQR,
        ]
        Estimated model for which t-test will be calculated.
    alpha : float, optional
        Significance level, by default 0.05

    Returns
    -------
    (float, float)
        t-statistic and p-value for the t-test.
    """
    assert 0 < alpha < 1, "alpha must be between 0 and 1"

    z = np.array(model.z).flatten()

    y = np.array(model.y).T
    yhat = np.array(model.get_frontier()).T
    data = (np.stack([z, y, yhat], axis=0)).T
    sum_z = np.sum(np.square(data[:, 0] - np.average(data[:, 0])))
    sum_y = np.sum(np.square(data[:, 1] - data[:, 2]))
    df = len(data) - 2
    idf = 1 / df
    se = np.sqrt(idf * sum_y) / np.sqrt(sum_z)
    t_value = (model.get_lamda()) / se
    print(f"d: {model.get_lamda()[0]}")
    print(f"t-value: {t_value[0]}")

    print(f"t-score({alpha}, {df}): {t.ppf(alpha, df)}")
    print(f"p-value: {1-t.cdf(abs(t_value), df)[0]}")
    return t_value[0], 1 - t.cdf(abs(t_value), df)[0]
