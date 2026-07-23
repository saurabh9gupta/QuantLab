import pandas as pd


class TransactionCostModel:
    """
    Transaction cost model for QuantLab.

    Estimates portfolio turnover, transaction costs and
    net strategy returns after trading costs.

    Parameters
    ----------
    bps : float, default=10
        Transaction cost in basis points.

        Example
        -------
        10 = 0.10%
        25 = 0.25%
    """

    def __init__(self, bps=10):
        self.bps = bps
        self.cost_rate = bps / 10000

    def turnover(self, weights):
        """
        Calculate portfolio turnover.

        Turnover is defined as the absolute change in
        portfolio weights between consecutive periods.

        Parameters
        ----------
        weights : pandas.DataFrame

        Returns
        -------
        pandas.Series
        """

        turnover = (
            weights
            .diff()
            .abs()
            .sum(axis=1)
        )/2

        turnover.iloc[0] = weights.iloc[0].abs().sum() / 2

        return turnover.fillna(0)

    def transaction_cost(self, weights):
        """
        Calculate transaction cost for each rebalance.

        Parameters
        ----------
        weights : pandas.DataFrame

        Returns
        -------
        pandas.Series
        """

        turnover = self.turnover(weights)

        costs = turnover * self.cost_rate

        return costs

    def net_returns(
        self,
        strategy_returns,
        weights
    ):
        """
        Calculate strategy returns after transaction costs.

        Parameters
        ----------
        strategy_returns : pandas.Series

        weights : pandas.DataFrame

        Returns
        -------
        pandas.Series
        """

        costs = self.transaction_cost(weights)

        net_returns = (
            strategy_returns.fillna(0)
            - costs
        )

        return net_returns

    def cumulative_returns(
        self,
        returns
    ):
        """
        Calculate cumulative returns.

        Parameters
        ----------
        returns : pandas.Series

        Returns
        -------
        pandas.Series
        """

        cumulative = (
            1 + returns.fillna(0)
        ).cumprod()

        return cumulative

    def summary(
        self,
        strategy_returns,
        weights
    ):
        """
        Generate transaction cost summary.

        Parameters
        ----------
        strategy_returns : pandas.Series

        weights : pandas.DataFrame

        Returns
        -------
        pandas.Series
        """

        turnover = self.turnover(weights)

        costs = self.transaction_cost(weights)

        net_returns = self.net_returns(
            strategy_returns,
            weights
        )

        summary = pd.Series({

            "Transaction Cost (bps)": self.bps,

            "Average Turnover":
                turnover.mean(),

            "Maximum Turnover":
                turnover.max(),

            "Total Turnover":
                turnover.sum(),

            "Average Cost":
                costs.mean(),

            "Total Cost":
                costs.sum(),

            "Gross Return":
                (1 + strategy_returns.fillna(0)).prod() - 1,

            "Net Return":
                (1 + net_returns).prod() - 1

        })

        return summary

    def cost_sensitivity(
        self,
        strategy_returns,
        weights,
        bps_list=(0, 5, 10, 20, 50)
    ):
        """
        Evaluate strategy under different transaction costs.

        Parameters
        ----------
        strategy_returns : pandas.Series

        weights : pandas.DataFrame

        bps_list : iterable

        Returns
        -------
        pandas.DataFrame
        """

        results = []

        turnover = self.turnover(weights)

        gross_return = (
            1 + strategy_returns.fillna(0)
        ).prod() - 1

        for bps in bps_list:

            rate = bps / 10000

            costs = turnover * rate

            net_returns = (
                strategy_returns.fillna(0)
                - costs
            )

            net_return = (
                1 + net_returns
            ).prod() - 1

            results.append({

                "Transaction Cost (bps)": bps,

                "Gross Return": gross_return,

                "Net Return": net_return,

                "Total Cost": costs.sum()

            })

        return pd.DataFrame(results)