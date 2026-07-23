import pandas as pd
import pytest

from src.portfolio.constructor import PortfolioConstructor


def test_long_short_portfolio_is_dollar_neutral():

    signals = pd.DataFrame(
        {
            "AAPL": [1],
            "MSFT": [1],
            "JPM": [-1],
            "XOM": [-1],
        }
    )

    constructor = PortfolioConstructor()

    weights = constructor.equal_weight_portfolio(
        signals
    )

    # Long book = +1
    assert weights[
        weights > 0
    ].sum(axis=1).iloc[0] == pytest.approx(1.0)

    # Short book = -1
    assert weights[
        weights < 0
    ].sum(axis=1).iloc[0] == pytest.approx(-1.0)

    # Net exposure = 0
    assert weights.sum(axis=1).iloc[0] == pytest.approx(0.0)

    # Gross exposure = 2
    assert weights.abs().sum(axis=1).iloc[0] == pytest.approx(2.0)


def test_equal_weight_allocation():

    signals = pd.DataFrame(
        {
            "AAPL": [1],
            "MSFT": [1],
            "JPM": [-1],
            "XOM": [-1],
        }
    )

    constructor = PortfolioConstructor()

    weights = constructor.equal_weight_portfolio(
        signals
    )

    assert weights.iloc[0]["AAPL"] == pytest.approx(0.5)
    assert weights.iloc[0]["MSFT"] == pytest.approx(0.5)

    assert weights.iloc[0]["JPM"] == pytest.approx(-0.5)
    assert weights.iloc[0]["XOM"] == pytest.approx(-0.5)