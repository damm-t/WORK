"""
Shock Detector — handling the UNEXPECTED
========================================
Backtests know every flip in advance; live trading does not. This module
gives the system reflexes for surprise data:

  1. GAP SHOCK    price gapped/moved vs previous close beyond threshold
  2. VELOCITY     violent move within the last ~30 minutes of intraday bars
  3. EARNINGS     blackout window around scheduled earnings (no new entries)

Philosophy: we never predict the flip — we DETECT it within minutes of the
5-minute bars printing it, then hand the decision to pre-built playbooks
(freeze entries / shock-exit / tighten stops).

All thresholds configurable via env:
    GAP_SHOCK_PCT (2.5) · VELOCITY_SHOCK_PCT (1.2) · EARNINGS_BLACKOUT_DAYS (1)
"""

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd

from market.price_fetcher import fetch_prices

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
except Exception as e:                                    # pragma: no cover
    yf = None
    logger.warning(f"[shock_detector] yfinance unavailable: {e}")


def _env_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def gap_shock_threshold() -> float:
    return _env_float("GAP_SHOCK_PCT", 2.5)


def velocity_shock_threshold() -> float:
    return _env_float("VELOCITY_SHOCK_PCT", 2.8)


def detect_intraday_shock(ticker: str,
                          df_intraday: Optional[pd.DataFrame] = None,
                          prev_close: Optional[float] = None) -> Dict[str, Any]:
    """
    Pulls today's 5-minute bars (or uses supplied frame) and answers ONE
    question: is this ticker in an abnormal move RIGHT NOW?

    Returns dict:
        status, shocked(bool), direction('up'/'down'/'flat'),
        gap_pct (vs prev close, if known), velocity_pct (last ~30min),
        thresholds used.
    """
    t = ticker.upper().strip()
    gap_thr = gap_shock_threshold()
    vel_thr = velocity_shock_threshold()

    if df_intraday is None:
        df_intraday = fetch_prices(t, period="1d", interval="5m")

    # --- PROJECT OMEGA: Circuit Breaker & Market Halt Detection ---
    if df_intraday is None or df_intraday.empty or len(df_intraday) < 3:
        # If US equity market is active, missing intraday bars is an exchange halt signature
        try:
            from execution.deadmans_switch import is_us_equity_market_open
            if is_us_equity_market_open():
                reasons = ["Exchange circuit halt / data void during active market hours"]
                return {
                    "status": "market_halt",
                    "ticker": t,
                    "shocked": True,
                    "circuit_breaker": True,
                    "direction": "down",
                    "last_price": float(prev_close) if prev_close else None,
                    "gap_pct": None,
                    "velocity_pct": 0.0,
                    "thresholds": {"gap_pct": gap_thr, "velocity_pct": vel_thr},
                    "reasons": reasons,
                    "detail": reasons[0],
                }
        except Exception:
            pass

        # Check pre-market quote or snapshot against prev_close if available
        if prev_close and float(prev_close) > 0:
            quote_price = None
            try:
                from market.price_fetcher import fetch_latest_price
                quote_price = fetch_latest_price(t)
            except Exception as p_err:
                logger.debug(f"[shock_detector] fetch_latest_price fallback: {p_err}")

            if quote_price and quote_price > 0:
                gap_pct = (quote_price / float(prev_close) - 1.0) * 100.0
                if abs(gap_pct) >= gap_thr:
                    direction = "down" if gap_pct < 0 else "up"
                    reasons = [f"pre-market/halt gap {gap_pct:+.2f}% (±{gap_thr}%)"]
                    return {
                        "status": "halt_gap",
                        "ticker": t,
                        "shocked": True,
                        "circuit_breaker": True,
                        "direction": direction,
                        "last_price": round(quote_price, 2),
                        "gap_pct": round(gap_pct, 2),
                        "velocity_pct": 0.0,
                        "thresholds": {"gap_pct": gap_thr, "velocity_pct": vel_thr},
                        "reasons": reasons,
                        "detail": reasons[0],
                    }
            pass

        return {"status": "no_data", "ticker": t, "shocked": False}

    closes = df_intraday["Close"]
    last = float(closes.iloc[-1])

    # --- velocity: move over roughly the last 30 minutes (6 x 5m bars) ------
    lookback = min(len(closes) - 1, 6)
    base_vel = float(closes.iloc[-1 - lookback])
    velocity_pct = (last / base_vel - 1.0) * 100.0 if base_vel else 0.0

    # --- gap vs previous close (caller supplies, else derive from daily) ----
    gap_pct = None
    if prev_close:
        gap_pct = (last / float(prev_close) - 1.0) * 100.0

    vel_shock = abs(velocity_pct) >= vel_thr
    gap_shock = gap_pct is not None and abs(gap_pct) >= gap_thr
    shocked = bool(vel_shock or gap_shock)
    direction = "down" if (velocity_pct < 0 or (gap_pct or 0) < 0) else "up"

    reasons = []
    if gap_shock:
        reasons.append(f"gap {gap_pct:+.2f}% (±{gap_thr}%)")
    if vel_shock:
        reasons.append(f"velocity {velocity_pct:+.2f}%/{lookback * 5}min "
                       f"(±{vel_thr}%)")

    return {
        "status": "ok",
        "ticker": t,
        "shocked": shocked,
        "direction": direction,
        "last_price": round(last, 2),
        "gap_pct": round(gap_pct, 2) if gap_pct is not None else None,
        "velocity_pct": round(velocity_pct, 2),
        "thresholds": {"gap_pct": gap_thr, "velocity_pct": vel_thr},
        "reasons": reasons,
        "detail": "; ".join(reasons) if reasons else "normal tape",
    }


def earnings_blackout(ticker: str, days: int = None) -> Dict[str, Any]:
    """
    Best-effort check: is scheduled earnings within `days` trading days?
    Unknown data => NOT blacked out (returns False) but flagged unknown.
    """
    days = int(days if days is not None
               else os.getenv("EARNINGS_BLACKOUT_DAYS", "1"))
    t = ticker.upper().strip()
    info: Dict[str, Any] = {"ticker": t, "blackout": False, "unknown": False,
                            "days": days}
    if yf is None or days <= 0:
        info["unknown"] = True
        return info

    yf_log = logging.getLogger("yfinance")
    prev_level = yf_log.level
    yf_log.setLevel(logging.CRITICAL)                 # silence 429 spam
    try:
        cal = yf.Ticker(t).calendar or {}
        dates = cal.get("Earnings Date") or []
        if not isinstance(dates, list):
            dates = [dates]
        if not dates:
            info["unknown"] = True
            return info
        next_date = pd.Timestamp(min(dates)).tz_localize(None)
        days_until = (next_date - pd.Timestamp.today().normalize()).days
        info["next_earnings"] = str(next_date.date())
        info["days_until"] = int(days_until)
        info["blackout"] = 0 <= days_until <= days
    except Exception as e:                                # noqa: BLE001
        logger.debug(f"[shock_detector] earnings lookup failed {t}: {e}")
        info["unknown"] = True
        try:
            from market.fundamentals import fetch_company_profile
            prof = fetch_company_profile(t)
            if prof and prof.get("next_earnings_date"):
                next_date = pd.Timestamp(prof["next_earnings_date"]).tz_localize(None)
                days_until = (next_date - pd.Timestamp.today().normalize()).days
                info["next_earnings"] = str(next_date.date())
                info["days_until"] = int(days_until)
                info["blackout"] = 0 <= days_until <= days
                info["unknown"] = False
        except Exception:
            pass
    finally:
        yf_log.setLevel(prev_level)
    return info


def fetch_prev_close(ticker: str) -> Optional[float]:
    """Previous session close (for gap math) from short daily history."""
    try:
        df = fetch_prices(ticker.upper(), period="5d", interval="1d")
        if df is not None and len(df) >= 2:
            return float(df["Close"].iloc[-2])
    except Exception as e:                                # noqa: BLE001
        logger.debug(f"[shock_detector] prev close failed {ticker}: {e}")
    return None