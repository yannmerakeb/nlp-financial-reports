'''import os
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
        Cleans extracted 10-K text:
        - Removes HTML tags
        - Normalizes whitespace
        - Fixes common token merging issues
        - Lowercases everything
        - Normalizes section headers
        """
        # Remove HTML tags
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text()

        # Normalize whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text)

        # Fix merged words: lowercase-uppercase, digits-letters
        plain_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', plain_text)
        plain_text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', plain_text)
        plain_text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', plain_text)

        # Normalize section headers (e.g., item 1.business → item 1 business)
        plain_text = re.sub(r'(item\s*\d+[a-z]?)\.(?=\w)', r'\1 ', plain_text, flags=re.IGNORECASE)

        return plain_text.strip().lower()

    def remove_xbrl_noise(self, text: str) -> str:
        """
        Removes structural and XBRL-specific noise:
        - URLs, long alphanumeric strings, dates, CIKs, XBRL tags, durations
        """
        # Insert space between glued tokens (e.g. noncurrenthttp)
        text = re.sub(r'([a-z])(?=http)', r'\1 ', text)

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', ' ', text)

        # Remove XBRL tags (e.g., us-gaap:something, tsla:something)
        text = re.sub(r'\b[a-z]{2,10}:[a-zA-Z0-9_\-\.]+\b', ' ', text)

        # Remove long IDs and CIKs
        text = re.sub(r'\b\d{8,12}\b', ' ', text)

        # Remove dates
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', ' ', text)

        # Remove durations (e.g., fy2020, p10y, p6m)
        text = re.sub(r'\bfy\d{2,4}\b', ' ', text)
        text = re.sub(r'\bp\d+y\b', ' ', text)
        text = re.sub(r'\bp\d+m\b', ' ', text)
        text = re.sub(r'\bp\d+y\d+m?\d*d?\b', ' ', text)

        # Remove footnote symbols (†, *, ‡, etc.)
        text = re.sub(r'[†‡*]+', ' ', text)

        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def preprocess_file(self, filename: str):
        """
        Process a single file: extract, clean, remove noise, save.
        """
        raw_path = os.path.join(self.raw_dir, filename)
        processed_path = os.path.join(self.processed_dir, filename)

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        extracted = self.extract_text(raw_content)
        cleaned = self.clean_text(extracted)
        cleaned = self.remove_xbrl_noise(cleaned)

        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"[✓] Preprocessed: {filename}")

    def batch_preprocess(self):
        """
        Preprocess all .txt files in the raw directory.
        """
        for fname in os.listdir(self.raw_dir):
            if fname.endswith(".txt") or fname.endswith(".htm"):
                self.preprocess_file(fname)'''

import os
import re
from typing import Dict
from bs4 import BeautifulSoup

class Preprocessor:
    def __init__(self, raw_dir: str = "../data/raw", processed_dir: str = "../data/processed"):
        """Initialize the Preprocessor with directories for raw and processed data."""
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(processed_dir, exist_ok=True)

    def extract_text(self, raw_content: str) -> str:
        """
        Extracts the first meaningful <TEXT> section from the full 10-K file.
        """
        matches = re.findall(r'<TEXT>(.*?)</TEXT>', raw_content, re.DOTALL | re.IGNORECASE)
        if matches:
            text = matches[0].strip()
            if len(text) < 1000:  # Ensure substantial content
                print(f"Warning: Extracted text is too short ({len(text)} chars)")
            return text
        print("Error: No <TEXT> section found")
        return ""

    def clean_text(self, text: str) -> str:
        """
        Cleans extracted 10-K section text:
        - Removes HTML/XBRL tags
        - Normalizes whitespace
        - Fixes token merging issues (e.g., camelCase, digits-letters)
        - Lowercases everything
        - Normalizes section headers
        """
        # Remove HTML/XBRL tags
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text(separator=" ")

        # Normalize whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text)

        # Fix merged words: lowercase-uppercase, digits-letters
        plain_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', plain_text)
        plain_text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', plain_text)
        plain_text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', plain_text)

        # Normalize section headers (e.g., item 1.business → item 1 business)
        plain_text = re.sub(r'(item\s*\d+[a-z]?)\.(?=\w)', r'\1 ', plain_text, flags=re.IGNORECASE)

        return plain_text.strip().lower()

    def remove_xbrl_noise(self, text: str) -> str:
        """
        Removes structural and XBRL-specific noise from cleaned text:
        - URLs, long alphanumeric strings, dates, CIKs, XBRL tags, durations
        - Preserves narrative text and contextual numbers (e.g., 5.2%)
        """
        # Insert space before URLs
        text = re.sub(r'([a-z])(?=http)', r'\1 ', text)

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', ' ', text)

        # Remove XBRL tags (e.g., us-gaap:something, aapl:something)
        text = re.sub(r'\b[a-z]{2,10}:[a-z0-9_\-\.]+\b', ' ', text, flags=re.IGNORECASE)

        # Remove long IDs and CIKs
        text = re.sub(r'\b\d{8,12}\b', ' ', text)

        # Remove dates
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b|\b\d{2}-\d{2}-\d{4}\b', ' ', text)

        # Remove durations (e.g., fy2020, p10y, p6m)
        text = re.sub(r'\bfy\d{2,4}\b|\bp\d+[ymdw]\b|\bp\d+y\d+m?\d*d?\b', ' ', text, flags=re.IGNORECASE)

        # Remove footnote symbols
        text = re.sub(r'[†‡*©®]+', ' ', text)

        # Remove isolated table numbers (e.g., '4.1' but keep '5.2%')
        text = re.sub(r'\b\d+\.\d+\b(?!\s*%)', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extracts raw text for Item 1 (Business), Item 1A (Risk Factors), and Item 7 (MD&A).
        Uses the last occurrence of headers 'Item 1.', 'Item 1A.', and 'Item 7.' to capture content.
        Returns a dictionary with section names and their raw content, in document order.
        """
        sections = {}
        # Define section headers and their next likely delimiters
        section_patterns = [
            ('item_1_business', r'Item 1\.', r'Item 1[AB]\.|Item 2\.'),
            ('item_1a_risk_factors', r'Item 1A\.', r'Item [1B2]\.|Item 3\.'),
            ('item_7_mda', r'Item 7\.', r'Item 7A\.|Item 8\.')
        ]

        for section_name, start_pattern, end_pattern in section_patterns:
            # Find all occurrences of the start header
            start_matches = [(m.start(), m.group()) for m in re.finditer(start_pattern, text)]
            if not start_matches:
                print(f"Warning: No header found for {section_name}")
                continue

            # Use the last occurrence
            start_pos = start_matches[-1][0]

            # Find the next section header (end delimiter)
            end_match = re.search(end_pattern, text[start_pos + len(start_matches[-1][1]):], re.DOTALL | re.IGNORECASE)
            end_pos = (end_match.start() + start_pos + len(start_matches[-1][1])) if end_match else len(text)

            # Extract raw section content
            content = text[start_pos:end_pos].strip()

            # Remove the header itself from the content
            content = re.sub(start_pattern, '', content, count=1).strip()

            # Validate content length to avoid artifacts
            if len(content) > 100:
                sections[section_name] = content
            else:
                print(f"Warning: Section {section_name} too short ({len(content)} chars)")

        return sections

    def preprocess_file(self, filename: str):
        """
        Process a single file: extract raw sections, clean, remove noise, save in one file.
        Outputs a single .txt file with cleaned Item 1, Item 1A, and Item 7 in order, separated by headers.
        """
        raw_path = os.path.join(self.raw_dir, filename)
        processed_path = os.path.join(self.processed_dir, filename)

        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except UnicodeDecodeError:
            print(f"Error: Failed to decode {filename}")
            return

        extracted = self.extract_text(raw_content)
        if not extracted:
            print(f"Failed preprocessing for {filename}")
            return

        # Extract raw sections
        sections = self.extract_sections(extracted)
        if not sections:
            print(f"Error: No sections extracted for {filename}")
            return

        # Clean each section
        output_content = ""
        section_order = ['item_1_business', 'item_1a_risk_factors', 'item_7_mda']
        for section_name in section_order:
            if section_name in sections:
                cleaned = self.clean_text(sections[section_name])
                cleaned = self.remove_xbrl_noise(cleaned)
                if len(cleaned) > 100:  # Ensure cleaned section is substantial
                    output_content += f"--- {section_name.upper()} ---\n{cleaned}\n\n"
                else:
                    print(f"Warning: Cleaned section {section_name} too short ({len(cleaned)} chars)")

        if not output_content:
            print(f"Error: No cleaned sections for {filename}")
            return

        # Save combined cleaned sections to a single file
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(output_content.strip())
        print(f"[✓] Preprocessed: {processed_path}")

    def batch_preprocess(self):
        """
        Preprocess all .txt or .htm files in the raw directory.
        """
        for fname in os.listdir(self.raw_dir):
            if fname.endswith((".txt", ".htm")):
                print(f"Preprocessing {fname}")
                self.preprocess_file(fname)


if __name__ == "__main__":
    pre = Preprocessor()
    pre.batch_preprocess()