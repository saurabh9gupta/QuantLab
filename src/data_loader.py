import os

import pandas as pd
import yfinance as yf


class DataLoader:
    """
    Downloads and manages market data.
    """

    def __init__(self, universe_path, output_path):
        self.universe_path = universe_path
        self.output_path = output_path

    def load_universe(self):
        """
        Load investment universe.
        """
        return pd.read_csv(self.universe_path)

    def download_prices(
        self,
        start_date="2018-01-01",
        end_date=None,
    ):
        """
        Download daily adjusted close prices.
        """

        universe = self.load_universe()

        tickers = universe["Ticker"].tolist()

        print(f"Downloading {len(tickers)} stocks...")

        prices = yf.download(
            tickers=tickers,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False,
        )

        prices = prices["Close"]

        filepath = os.path.join(
            self.output_path,
            "daily_prices.csv"
        )

        prices.to_csv(filepath)

        print(f"Saved to {filepath}")

        return prices