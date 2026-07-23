import numpy as np
import pandas as pd


class PerformanceAnalytics:

    """
    Analyse portfolio performance.
    """

    def __init__(self, periods_per_year=52):

        self.periods = periods_per_year

    def annual_return(self, returns):

        compounded = (1 + returns.fillna(0)).prod()

        years = len(returns) / self.periods

        return compounded ** (1 / years) - 1

    def annual_volatility(self, returns):

        return returns.std() * np.sqrt(self.periods)

    def sharpe_ratio(
        self,
        returns,
        risk_free_rate=0
    ):

        excess = self.annual_return(returns) - risk_free_rate

        vol = self.annual_volatility(returns)

        return excess / vol

    def max_drawdown(self, returns):

        wealth = (1 + returns.fillna(0)).cumprod()

        peak = wealth.cummax()

        drawdown = wealth / peak - 1

        return drawdown.min()

    def win_rate(self, returns):

        return (returns > 0).mean()

    def summary(self, returns):

        print("=" * 60)

        print("PERFORMANCE REPORT")

        print("=" * 60)

        print(f"Annual Return      : {self.annual_return(returns):.2%}")

        print(f"Annual Volatility  : {self.annual_volatility(returns):.2%}")

        print(f"Sharpe Ratio       : {self.sharpe_ratio(returns):.2f}")

        print(f"Maximum Drawdown   : {self.max_drawdown(returns):.2%}")

        print(f"Winning Weeks      : {self.win_rate(returns):.2%}")