from src.portfolio.constructor import PortfolioConstructor
from src.backtester import Backtester
from src.performance import PerformanceAnalytics
from src.risk import RiskAnalytics

from src.strategies.momentum import MomentumStrategy


class ResearchPipeline:
    """
    End-to-end quantitative research pipeline.
    """

    def __init__(self, strategy=None):

        # Default Strategy
        if strategy is None:
            strategy = MomentumStrategy()

        self.strategy = strategy

        # Portfolio Construction
        self.portfolio_engine = PortfolioConstructor()

        # Backtesting
        self.backtester = Backtester()

        # Analytics
        self.performance = PerformanceAnalytics()
        self.risk = RiskAnalytics()

    def run(self, prices):
        """
        Run the complete research pipeline.

        Parameters
        ----------
        prices : pandas.DataFrame
            Daily adjusted close prices.

        Returns
        -------
        dict
            Dictionary containing all intermediate and final outputs.
        """

        # Convert daily prices to weekly returns
        weekly_returns = (
            prices
            .resample("W-FRI")
            .last()
            .dropna(how="all")
            .pct_change()
        )

        # Generate strategy signals
        signals = self.strategy.generate_signals(weekly_returns)

        # Portfolio weights
        weights = self.portfolio_engine.equal_weight_portfolio(
            signals
        )

        # Strategy returns
        strategy_returns = self.backtester.calculate_portfolio_returns(
            weights,
            weekly_returns
        )

        # Cumulative performance
        cumulative_returns = self.backtester.cumulative_returns(
            strategy_returns
        )

        return {
            "weekly_returns": weekly_returns,
            "signals": signals,
            "weights": weights,
            "strategy_returns": strategy_returns,
            "cumulative_returns": cumulative_returns,
        }