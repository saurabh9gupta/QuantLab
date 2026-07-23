import pandas as pd

from src.strategies.momentum import MomentumStrategy


def test_momentum_selects_winners_and_losers():
    """
    Momentum strategy should go long the strongest assets
    and short the weakest assets after sufficient lookback.
    """

    dates = pd.date_range(
        "2024-01-05",
        periods=4,
        freq="W-FRI"
    )

    returns = pd.DataFrame(
        {
            "AAPL": [0.10, 0.08, 0.06, 0.05],
            "MSFT": [0.05, 0.04, 0.03, 0.02],
            "JPM": [-0.02, -0.03, -0.04, -0.05],
            "XOM": [-0.08, -0.07, -0.06, -0.04],
        },
        index=dates,
    )

    strategy = MomentumStrategy(
        lookback=2,
        top_n=1,
        bottom_n=1
    )

    signals = strategy.generate_signals(returns)

    # Insufficient history at the beginning
    assert (signals.iloc[0] == 0).all()

    # AAPL should be the strongest cumulative performer
    assert signals.iloc[-1]["AAPL"] == 1

    # XOM should be the weakest cumulative performer
    assert signals.iloc[-1]["XOM"] == -1

    # Exactly one long and one short
    assert (signals.iloc[-1] == 1).sum() == 1
    assert (signals.iloc[-1] == -1).sum() == 1


def test_momentum_signals_are_neutral():
    """
    With equal numbers of long and short selections,
    raw momentum signals should sum to zero.
    """

    dates = pd.date_range(
        "2024-01-05",
        periods=3,
        freq="W-FRI"
    )

    returns = pd.DataFrame(
        {
            "A": [0.10, 0.08, 0.06],
            "B": [0.05, 0.04, 0.03],
            "C": [-0.03, -0.04, -0.05],
            "D": [-0.08, -0.07, -0.06],
        },
        index=dates,
    )

    strategy = MomentumStrategy(
        lookback=2,
        top_n=1,
        bottom_n=1
    )

    signals = strategy.generate_signals(returns)

    active = signals.loc[
        signals.abs().sum(axis=1) > 0
    ]

    assert (active.sum(axis=1) == 0).all()