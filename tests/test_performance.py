import numpy as np
import pandas as pd
import pytest

from src.performance import PerformanceAnalytics


def test_annual_volatility():

    returns = pd.Series(
        [0.01, -0.01, 0.01, -0.01]
    )

    analytics = PerformanceAnalytics()

    expected = returns.std() * np.sqrt(52)

    assert analytics.annual_volatility(
        returns
    ) == pytest.approx(expected)


def test_max_drawdown():

    returns = pd.Series(
        [0.10, -0.20, 0.05]
    )

    analytics = PerformanceAnalytics()

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()

    expected = (
        cumulative / running_max - 1
    ).min()

    assert analytics.max_drawdown(
        returns
    ) == pytest.approx(expected)


def test_win_rate():

    returns = pd.Series(
        [0.10, -0.05, 0.02, -0.01]
    )

    analytics = PerformanceAnalytics()

    assert analytics.win_rate(
        returns
    ) == pytest.approx(0.5)