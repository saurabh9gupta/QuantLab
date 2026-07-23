import pandas as pd


class SignalGenerator:
    """
    Generate trading signals for different strategies.
    """

    def __init__(self):
        pass

    def weekly_returns(self, prices):
        """
        Convert daily prices to weekly returns.
        """

        weekly_prices = prices.resample("W-FRI").last().dropna(how="all")

        weekly_returns = weekly_prices.pct_change()

        return weekly_returns

    def rank_assets(self, weekly_returns):
        """
        Rank assets by weekly return.
        """

        return weekly_returns.rank(
            axis=1,
            ascending=False,
            method="first"
        )

    def generate_long_short_signals(
        self,
        weekly_returns
    ):
        """
        Long highest return.
        Short lowest return.
        """

        signals = pd.DataFrame(
            0,
            index=weekly_returns.index,
            columns=weekly_returns.columns
        )

        for date in weekly_returns.index:

            row = weekly_returns.loc[date].dropna()
            
            #skip weeks with no valid returns
            if row.empty:
                continue

            winner = row.idxmax()

            loser = row.idxmin()

            signals.loc[date, winner] = 1

            signals.loc[date, loser] = -1

        return signals