import pandas as pd
import numpy as np


class ReturnCalculator:
    """
    Calculates financial returns.
    """

    def __init__(self):
        pass

    def simple_returns(self, prices):
        """
        Calculate percentage returns.
        """

        returns = prices.pct_change()

        return returns

    def log_returns(self, prices):
        """
        Calculate logarithmic returns.
        """

        returns = np.log(prices / prices.shift(1))

        return returns

    def cumulative_returns(self, returns):
        """
        Calculate cumulative returns.
        """

        cumulative = (1 + returns).cumprod()

        return cumulative

    def summary(self, returns):
        """
        Print summary statistics.
        """

        print("=" * 60)
        print("RETURN SUMMARY")
        print("=" * 60)

        print(f"Rows : {returns.shape[0]}")
        print(f"Cols : {returns.shape[1]}")

        print("\nMissing Values")

        print(returns.isna().sum())

        print("\nMean Daily Returns")

        print(returns.mean())

        print("\nDaily Volatility")

        print(returns.std())