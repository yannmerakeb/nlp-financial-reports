## 📝 Project Overview

This project aims to detect ambiguous or strategically vague language in corporate financial disclosures (specifically SEC 10-K filings), using both linguistic feature engineering and transformer-based NLP models.  
We investigate whether such language correlates with poor post-disclosure market performance, suggesting potential obfuscation tactics by companies.

---

## 📁 Project Structure

The project tree is organized as follows :

```bash
nlp-financial-reports/
│
├── data/
│ ├── raw/ # Original 10-K filings and market data
│ └── processed/ # Cleaned and labeled text data
│
├── notebooks/
│ ├── 01_data_exploration.ipynb
│ ├── 02_feature_engineering.ipynb
│ └── 03_modeling.ipynb
│
├── src/
│ ├── data_loader.py # EDGAR scraper and market data fetcher
│ ├── preprocessing.py # Text cleaning and segmentation
│ ├── features.py # Linguistic features, readability scores, etc.
│ ├── baseline.py # TF-IDF + Logistic Regression (baseline model)
│ ├── model.py # Fine-tuning transformer models (main model)
│ └── evaluation.py # Metrics, visualizations, comparison
│
├── results/
│ ├── figures/ # Plots and graphs
│ └── metrics.json # Evaluation metrics
│
├── README.md
├── requirements.txt
└── .gitignore
```

---
## ⚙️ Setup & Installation (TO MODIFY/COMPLETE FROM THIS SECTION)

```bash
# Clone the repository
git clone https://github.com/your-username/nlp-financial-reports.git
cd nlp-financial-reports

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

---

## 🚀 How to Use

1. **Prepare the data**

   * Download and store raw 10-K filings in `data/raw/`
   * Use `src/data_loader.py` to extract text from SEC EDGAR and match filings to market data

2. **Preprocess and engineer features**

   * Run `notebooks/01_data_exploration.ipynb` and `02_feature_engineering.ipynb`
   * Extract linguistic features and readability scores

3. **Train models**

   * Use `src/baseline.py` to train the baseline TF-IDF + Logistic Regression model
   * Use `src/model.py` for fine-tuning transformer models (e.g., RoBERTa, FinBERT)

4. **Evaluate and compare**

   * Use `src/evaluation.py` to assess model performance
   * Compare results of the transformer model to the baseline
   * *(Optional)* Analyze correlation between detected ambiguity and market reaction

---

## 📊 Methodology

### Data Collection

Describe here how you gather and store 10-K filings and market data.

### Data Preparation

Explain your cleaning, segmentation, and labeling process.

### Feature Engineering

Detail linguistic features extracted (e.g., ambiguity indicators, readability scores, sentiment, etc.).

### Modeling

Explain the baseline model choice and architecture of the transformer model.

### Evaluation

Define metrics used (accuracy, F1-score, ROC AUC, etc.) and how you compare baseline and main models.

---

## 📈 Results

Summarize key findings, model performances, and any interesting observations regarding ambiguous language and market impact.

---

## 🗣️ Presentation

Include link or path to final slides and any supporting materials for your project presentation.

---