# AI Workplace Intelligence

A research tool for analyzing how Fortune 500 companies are publicly discussing and deploying AI in the workplace. This project uses two interactive [Marimo](https://marimo.io) notebooks that automatically scrape company policy sources and run NLP analysis — topic modeling and named entity recognition — on the extracted text.

---

## What This Project Does

The project starts from a curated CSV database of Fortune 500 companies, each with one or more source URLs (news articles, press releases, policy pages, etc.) related to their AI workplace practices. Both notebooks read that CSV, scrape the text from every URL, and run a different kind of NLP analysis on the result.

**BERTOPIC Table.py** asks: *What themes are emerging across all these sources?* It uses topic modeling to automatically group documents into clusters of related ideas and visualizes those clusters interactively.

**NER Table.py** asks: *Who and what is being talked about?* It uses named entity recognition to pull out every organization, person, location, date, product, and piece of legislation mentioned across all sources, then lets you filter and explore them.

Neither notebook requires any prior NLP knowledge to use — both are point-and-click once running.

---

## Project Structure

```
pythonProject/
├── BERTOPIC Table.py          # Topic modeling notebook
├── NER Table.py               # Named entity recognition notebook
├── AI Workplace database.csv  # Your input data (not included in repo)
├── pyproject.toml             # Dependencies managed by uv
└── uv.lock                    # Locked dependency versions
```

---

## Setup

### Prerequisites

You need the following installed on your machine before starting:

- **Python 3.12** — [python.org](https://www.python.org/downloads/)
- **uv** — a fast Python package manager. Install it with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 1. Clone the repository

```bash
git clone https://github.com/therazdaily/ai-workplace-intelligence.git
cd ai-workplace-intelligence
```

### 2. Install dependencies

All dependencies are defined in `pyproject.toml` and locked in `uv.lock`. Install them with:

```bash
uv sync
```

This installs everything including Marimo, BERTopic, spaCy, Plotly, BeautifulSoup, and all supporting libraries.

### 3. Download the spaCy language model

The NER notebook requires a large transformer-based spaCy model. Download it once with:

```bash
uv run python -m spacy download en_core_web_trf
```

This only needs to be done once.

### 4. Add your data file

Place your input CSV in the project root, named exactly:

```
AI Workplace database.csv
```

The CSV should contain the following columns (extra columns are ignored):

| Column | Description |
|---|---|
| `Company Name` | Fortune 500 company name |
| `Fortune 100/500 rank` | Company ranking |
| `Industry` | Industry sector |
| `Source Title` | Title of the source article or page |
| `Source URL` | URL to scrape |
| `Relevant to Internal AI Workflow Use/Aug?` | Relevance flag |
| `Relevant to Automation Impact?` | Relevance flag |

---

## Running the Notebooks

Both notebooks are run using Marimo's edit mode, which opens an interactive browser-based interface. Run them one at a time — they are independent of each other and can be run in any order.

### Topic Modeling (run first if exploring themes)

```bash
uv run marimo edit "BERTOPIC Table.py" --no-sandbox
```

### Named Entity Recognition

```bash
uv run marimo edit "NER Table.py" --no-sandbox
```

Marimo will open automatically in your browser. If it doesn't, look for the local URL printed in the terminal (typically `http://localhost:2718`) and open it manually.

---

## How to Use Each Notebook

### BERTOPIC Table.py

When the notebook opens, it immediately begins scraping all URLs in the CSV. This may take a few minutes depending on the number of rows. Once scraping is complete, a summary line will appear showing how many rows were loaded and how many had usable text.

From there:

1. Use the **status and relevance filters** to narrow down which rows are shown in the source table.
2. Click **Run Topic Modeling** to start BERTopic analysis on the scraped text. This is the slow step — BERTopic runs sentence embeddings, UMAP dimensionality reduction, and HDBSCAN clustering. Expect several minutes on a large dataset.
3. Once complete, five visualizations appear below the button:
   - **Topic overview table** — each topic with its top keywords
   - **Documents by topic table** — every document assigned to a topic
   - **Top words per topic** — bar chart of keyword weights
   - **Intertopic distance map** — 2D map of how topics relate to each other
   - **Topic similarity heatmap** — pairwise topic overlap
   - **Document map** — every document plotted in 2D embedding space, colored by topic

### NER Table.py

When the notebook opens, scraping begins automatically (same as above).

Once scraping is complete:

1. Click **Run NER Analysis** to start named entity recognition. spaCy will process each document and extract entities. This takes a few minutes.
2. Once complete, a set of filters appears at the top:
   - **Entity Type** — filter by ORG, PERSON, GPE, DATE, PRODUCT, or LAW
   - **Company** — filter to a specific Fortune 500 company
   - **Search** — free-text search across entity names
3. Five outputs appear below the filters:
   - **All Extracted Entities** — full table of every mention with surrounding context
   - **Entity type distribution** — donut chart of entity category breakdown
   - **Top 20 most mentioned entities** — bar chart across all types
   - **Top 20 organizations** — bar chart of most-mentioned ORGs
   - **Top 20 people** — bar chart of most-mentioned individuals

---

## Dependencies

All dependencies are managed by `uv` and defined in `pyproject.toml`. Key libraries:

| Library | Purpose |
|---|---|
| `marimo` | Reactive notebook runtime |
| `bertopic` | Topic modeling |
| `spacy` + `en_core_web_trf` | Named entity recognition |
| `sentence-transformers` | Text embeddings for BERTopic |
| `umap-learn` | Dimensionality reduction |
| `hdbscan` | Density-based clustering |
| `plotly` | Interactive visualizations |
| `beautifulsoup4` | Web scraping |
| `requests` | HTTP requests for scraping |
| `pandas` | Data manipulation |

To see the full locked dependency list, refer to `uv.lock`.

---

## Notes

- Scraping runs on every notebook launch. Pages behind paywalls, login walls, or bot-detection will return limited or no text — this is expected.
- The spaCy transformer model (`en_core_web_trf`) is accurate but slow. On large datasets (200+ rows), NER may take 10–20 minutes.
- BERTopic requires a minimum number of documents to form meaningful topics. If your dataset is small (under ~30 rows with usable text), topic quality may be low.
- Both notebooks are read-only with respect to your CSV — they never modify the input file.