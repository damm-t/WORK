import json
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    import yfinance as yf
except Exception as e:
    yf = None
    print(f"[news_fetcher] Error: {e}")

YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
CACHE_DIR = Path("ingestion/cache")


def fetch_news(ticker: str, max_articles: int = 20) -> list[dict]:
    try:
        return fetch_yfinance_news(ticker, max_articles=max_articles)
    except Exception as e:
        print(f"[news_fetcher] Error fetching {ticker}: {e}")
        return []


def fetch_yfinance_news(ticker: str, max_articles: int = 20) -> list[dict]:
    try:
        results = _fetch_with_yfinance(ticker, max_articles)
        if not results:
            results = _fetch_with_yahoo_search(ticker, max_articles)

        if results:
            _save_cache(ticker, results)
            return results

        return _load_cache(ticker)
    except Exception as e:
        if "Expecting value" in str(e):
            print("[yfinance_news] Error: Yahoo Finance returned a non-JSON response, likely rate limited")
            return _load_cache(ticker)

        print(f"[yfinance_news] Error: {e}")
        return _load_cache(ticker)


def _fetch_with_yfinance(ticker: str, max_articles: int) -> list[dict]:
    try:
        if yf is None:
            return []

        stock = yf.Ticker(ticker)
        news_items = stock.get_news() or []
        results = []
        for item in news_items[:max_articles]:
            article = _normalize(item, ticker)
            if article:
                results.append(article)

        return results
    except Exception as e:
        print(f"[yfinance_news] Error: {e}")
        return []


def _fetch_with_yahoo_search(ticker: str, max_articles: int) -> list[dict]:
    try:
        response = requests.get(
            YAHOO_SEARCH_URL,
            params={"q": ticker},
            headers=YAHOO_HEADERS,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        news_items = data.get("news", [])
        results = []
        for item in news_items[:max_articles]:
            article = _normalize(item, ticker)
            if article:
                results.append(article)

        return results
    except Exception as e:
        print(f"[yfinance_news] Error: {e}")
        return []


def _normalize(item: dict, ticker: str) -> dict:
    try:
        content = item.get("content", {})
        canonical_url = item.get("canonicalUrl", {})
        summary = item.get("summary", "") or content.get("summary", "")
        title = item.get("title", "") or content.get("title", "")
        provider_time = (
            item.get("providerPublishTime", "")
            or content.get("pubDate", "")
            or item.get("pubDate", "")
        )
        url = (
            item.get("link", "")
            or item.get("url", "")
            or canonical_url.get("url", "")
        )
        return {
            "source":       "yfinance_news",
            "ticker":       ticker,
            "title":        str(title),
            "body":         str(summary),
            "published_at": _normalize_published_at(provider_time),
            "url":          str(url),
        }
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return {}


def _normalize_published_at(published_at_value) -> str:
    try:
        if isinstance(published_at_value, (int, float)):
            return datetime.fromtimestamp(float(published_at_value), tz=timezone.utc).isoformat()

        return str(published_at_value or "")
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return ""


def _save_cache(ticker: str, articles: list[dict]) -> None:
    try:
        if not articles:
            return None

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _get_cache_path(ticker)
        cache_path.write_text(json.dumps(articles), encoding="utf-8")
        return None
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return None


def _load_cache(ticker: str) -> list[dict]:
    try:
        cache_path = _get_cache_path(ticker)
        if not cache_path.exists():
            return []

        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return []


def _get_cache_path(ticker: str) -> Path:
    try:
        safe_ticker = str(ticker).upper()
        return CACHE_DIR / f"{safe_ticker}_news.json"
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return Path("ingestion/cache/INVALID_news.json")
