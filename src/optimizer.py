import pandas as pd

from src.pipeline import ResearchPipeline
from src.performance import PerformanceAnalytics
from src.strategies.momentum import MomentumStrategy


class ParameterOptimizer:
    """
    Optimizes the momentum lookback parameter.
    """

    def __init__(self):

        self.performance = PerformanceAnalytics()

    def optimize_lookback(
        self,
        prices,
        lookbacks
    ):

        results = []

        for lookback in lookbacks:

            print(f"Running lookback = {lookback}")

            strategy = MomentumStrategy(
                lookback=lookback,
                top_n=5,
                bottom_n=5
            )

            pipeline = ResearchPipeline(
                strategy=strategy
            )

            output = pipeline.run(prices)

            returns = output["strategy_returns"]

            results.append({

                "Lookback": lookback,

                "Annual Return":
                    self.performance.annual_return(returns),

                "Annual Volatility":
                    self.performance.annual_volatility(returns),

                "Sharpe":
                    self.performance.sharpe_ratio(returns),

                "Max Drawdown":
                    self.performance.max_drawdown(returns),

                "Win Rate":
                    self.performance.win_rate(returns)

            })

        results = (
            pd.DataFrame(results)
            .sort_values(
                by="Sharpe",
                ascending=False
            )
            .reset_index(drop=True)
        )

        return results