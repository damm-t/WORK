"""
News Memory — SQLite-backed narrative store with similarity search
==================================================================
Our pragmatic "vector DB": stores every headline the system has analysed
(together with its FinBERT verdict) and finds *similar past narratives*
via token-vector cosine similarity — zero external infrastructure,
fully offline, instantly explainable.

Later upgrade path: swap `_vec()` for transformer embeddings and the SQL
lookup for FAISS/Chroma — the interface stays identical.

Usage:
    python -m nlp.news_memory --remember NVDA "Some headline here" positive 0.91
    python -m nlp.news_memory --similar "chip earnings blowout"
    python -m nlp.news_memory --stats
"""

import argparse
import json
import math
import re
import sqlite3
import time
from pathlib import Path

DB_PATH = Path("nlp/news_memory.db")

_STOP = set("""a an the of in on for to with and or is are was were be been being
at as by from about after before over under this that these those it its their
his her our your they them he she we you i not no yes but so than then now new
says said will would could should may might can had have has did do does done
out up down off above below more most other some such only own same very just
also into amid vs per due hit hits fall falls rise rises stock stocks shares
share inc corp ltd plc group company companies""".split())


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS articles (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               ts REAL, ticker TEXT, title TEXT,
               sentiment TEXT, score REAL)"""
    )
    return conn


def _tokens(text: str) -> list:
    return [w for w in re.findall(r"[a-z]{3,}", str(text).lower()) if w not in _STOP]


def _vec(tokens: list) -> dict:
    v = {}
    for tok in tokens:
        v[tok] = v.get(tok, 0.0) + 1.0
    norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {k: x / norm for k, x in v.items()}


def remember(ticker: str, title: str, sentiment: str = "neutral",
             score: float = 0.0) -> int:
    """Stores one analysed headline. Returns row id."""
    conn = _conn()
    cur = conn.execute(
        "INSERT INTO articles (ts, ticker, title, sentiment, score) "
        "VALUES (?, ?, ?, ?, ?)",
        (time.time(), str(ticker).upper(), str(title),
         str(sentiment).lower(), float(score)),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def similar(text: str, top_k: int = 5) -> list:
    """Finds the most similar stored headlines (cosine on token vectors)."""
    q = _vec(_tokens(text))
    if not q:
        return []
    conn = _conn()
    rows = conn.execute(
        "SELECT ts, ticker, title, sentiment, score FROM articles "
        "ORDER BY id DESC LIMIT 5000"
    ).fetchall()
    conn.close()

    scored = []
    for ts, ticker, title, sentiment, score in rows:
        v = _vec(_tokens(title))
        sim = sum(q.get(tok, 0.0) * val for tok, val in v.items())
        if sim > 0.05:
            scored.append({
                "similarity": round(sim, 3),
                "ticker": ticker,
                "title": title,
                "sentiment": sentiment,
                "finbert_score": round(float(score or 0.0), 3),
                "age_days": round((time.time() - ts) / 86400.0, 1),
            })
    scored.sort(key=lambda r: -r["similarity"])
    return scored[:top_k]


def stats() -> dict:
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    per_ticker = conn.execute(
        "SELECT ticker, COUNT(*) FROM articles GROUP BY ticker ORDER BY 2 DESC"
    ).fetchall()
    conn.close()
    return {"total": total,
            "per_ticker": {t: n for t, n in per_ticker}}


def _main() -> None:
    p = argparse.ArgumentParser(description="News Memory (SQLite narrative store)")
    p.add_argument("--remember", nargs=4, metavar=("TICKER", "TITLE", "SENTIMENT",
                                                   "SCORE"))
    p.add_argument("--similar", type=str, help="find similar past narratives")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--top", type=int, default=5)
    a = p.parse_args()

    if a.remember:
        rid = remember(a.remember[0], a.remember[1], a.remember[2],
                       float(a.remember[3]))
        print(f"stored #{rid}")
    elif a.similar:
        res = similar(a.similar, top_k=a.top)
        if not res:
            print("No similar narratives stored yet.")
        for r in res:
            print(json.dumps(r, indent=2))
    elif a.stats:
        print(json.dumps(stats(), indent=2))
    else:
        p.print_help()


if __name__ == "__main__":
    _main()