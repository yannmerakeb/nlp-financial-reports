import os
import re
from bs4 import BeautifulSoup

class Preprocessor:
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(processed_dir, exist_ok=True)

    def extract_text(self, raw_content: str) -> str:
        """
        Extracts the first meaningful <TEXT> section from the full 10-K file.
        """
        matches = re.findall(r'<TEXT>(.*?)</TEXT>', raw_content, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0]
        return ""

    def clean_text(self, text: str) -> str:
        """
        Applies basic cleaning to the raw extracted text:
        - Removes HTML tags
        - Normalizes spaces
        - Lowercases everything
        """
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text()
        plain_text = re.sub(r'\s+', ' ', plain_text)  # Normalize whitespace
        return plain_text.strip().lower()

    def preprocess_file(self, filename: str):
        """
        Process a single file from raw → processed.
        """
        raw_path = os.path.join(self.raw_dir, filename)
        processed_path = os.path.join(self.processed_dir, filename)

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        extracted = self.extract_text(raw_content)
        cleaned = self.clean_text(extracted)

        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"[✓] Preprocessed: {filename}")

    def batch_preprocess(self):
        """
        Preprocesses all raw files and saves cleaned versions.
        """
        for fname in os.listdir(self.raw_dir):
            if fname.endswith(".txt"):
                self.preprocess_file(fname)


if __name__ == "__main__":
    pre = Preprocessor()
    pre.batch_preprocess()
