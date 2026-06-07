import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # AI Workplace Policy — Named Entity Recognition

    This notebook runs Named Entity Recognition (NER) on the scraped text from the AI Workplace database. It extracts organizations, people, locations, and dates mentioned across all sources, giving a picture of who and what is being talked about in the context of AI in the workplace.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests
    import concurrent.futures
    from bs4 import BeautifulSoup
    import spacy
    import plotly.express as px
    import sys
    sys.path.insert(0, "/Users/mobinariazi/SocialMediaLab/pythonProject/.venv/lib/python3.12/site-packages")

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
    df = _raw[_present].copy()

    def check_and_scrape(url):
        if not isinstance(url, str) or not url.strip().startswith("http"):
            return url, ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=True)
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return url, " ".join(soup.get_text(separator=" ").split())[:2000]
        except Exception:
            try:
                resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=False)
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return url, " ".join(soup.get_text(separator=" ").split())[:2000]
            except Exception as e:
                return url, f"[could not scrape: {str(e)[:60]}]"

    _all_urls = df["Source URL"].tolist() if "Source URL" in df.columns else []
    _urls = list(dict.fromkeys(u for u in _all_urls if isinstance(u, str) and u.strip()))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as _pool:
        _results = dict(_pool.map(check_and_scrape, _urls))

    df["Scraped Text"] = df["Source URL"].map(_results).fillna("")

    mo.md(f"Loaded and scraped **{len(df):,}** rows — **{df['Scraped Text'].str.len().gt(50).sum()}** with usable text.")
    return df, mo, pd, px, spacy


@app.cell
def _(mo):
    run_ner = mo.ui.run_button(label="Run NER Analysis")
    run_ner
    return (run_ner,)


@app.cell
def _(df, mo, pd, run_ner, spacy):
    mo.stop(not run_ner.value)

    nlp = spacy.load("en_core_web_trf")

    ENTITY_TYPES = ["ORG", "PERSON", "GPE", "DATE", "PRODUCT", "LAW"]

    CUSTOM_STOPWORDS = [
        "getty", "images", "disable", "browser",
        "enable", "subscribe", "subscription", "cookie",
        "cookies", "paywall", "login", "sign", "account", "register",
        "advertisement", "advertising", "ad", "sponsored", "blocker",
        "com", "block", "blocking", "loading", "click",
        "please", "accept", "decline", "consent", "gdpr", "ccpa",
        "password", "username", "forgot",
        "copyright", "reserved", "rights", "inc", "llc", "ltd", "stream", "ip", "site", "page", "javascript", "js",
        "reuters", "bloomberg", "reload", "refresh",
    ]

    _rows = []
    for _, row in df.iterrows():
        text = row.get("Scraped Text", "")
        if not isinstance(text, str) or len(text.strip()) < 20:
            continue
        doc = nlp(text[:10000])
        for ent in doc.ents:
            if ent.label_ in ENTITY_TYPES:
                if ent.text.strip().lower() not in CUSTOM_STOPWORDS:
                    _rows.append({
                        "Company Name": row.get("Company Name", ""),
                        "Fortune 100/500 rank": row.get("Fortune 100/500 rank", ""),
                        "Industry": row.get("Industry", ""),
                        "Source Title": row.get("Source Title", ""),
                        "Source URL": row.get("Source URL", ""),
                        "Relevant to Internal AI Workflow Use/Aug?": row.get(
                            "Relevant to Internal AI Workflow Use/Aug?", ""),
                        "Relevant to Automation Impact?": row.get("Relevant to Automation Impact?", ""),
                        "Entity": ent.text.strip(),
                        "Entity Type": ent.label_,
                        "Context": text[max(0, ent.start_char - 100):ent.end_char + 100].strip(),
                    })

    ner_df = pd.DataFrame(_rows)
    return (ner_df,)


@app.cell
def _(mo, ner_df, run_ner):
    mo.stop(not run_ner.value)

    entity_filter = mo.ui.dropdown(
        options=["All", "ORG", "PERSON", "GPE", "DATE", "PRODUCT", "LAW"],
        value="All",
        label="Entity Type",
    )
    company_filter = mo.ui.dropdown(
        options=["All"] + sorted(ner_df["Company Name"].unique().tolist()),
        value="All",
        label="Company",
    )
    search_entity = mo.ui.text(placeholder="Search entities...", label="Search")

    mo.hstack([entity_filter, company_filter, search_entity], gap=2)
    return company_filter, entity_filter, search_entity


@app.cell
def _(company_filter, entity_filter, mo, ner_df, run_ner, search_entity):
    mo.stop(not run_ner.value)

    filtered_ner = ner_df.copy()

    if entity_filter.value != "All":
        filtered_ner = filtered_ner[filtered_ner["Entity Type"] == entity_filter.value]

    if company_filter.value != "All":
        filtered_ner = filtered_ner[filtered_ner["Company Name"] == company_filter.value]

    if search_entity.value:
        filtered_ner = filtered_ner[
            filtered_ner["Entity"].str.contains(search_entity.value, case=False, na=False)
        ]

    mo.md(f"**{len(filtered_ner):,}** entities shown")
    return (filtered_ner,)


@app.cell
def _(mo, run_ner):
    mo.stop(not run_ner.value)
    mo.md("""
    ### All Extracted Entities
    Every entity mention found across all scraped articles. Each row shows the entity, its type, the surrounding context, and which company and source it came from.
    """)
    return


@app.cell
def _(filtered_ner, mo, run_ner):
    mo.stop(not run_ner.value)
    mo.ui.table(
        filtered_ner[["Company Name", "Fortune 100/500 rank", "Industry", "Source Title", "Source URL",
                      "Relevant to Internal AI Workflow Use/Aug?", "Relevant to Automation Impact?", "Entity",
                      "Entity Type", "Context"]],
        selection=None,
        pagination=True,
        page_size=25,
    )
    return


@app.cell
def _(mo, run_ner):
    mo.stop(not run_ner.value)
    mo.md("""
    ### Entity Breakdown by Type
    A count of each entity category found across all documents. Shows whether the coverage skews toward organizations, people, locations, dates, products, or legislation.
    """)
    return


@app.cell
def _(filtered_ner, mo, px, run_ner):
    mo.stop(not run_ner.value)

    breakdown = (
        filtered_ner.groupby("Entity Type")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    fig_donut = px.pie(
        breakdown,
        names="Entity Type",
        values="Count",
        hole=0.4,
        title="Entity Type Distribution",
        color_discrete_sequence=px.colors.sequential.Blues,
    )

    mo.vstack([
        fig_donut,
        mo.ui.table(breakdown, selection=None, pagination=True, page_size=10),
    ])
    return


@app.cell
def _(mo, run_ner):
    mo.stop(not run_ner.value)
    mo.md("""
    ### Most Frequently Mentioned Entities
    The top 20 entities ranked by how many times they appear across all documents. High frequency entities reveal the key players, places, and products dominating the conversation.
    """)
    return


@app.cell
def _(filtered_ner, mo, px, run_ner):
    mo.stop(not run_ner.value)

    top_entities = (
        filtered_ner.groupby(["Entity", "Entity Type"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(20)
    )

    fig_top = px.bar(
        top_entities,
        x="Count",
        y="Entity",
        color="Entity Type",
        orientation="h",
        title="Top 20 Most Mentioned Entities",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        height=600,
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"})

    mo.vstack([
        fig_top,
        mo.ui.table(top_entities, selection=None, pagination=True, page_size=20),
    ])
    return


@app.cell
def _(mo, run_ner):
    mo.stop(not run_ner.value)
    mo.md("""
    ### Top Organizations Mentioned
    The most frequently mentioned organizations across all sources. Reveals which companies, institutions, and agencies are central to the AI workplace conversation.
    """)
    return


@app.cell
def _(filtered_ner, mo, px, run_ner):
    mo.stop(not run_ner.value)

    top_orgs = (
        filtered_ner[filtered_ner["Entity Type"] == "ORG"]
        .groupby("Entity")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(20)
    )

    fig_orgs = px.bar(
        top_orgs,
        x="Count",
        y="Entity",
        orientation="h",
        title="Top 20 Organizations Mentioned",
        color="Count",
        color_continuous_scale="Blues",
        height=600,
    )
    fig_orgs.update_layout(yaxis={"categoryorder": "total ascending"})

    mo.vstack([
        fig_orgs,
        mo.ui.table(top_orgs, selection=None, pagination=True, page_size=20),
    ])
    return


@app.cell
def _(mo, run_ner):
    mo.stop(not run_ner.value)
    mo.md("""
    ### Top People Mentioned
    The most frequently named individuals across all sources. Shows which executives, politicians, and researchers are most prominent in AI workplace coverage.
    """)
    return


@app.cell
def _(filtered_ner, mo, px, run_ner):
    mo.stop(not run_ner.value)

    top_persons = (
        filtered_ner[filtered_ner["Entity Type"] == "PERSON"]
        .groupby("Entity")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(20)
    )

    fig_persons = px.bar(
        top_persons,
        x="Count",
        y="Entity",
        orientation="h",
        title="Top 20 People Mentioned",
        color="Count",
        color_continuous_scale="Blues",
        height=600,
    )
    fig_persons.update_layout(yaxis={"categoryorder": "total ascending"})

    mo.vstack([
        fig_persons,
        mo.ui.table(top_persons, selection=None, pagination=True, page_size=20),
    ])
    return


if __name__ == "__main__":
    app.run()
