import pandas as pd

from src.strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Cross-sectional mean-reversion strategy.

    Assets with the weakest recent performance are bought,
    while assets with the strongest recent performance are sold.

    Parameters
    ----------
    lookback : int
        Number of weeks used to calculate historical returns.

    top_n : int
        Number of recent losers to buy.

    bottom_n : int
        Number of recent winners to short.
    """

    def __init__(
        self,
        lookback=4,
        top_n=3,
        bottom_n=3
    ):
        self.lookback = lookback
        self.top_n = top_n
        self.bottom_n = bottom_n

    def generate_signals(self, weekly_returns):
        """
        Generate cross-sectional mean-reversion signals.

        Returns
        -------
        pandas.DataFrame

        Signal convention:

        +1 = Long
        -1 = Short
         0 = Neutral
        """

        # Calculate cumulative return over lookback window
        historical_returns = (
            (1 + weekly_returns)
            .rolling(self.lookback)
            .apply(lambda x: x.prod() - 1)
        )

        signals = pd.DataFrame(
            0,
            index=historical_returns.index,
            columns=historical_returns.columns
        )

        for date in historical_returns.index:

            row = historical_returns.loc[date].dropna()

            if row.empty:
                continue

            n_assets = len(row)

            # -----------------------------------------
            # LONG recent losers
            # -----------------------------------------

            n_long = min(
                self.top_n,
                n_assets
            )

            losers = row.nsmallest(
                n_long
            ).index

            # Remove long positions before choosing shorts
            remaining = row.drop(
                losers
            )

            # -----------------------------------------
            # SHORT recent winners
            # -----------------------------------------

            if remaining.empty:

                winners = []

            else:

                n_short = min(
                    self.bottom_n,
                    len(remaining)
                )

                winners = remaining.nlargest(
                    n_short
                ).index

            # -----------------------------------------
            # Assign signals
            # -----------------------------------------

            signals.loc[
                date,
                losers
            ] = 1

            if len(winners) > 0:

                signals.loc[
                    date,
                    winners
                ] = -1

        return signals