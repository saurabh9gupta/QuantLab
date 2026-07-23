import pandas as pd


class DataPreparation:
    """
    Data preparation pipeline for QuantLab.
    """

    def __init__(self, universe):
        self.universe = universe

    def prepare_price_matrix(self, df):
        """
        Convert raw stock data into a price matrix.
        """

        data = df.copy()

        data["Date"] = pd.to_datetime(data["Date"])

        data = data[data["Ticker"].isin(self.universe)]

        prices = data.pivot(
            index="Date",
            columns="Ticker",
            values="Adj Close"
        )

        prices = prices.sort_index()

        return prices

    def validate_price_matrix(self, prices):
        """
        Validate prepared price matrix.
        """

        print("=" * 60)
        print("PRICE MATRIX VALIDATION")
        print("=" * 60)

        print(f"Rows          : {prices.shape[0]}")
        print(f"Columns       : {prices.shape[1]}")
        print(f"Start Date    : {prices.index.min().date()}")
        print(f"End Date      : {prices.index.max().date()}")

        print("\nMissing Values")
        print(prices.isna().sum())

        print("\nDuplicate Dates")
        print(prices.index.duplicated().sum())

        print("\nData Types")
        print(prices.dtypes)

    def handle_missing_values(
        self,
        prices,
        method="ffill"
    ):
        """
        Handle missing values.

        Parameters
        ----------
        method

        ffill : forward fill only

        drop : forward fill then remove remaining NaNs
        """

        cleaned = prices.copy()

        cleaned = cleaned.sort_index()

        if method == "ffill":

            cleaned = cleaned.ffill()

            return cleaned

        elif method == "drop":

            cleaned = cleaned.ffill()

            cleaned = cleaned.dropna()

            return cleaned

        else:

            raise ValueError(
                "method must be 'ffill' or 'drop'"
            )

    def save_dataset(
        self,
        prices,
        output_path
    ):
        """
        Save processed dataset.
        """

        prices.to_csv(output_path)

        print(f"\nDataset saved to:\n{output_path}")