import pandas as pd


class PortfolioConstructor:
    """
    Convert trading signals into portfolio weights.
    Supports long/short equal-weight portfolios.
    """

    def equal_weight_portfolio(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert signals into equal-weight positions.

        Long positions sum to +1.
        Short positions sum to -1.
        """

        weights = signals.astype(float).copy()

        for date in weights.index:

            longs = weights.loc[date] == 1
            shorts = weights.loc[date] == -1

            n_long = longs.sum()
            n_short = shorts.sum()

            if n_long > 0:
                weights.loc[date, longs] = 1.0 / n_long

            if n_short > 0:
                weights.loc[date, shorts] = -1.0 / n_short

        return weights