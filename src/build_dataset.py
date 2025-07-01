"""
Module for building the main dataset from preprocessed filings.
"""
import os
import glob
import pandas as pd


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_PROCESSED_DIR = os.path.join(project_root, "data", "processed")
DEFAULT_OUTPUT_FILE  = os.path.join(DEFAULT_PROCESSED_DIR, "reports.parquet")

class DatasetBuilder:
    """
    Gathers processed filings into a single DataFrame and saves as Parquet.
    """
    def __init__(self, processed_dir: str = DEFAULT_PROCESSED_DIR, output_file: str = DEFAULT_OUTPUT_FILE):
        self.processed_dir = processed_dir
        self.output_file = output_file

    def _gather_files(self) -> list[str]:
        """
        Finds all .txt files in the processed directory.
        """
        pattern = os.path.join(self.processed_dir, "*.txt")
        return glob.glob(pattern)

    def _parse_filename(self, filename: str) -> tuple[str, int]:
        """
        Extracts ticker and year from filename 'TICKER_10K_YEAR.txt'.
        """
        base = os.path.splitext(os.path.basename(filename))[0]
        parts = base.split("_")
        ticker = parts[0]
        year = int(parts[-1])
        return ticker, year

    def build(self) -> pd.DataFrame:
        """
        Reads all processed text files, splits into sections, and returns a DataFrame.
        Columns: filing_id, ticker, year, item1, item1a, item7
        """
        records = []
        for path in self._gather_files():
            content = open(path, encoding="utf-8").read().strip()
            ticker, year = self._parse_filename(path)
            filing_id = os.path.splitext(os.path.basename(path))[0]

            # Expect sections separated by double newline
            try:
                item1, item1a, item7 = content.split("\n\n")
            except ValueError:
                # If splitting fails, treat entire content as one field
                item1, item1a, item7 = content, "", ""

            records.append({
                "filing_id": filing_id,
                "ticker": ticker,
                "year": year,
                "item1": item1,
                "item1a": item1a,
                "item7": item7,
            })
        df = pd.DataFrame(records)
        return df

    def save(self) -> None:
        """
        Builds the dataset and writes it to the output Parquet file.
        """
        df = self.build()
        print(df)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df.to_parquet(self.output_file, index=False)
        print(f"Dataset saved to: {self.output_file}")


if __name__ == "__main__":
    builder = DatasetBuilder()
    builder.save()