

"""
Module for linguistic feature engineering on financial report texts.
"""
import os
import re
import pandas as pd
import numpy as np
import textstat
import spacy

from collections import Counter


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INPUT_FILE  = os.path.join(project_root, "data", "processed", "reports_with_market.parquet")
DEFAULT_OUTPUT_FILE = os.path.join(project_root, "data", "processed", "reports_features.parquet")


class FeatureEngineer:
    """
    Extracts linguistic features from report sections and saves enriched DataFrame.

    :param input_file: Path to Parquet with columns ['item1', 'item1a', 'item7', 'abnormal7d', ...]
    :param output_file: Path to write final Parquet with features appended
    """
    def __init__(self,
                 input_file: str = DEFAULT_INPUT_FILE,
                 output_file: str = DEFAULT_OUTPUT_FILE):
        self.input_file = input_file
        self.output_file = output_file
        # Load SpaCy English model (or French 'fr_core_news_sm' if necessary)
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
        # Define hedge words list
        self.hedge_words = set([w.lower() for w in [
            'may','might','could','possible','unlikely','probable',
            'estimate','expect','believe','anticipate','intend'
        ]])

    def _hedge_ratio(self, text: str) -> float:
        """
        Proportion of hedge words in the text.
        """
        tokens = [m.group(0).lower() for m in re.finditer(r"\w+", text)]
        if not tokens:
            return 0.0
        return sum(1 for w in tokens if w in self.hedge_words) / len(tokens)

    def _fog_index(self, text: str) -> float:
        """
        Gunning Fog readability index.
        """
        try:
            return textstat.gunning_fog(text)
        except Exception:
            return np.nan

    def _passive_ratio(self, text: str) -> float:
        """
        Ratio of passive constructions ("by" + past participle) to sentences.
        """
        doc = self.nlp(text)
        sentences = list(doc.sents)
        if not sentences:
            return 0.0
        passive = 0
        for sent in sentences:
            for token in sent:
                if token.dep_ == 'agent' and token.text.lower() == 'by':
                    passive += 1
                    break
        return passive / len(sentences)

    def _lexical_diversity(self, text: str) -> float:
        """
        Type-Token Ratio (unique tokens / total tokens).
        """
        tokens = [m.group(0).lower() for m in re.finditer(r"\w+", text)]
        if not tokens:
            return 0.0
        return len(set(tokens)) / len(tokens)

    def transform(self) -> pd.DataFrame:
        """
        Loads input, computes features, and returns enriched DataFrame.
        """
        df = pd.read_parquet(self.input_file)
        # Prepare columns
        features = []
        for _, row in df.iterrows():
            # Choose section for features (e.g., item1a Risk Factors)
            text = row.get('item1a', '') or row.get('item1', '') + ' ' + row.get('item7', '')
            hedge = self._hedge_ratio(text)
            fog   = self._fog_index(text)
            passive = self._passive_ratio(text)
            lexdiv = self._lexical_diversity(text)
            features.append({
                'hedge_ratio': hedge,
                'fog_index': fog,
                'passive_ratio': passive,
                'lexical_diversity': lexdiv
            })
        feat_df = pd.DataFrame(features, index=df.index)
        result = pd.concat([df, feat_df], axis=1)
        return result

    def save(self) -> None:
        """
        Computes features and saves to output file.
        """
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df_feats = self.transform()
        df_feats.to_parquet(self.output_file, index=False)
        print(f"Saved features to {self.output_file}")


