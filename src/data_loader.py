import pandas as pd
import os
import requests
import time
from typing import List

HEADERS = {
    "User-Agent": "Yann Merakeb yann.merakeb@dauphine.eu"
}

class DataLoader:
    def __init__(self, save_dir: str = "../data/raw", delay: float = 0.5):
        """
        Initializes the DataLoader with a directory to save files and a delay for rate limiting.
        """
        self.save_dir = save_dir
        self.delay = delay
        os.makedirs(save_dir, exist_ok=True)

    def get_cik(self, ticker: str) -> str:
        """
        Returns the full 10-digit CIK for a given stock ticker.
        """
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        for entry in data.values():
            if entry["ticker"].lower() == ticker.lower():
                return str(entry["cik_str"]).zfill(10)

        raise ValueError(f"CIK not found for ticker: {ticker}")

    def get_10k_filings(self, cik: str, count: int = 5) -> (List[str], List[str]):
        """
        Fetches URLs of the most recent 10-K filings for a given CIK.
        """
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(submissions_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # Filter on 10-K filings
        recent_data = pd.DataFrame(data["filings"]["recent"])
        recent_data = recent_data[recent_data["form"] == '10-K']
        # filings = list(recent_data['accessionNumber'].head(count).str.replace('-', ''))
        filings = list(recent_data['accessionNumber'].head(count))

        # Extract years from reportDate
        years = recent_data['reportDate'].head(count).str[:4].tolist()

        return filings, years

    def download_filing(self, cik: str, accession_number: str, filename: str):
        """
        Downloads the complete 10-K document from SEC archives.
        """
        # Format the accession number if needed (remove hyphens if they exist)
        clean_accession = accession_number.replace('-', '')

        # Build the URL to access the complete file (.txt format)
        txt_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_accession}/{accession_number}.txt"

        # Download the complete document
        response = requests.get(txt_url, headers=HEADERS)
        response.raise_for_status()

        # Save the document
        with open(os.path.join(self.save_dir, filename), "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"[✓] Downloaded: {filename}")

        # Respect SEC API rate limit
        time.sleep(self.delay)

    def fetch_10k_filings(self, ticker: str, count: int = 5):
        """
        High-level method to fetch and save the latest 10-K filings for a given ticker.
        """
        cik = self.get_cik(ticker)
        print(f"[+] Ticker: {ticker.upper()} → CIK: {cik}")

        accession_numbers, years = self.get_10k_filings(cik, count)
        print(f"[+] Found {len(accession_numbers)} 10-K filings")

        for accession, year in zip(accession_numbers, years):
            # year = f"20{accession.split('-')[1]}"
            fname = f"{ticker}_10K_{year}.txt"
            self.download_filing(cik, accession, fname)

if __name__ == "__main__":
    client = DataLoader()

    # Download 10-K filings over 5 years for a list of tickers
    #tickers = ["AAPL", "TSLA", "JPM", "CVX", "KO", "AMC", "GME", "PLTR", "MSFT", "JNJ"]
    tickers = ["AAPL", "TSLA"]
    for ticker in tickers:
        client.fetch_10k_filings(ticker, count=3)