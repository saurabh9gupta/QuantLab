import pandas as pd

from src.strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Cross-sectional momentum strategy.

    Selects the top N and bottom N assets based on
    historical cumulative returns.
    """

    def __init__(
        self,
        lookback=13,
        top_n=3,
        bottom_n=3
    ):
        self.lookback = lookback
        self.top_n = top_n
        self.bottom_n = bottom_n

    def generate_signals(self, weekly_returns):

        # Calculate cumulative momentum
        momentum = (
            (1 + weekly_returns)
            .rolling(self.lookback)
            .apply(lambda x: x.prod() - 1)
        )

        signals = pd.DataFrame(
            0,
            index=momentum.index,
            columns=momentum.columns
        )

        for date in momentum.index:

            row = momentum.loc[date].dropna()

            if row.empty:
                continue

            # Number of available assets
            n_assets = len(row)

            # Ensure we never request more assets than exist
            top_n = min(self.top_n, n_assets)

            # Select winners
            winners = row.nlargest(top_n).index

            # Remove winners before selecting losers
            remaining = row.drop(winners)

            if remaining.empty:
                losers = []
            else:
                bottom_n = min(self.bottom_n, len(remaining))
                losers = remaining.nsmallest(bottom_n).index

            signals.loc[date, winners] = 1

            if len(losers) > 0:
                signals.loc[date, losers] = -1

        return signals