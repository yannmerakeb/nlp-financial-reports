# 🧠 Evasive Language in Financial Disclosures

**NLP-based analysis of ambiguous language in financial reports**

This project explores how companies may use vague, evasive, or ambiguous language in their financial disclosures — particularly SEC 10-K filings — to potentially obscure negative information or hedge against uncertainty. We leverage modern NLP techniques to detect such language patterns and assess their impact on post-disclosure market reactions.

---

## 📁 Project Structure

nlp-financial-reports/
│
├── data/
│ ├── raw/ # Original 10-K filings and market data
│ └── processed/ # Cleaned text, extracted features, labels
│
├── notebooks/
│ ├── 01_data_exploration.ipynb
│ ├── 02_feature_engineering.ipynb
│ └── 03_modeling.ipynb
│
├── src/
│ ├── data_loader.py # Data download and EDGAR scraping
│ ├── preprocessing.py # Text cleaning and tokenization
│ ├── features.py # Linguistic and semantic feature extraction
│ ├── model.py # Main model training pipeline
│ ├── baseline.py # Baseline TF-IDF model
│ └── evaluation.py # Metrics, plots, and evaluation logic
│
├── results/
│ ├── figures/ # Visualizations
│ └── metrics.json # Evaluation results
│
├── presentation/
│ └── final_slides.pdf # Project presentation
│
├── README.md
├── requirements.txt
└── .gitignore
