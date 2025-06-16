import pandas as pd
import os
import requests
import time
import re
from bs4 import BeautifulSoup
from typing import List

HEADERS = {
    "User-Agent": "Yann Merakeb yann.merakeb@dauphine.eu"
}

class DataLoader:
    def __init__(self, save_dir: str = "../data/raw", delay: float = 0.5):
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

    def get_10k_filings(self, cik: str, count: int = 5) -> List[str]:
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

        return filings

    def download_filing(self, cik: str, accession_number: str, filename: str):
        """
        Downloads the complete 10-K document from SEC archives.
        """
        # Format the accession number if needed (remove hyphens if they exist)
        clean_accession = accession_number.replace('-', '')

        # Build the URL to access the complete file (.txt format)
        txt_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_accession}/{accession_number}.txt"

        try:
            # Download the complete document
            response = requests.get(txt_url, headers=HEADERS)
            response.raise_for_status()

            # Save the document
            with open(os.path.join(self.save_dir, filename), "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"[✓] Downloaded: {filename}")
        except requests.exceptions.HTTPError as e:
            # If it fails, try an alternative URL format
            try:
                # Alternative format with hyphens in the accession
                formatted_accession = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
                alt_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_accession}/{formatted_accession}.txt"
                response = requests.get(alt_url, headers=HEADERS)
                response.raise_for_status()

                with open(os.path.join(self.save_dir, filename), "w", encoding="utf-8") as f:
                    f.write(response.text)

                print(f"[✓] Downloaded: {filename} (alternative URL)")
            except requests.exceptions.HTTPError:
                print(f"[!] Download failed: {filename} - {str(e)}")

        # Respect SEC API rate limit
        time.sleep(self.delay)

    def fetch_10k_filings(self, ticker: str, count: int = 5):
        """
        High-level method to fetch and save the latest 10-K filings for a given ticker.
        """
        cik = self.get_cik(ticker)
        print(f"[+] Ticker: {ticker.upper()} → CIK: {cik}")

        accession_numbers = self.get_10k_filings(cik, count)
        print(f"[+] Found {len(accession_numbers)} 10-K filings")

        for i, accession in enumerate(accession_numbers):
            year = f"20{accession.split('-')[1]}"
            fname = f"{ticker}_10K_{year}.txt"
            self.download_filing(cik, accession, fname)

if __name__ == "__main__":
    client = DataLoader()
    client.fetch_10k_filings("AAPL", count=20)