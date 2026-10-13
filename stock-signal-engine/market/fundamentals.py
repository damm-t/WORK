"""
Fundamental Analysis & Quality Sanity Module
=============================================
Fetches official US-GAAP quarterly/annual filings from the SEC EDGAR API,
computes solvency/profitability ratios, and evaluates company quality.

Includes 7-day persistent caching in market/cache/fundamentals.json.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "stock-signal-bot@gmail.com")
CACHE_DIR = Path("market/cache")
CACHE_FILE = CACHE_DIR / "fundamentals.json"
CIK_CACHE_FILE = CACHE_DIR / "sec_cik_map.json"
CACHE_MAX_AGE_SECONDS = 7 * 24 * 3600  # 7 days TTL (filings are quarterly)

_cik_map: Optional[dict] = None
_fundamentals_cache: Optional[dict] = None


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _load_cik_map() -> dict:
    global _cik_map
    if _cik_map is not None:
        return _cik_map

    _ensure_cache_dir()
    if CIK_CACHE_FILE.exists():
        try:
            with open(CIK_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    _cik_map = data
                    return _cik_map
        except Exception as e:
            logger.debug(f"[fundamentals] Error loading CIK cache: {e}")

    # Fetch from SEC
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": SEC_USER_AGENT}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            raw = res.json()
            mapping = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in raw.values() if "ticker" in v}
            _cik_map = mapping
            with open(CIK_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(mapping, f)
            return _cik_map
    except Exception as e:
        logger.warning(f"[fundamentals] Failed to fetch CIK map from SEC: {e}")

    _cik_map = {}
    return _cik_map


def _load_fundamentals_cache() -> dict:
    global _fundamentals_cache
    if _fundamentals_cache is not None:
        return _fundamentals_cache

    _ensure_cache_dir()
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _fundamentals_cache = json.load(f)
                return _fundamentals_cache
        except Exception as e:
            logger.debug(f"[fundamentals] Error loading cache: {e}")

    _fundamentals_cache = {}
    return _fundamentals_cache


def _save_fundamentals_cache():
    if _fundamentals_cache is None:
        return
    _ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_fundamentals_cache, f, indent=2)
    except Exception as e:
        logger.debug(f"[fundamentals] Error saving cache: {e}")


def fetch_fundamentals(ticker: str, force_refresh: bool = False) -> dict:
    """
    Retrieves normalized GAAP financial metrics for a ticker.
    Reads from local cache if within 7-day TTL; otherwise queries SEC EDGAR.
    """
    sym = ticker.upper().strip()
    cache = _load_fundamentals_cache()
    now = time.time()

    if not force_refresh and sym in cache:
        entry = cache[sym]
        if now - entry.get("timestamp", 0) < CACHE_MAX_AGE_SECONDS:
            return entry.get("metrics", {})

    cik_map = _load_cik_map()
    cik = cik_map.get(sym)
    if not cik:
        return cache.get(sym, {}).get("metrics", {})

    try:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        headers = {"User-Agent": SEC_USER_AGENT}
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200:
            return cache.get(sym, {}).get("metrics", {})

        data = res.json()
        dei = data.get("facts", {}).get("dei", {})

        def _latest(tags: list[str]) -> Optional[float]:
            for tag in tags:
                for src in (us_gaap, dei):
                    if tag in src:
                        units = src[tag].get("units", {})
                        for u in ("USD", "shares", "USD/shares"):
                            if u in units and units[u]:
                                items = sorted(units[u], key=lambda x: (x.get("filed", ""), x.get("end", "")))
                                val = items[-1].get("val")
                                if val is not None and float(val) > 0:
                                    return float(val)
            return None

        rev = _latest(["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "TotalRevenuesAndOtherIncome"])
        ni = _latest(["NetIncomeLoss", "ProfitLoss"])
        eps = _latest(["EarningsPerShareDiluted", "EarningsPerShareBasic"])
        assets = _latest(["Assets"])
        liab = _latest(["Liabilities"])
        equity = _latest(["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"])
        shares = _latest(["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"])

        margin = (ni / rev * 100.0) if (rev and ni and rev > 0) else None
        debt_to_equity = (liab / equity) if (liab and equity and equity > 0) else None
        roe = (ni / equity * 100.0) if (ni and equity and equity > 0) else None
        is_profitable = (ni is not None and ni > 0) and (eps is not None and eps > 0)

        metrics = {
            "ticker": sym,
            "revenue": rev,
            "net_income": ni,
            "eps": round(eps, 2) if eps is not None else None,
            "assets": assets,
            "liabilities": liab,
            "equity": equity,
            "shares_outstanding": shares,
            "profit_margin_pct": round(margin, 2) if margin is not None else None,
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity is not None else None,
            "roe_pct": round(roe, 2) if roe is not None else None,
            "is_profitable": bool(is_profitable),
        }

        cache[sym] = {"timestamp": now, "metrics": metrics}
        _save_fundamentals_cache()
        return metrics

    except Exception as e:
        logger.debug(f"[fundamentals] Error fetching {sym}: {e}")
        return cache.get(sym, {}).get("metrics", {})


def evaluate_fundamental_quality(ticker: str, sector: Optional[str] = None, max_debt_to_equity: float = 3.5) -> dict:
    """
    Evaluates financial health and calculates fundamental quality points (-15 to +15 scale).

    Quality checks:
      1. Profitable (Net Income > 0 and Diluted EPS > 0) -> +8 pts
      2. Solvency / Healthy Leverage:
         - Standard corporations: Liabilities / Equity <= 2.0 -> +4 pts; > max_debt_to_equity -> passed = False
         - Financials / Real Estate: High leverage is structural (deposits/leases); evaluated via ROE / Margin.
      3. Quality Margins (Net Margin >= 15% or ROE >= 15%) -> +3 pts
      4. Penalties / Gate:
         - Unprofitable (EPS <= 0) -> -15 pts penalty, passed = False
    """
    sym = ticker.upper().strip()
    metrics = fetch_fundamentals(sym)

    if not metrics or metrics.get("eps") is None:
        # Graceful neutral fallback when filing data is pending/unavailable
        return {
            "ticker": sym,
            "passed": True,
            "quality_score": 0.0,
            "reasons": ["Fundamentals unverified (neutral 0)"],
            "metrics": metrics or {},
        }

    reasons = []
    pts = 0.0
    passed = True

    eps = metrics.get("eps")
    is_profitable = metrics.get("is_profitable", False)
    de = metrics.get("debt_to_equity")
    margin = metrics.get("profit_margin_pct")
    roe = metrics.get("roe_pct")
    sec_name = str(sector or "").strip().lower()
    is_asset_levered = "financial" in sec_name or "real estate" in sec_name

    # Check 1: Profitability
    if eps is not None and eps <= 0:
        passed = False
        pts -= 15.0
        reasons.append(f"UNPROFITABLE: Diluted EPS ${eps:.2f} (-15)")
    elif is_profitable:
        pts += 8.0
        reasons.append(f"Profitable: EPS ${eps:.2f} (+8)")

    # Check 2: Solvency & Balance Sheet
    if is_asset_levered:
        # Bank deposits & REIT asset mortgages are structural balance sheet liabilities
        if (roe is not None and roe >= 8.0) or (margin is not None and margin >= 15.0):
            pts += 4.0
            reasons.append(f"Capital efficient {sector} (+4)")
        else:
            reasons.append(f"Standard {sector} balance sheet (+0)")
    elif de is not None:
        if de <= 2.0:
            pts += 4.0
            reasons.append(f"Healthy D/E {de:.1f}x (+4)")
        elif de > max_debt_to_equity:
            passed = False
            reasons.append(f"OVERLEVERAGED: D/E {de:.1f}x exceeds {max_debt_to_equity:.1f}x cap")
        else:
            reasons.append(f"Moderate D/E {de:.1f}x (+0)")

    # Check 3: Margins / Return on Equity
    if margin is not None and margin >= 15.0:
        pts += 3.0
        reasons.append(f"High Margin {margin:.1f}% (+3)")
    elif roe is not None and roe >= 15.0:
        pts += 3.0
        reasons.append(f"Strong ROE {roe:.1f}% (+3)")

    quality_score = round(max(-15.0, min(15.0, pts)), 1)

    return {
        "ticker": sym,
        "passed": passed,
        "quality_score": quality_score,
        "reasons": reasons,
        "metrics": metrics,
    }
