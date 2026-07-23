import pandas as pd


class Backtester:
    """
    Backtesting engine for long/short strategies.
    """

    def __init__(self):
        pass

    def calculate_portfolio_returns(
        self,
        weights,
        asset_returns
    ):
        """
        Calculate portfolio returns using previous week's weights.
        """

        shifted_weights = weights.shift(1)

        portfolio_returns = (
            shifted_weights * asset_returns
        ).sum(axis=1)

        return portfolio_returns

    def cumulative_returns(
        self,
        portfolio_returns
    ):
        """
        Calculate cumulative portfolio performance.
        """

        cumulative = (1 + portfolio_returns.fillna(0)).cumprod()

        return cumulative

    def summary(
        self,
        portfolio_returns
    ):
        """
        Print basic strategy statistics.
        """

        print("=" * 60)
        print("BACKTEST SUMMARY")
        print("=" * 60)

        print(f"Observations : {len(portfolio_returns)}")

        print(f"Mean Weekly Return : {portfolio_returns.mean():.4%}")

        print(f"Weekly Volatility : {portfolio_returns.std():.4%}")

        print(f"Best Week : {portfolio_returns.max():.4%}")

        print(f"Worst Week : {portfolio_returns.min():.4%}")