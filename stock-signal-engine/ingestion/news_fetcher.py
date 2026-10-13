import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    import yfinance as yf
except Exception as e:
    yf = None
    print(f"[news_fetcher] Error: {e}")

try:
    from alpaca.data.historical.news import NewsClient, NewsRequest
except Exception as e:
    NewsClient, NewsRequest = None, None
    print(f"[news_fetcher] Alpaca News import warning: {e}")

YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
CACHE_DIR = Path("ingestion/cache")
CACHE_MAX_AGE_HOURS = 6   # cached news older than this is treated as stale

_alpaca_news_client = None


def _get_alpaca_news_client():
    global _alpaca_news_client
    if _alpaca_news_client is not None:
        return _alpaca_news_client
    if NewsClient is None:
        return None
    try:
        from config import get_settings
        settings = get_settings()
        if getattr(settings, "APCA_API_KEY_ID", None) and getattr(settings, "APCA_API_SECRET_KEY", None):
            _alpaca_news_client = NewsClient(
                api_key=settings.APCA_API_KEY_ID,
                secret_key=settings.APCA_API_SECRET_KEY,
            )
            return _alpaca_news_client
    except Exception as e:
        print(f"[news_fetcher] Alpaca NewsClient init error: {e}")
    return None


def fetch_alpaca_news(ticker: str, max_articles: int = 20) -> list[dict]:
    client = _get_alpaca_news_client()
    if client is None:
        return []
    try:
        req = NewsRequest(symbols=ticker.upper(), limit=max_articles)
        res = client.get_news(req)
        raw_items = []
        if hasattr(res, "data") and isinstance(res.data, dict):
            raw_items = res.data.get("news", [])
        elif hasattr(res, "news"):
            raw_items = getattr(res, "news", [])

        results = []
        for item in raw_items:
            norm = _normalize_alpaca(item, ticker.upper())
            if norm:
                results.append(norm)
        return results
    except Exception as e:
        print(f"[alpaca_news] Error fetching {ticker}: {e}")
        return []


def _normalize_alpaca(item, ticker: str) -> dict:
    try:
        if isinstance(item, dict):
            title = item.get("headline", "") or item.get("title", "")
            body = item.get("summary", "") or item.get("content", "")
            created = item.get("created_at") or item.get("updated_at")
            url = item.get("url", "")
            source_name = item.get("source", "benzinga")
            author = item.get("author", "")
        else:
            title = getattr(item, "headline", "") or getattr(item, "title", "")
            body = getattr(item, "summary", "") or getattr(item, "content", "")
            created = getattr(item, "created_at", None) or getattr(item, "updated_at", None)
            url = getattr(item, "url", "")
            source_name = getattr(item, "source", "benzinga")
            author = getattr(item, "author", "")

        pub_str = ""
        if isinstance(created, datetime):
            pub_str = created.isoformat()
        elif created:
            pub_str = str(created)

        norm = {
            "source": f"alpaca_{source_name}",
            "ticker": ticker.upper(),
            "title": str(title).strip(),
            "body": str(body).strip(),
            "published_at": pub_str,
            "url": str(url).strip(),
            "author": str(author).strip(),
        }
        try:
            from data.point_in_time import align_timestamp_point_in_time
            session = align_timestamp_point_in_time(pub_str)
            norm["effective_trade_date"] = session.effective_trade_date
            norm["calendar_date"] = session.calendar_date
            norm["is_after_hours"] = session.is_after_hours
            norm["market_phase"] = session.market_phase
            norm["execution_bar"] = session.execution_bar
        except Exception:
            pass
        return norm
    except Exception as e:
        print(f"[news_fetcher] Alpaca normalize error: {e}")
        return {}


def fetch_news(ticker: str, max_articles: int = 20) -> list[dict]:
    """
    Fetches news for a ticker.
    1. Primary: Alpaca Institutional News API (Benzinga feeds)
    2. Fallback: Yahoo Finance news
    3. Final Fallback: Local news cache
    """
    try:
        # 1. Primary: Alpaca institutional news
        results = fetch_alpaca_news(ticker, max_articles=max_articles)
        if results:
            _save_cache(ticker, results)
            return results

        # 2. Fallback: Yahoo Finance news
        y_results = fetch_yfinance_news(ticker, max_articles=max_articles)
        if y_results:
            return y_results

        # 3. Final Fallback: Local cache
        return _load_cache(ticker)
    except Exception as e:
        print(f"[news_fetcher] Error fetching {ticker}: {e}")
        return _load_cache(ticker)


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
        norm = {
            "source":       "yfinance_news",
            "ticker":       ticker,
            "title":        str(title),
            "body":         str(summary),
            "published_at": _normalize_published_at(provider_time),
            "url":          str(url),
        }
        try:
            from data.point_in_time import align_timestamp_point_in_time
            session = align_timestamp_point_in_time(norm["published_at"])
            norm["effective_trade_date"] = session.effective_trade_date
            norm["calendar_date"] = session.calendar_date
            norm["is_after_hours"] = session.is_after_hours
            norm["market_phase"] = session.market_phase
            norm["execution_bar"] = session.execution_bar
        except Exception:
            pass
        return norm
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

        # Freshness guard: never trade on stale cached headlines.
        # If Yahoo rate-limits us, returning [] is safer than old news.
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600.0
        if age_hours > CACHE_MAX_AGE_HOURS:
            print(f"[news_fetcher] Cache for {ticker} is {age_hours:.1f}h old "
                  f"(limit {CACHE_MAX_AGE_HOURS}h) — ignoring stale news")
            return []

        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[news_fetcher] Error loading cache: {e}")
        return []


def _get_cache_path(ticker: str) -> Path:
    try:
        safe_ticker = str(ticker).upper()
        return CACHE_DIR / f"{safe_ticker}_news.json"
    except Exception as e:
        print(f"[news_fetcher] Error: {e}")
        return Path("ingestion/cache/INVALID_news.json")
