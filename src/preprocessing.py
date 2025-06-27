import os
import re
from bs4 import BeautifulSoup

class Preprocessor:
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)

    def extract_between_items(self, raw_content: str, start_label: str, end_label: str, occurrence: int = 2) -> str:
        """
        Extracts content between the nth occurrence of start_label and the nth occurrence of end_label.
        If end_label occurrence comes before start_label or not found, returns empty string.
        """
        # Find all start positions
        start_iter = list(re.finditer(start_label, raw_content, flags=re.IGNORECASE))
        end_iter = list(re.finditer(end_label, raw_content, flags=re.IGNORECASE))
        if len(start_iter) < occurrence or len(end_iter) < occurrence:
            return ''
        start_pos = start_iter[occurrence-1].start()
        end_pos = end_iter[occurrence-1].start()
        if end_pos <= start_pos:
            return ''
        return raw_content[start_pos:end_pos]

    def clean_html(self, text: str) -> str:
        """
        Removes HTML tags and scripts/styles from the text using BeautifulSoup.
        """
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator=" ")

    def normalize_whitespace(self, text: str) -> str:
        """
        Collapses multiple whitespace characters into single spaces and trims.
        """
        return re.sub(r"\s+", " ", text).strip()

    def preprocess_file(self, filename: str) -> None:
        raw_path = os.path.join(self.raw_dir, filename)
        with open(raw_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()

        # Extract between 2nd occurrence of Item 1. and 2nd occurrence of Item 8.
        extracted = self.extract_between_items(raw_content,
                                              r'Item\s+1\.',
                                              r'Item\s+8\.',
                                              occurrence=2)
        if not extracted:
            print(f"[!] Occurrences not found or invalid order in {filename}, skipping.")
            return

        # Clean and normalize
        clean = self.clean_html(extracted)
        clean = self.normalize_whitespace(clean)

        # Extract specific items
        item_1 = self.extract_between_items(clean, r'Item\s+1\.', r'Item\s+1a\.', 1)
        item_1a = self.extract_between_items(clean, r'Item\s+1a\.', r'Item\s+1b\.', 1)
        item_7 = self.extract_between_items(clean, r'Item\s+7\.', r'Item\s+7a\.', 1)

        final_text = f"{item_1}\n\n{item_1a}\n\n{item_7}"

        # Save with original basename and .txt extension
        base = os.path.splitext(filename)[0]
        out_name = f"{base}.txt"
        processed_path = os.path.join(self.processed_dir, out_name)
        with open(processed_path, 'w', encoding='utf-8') as out:
            out.write(final_text)
        print(f"[✓] Preprocessed: {processed_path}")

    def batch_preprocess(self):
        """
        Preprocess all .txt or .htm files in the raw directory.
        """
        for fname in os.listdir(self.raw_dir):
            if fname.lower().endswith(('.txt', '.htm')):
                print(f"Preprocessing {fname}")
                self.preprocess_file(fname)

if __name__ == "__main__":
    pre = Preprocessor()
    pre.batch_preprocess()