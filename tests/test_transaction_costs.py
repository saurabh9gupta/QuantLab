import pandas as pd
import pytest

from src.transaction_costs import TransactionCostModel


def test_turnover_calculation():
    """
    Turnover should include initial portfolio establishment
    and subsequent changes in portfolio weights.
    """

    weights = pd.DataFrame(
        {
            "A": [1.0, 0.0],
            "B": [-1.0, 0.0],
        }
    )

    model = TransactionCostModel(
        bps=10
    )

    turnover = model.turnover(
        weights
    )

    # Initial portfolio:
    # (|1| + |-1|) / 2 = 1.0
    assert turnover.iloc[0] == pytest.approx(1.0)

    # Closing the portfolio:
    # (|0-1| + |0-(-1)|) / 2 = 1.0
    assert turnover.iloc[1] == pytest.approx(1.0)


def test_transaction_cost_calculation():
    """
    Transaction costs should equal turnover multiplied
    by the basis-point cost rate.
    """

    weights = pd.DataFrame(
        {
            "A": [1.0, 0.5],
            "B": [-1.0, -0.5],
        }
    )

    model = TransactionCostModel(
        bps=10
    )

    costs = model.transaction_cost(
        weights
    )

    # 10 bps = 0.001
    #
    # Initial turnover = (1 + 1) / 2 = 1
    assert costs.iloc[0] == pytest.approx(0.001)

    # Second-period turnover:
    # (|0.5 - 1| + |-0.5 - (-1)|) / 2
    # = (0.5 + 0.5) / 2
    # = 0.5
    assert costs.iloc[1] == pytest.approx(0.0005)


def test_net_returns_after_costs():
    """
    Net returns should equal gross strategy returns
    minus transaction costs.
    """

    weights = pd.DataFrame(
        {
            "A": [1.0, 1.0],
            "B": [-1.0, -1.0],
        }
    )

    strategy_returns = pd.Series(
        [0.02, 0.03]
    )

    model = TransactionCostModel(
        bps=10
    )

    net_returns = model.net_returns(
        strategy_returns,
        weights
    )

    # Initial portfolio establishment costs 10 bps.
    assert net_returns.iloc[0] == pytest.approx(0.019)

    # No rebalance in period 2 -> zero transaction cost.
    assert net_returns.iloc[1] == pytest.approx(0.03)


def test_zero_bps_produces_gross_returns():
    """
    With zero transaction costs, net returns should
    equal gross returns exactly.
    """

    weights = pd.DataFrame(
        {
            "A": [1.0, 0.0],
            "B": [-1.0, 0.0],
        }
    )

    strategy_returns = pd.Series(
        [0.02, -0.01]
    )

    model = TransactionCostModel(
        bps=0
    )

    net_returns = model.net_returns(
        strategy_returns,
        weights
    )

    pd.testing.assert_series_equal(
        net_returns,
        strategy_returns.astype(float)
    )