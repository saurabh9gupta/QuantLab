import numpy as np
import pandas as pd

from src.pipeline import ResearchPipeline
from src.performance import PerformanceAnalytics


class MultiStrategyEngine:
    """
    Engine for running, comparing, and combining
    multiple quantitative strategies.

    Each strategy is passed through the standard
    QuantLab ResearchPipeline.
    """

    def __init__(
        self,
        strategies,
        allocations=None
    ):
        """
        Parameters
        ----------
        strategies : dict
            Dictionary containing strategy objects.

            Example:

            {
                "Momentum": MomentumStrategy(),
                "Mean Reversion": MeanReversionStrategy()
            }

        allocations : dict, optional
            Portfolio allocation assigned to each strategy.

            If None, strategies receive equal allocations.
        """

        if not strategies:
            raise ValueError(
                "At least one strategy must be supplied."
            )

        self.strategies = strategies

        # -----------------------------------------
        # Strategy allocations
        # -----------------------------------------

        if allocations is None:

            equal_weight = (
                1.0 / len(strategies)
            )

            allocations = {
                name: equal_weight
                for name in strategies
            }

        # Check that allocation names match strategies

        if set(allocations.keys()) != set(strategies.keys()):

            raise ValueError(
                "Allocation names must match strategy names."
            )

        allocation_sum = sum(
            allocations.values()
        )

        if not np.isclose(
            allocation_sum,
            1.0
        ):

            raise ValueError(
                "Strategy allocations must sum to 1."
            )

        self.allocations = allocations

        self.performance = PerformanceAnalytics()

    def run_strategies(
        self,
        prices
    ):
        """
        Run every strategy through ResearchPipeline.

        Returns
        -------
        dict
            Full pipeline output for every strategy.
        """

        results = {}

        for name, strategy in self.strategies.items():

            pipeline = ResearchPipeline(
                strategy=strategy
            )

            results[name] = pipeline.run(
                prices
            )

        return results

    def strategy_returns(
        self,
        results
    ):
        """
        Extract strategy return series and combine
        them into a DataFrame.
        """

        returns = {}

        for name, output in results.items():

            returns[name] = output[
                "strategy_returns"
            ]

        returns = pd.DataFrame(
            returns
        )

        return returns

    def combined_returns(
        self,
        strategy_returns
    ):
        """
        Construct the multi-strategy portfolio.

        Combined return is the weighted sum of
        individual strategy returns.
        """

        combined = pd.Series(
            0.0,
            index=strategy_returns.index,
            dtype=float
        )

        for name, allocation in self.allocations.items():

            combined = (
                combined
                + strategy_returns[name].fillna(0)
                * allocation
            )

        combined.name = "Combined"

        return combined

    def correlation_matrix(
        self,
        strategy_returns
    ):
        """
        Calculate strategy return correlations.
        """

        return strategy_returns.corr()

    def performance_summary(
        self,
        strategy_returns,
        combined_returns=None
    ):
        """
        Compare performance across strategies.

        Optionally includes the combined
        multi-strategy portfolio.
        """

        returns = strategy_returns.copy()

        if combined_returns is not None:

            returns["Combined"] = (
                combined_returns
            )

        summary = []

        for name in returns.columns:

            r = returns[name].dropna()

            summary.append({

                "Strategy":
                    name,

                "Annual Return":
                    self.performance.annual_return(
                        r
                    ),

                "Annual Volatility":
                    self.performance.annual_volatility(
                        r
                    ),

                "Sharpe Ratio":
                    self.performance.sharpe_ratio(
                        r
                    ),

                "Maximum Drawdown":
                    self.performance.max_drawdown(
                        r
                    ),

                "Win Rate":
                    self.performance.win_rate(
                        r
                    )

            })

        summary = pd.DataFrame(
            summary
        )

        summary = summary.set_index(
            "Strategy"
        )

        return summary

    def cumulative_returns(
        self,
        strategy_returns,
        combined_returns=None
    ):
        """
        Calculate cumulative wealth curves.
        """

        returns = strategy_returns.copy()

        if combined_returns is not None:

            returns["Combined"] = (
                combined_returns
            )

        cumulative = (
            1 + returns.fillna(0)
        ).cumprod()

        return cumulative