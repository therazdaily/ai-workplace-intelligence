import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # AI Workplace Policy — BERTopic Analysis

    This notebook runs BERTopic Analysis on the scraped text from the AI Workplace database. BERTopic is a powerful topic modeling technique that groups documents into topics based on their semantic content. It uses advanced language models to understand the meaning of the text, then clusters similar documents together and identifies the most representative words for each topic. This helps us uncover the main themes and trends in how AI is being discussed in the workplace across different companies and sources.

    Run using: `uv run marimo edit "BERTOPIC Table.py" --no-sandbox`
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests
    import concurrent.futures
    from bs4 import BeautifulSoup

    INPUT_FILE = "AI Workplace database.csv"
    COLUMNS = [
        "Company Name",
        "Fortune 100/500 rank",
        "Industry",
        "Source Title",
        "Source URL",
        "Relevant to Internal AI Workflow Use/Aug?",
        "Relevant to Automation Impact?",
    ]

    try:
        _raw = pd.read_csv(INPUT_FILE, dtype=str).fillna("")
    except FileNotFoundError:
        mo.stop(True, mo.callout(
            mo.md(f"**File not found:** `{INPUT_FILE}`  \nCheck the path and try again."),
            kind="danger",
        ))

    _present = [c for c in COLUMNS if c in _raw.columns]
    missing = [c for c in COLUMNS if c not in _raw.columns]
    df = _raw[_present].copy()

    def check_and_scrape(url):
        if not isinstance(url, str) or not url.strip().startswith("http"):
            return url, "[skip] Not a URL", ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        status = "[broken] failed"
        try:
            head = requests.head(url, headers=headers, timeout=8, allow_redirects=True, verify=True)
            status = f"[ok] {head.status_code}" if head.status_code < 400 else f"[broken] HTTP {head.status_code}"
        except requests.exceptions.SSLError:
            try:
                head = requests.head(url, headers=headers, timeout=8, allow_redirects=True, verify=False)
                status = f"[ok] {head.status_code} (ssl warning)" if head.status_code < 400 else f"[broken] HTTP {head.status_code}"
            except Exception as e:
                status = f"[broken] {str(e)[:60]}"
        except Exception as e:
            status = f"[broken] {str(e)[:60]}"

        if status.startswith("[broken]") or status.startswith("[skip]"):
            return url, status, ""

        text = ""
        try:
            resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=True)
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                import fitz
                import io
                doc = fitz.open(stream=io.BytesIO(resp.content), filetype="pdf")
                text = " ".join(page.get_text() for page in doc)
                text = " ".join(text.split())[:2000]
            else:
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = " ".join(soup.get_text(separator=" ").split())[:2000]
        except Exception:
            try:
                resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=False)
                content_type = resp.headers.get("Content-Type", "")
                if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                    import fitz
                    import io
                    doc = fitz.open(stream=io.BytesIO(resp.content), filetype="pdf")
                    text = " ".join(page.get_text() for page in doc)
                    text = " ".join(text.split())[:2000]
                else:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    text = " ".join(soup.get_text(separator=" ").split())[:2000]
            except Exception as e:
                text = f"[could not scrape: {str(e)[:60]}]"

        return url, status, text

    _all_urls = df["Source URL"].tolist() if "Source URL" in df.columns else []
    _urls = list(dict.fromkeys(u for u in _all_urls if isinstance(u, str) and u.strip()))
    empty_count = sum(1 for u in _all_urls if not isinstance(u, str) or not u.strip())

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as _pool:
        _results = list(_pool.map(check_and_scrape, _urls))

    result_df = pd.DataFrame(_results, columns=["Source URL", "Status", "Scraped Text"])

    merged_df = df.merge(result_df, on="Source URL", how="left")
    merged_df["Status"] = merged_df["Status"].fillna("not checked")
    merged_df["Scraped Text"] = merged_df["Scraped Text"].fillna("")

    _cols = list(df.columns)
    _url_idx = _cols.index("Source URL")
    _ordered = _cols[:_url_idx + 1] + ["Status"] + _cols[_url_idx + 1:] + ["Scraped Text"]
    merged_df = merged_df[_ordered]

    relevance_filter = mo.ui.dropdown(
        options=["All", "Augmentation only", "Automation only", "Both"],
        value="All",
        label="Relevant to",
    )
    status_filter = mo.ui.dropdown(
        options=["All", "ok", "broken", "skip"],
        value="All",
        label="URL Status",
    )

    mo.hstack([relevance_filter, status_filter], gap=2)
    return (
        empty_count,
        merged_df,
        missing,
        mo,
        relevance_filter,
        result_df,
        status_filter,
    )


@app.cell
def _(
    empty_count,
    merged_df,
    missing,
    mo,
    relevance_filter,
    result_df,
    status_filter,
):
    filtered = merged_df.copy()

    _ai_col   = "Relevant to Internal AI Workflow Use/Aug?"
    _auto_col = "Relevant to Automation Impact?"
    if relevance_filter.value == "Augmentation only":
        if _ai_col in filtered.columns and _auto_col in filtered.columns:
            filtered = filtered[
                (filtered[_ai_col].str.strip().str.lower() == "yes") &
                (filtered[_auto_col].str.strip().str.lower() != "yes")
            ]
    elif relevance_filter.value == "Automation only":
        if _ai_col in filtered.columns and _auto_col in filtered.columns:
            filtered = filtered[
                (filtered[_auto_col].str.strip().str.lower() == "yes") &
                (filtered[_ai_col].str.strip().str.lower() != "yes")
            ]
    elif relevance_filter.value == "Both":
        if _ai_col in filtered.columns and _auto_col in filtered.columns:
            filtered = filtered[
                (filtered[_ai_col].str.strip().str.lower() == "yes") &
                (filtered[_auto_col].str.strip().str.lower() == "yes")
            ]

    if status_filter.value != "All":
        filtered = filtered[filtered["Status"].str.startswith(f"[{status_filter.value}]")]

    _ok   = result_df["Status"].str.startswith("[ok]").sum()
    _warn = result_df["Status"].str.startswith("[skip]").sum()
    _bad  = result_df["Status"].str.startswith("[broken]").sum()
    _empty_note = f" + {empty_count} rows with no URL" if empty_count else ""

    _items = []
    if missing:
        _items.append(mo.callout(
            mo.md("**Some columns were not found in the CSV and were skipped:**  \n"
                  + ", ".join(f"`{c}`" for c in missing)),
            kind="warn",
        ))
    _items += [
        mo.md(f"**{len(filtered):,}** of **{len(merged_df):,}** rows shown · **{_ok} reachable / {_warn} skipped / {_bad} broken** out of {len(result_df)} unique URLs{_empty_note}"),
        mo.ui.table(filtered, selection=None, pagination=True, page_size=25),
    ]

    mo.vstack(_items)
    return (filtered,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    BERTopic reads every scraped article and converts it into a set of numbers that capture its meaning, then groups articles that are mathematically close together into topics. It then maps similar articles into neighborhoods — BERTopic draws the boundaries around those neighborhoods and calls each one a topic. It then looks at which words appear most uniquely in each cluster to generate a label.
    """)
    return


@app.cell
def _(mo):
    run_bertopic = mo.ui.run_button(label="Run BERTopic Analysis")
    run_bertopic
    return (run_bertopic,)


@app.cell
def _(mo, run_bertopic):
    get_ran, set_ran = mo.state(False)
    if run_bertopic.value:
        set_ran(True)
    return (get_ran,)


@app.cell
def _(filtered, mo, run_bertopic):
    import sys
    sys.path.insert(0, "/Users/mobinariazi/SocialMediaLab/pythonProject/.venv/lib/python3.12/site-packages")

    from umap import UMAP as _UMAP
    from hdbscan import HDBSCAN as _HDBSCAN
    from sentence_transformers import SentenceTransformer as _ST
    from sklearn.feature_extraction.text import CountVectorizer as _CV
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    from bertopic import BERTopic as _BERTopic
    from bertopic.representation import KeyBERTInspired as _KBI
    from bertopic.vectorizers import ClassTfidfTransformer as _CTF

    mo.stop(not run_bertopic.value)

    docs_df = filtered[
        (filtered["Scraped Text"].str.strip().str.split().str.len() > 20) &
        (~filtered["Scraped Text"].str.strip().str.startswith("["))
    ].copy().reset_index(drop=True)

    docs = docs_df["Scraped Text"].tolist()

    mo.stop(len(docs) == 0, mo.md("No successfully scraped documents to analyze."))

    _custom_stopwords = [
        "getty", "images", "disable", "browser",
        "enable", "subscribe", "subscription", "cookie",
        "cookies", "paywall", "login", "sign", "account", "register",
        "advertisement", "advertising", "ad", "sponsored", "blocker",
        "com", "block", "blocking", "loading", "click",
        "please", "accept", "decline", "consent", "gdpr", "ccpa",
        "password", "username", "forgot",
        "copyright", "reserved", "rights", "inc", "llc", "ltd",
        "stream", "ip", "site", "page", "javascript", "js",
        "reuters", "bloomberg", "reload", "refresh",
    ]
    _all_stopwords = list(ENGLISH_STOP_WORDS) + _custom_stopwords

    model = _BERTopic(
        embedding_model=_ST("all-MiniLM-L6-v2"),
        umap_model=_UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine"),
        hdbscan_model=_HDBSCAN(min_cluster_size=5, metric="euclidean", cluster_selection_method="eom", prediction_data=True),
        vectorizer_model=_CV(stop_words=_all_stopwords),
        ctfidf_model=_CTF(),
        representation_model=_KBI(),
        top_n_words=10,
        nr_topics=10,
    )

    topics, probs = model.fit_transform(docs)
    info = model.get_topic_info()

    docs_df["Topic"] = topics
    docs_df["Topic Label"] = docs_df["Topic"].map(info.set_index("Topic")["Name"].to_dict())

    n_found = len(info) - 1
    n_outliers = docs_df[docs_df["Topic"] == -1].shape[0]

    mo.md(f"**{n_found} topics** found across {len(docs_df)} documents — {n_outliers} outliers.")
    return docs, docs_df, info, model, n_found


@app.cell
def _(docs_df, get_ran, info, mo):
    mo.stop(not get_ran())

    _available_cols = [c for c in ["Company Name", "Source URL", "Topic", "Topic Label"] if c in docs_df.columns]

    mo.vstack([
        mo.md("### Topic Overview"),
        mo.ui.table(info[["Topic","Name","Count","Representation"]], selection=None, pagination=True, page_size=15),
        mo.md("### Documents by Topic"),
        mo.ui.table(docs_df[_available_cols], selection=None, pagination=True, page_size=20),
    ])
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    mo.vstack([
        mo.md("### Top Words per Topic"),
        mo.md("A bar chart showing the most representative words for each topic. The slider controls how many words are shown per topic — drag it up to see more keywords, down to focus on the strongest ones."),
    ])
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    n_words_bar = mo.ui.slider(start=3, stop=20, step=1, value=8, label="Words per topic", show_value=True)
    n_words_bar
    return (n_words_bar,)


@app.cell
def _(get_ran, mo, model, n_found, n_words_bar):
    mo.stop(not get_ran())
    try:
        model.visualize_barchart(top_n_topics=n_found, n_words=n_words_bar.value)
    except Exception as e:
        mo.md(f"Could not render bar chart — not enough topics. (`{e}`)")
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    mo.vstack([
        mo.md("### Intertopic Distance Map"),
        mo.md("A 2D scatter plot showing how topics relate to each other in semantic space. Topics that are close together share similar language. The slider controls how many topics are plotted."),
    ])
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    top_n_dist = mo.ui.slider(start=1, stop=50, step=1, value=10, label="Topics to show", show_value=True)
    top_n_dist
    return (top_n_dist,)


@app.cell
def _(get_ran, mo, model, top_n_dist):
    mo.stop(not get_ran())
    try:
        model.visualize_topics(top_n_topics=top_n_dist.value)
    except Exception as e:
        mo.md(f"Could not render intertopic distance map — not enough topics. Try reducing **Min cluster size** or increasing the dataset. (`{e}`)")
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    mo.vstack([
        mo.md("### Topic Similarity Heatmap"),
        mo.md("A grid showing pairwise similarity scores between all topics. Darker cells mean two topics share more vocabulary. The slider lets you focus on a subset of topics."),
    ])
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    top_n_heat = mo.ui.slider(start=1, stop=50, step=1, value=10, label="Topics to show", show_value=True)
    top_n_heat
    return (top_n_heat,)


@app.cell
def _(get_ran, mo, model, top_n_heat):
    mo.stop(not get_ran())
    try:
        model.visualize_heatmap(top_n_topics=top_n_heat.value)
    except Exception as e:
        mo.md(f"Could not render heatmap — not enough topics. (`{e}`)")
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    mo.vstack([
        mo.md("### Document Map"),
        mo.md("Plots every document as a point in 2D space, colored by topic. Good for spotting clusters and outliers. The sample fraction slider lets you render a random subset if you have too many documents to display clearly."),
    ])
    return


@app.cell
def _(get_ran, mo):
    mo.stop(not get_ran())
    sample_docs = mo.ui.slider(start=0.1, stop=1.0, step=0.05, value=1.0, label="Doc sample fraction", show_value=True)
    sample_docs
    return (sample_docs,)


@app.cell
def _(docs, get_ran, mo, model, sample_docs):
    mo.stop(not get_ran())
    try:
        model.visualize_documents(docs, custom_labels=True, sample=sample_docs.value)
    except Exception as e:
        mo.md(f"Could not render document map. (`{e}`)")
    return


if __name__ == "__main__":
    app.run()