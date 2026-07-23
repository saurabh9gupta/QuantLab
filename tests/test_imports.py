"""
Smoke tests for the QuantLab package.

These tests verify that the core research modules can be imported
successfully in a clean Python environment.
"""


def test_core_imports():

    from src.backtester import Backtester
    from src.data_preparation import DataPreparation
    from src.factor import FactorAttribution
    from src.multi_strategy import MultiStrategyEngine
    from src.optimizer import ParameterOptimizer
    from src.performance import PerformanceAnalytics
    from src.pipeline import ResearchPipeline
    from src.portfolio.constructor import PortfolioConstructor
    from src.portfolio_risk import PortfolioRiskManager
    from src.report import PerformanceReport
    from src.returns import ReturnCalculator
    from src.risk import RiskAnalytics
    from src.signals import SignalGenerator
    from src.transaction_costs import TransactionCostModel
    from src.walk_forward import WalkForwardOptimizer

    assert Backtester is not None
    assert DataPreparation is not None
    assert FactorAttribution is not None
    assert MultiStrategyEngine is not None
    assert ParameterOptimizer is not None
    assert PerformanceAnalytics is not None
    assert ResearchPipeline is not None
    assert PortfolioConstructor is not None
    assert PortfolioRiskManager is not None
    assert PerformanceReport is not None
    assert ReturnCalculator is not None
    assert RiskAnalytics is not None
    assert SignalGenerator is not None
    assert TransactionCostModel is not None
    assert WalkForwardOptimizer is not None