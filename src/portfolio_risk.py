import numpy as np
import pandas as pd


class PortfolioRiskManager:
    """
    Portfolio-level risk management and strategy allocation engine.

    Supports:
    - Equal-weight allocation
    - Inverse-volatility allocation
    - Portfolio volatility
    - Marginal contribution to risk
    - Component contribution to risk
    - Percentage contribution to risk
    - Diversification ratio
    """

    def __init__(self, periods_per_year=52):
        self.periods_per_year = periods_per_year

    def _clean_returns(self, returns):
        """
        Align strategy returns and remove observations
        containing missing or infinite values.
        """

        clean = returns.copy()

        clean = clean.replace(
            [np.inf, -np.inf],
            np.nan
        )

        clean = clean.dropna()

        return clean

    def annualized_volatility(self, returns):
        """
        Annualized volatility of each strategy.
        """

        clean = self._clean_returns(returns)

        return (
            clean.std()
            * np.sqrt(self.periods_per_year)
        )

    def covariance_matrix(self, returns):
        """
        Annualized covariance matrix.
        """

        clean = self._clean_returns(returns)

        return (
            clean.cov()
            * self.periods_per_year
        )

    def equal_weights(self, returns):
        """
        Equal capital allocation across strategies.
        """

        n_strategies = returns.shape[1]

        if n_strategies == 0:
            raise ValueError(
                "Returns DataFrame contains no strategies."
            )

        weights = pd.Series(
            1.0 / n_strategies,
            index=returns.columns,
            name="Equal Weight"
        )

        return weights

    def inverse_volatility_weights(self, returns):
        """
        Allocate capital inversely proportional
        to strategy volatility.
        """

        volatility = self.annualized_volatility(
            returns
        )

        if (volatility <= 0).any():
            raise ValueError(
                "Strategy volatility must be greater than zero."
            )

        inverse_vol = 1.0 / volatility

        weights = (
            inverse_vol
            / inverse_vol.sum()
        )

        weights.name = "Inverse Volatility Weight"

        return weights

    def portfolio_returns(
        self,
        returns,
        weights
    ):
        """
        Calculate portfolio returns from strategy returns
        and allocation weights.
        """

        clean = returns.copy()

        weights = weights.reindex(
            clean.columns
        )

        if weights.isna().any():
            raise ValueError(
                "Weights must be supplied for every strategy."
            )

        return (
            clean.fillna(0)
            .mul(weights, axis=1)
            .sum(axis=1)
        )

    def portfolio_volatility(
        self,
        returns,
        weights
    ):
        """
        Annualized portfolio volatility using
        the covariance matrix.
        """

        covariance = self.covariance_matrix(
            returns
        )

        weights = weights.reindex(
            covariance.columns
        )

        w = weights.values

        variance = (
            w.T
            @ covariance.values
            @ w
        )

        return np.sqrt(variance)

    def marginal_risk_contribution(
        self,
        returns,
        weights
    ):
        """
        Marginal contribution of each strategy
        to portfolio volatility.
        """

        covariance = self.covariance_matrix(
            returns
        )

        weights = weights.reindex(
            covariance.columns
        )

        portfolio_vol = self.portfolio_volatility(
            returns,
            weights
        )

        if portfolio_vol == 0:
            return pd.Series(
                np.nan,
                index=covariance.columns
            )

        marginal = (
            covariance.values
            @ weights.values
        ) / portfolio_vol

        return pd.Series(
            marginal,
            index=covariance.columns,
            name="Marginal Risk Contribution"
        )

    def component_risk_contribution(
        self,
        returns,
        weights
    ):
        """
        Component contribution to portfolio volatility.

        Weight × marginal risk contribution.
        """

        marginal = self.marginal_risk_contribution(
            returns,
            weights
        )

        weights = weights.reindex(
            marginal.index
        )

        component = (
            weights * marginal
        )

        component.name = "Component Risk Contribution"

        return component

    def percentage_risk_contribution(
        self,
        returns,
        weights
    ):
        """
        Percentage contribution of each strategy
        to total portfolio volatility.
        """

        component = self.component_risk_contribution(
            returns,
            weights
        )

        total = component.sum()

        if total == 0:
            return pd.Series(
                np.nan,
                index=component.index
            )

        percentage = (
            component / total
        )

        percentage.name = "Percentage Risk Contribution"

        return percentage

    def diversification_ratio(
        self,
        returns,
        weights
    ):
        """
        Weighted-average standalone volatility divided
        by portfolio volatility.

        Values greater than 1 indicate diversification.
        """

        volatility = self.annualized_volatility(
            returns
        )

        weights = weights.reindex(
            volatility.index
        )

        weighted_volatility = (
            weights * volatility
        ).sum()

        portfolio_vol = self.portfolio_volatility(
            returns,
            weights
        )

        if portfolio_vol == 0:
            return np.nan

        return (
            weighted_volatility
            / portfolio_vol
        )

    def risk_summary(
        self,
        returns,
        weights
    ):
        """
        Produce strategy-level allocation and risk summary.
        """

        volatility = self.annualized_volatility(
            returns
        )

        marginal = self.marginal_risk_contribution(
            returns,
            weights
        )

        component = self.component_risk_contribution(
            returns,
            weights
        )

        percentage = self.percentage_risk_contribution(
            returns,
            weights
        )

        summary = pd.DataFrame({

            "Weight":
                weights,

            "Annual Volatility":
                volatility,

            "Marginal Risk Contribution":
                marginal,

            "Component Risk Contribution":
                component,

            "Risk Contribution %":
                percentage

        })

        return summary