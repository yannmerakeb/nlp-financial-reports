### src/vectorization.py

"""
Module for text vectorization and feature generation in preparation for SVM and embedding-based models.
"""
import os
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class TfidfFeatureExtractor:
    """
    Generates TF-IDF features for documents and optionally reduces dimensionality via PCA.

    :param max_features: maximum number of TF-IDF features (vocabulary size)
    :param pca_components: if >0, number of PCA components to reduce TF-IDF vectors to
    :param output_file: path to save the feature matrix as Parquet
    """
    def __init__(self,
                 max_features: int = 10000,
                 pca_components: int = 0,
                 output_file: str = "data/processed/tfidf_features.parquet"):
        self.max_features = max_features
        self.pca_components = pca_components
        self.output_file = output_file
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            lowercase=True,
            stop_words='english',
            ngram_range=(1,2)
        )
        if self.pca_components > 0:
            self.pca = PCA(n_components=self.pca_components, random_state=42)
        else:
            self.pca = None

    def fit_transform(self, texts: pd.Series) -> pd.DataFrame:
        """
        Fits the TF-IDF vectorizer on provided texts and returns a DataFrame of features.
        """
        tfidf_matrix = self.vectorizer.fit_transform(texts.fillna(''))
        features = tfidf_matrix.toarray()
        df_feat = pd.DataFrame(
            features,
            index=texts.index,
            columns=self.vectorizer.get_feature_names_out()
        )
        if self.pca:
            pca_scores = self.pca.fit_transform(df_feat)
            cols = [f'pca_{i+1}' for i in range(self.pca_components)]
            df_feat = pd.DataFrame(pca_scores, index=texts.index, columns=cols)
        return df_feat

    def save(self, df_feat: pd.DataFrame) -> None:
        """
        Saves the TF-IDF (or PCA-reduced) features to Parquet.
        """
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df_feat.to_parquet(self.output_file, index=True)
        print(f"[✓] Saved TF-IDF features to {self.output_file}")

class EmbeddingFeatureExtractor:
    """
    Generates fixed-size sentence embeddings using a pre-trained model.
    Falls back to average word embeddings if SentenceTransformer unavailable.
    """
    def __init__(self,
                 model_name: str = 'all-MiniLM-L6-v2',
                 output_file: str = 'data/processed/embedding_features.parquet'):
        self.model_name = model_name
        self.output_file = output_file
        if SentenceTransformer:
            self.model = SentenceTransformer(self.model_name)
        else:
            raise ImportError(
                'sentence-transformers not installed; please pip install sentence-transformers'
            )

    def transform(self, texts: pd.Series) -> pd.DataFrame:
        """
        Encodes each text into a fixed-size embedding vector.
        """
        embeddings = self.model.encode(
            texts.fillna('').tolist(),
            convert_to_numpy=True,
            show_progress_bar=True
        )
        cols = [f'emb_{i+1}' for i in range(embeddings.shape[1])]
        df_embed = pd.DataFrame(embeddings, index=texts.index, columns=cols)
        return df_embed

    def save(self, df_embed: pd.DataFrame) -> None:
        """
        Saves the embedding features to Parquet.
        """
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df_embed.to_parquet(self.output_file, index=True)
        print(f"[✓] Saved embedding features to {self.output_file}")
