# AI Workplace Intelligence Notebook

A Marimo-based interactive notebook that analyzes how Fortune 100/500 companies are publicly discussing and deploying AI in the workplace. It ingests a curated CSV database of company news sources, scrapes and checks every URL, and runs BERTopic topic modeling on the scraped text — all in one interactive interface.

---

## What It Does

1. **Loads** a CSV database of companies and their AI-related news sources
2. **Scrapes** every URL in parallel — checking reachability and extracting page text
3. **Filters** the data interactively by relevance type and URL status
4. **Runs BERTopic** on the scraped text to surface latent topics across sources
5. **Visualizes** the results through four interactive charts

---

## Data

The notebook expects a CSV file at: /Users/mobinariazi/Downloads/AI Workplace database.csv

Update `INPUT_FILE` in the second cell to point to your local copy.

The CSV should contain the following columns:

| Column | Description |
|---|---|
| Company name | Name of the Fortune 100/500 company |
| Fortune 100/500 rank | Company ranking |
| Industry | Sector |
| Source Title | Title of the news article or source |
| Source URL | Link to the source |
| Relevant to Internal AI Workflow Use/Aug? | Yes/No flag for augmentation relevance |
| Relevant to Automation Impact? | Yes/No flag for automation relevance |

---

## How to Run

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [Marimo](https://marimo.io) as the notebook runtime.

```bash
# Install dependencies
uv sync

# Run the notebook
uv run marimo edit "BERTOPIC Table.py"
```

---

## Dependencies

```toml
[project]
name = "ai-workplace-intelligence"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "marimo",
    "pandas",
    "requests",
    "beautifulsoup4",
    "bertopic",
    "sentence-transformers",
    "umap-learn",
    "hdbscan",
    "scikit-learn",
]
```

---

## Notebook Structure

### Section 1 — Data Collection & Table

The notebook loads the CSV, checks every URL for reachability (HEAD request), and scrapes the visible text from each page (GET request, stripped of nav/footer/scripts). Results are merged back into the original table with two new columns: **Status** and **Scraped Text**.

Two dropdowns above the table let you filter in real time:
- **Relevant to** — filter by AI augmentation, automation impact, both, or all
- **URL Status** — show only reachable, broken, or skipped links

### Section 2 — BERTopic Analysis

Click **Run BERTopic Analysis** to fit a topic model on the scraped text. The model uses:
- **Sentence Transformers** (`all-MiniLM-L6-v2`) for text embeddings
- **UMAP** for dimensionality reduction
- **HDBSCAN** for clustering
- **KeyBERT** for topic representation

After fitting, two tables appear automatically:
- **Topic Overview** — each topic with its name, document count, and top keywords
- **Documents by Topic** — every source mapped to its assigned topic

### Section 3 — Visualizations

Four interactive visualizations are available after the model runs. Each has a slider to dynamically adjust what is rendered — no need to rerun the model.

| Visualization | What it shows | Slider |
|---|---|---|
| Top Words per Topic | Bar chart of most representative keywords per topic | Words per topic |
| Intertopic Distance Map | 2D scatter of topic relationships in semantic space | Topics to show |
| Topic Similarity Heatmap | Pairwise similarity scores between topics | Topics to show |
| Document Map | Every document plotted in 2D space colored by topic | Sample fraction |

---

## What is Marimo?

[Marimo](https://marimo.io) is a reactive Python notebook where cells automatically re-run when their dependencies change. Unlike Jupyter, there is no hidden state — every cell is a pure function of its inputs. This makes it safe to use UI elements like sliders and dropdowns that instantly update downstream cells without manually re-running anything.

Marimo notebooks are also plain Python files, which means they work with version control, can be run as scripts, and are fully compatible with uv and standard Python tooling.

---

## Project Structure

