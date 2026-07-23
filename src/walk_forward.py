import numpy as np
import pandas as pd

from src.pipeline import ResearchPipeline
from src.performance import PerformanceAnalytics
from src.strategies.momentum import MomentumStrategy


class WalkForwardOptimizer:
    """
    Walk-forward optimization engine for momentum strategies.

    For each walk-forward period:

    1. Optimize momentum lookback on the training window.
    2. Select the lookback with the highest Sharpe ratio.
    3. Run that strategy over the subsequent test window.
    4. Store out-of-sample returns and parameter selections.
    """

    def __init__(
        self,
        lookbacks=None,
        top_n=3,
        bottom_n=3,
        train_years=5,
        test_years=1,
        periods_per_year=52
    ):

        if lookbacks is None:
            lookbacks = [1, 2, 4, 8, 13, 26]

        self.lookbacks = lookbacks
        self.top_n = top_n
        self.bottom_n = bottom_n

        self.train_years = train_years
        self.test_years = test_years

        self.periods_per_year = periods_per_year

        self.performance = PerformanceAnalytics(
            periods_per_year=periods_per_year
        )

    def _run_strategy(
        self,
        prices,
        lookback
    ):
        """
        Run a momentum strategy for a given lookback.
        """

        strategy = MomentumStrategy(
            lookback=lookback,
            top_n=self.top_n,
            bottom_n=self.bottom_n
        )

        pipeline = ResearchPipeline(
            strategy=strategy
        )

        results = pipeline.run(prices)

        return results["strategy_returns"]

    def _evaluate_lookbacks(
        self,
        training_prices
    ):
        """
        Evaluate candidate lookbacks on the training sample.
        """

        results = []

        for lookback in self.lookbacks:

            returns = self._run_strategy(
                training_prices,
                lookback
            )

            sharpe = self.performance.sharpe_ratio(
                returns
            )

            results.append({
                "Lookback": lookback,
                "Sharpe": sharpe
            })

        results = pd.DataFrame(results)

        results = results.replace(
            [np.inf, -np.inf],
            np.nan
        )

        results = results.dropna(
            subset=["Sharpe"]
        )

        if results.empty:
            return None, results

        best_row = results.loc[
            results["Sharpe"].idxmax()
        ]

        best_lookback = int(
            best_row["Lookback"]
        )

        return best_lookback, results

    def run(self, prices):
        """
        Execute walk-forward optimization.

        Parameters
        ----------
        prices : pandas.DataFrame
            Daily price matrix.

        Returns
        -------
        dict
            Contains:

            out_of_sample_returns
            parameter_history
            optimization_history
        """

        prices = prices.sort_index().copy()

        start_date = prices.index.min()
        end_date = prices.index.max()

        train_start = start_date

        parameter_history = []
        optimization_history = []

        oos_returns = []

        while True:

            train_end = (
                train_start
                + pd.DateOffset(years=self.train_years)
            )

            test_end = (
                train_end
                + pd.DateOffset(years=self.test_years)
            )

            if train_end >= end_date:
                break

            if test_end > end_date:
                test_end = end_date

            training_prices = prices.loc[
                (prices.index >= train_start)
                &
                (prices.index < train_end)
            ]

            # ------------------------------------------------
            # Include training history in the test dataset
            # so momentum can be calculated at the beginning
            # of the test period.
            # ------------------------------------------------

            test_with_history = prices.loc[
                (prices.index >= train_start)
                &
                (prices.index < test_end)
            ]

            if training_prices.empty:
                break

            best_lookback, optimization = (
                self._evaluate_lookbacks(
                    training_prices
                )
            )

            if best_lookback is None:
                train_start = (
                    train_start
                    + pd.DateOffset(
                        years=self.test_years
                    )
                )

                continue

            # Store optimization results

            optimization = optimization.copy()

            optimization["Train Start"] = train_start
            optimization["Train End"] = train_end

            optimization_history.append(
                optimization
            )

            # Run selected parameter

            test_returns = self._run_strategy(
                test_with_history,
                best_lookback
            )

            # Keep only genuinely out-of-sample observations

            test_returns = test_returns.loc[
                (test_returns.index >= train_end)
                &
                (test_returns.index < test_end)
            ]

            oos_returns.append(
                test_returns
            )

            parameter_history.append({

                "Train Start": train_start,

                "Train End": train_end,

                "Test Start": train_end,

                "Test End": test_end,

                "Selected Lookback":
                    best_lookback

            })

            # Expanding through time using rolling
            # five-year training windows.

            train_start = (
                train_start
                + pd.DateOffset(
                    years=self.test_years
                )
            )

            if test_end >= end_date:
                break

        if oos_returns:

            out_of_sample_returns = pd.concat(
                oos_returns
            ).sort_index()

            out_of_sample_returns = (
                out_of_sample_returns[
                    ~out_of_sample_returns
                    .index
                    .duplicated(
                        keep="first"
                    )
                ]
            )

        else:

            out_of_sample_returns = pd.Series(
                dtype=float
            )

        parameter_history = pd.DataFrame(
            parameter_history
        )

        if optimization_history:

            optimization_history = pd.concat(
                optimization_history,
                ignore_index=True
            )

        else:

            optimization_history = pd.DataFrame()

        return {

            "out_of_sample_returns":
                out_of_sample_returns,

            "parameter_history":
                parameter_history,

            "optimization_history":
                optimization_history
        }