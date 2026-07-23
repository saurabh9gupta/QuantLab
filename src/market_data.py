import pandas as pd


class MarketData:

    def __init__(self, frequency="W-FRI"):
        self.frequency = frequency

    def weekly_prices(self, prices):

        return (
            prices
            .resample(self.frequency)
            .last()
            .dropna(how="all")
        )

    def weekly_returns(self, prices):

        weekly = self.weekly_prices(prices)

        return weekly.pct_change()