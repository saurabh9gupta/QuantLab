import numpy as np
import pandas as pd


class FactorAttribution:
    """
    Performance attribution relative to an equal-weight benchmark.

    Metrics:
    - Alpha
    - Beta
    - Correlation
    - R Squared
    - Tracking Error
    - Information Ratio
    """

    def __init__(self, periods_per_year=52):
        self.periods_per_year = periods_per_year

    def benchmark_returns(self, weekly_returns):
        """
        Create an equal-weight benchmark from the investment universe.
        """
        return weekly_returns.mean(axis=1)

    def _align_returns(self, strategy_returns, benchmark_returns):
        """
        Align strategy and benchmark returns and remove missing values.
        """
        data = pd.concat(
            [strategy_returns, benchmark_returns],
            axis=1,
            join="inner"
        ).dropna()

        data.columns = ["Strategy", "Benchmark"]

        return data

    def active_returns(self, strategy_returns, benchmark_returns):
        """
        Active return = Strategy - Benchmark
        """
        data = self._align_returns(
            strategy_returns,
            benchmark_returns
        )

        return data["Strategy"] - data["Benchmark"]

    def beta(self, strategy_returns, benchmark_returns):
        """
        Portfolio beta relative to benchmark.
        """
        data = self._align_returns(
            strategy_returns,
            benchmark_returns
        )

        covariance = data["Strategy"].cov(
            data["Benchmark"]
        )

        variance = data["Benchmark"].var()

        if variance == 0:
            return np.nan

        return covariance / variance

    def alpha(self, strategy_returns, benchmark_returns):
        """
        Annualized alpha.
        """
        data = self._align_returns(
            strategy_returns,
            benchmark_returns
        )

        beta = self.beta(
            strategy_returns,
            benchmark_returns
        )

        annual_strategy = (
            data["Strategy"].mean()
            * self.periods_per_year
        )

        annual_benchmark = (
            data["Benchmark"].mean()
            * self.periods_per_year
        )

        return annual_strategy - beta * annual_benchmark

    def correlation(self, strategy_returns, benchmark_returns):
        """
        Correlation with benchmark.
        """
        data = self._align_returns(
            strategy_returns,
            benchmark_returns
        )

        return data["Strategy"].corr(
            data["Benchmark"]
        )

    def r_squared(self, strategy_returns, benchmark_returns):
        """
        Coefficient of determination.
        """
        corr = self.correlation(
            strategy_returns,
            benchmark_returns
        )

        return corr ** 2

    def tracking_error(self, strategy_returns, benchmark_returns):
        """
        Annualized tracking error.
        """
        active = self.active_returns(
            strategy_returns,
            benchmark_returns
        )

        return (
            active.std()
            * np.sqrt(self.periods_per_year)
        )

    def information_ratio(
        self,
        strategy_returns,
        benchmark_returns
    ):
        """
        Annualized Information Ratio.
        """
        active = self.active_returns(
            strategy_returns,
            benchmark_returns
        )

        annual_active = (
            active.mean()
            * self.periods_per_year
        )

        te = self.tracking_error(
            strategy_returns,
            benchmark_returns
        )

        if te == 0 or np.isnan(te):
            return np.nan

        return annual_active / te

    def rolling_beta(
        self,
        strategy_returns,
        benchmark_returns,
        window=26
    ):
        """
        Rolling beta over a specified window.
        """
        data = self._align_returns(
            strategy_returns,
            benchmark_returns
        )

        rolling_beta = (
            data["Strategy"]
            .rolling(window)
            .cov(data["Benchmark"])
            /
            data["Benchmark"]
            .rolling(window)
            .var()
        )

        return rolling_beta

    def summary(
        self,
        strategy_returns,
        benchmark_returns
    ):
        """
        Summary statistics.
        """
        summary = pd.Series({

            "Alpha":
                self.alpha(
                    strategy_returns,
                    benchmark_returns
                ),

            "Beta":
                self.beta(
                    strategy_returns,
                    benchmark_returns
                ),

            "Correlation":
                self.correlation(
                    strategy_returns,
                    benchmark_returns
                ),

            "R Squared":
                self.r_squared(
                    strategy_returns,
                    benchmark_returns
                ),

            "Tracking Error":
                self.tracking_error(
                    strategy_returns,
                    benchmark_returns
                ),

            "Information Ratio":
                self.information_ratio(
                    strategy_returns,
                    benchmark_returns
                )

        })

        return summary