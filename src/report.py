import numpy as np
import pandas as pd
from pathlib import Path


class PerformanceReport:
    """
    Professional performance reporting engine.

    Provides:
    - Return analytics
    - Risk-adjusted performance metrics
    - Drawdown analysis
    - Distribution statistics
    - Rolling statistics
    - Calendar returns
    - Multi-strategy comparison
    - Automated research report export
    """

    def __init__(self, periods_per_year=52):
        self.periods_per_year = periods_per_year

    # --------------------------------------------------------
    # Data Cleaning
    # --------------------------------------------------------

    def _clean_returns(self, returns):
        """
        Remove missing and infinite observations.
        """

        clean = returns.copy()

        clean = clean.replace(
            [np.inf, -np.inf],
            np.nan
        )

        clean = clean.dropna()

        return clean

    # --------------------------------------------------------
    # Return Statistics
    # --------------------------------------------------------

    def cumulative_returns(self, returns):
        """
        Calculate cumulative wealth growth.
        """

        clean = self._clean_returns(returns)

        return (
            1 + clean
        ).cumprod()

    def cagr(self, returns):
        """
        Calculate compound annual growth rate.
        """

        clean = self._clean_returns(returns)

        if clean.empty:
            return np.nan

        cumulative = self.cumulative_returns(
            clean
        )

        years = (
            len(clean)
            / self.periods_per_year
        )

        if years <= 0:
            return np.nan

        ending_value = cumulative.iloc[-1]

        if ending_value <= 0:
            return np.nan

        return (
            ending_value ** (1 / years)
            - 1
        )

    def annual_return(self, returns):
        """
        Calculate geometric annualized return.

        Annual Return is defined consistently with CAGR
        throughout QuantLab.
        """

        return self.cagr(returns)

    def annual_volatility(self, returns):
        """
        Calculate annualized volatility.
        """

        clean = self._clean_returns(returns)

        if clean.empty:
            return np.nan

        return (
            clean.std()
            * np.sqrt(
                self.periods_per_year
            )
        )

    # --------------------------------------------------------
    # Risk-Adjusted Ratios
    # --------------------------------------------------------

    def sharpe_ratio(
        self,
        returns,
        risk_free_rate=0
    ):
        """
        Calculate Sharpe ratio using geometric
        annualized return.
        """

        annual_return = self.annual_return(
            returns
        )

        volatility = self.annual_volatility(
            returns
        )

        if (
            pd.isna(volatility)
            or volatility == 0
        ):
            return np.nan

        return (
            annual_return
            - risk_free_rate
        ) / volatility

    def sortino_ratio(
        self,
        returns,
        risk_free_rate=0
    ):
        """
        Calculate Sortino ratio.
        """

        clean = self._clean_returns(
            returns
        )

        downside = clean[
            clean < 0
        ]

        if downside.empty:
            return np.nan

        downside_vol = (
            downside.std()
            * np.sqrt(
                self.periods_per_year
            )
        )

        if (
            pd.isna(downside_vol)
            or downside_vol == 0
        ):
            return np.nan

        return (
            self.annual_return(clean)
            - risk_free_rate
        ) / downside_vol

    # --------------------------------------------------------
    # Drawdown
    # --------------------------------------------------------

    def drawdown_series(self, returns):
        """
        Calculate drawdown through time.
        """

        cumulative = self.cumulative_returns(
            returns
        )

        running_max = cumulative.cummax()

        drawdown = (
            cumulative
            / running_max
            - 1
        )

        return drawdown

    def max_drawdown(self, returns):
        """
        Calculate maximum drawdown.
        """

        drawdown = self.drawdown_series(
            returns
        )

        if drawdown.empty:
            return np.nan

        return drawdown.min()

    def calmar_ratio(self, returns):
        """
        Calculate Calmar ratio.
        """

        mdd = self.max_drawdown(
            returns
        )

        if (
            pd.isna(mdd)
            or mdd == 0
        ):
            return np.nan

        return (
            self.cagr(returns)
            / abs(mdd)
        )

    # --------------------------------------------------------
    # Distribution Statistics
    # --------------------------------------------------------

    def skewness(self, returns):
        """
        Calculate return skewness.
        """

        clean = self._clean_returns(
            returns
        )

        return clean.skew()

    def kurtosis(self, returns):
        """
        Calculate excess kurtosis.
        """

        clean = self._clean_returns(
            returns
        )

        return clean.kurtosis()

    def win_rate(self, returns):
        """
        Percentage of periods with positive returns.
        """

        clean = self._clean_returns(
            returns
        )

        if clean.empty:
            return np.nan

        return (
            clean > 0
        ).mean()

    def best_period(self, returns):
        """
        Best observed period return.
        """

        clean = self._clean_returns(
            returns
        )

        if clean.empty:
            return np.nan

        return clean.max()

    def worst_period(self, returns):
        """
        Worst observed period return.
        """

        clean = self._clean_returns(
            returns
        )

        if clean.empty:
            return np.nan

        return clean.min()

    # --------------------------------------------------------
    # Rolling Statistics
    # --------------------------------------------------------

    def rolling_volatility(
        self,
        returns,
        window=26
    ):
        """
        Calculate rolling annualized volatility.
        """

        clean = self._clean_returns(
            returns
        )

        return (
            clean
            .rolling(window)
            .std()
            * np.sqrt(
                self.periods_per_year
            )
        )

    def rolling_sharpe(
        self,
        returns,
        window=26
    ):
        """
        Calculate rolling Sharpe ratio.

        Rolling mean return is annualized arithmetically
        because each rolling window represents a local
        estimate of expected periodic return.
        """

        clean = self._clean_returns(
            returns
        )

        rolling_mean = (
            clean
            .rolling(window)
            .mean()
            * self.periods_per_year
        )

        rolling_vol = (
            clean
            .rolling(window)
            .std()
            * np.sqrt(
                self.periods_per_year
            )
        )

        rolling_sharpe = (
            rolling_mean
            / rolling_vol
        )

        return rolling_sharpe.replace(
            [np.inf, -np.inf],
            np.nan
        )

    # --------------------------------------------------------
    # Calendar Returns
    # --------------------------------------------------------

    def monthly_returns(self, returns):
        """
        Calculate calendar monthly returns.
        """

        cumulative = self.cumulative_returns(
            returns
        )

        return (
            cumulative
            .resample("M")
            .last()
            .pct_change()
        )

    def yearly_returns(self, returns):
        """
        Calculate calendar yearly returns.
        """

        cumulative = self.cumulative_returns(
            returns
        )

        return (
            cumulative
            .resample("Y")
            .last()
            .pct_change()
        )

    # --------------------------------------------------------
    # Individual Strategy Summary
    # --------------------------------------------------------

    def summary(self, returns):
        """
        Generate complete performance summary.
        """

        return pd.Series({

            "CAGR":
                self.cagr(returns),

            "Annual Return":
                self.annual_return(returns),

            "Annual Volatility":
                self.annual_volatility(returns),

            "Sharpe Ratio":
                self.sharpe_ratio(returns),

            "Sortino Ratio":
                self.sortino_ratio(returns),

            "Calmar Ratio":
                self.calmar_ratio(returns),

            "Maximum Drawdown":
                self.max_drawdown(returns),

            "Win Rate":
                self.win_rate(returns),

            "Best Week":
                self.best_period(returns),

            "Worst Week":
                self.worst_period(returns),

            "Skewness":
                self.skewness(returns),

            "Kurtosis":
                self.kurtosis(returns)

        })

    # --------------------------------------------------------
    # Multiple Strategy Summary
    # --------------------------------------------------------

    def compare_strategies(
        self,
        returns
    ):
        """
        Generate a performance table for multiple
        strategy return series.

        Parameters
        ----------
        returns : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        summaries = {}

        for column in returns.columns:

            summaries[column] = (
                self.summary(
                    returns[column]
                )
            )

        comparison = pd.DataFrame(
            summaries
        ).T

        comparison.index.name = (
            "Strategy"
        )

        return comparison

    # --------------------------------------------------------
    # Research Diagnostics
    # --------------------------------------------------------

    def diagnostics(
        self,
        returns
    ):
        """
        Generate quality-control diagnostics for
        a strategy return series.
        """

        clean = returns.replace(
            [np.inf, -np.inf],
            np.nan
        )

        diagnostics = pd.Series({

            "Observations":
                len(returns),

            "Valid Observations":
                clean.notna().sum(),

            "Missing Observations":
                clean.isna().sum(),

            "Zero Return Periods":
                (clean == 0).sum(),

            "Positive Periods":
                (clean > 0).sum(),

            "Negative Periods":
                (clean < 0).sum(),

            "Start Date":
                returns.index.min(),

            "End Date":
                returns.index.max()

        })

        return diagnostics

    # --------------------------------------------------------
    # Automated Research Report
    # --------------------------------------------------------

    def generate_research_report(
        self,
        returns,
        output_dir="../results",
        report_name="quantlab_research_report"
    ):
        """
        Generate and save core QuantLab research tables.

        Parameters
        ----------
        returns : pandas.Series or pandas.DataFrame
            Strategy return series.

        output_dir : str or Path
            Directory where report files are saved.

        report_name : str
            Prefix used for generated files.

        Returns
        -------
        dict
            Dictionary containing generated report tables.
        """

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # Single Strategy
        # ----------------------------------------------------

        if isinstance(
            returns,
            pd.Series
        ):

            strategy_name = (
                returns.name
                if returns.name is not None
                else "Strategy"
            )

            performance = (
                self.summary(
                    returns
                )
                .to_frame(
                    name=strategy_name
                )
                .T
            )

            diagnostics = (
                self.diagnostics(
                    returns
                )
                .to_frame(
                    name=strategy_name
                )
                .T
            )

            cumulative = (
                self.cumulative_returns(
                    returns
                )
                .to_frame(
                    name=strategy_name
                )
            )

            drawdown = (
                self.drawdown_series(
                    returns
                )
                .to_frame(
                    name=strategy_name
                )
            )

        # ----------------------------------------------------
        # Multiple Strategies
        # ----------------------------------------------------

        elif isinstance(
            returns,
            pd.DataFrame
        ):

            performance = (
                self.compare_strategies(
                    returns
                )
            )

            diagnostics = pd.DataFrame({

                column:
                    self.diagnostics(
                        returns[column]
                    )

                for column
                in returns.columns

            }).T

            diagnostics.index.name = (
                "Strategy"
            )

            cumulative = pd.DataFrame(
                index=returns.index
            )

            drawdown = pd.DataFrame(
                index=returns.index
            )

            for column in returns.columns:

                cumulative[column] = (
                    self.cumulative_returns(
                        returns[column]
                    )
                )

                drawdown[column] = (
                    self.drawdown_series(
                        returns[column]
                    )
                )

        else:

            raise TypeError(
                "returns must be a pandas Series "
                "or pandas DataFrame."
            )

        # ----------------------------------------------------
        # Save Outputs
        # ----------------------------------------------------

        performance.to_csv(
            output_dir
            / f"{report_name}_performance.csv"
        )

        diagnostics.to_csv(
            output_dir
            / f"{report_name}_diagnostics.csv"
        )

        cumulative.to_csv(
            output_dir
            / f"{report_name}_cumulative.csv"
        )

        drawdown.to_csv(
            output_dir
            / f"{report_name}_drawdown.csv"
        )

        # ----------------------------------------------------
        # Return Report Objects
        # ----------------------------------------------------

        return {

            "performance":
                performance,

            "diagnostics":
                diagnostics,

            "cumulative":
                cumulative,

            "drawdown":
                drawdown

        }