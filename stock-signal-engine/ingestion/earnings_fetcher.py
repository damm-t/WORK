import os
import requests
from dotenv import load_dotenv

load_dotenv()

# SEC requires User-Agent with contact email or they block you
# Add to .env: SEC_USER_AGENT=yourname@gmail.com
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-signal-bot@gmail.com")

BASE_URL = "https://efts.sec.gov/LATEST/search-index"


def fetch_earnings(ticker: str, start_date: str = "2024-01-01", max_filings: int = 10) -> list[dict]:
    headers = {"User-Agent": SEC_USER_AGENT}
    params = {
        "q": f'"{ticker}"',
        "dateRange": "custom",
        "startdt": start_date,
        "forms": "8-K"
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            return []

        return [_normalize(hit, ticker) for hit in hits[:max_filings]]

    except Exception as e:
        print(f"[earnings_fetcher] Error fetching {ticker}: {e}")
        return []


def _normalize(hit: dict, ticker: str) -> dict:
    try:
        source = hit.get("_source", {})
        return {
            "source":       "sec_edgar",
            "ticker":       ticker,
            "title":        source.get("file_date", "") + " — " + source.get("form_type", "8-K"),
            "body":         source.get("period_of_report", ""),
            "published_at": source.get("file_date", "") + "T00:00:00+00:00",
            "url":          f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K"
        }
    except Exception as e:
        print(f"[earnings_fetcher] Error: {e}")
        return {}
