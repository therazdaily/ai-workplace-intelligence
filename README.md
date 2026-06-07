# AI Workplace Intelligence — Research Notebooks

Two interactive Marimo notebooks that analyze how Fortune 500 companies are publicly discussing and deploying AI in the workplace. Both notebooks automatically scrape every URL in the dataset and run NLP analysis on the extracted text.

---

## Notebooks

### BERTOPIC Table.py — Topic Modeling
Scrapes every URL, checks reachability, and runs BERTopic topic modeling to surface the main themes across all sources. Produces an interactive table with URL status and scraped text, followed by four topic visualizations.

Run with:
```bash
uv run marimo edit "BERTOPIC Table.py" --no-sandbox
```

### NER Table.py — Named Entity Recognition
Scrapes every URL and runs spaCy NER to extract organizations, people, locations, dates, products, and legislation mentioned across all sources. Produces five interactive charts and tables.

Run with:
```bash
uv run marimo edit "NER Table.py" --no-sandbox
```

---

## Data

Both notebooks read from: AI Workplace database.csv

Place it in the project root before running. The CSV contains Fortune 500 company names, industry, source titles, URLs, and relevance flags for AI augmentation and automation impact.

---

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [Marimo](https://marimo.io) as the notebook runtime.

```bash
# Install dependencies
uv sync

# Download spaCy model (required for NER notebook)
uv run python -m spacy download en_core_web_trf
```

---

## What Each Notebook Produces

**BERTOPIC Table.py**
- Interactive table with URL status and scraped text
- Relevance and status filters
- Topic overview and documents by topic tables
- Top words per topic bar chart
- Intertopic distance map
- Topic similarity heatmap
- Document map

**NER Table.py**
- Interactive table of every entity mention with context
- Entity type distribution donut chart
- Top 20 most mentioned entities bar chart
- Top 20 organizations bar chart
- Top 20 people bar chart
- Filters by entity type, company, and search

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Marimo | Reactive Python notebook runtime |
| BERTopic | Topic modeling |
| spaCy `en_core_web_trf` | Named entity recognition |
| Sentence Transformers | Text embeddings for BERTopic |
| UMAP | Dimensionality reduction |
| HDBSCAN | Clustering |
| Plotly | Interactive visualizations |
| BeautifulSoup | Web scraping |
| uv | Dependency management |