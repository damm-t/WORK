import os
import requests
from dotenv import load_dotenv

load_dotenv()

# SEC requires User-Agent with contact email or they block you
# Add to .env: SEC_USER_AGENT=yourname@gmail.com
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-signal-bot@gmail.com")

BASE_URL = "https://efts.sec.gov/LATEST/search-index"


def fetch_earnings(ticker: str, start_date: str = "2024-01-01") -> list[dict]:
    """
    Fetch 8-K earnings filings for a ticker from SEC EDGAR.
    start_date format: "YYYY-MM-DD"
    Returns normalized list of filing dicts.
    """

    # Always pass headers — SEC blocks requests without User-Agent
    headers = {"User-Agent": SEC_USER_AGENT}

    # params dict — requests builds the URL for you
    # ?q="AAPL"&dateRange=custom&startdt=...&forms=8-K
    params = {
        "q": f'"{ticker}"',       # quotes around ticker = exact match
        "dateRange": "custom",
        "startdt": start_date,
        "forms": "8-K"            # 8-K = material events like earnings
    }

    try:
        # Pass headers separately — not part of params
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()   # throws on 4xx/5xx

        data = response.json()        # requests uses .json(), not .data

        # SEC returns hits inside data["hits"]["hits"]
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            return []

        return [_normalize(hit, ticker) for hit in hits]

    except Exception as e:
        print(f"[earnings_fetcher] Error fetching {ticker}: {e}")  # always print e!
        return []


def _normalize(hit: dict, ticker: str) -> dict:
    """Map a raw SEC EDGAR hit → our standard schema."""

    # SEC nests the useful fields inside hit["_source"]
    source = hit.get("_source", {})

    return {
        "source":       "sec_edgar",
        "ticker":       ticker,
        "title":        source.get("file_date", "") + " — " + source.get("form_type", "8-K"),
        "body":         source.get("period_of_report", ""),  # full text comes in NLP layer
        "published_at": source.get("file_date", "") + "T00:00:00+00:00",
        "url":          f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K"
    }