
"""
Module for fetching market data and computing abnormal returns using yfinance with robust fallback.
"""
import os
import yfinance as yf
import pandas as pd
import numpy as np
import traceback

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_PROCESSED_DIR        = os.path.join(project_root, "data", "processed")
DEFAULT_REPORTS_FILE         = os.path.join(DEFAULT_PROCESSED_DIR, "reports.parquet")
DEFAULT_ENRICHED_REPORTS_FILE = os.path.join(DEFAULT_PROCESSED_DIR, "reports_with_market.parquet")

class MarketDataFetcher:
    """
    Retrieves historical price data and computes abnormal returns.
    Uses yfinance download; fallback to Ticker.history if needed.
    """
    def __init__(self, output_file: str = DEFAULT_ENRICHED_REPORTS_FILE):
        """
        :param output_file: Path to save the dataset enriched with market returns
        """
        self.output_file = output_file

    def _download_prices(self, ticker: str, start: str, end: str) -> pd.Series:
        """
        Downloads adjusted close prices for a given ticker and date range.
        Tries yfinance download first, then yfinance Ticker.history if result is empty or fails.
        """
        if isinstance(ticker, (list, tuple)):
            ticker = ticker[0]
        ticker = str(ticker).strip().upper()

        # Primary method: yfinance.download
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, threads=False)
            if df.empty:
                raise ValueError("Empty DataFrame from yfinance.download")
            print(f"[yfinance.download] Downloaded {ticker}: {df.shape}")
        except Exception as e:
            print(f"[!] yfinance.download failed for {ticker}: {e}\nFalling back to Ticker.history()")
            traceback.print_exc()
            try:
                tk = yf.Ticker(ticker)
                df = tk.history(start=start, end=end)
                if df.empty:
                    raise ValueError("Empty DataFrame from Ticker.history()")
                print(f"[yfinance.Ticker.history] Downloaded {ticker}: {df.shape}")
            except Exception as e2:
                print(f"[!] Ticker.history fallback failed for {ticker}: {e2}")
                traceback.print_exc()
                # Return empty Series
                return pd.Series(dtype=float)
        return df["Adj Close"].rename(ticker)

    def abnormal_return(self, prices: pd.Series, window: int = 7) -> float:
        """
        Computes simple return over a forward window.
        :param prices: Series of prices (at least window+1 long)
        :param window: Number of trading days to compute return
        :return: Return over the window, or np.nan if insufficient data
        """
        if len(prices) >= window + 1:
            return (prices.iloc[window] - prices.iloc[0]) / prices.iloc[0]
        return np.nan

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds abnormal return column to the filings DataFrame.
        Expects df columns: ticker, year
        """
        returns = []
        for _, row in df.iterrows():
            yr = row["year"]
            raw_t = row["ticker"]
            if isinstance(raw_t, (list, tuple)):
                raw_t = raw_t[0]
            ticker = str(raw_t).strip().upper()

            start = f"{yr}-01-01"
            end   = f"{yr}-12-31"
            prices = self._download_prices(ticker, start, end)
            ar = self.abnormal_return(prices)
            returns.append(ar)

        # Assemble enriched DataFrame
        df = df.copy()
        df["abnormal7d"] = returns
        return df

    def save(self, df: pd.DataFrame) -> None:
        """
        Saves the enriched DataFrame to the output Parquet file.
        """
        df.to_parquet(self.output_file, index=False)
        print(f"Market data enriched dataset saved to: {self.output_file}")

import os
import pandas as pd
import numpy as np


class LocalMarketDataLoader:
    """
    Loads price data from pre-downloaded CSV files to compute abnormal returns.
    """
    def __init__(self, price_file_paths: dict[str, str],
                 output_file: str = DEFAULT_ENRICHED_REPORTS_FILE):
        self.price_file_paths = price_file_paths
        self.output_file = output_file

    def _load_prices(self, ticker: str, start: str, end: str) -> pd.Series:
        """
        Loads adjusted close prices for a given ticker and date range from a local CSV.
        """

        ticker = str(ticker).strip().upper()
        # Verify mapping
        if ticker not in self.price_file_paths:
            raise ValueError(f"No local CSV provided for ticker '{ticker}'")
        file_path = self.price_file_paths[ticker]

        # Read CSV
        # Read CSV with semicolon delimiter and parse Date
        df = pd.read_csv(file_path, sep=';', parse_dates=['Date'], dayfirst=True)
        # The second column should be the ticker
        if len(df.columns) < 2:
            raise ValueError(f"CSV for '{ticker}' must have at least two columns: 'Date' and '{ticker}'")
        price_col = df.columns[1]
        if price_col != ticker:
            # Rename if header is not exactly ticker
            df = df.rename(columns={price_col: ticker})
        df = df.set_index('Date').sort_index()

        # Slice the date range
        try:
            series = df.loc[start:end, ticker]
        except KeyError:
            raise ValueError(f"Date range {start} to {end} not found in CSV for '{ticker}'")
        if series.empty:
            raise ValueError(f"No price data for '{ticker}' between {start} and {end}")
        return series

    def abnormal_return(self, prices: pd.Series, window: int = 7) -> float:
        """
        Computes simple forward return over a window of trading days.
        """

        if len(prices) >= window + 1:
            return (prices.iloc[window] - prices.iloc[0]) / prices.iloc[0]
        return np.nan

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches a filings DataFrame with 'abnormal7d' returns.
        """
        results = []
        for _, row in df.iterrows():
            ticker = str(row['ticker']).strip().upper()
            year = int(row['year'])
            start = f"{year}-01-01"
            end   = f"{year}-12-31"
            try:
                prices = self._load_prices(ticker, start, end)
                ar = self.abnormal_return(prices)
            except Exception as e:
                print(f"[!] Error for {ticker}: {e}")
                ar = np.nan
            results.append(ar)
        df_copy = df.copy()
        df_copy['abnormal7d'] = results
        return df_copy

    def save(self, df: pd.DataFrame) -> None:
        """
        Saves the enriched DataFrame to a Parquet file.
        """
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df.to_parquet(self.output_file, index=False)
        print(f"[✓] Saved enriched data to {self.output_file}")


if __name__ == "__main__":

    price_files = {
        "AAPL": "C:/Users/theod/OneDrive/Bureau/Theo/Master IEF Dauphine/S2/NLP/data/AAPL.csv",
        "MSFT": "C:/Users/theod/OneDrive/Bureau/Theo/Master IEF Dauphine/S2/NLP/data/MSFT.csv",
        "TSLA": "C:/Users/theod/OneDrive/Bureau/Theo/Master IEF Dauphine/S2/NLP/data/TSLA.csv",
    }

    loader = LocalMarketDataLoader(price_files)
    reports = pd.read_parquet("data/processed/reports.parquet")
    enriched = loader.enrich(reports)
    loader.save(enriched)