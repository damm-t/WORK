"""
Autopilot Dead-Man's Switch & Failsafe Daemon
============================================
Monitors autopilot liveness heartbeat (.run/autopilot_heartbeat.json).
If the host Mac drops, restarts, or the autopilot freezes during
regular US market hours while live Alpaca positions remain unmanaged,
this failsafe detects the timeout (>10 minutes) and optionally executes
an emergency safety flatten to prevent naked market exposure.

Usage:
    # Single check (used by watchdog.sh or cron)
    python -m execution.deadmans_switch --check

    # Autonomous watchdog loop
    python -m execution.deadmans_switch --daemon --interval 60

    # Auto-flatten positions if stale (>10 min during market hours)
    python -m execution.deadmans_switch --check --auto-flatten
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from execution.json_state import atomic_json_read, atomic_json_write

logger = logging.getLogger(__name__)

HEARTBEAT_PATH = Path(".run/autopilot_heartbeat.json")
LOG_PATH = Path("logs/deadmans_switch.log")
FLAG_PATH = Path(".run/deadman_triggered.json")
NY_TZ = ZoneInfo("America/New_York")

# Maximum acceptable heartbeat staleness during market hours (in seconds)
DEFAULT_MAX_STALENESS_SECONDS = 600  # 10 minutes


def is_us_equity_market_open() -> bool:
    """Checks whether US equity market is currently open.
    Primary: queries broker exchange clock (Alpaca / client.get_clock()).
    Fallback: local NY clock check with explicit fallback logging.
    """
    try:
        from execution import client
        clock = client.get_clock()
        return bool(getattr(clock, "is_open", False))
    except Exception as e:
        logger.debug(f"[deadmans_switch] Broker clock query failed ({e}); falling back to local NY clock")
        now_ny = datetime.now(NY_TZ)
        if now_ny.weekday() >= 5:  # Saturday or Sunday
            return False
        market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
        return market_open <= now_ny < market_close


def get_autopilot_heartbeat() -> Dict[str, Any]:
    return atomic_json_read(HEARTBEAT_PATH, default={})


def check_liveness(
    max_staleness: int = DEFAULT_MAX_STALENESS_SECONDS,
    auto_flatten: bool = False
) -> Dict[str, Any]:
    """
    Evaluates autopilot heartbeat freshness and open positions.
    Returns status assessment dict.
    """
    now = time.time()
    market_open = is_us_equity_market_open()
    hb = get_autopilot_heartbeat()
    hb_ts = float(hb.get("timestamp", 0.0) or 0.0)
    staleness = round(now - hb_ts, 1) if hb_ts > 0 else None

    report: Dict[str, Any] = {
        "timestamp": now,
        "time_iso": datetime.now(NY_TZ).strftime("%Y-%m-%d %H:%M:%S ET"),
        "market_open": market_open,
        "heartbeat_found": bool(hb),
        "heartbeat_age_seconds": staleness,
        "max_staleness_threshold": max_staleness,
        "is_stale": False,
        "emergency_triggered": False,
        "positions_at_risk": 0,
        "actions_taken": [],
    }

    if staleness is None:
        report["status"] = "NO_HEARTBEAT_FILE"
        report["is_stale"] = True
    elif staleness > max_staleness:
        report["status"] = "STALE"
        report["is_stale"] = True
    else:
        report["status"] = "HEALTHY"
        return report

    # If stale during market hours, inspect position risk
    if market_open and report["is_stale"]:
        logger.warning(
            f"[deadmans_switch] 🚨 AUTOPILOT STALE during market hours! "
            f"Heartbeat age: {staleness}s > {max_staleness}s threshold."
        )

        positions_count = 0
        alpaca_positions = []
        try:
            from execution import client
            alpaca_positions = client.get_all_positions()
            positions_count = len(alpaca_positions)
            report["positions_at_risk"] = positions_count
        except Exception as e:
            logger.error(f"[deadmans_switch] Error fetching Alpaca positions: {e}")
            report["actions_taken"].append(f"Alpaca connection error: {e}")

        # If live positions are unmanaged and auto-flatten is enabled
        should_flatten = auto_flatten or os.getenv("DEADMANS_AUTO_FLATTEN", "0") == "1"
        if positions_count > 0 and should_flatten:
            logger.critical(
                f"[deadmans_switch] 💥 EMERGENCY AUTO-FLATTEN ACTIVATED! "
                f"Liquidating {positions_count} open positions to prevent unmanaged loss."
            )
            report["emergency_triggered"] = True
            try:
                from execution import client
                client.cancel_orders()
                report["actions_taken"].append("Canceled all open bracket/limit orders")
                client.close_all_positions()
                report["actions_taken"].append(f"Liquidated all {positions_count} open positions")
                logger.info("[deadmans_switch] Emergency close completed successfully.")
            except Exception as close_err:
                logger.error(f"[deadmans_switch] Emergency liquidation failed: {close_err}")
                report["actions_taken"].append(f"Liquidation error: {close_err}")

        # Record alert flag
        atomic_json_write(FLAG_PATH, report)

    return report


def run_daemon(interval: int = 60, max_staleness: int = DEFAULT_MAX_STALENESS_SECONDS, auto_flatten: bool = False) -> None:
    """Continuous supervisor loop."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
        ]
    )
    logger.info(
        f"[deadmans_switch] Daemon booted (PID {os.getpid()}). "
        f"Interval: {interval}s, Staleness limit: {max_staleness}s, Auto-flatten: {auto_flatten}"
    )

    while True:
        try:
            res = check_liveness(max_staleness=max_staleness, auto_flatten=auto_flatten)
            if res["status"] != "HEALTHY":
                logger.warning(f"[deadmans_switch] Check result: {res['status']} | detail: {res}")
        except Exception as e:
            logger.error(f"[deadmans_switch] Supervisor cycle error: {e}")

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Autopilot Dead-Man's Switch")
    parser.add_argument("--check", action="store_true", help="Run a single check and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background")
    parser.add_argument("--interval", type=int, default=60, help="Daemon interval in seconds")
    parser.add_argument("--max-staleness", type=int, default=DEFAULT_MAX_STALENESS_SECONDS, help="Staleness threshold (s)")
    parser.add_argument("--auto-flatten", action="store_true", help="Emergency close positions if stale during market hours")
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval=args.interval, max_staleness=args.max_staleness, auto_flatten=args.auto_flatten)
    else:
        res = check_liveness(max_staleness=args.max_staleness, auto_flatten=args.auto_flatten)
        print(f"Status: {res['status']} | Heartbeat Age: {res.get('heartbeat_age_seconds')}s | Market Open: {res['market_open']}")
        if res["is_stale"] and res["market_open"]:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
