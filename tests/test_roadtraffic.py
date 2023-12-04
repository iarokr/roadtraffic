from roadtraffic.fintraffic import TrafficMeasurementStation
import roadtraffic.utils.funcs as funcs


tms = TrafficMeasurementStation(146, [(2019, 270), (2019, 271)])
tms.raw.load()
tms.raw.clean(direction=1, lanes=[1, 2, 3])
tms.raw_to_agg()
tms.agg_to_bag()


def test_cnls():
    tms.agg.estimate_model("mean", email="test1@test.test")
    assert tms.agg.models.get_problem_status("mean") == 1
    assert len(tms.agg.models.get_estimate("mean")) == 576
    assert len(tms.agg.models.get_frontier("mean")) == 576
    assert tms.agg.models.get_coefficients("mean").shape == (576, 2)
    assert len(tms.agg.models.get_models()) == 1


def test_pcnls():
    tms.agg.estimate_model("mean", penalty="l1", eta=10000, email="test2@test.test")
    assert tms.agg.models.get_problem_status("mean", penalty="l1", eta=10000) == 1


def test_cqr():
    tms.agg.estimate_model("quantile", quantiles=[0.5], email="test3@test.test")
    assert tms.agg.models.get_problem_status(quantile=0.5) == 1


def test_pcqr():
    tms.agg.estimate_model(
        "quantile", quantiles=[0.5], penalty="l1", eta=10000, email="test4@test.test"
    )
    assert (
        tms.agg.models.get_problem_status(
            quantile=0.5, penalty="l1", eta=10000
        )
        == 1
    )


def test_wcnls():
    tms.bag.estimate_model("mean", email="test5@test.test")
    assert tms.bag.models.get_problem_status("mean") == 1


def test_pwcnls():
    tms.bag.estimate_model("mean", penalty="l1", eta=10000, email="test6@test.test")
    assert tms.bag.models.get_problem_status("mean", penalty="l1", eta=10000) == 1


def test_wcqr():
    tms.bag.estimate_model("quantile", quantiles=[0.5], email="test7@test.test")
    assert tms.bag.models.get_problem_status(quantile=0.5) == 1


def test_pwcqr():
    tms.bag.estimate_model(
        "quantile", quantiles=[0.5], penalty="l1", eta=10000, email="test8@test.test"
    )
    assert (
        tms.bag.models.get_problem_status(
            quantile=0.5, penalty="l1", eta=10000
        )
        == 1
    )

def test_date_to_day():
    assert funcs.date_to_day(funcs.day_to_date(2019,270)) == (2019,270)
