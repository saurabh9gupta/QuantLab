import numpy as np
import pandas as pd


class RiskAnalytics:

    """
    Calculate portfolio risk metrics.
    """

    def __init__(self, periods_per_year=52):

        self.periods = periods_per_year

    def rolling_volatility(
        self,
        returns,
        window=26
    ):

        return (
            returns
            .rolling(window)
            .std()
            * np.sqrt(self.periods)
        )

    def rolling_sharpe(
        self,
        returns,
        window=26
    ):

        annual_return = (
            returns
            .rolling(window)
            .mean()
            * self.periods
        )

        annual_vol = (
            returns
            .rolling(window)
            .std()
            * np.sqrt(self.periods)
        )

        return annual_return / annual_vol

    def drawdown_series(
        self,
        returns
    ):

        wealth = (
            1 + returns.fillna(0)
        ).cumprod()

        peak = wealth.cummax()

        drawdown = wealth / peak - 1

        return drawdown

    def value_at_risk(
        self,
        returns,
        confidence=0.95
    ):

        return returns.quantile(
            1 - confidence
        )

    def conditional_var(
        self,
        returns,
        confidence=0.95
    ):

        var = self.value_at_risk(
            returns,
            confidence
        )

        return returns[
            returns <= var
        ].mean()