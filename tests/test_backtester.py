import pandas as pd
import pytest

from src.backtester import Backtester


def test_portfolio_returns_use_previous_period_weights():
    """
    Portfolio returns must use the previous period's weights.

    This prevents same-period signal information from being applied
    retrospectively to returns from that period.
    """

    dates = pd.date_range(
        "2024-01-05",
        periods=3,
        freq="W-FRI"
    )

    weights = pd.DataFrame(
        {
            "AAPL": [1.0, 0.0, 1.0],
            "MSFT": [-1.0, 0.0, -1.0],
        },
        index=dates,
    )

    asset_returns = pd.DataFrame(
        {
            "AAPL": [0.10, 0.05, -0.02],
            "MSFT": [-0.05, 0.01, 0.03],
        },
        index=dates,
    )

    backtester = Backtester()

    portfolio_returns = backtester.calculate_portfolio_returns(
        weights,
        asset_returns
    )

    # First period has no previous-period position.
    assert portfolio_returns.iloc[0] == pytest.approx(0.0)

    # Period 2 must use period 1 weights:
    # (1 * 5%) + (-1 * 1%) = 4%
    assert portfolio_returns.iloc[1] == pytest.approx(0.04)

    # Period 3 uses period 2 weights, which are zero.
    assert portfolio_returns.iloc[2] == pytest.approx(0.0)


def test_cumulative_returns():
    """
    Cumulative wealth should compound portfolio returns correctly.
    """

    returns = pd.Series(
        [0.10, -0.05, 0.02]
    )

    backtester = Backtester()

    cumulative = backtester.cumulative_returns(
        returns
    )

    expected_final_value = (
        1.10 * 0.95 * 1.02
    )

    assert cumulative.iloc[-1] == pytest.approx(
        expected_final_value
    )