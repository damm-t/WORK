#!/usr/bin/env python3
"""
archive_pre_upgrade_trades.py
-----------------------------
Safely archives historical legacy trades executed before the algorithm upgrade
(asymmetric R:R >= 2.2:1 + unchoked trailing ratchet + self-learning).

Moves pre-upgrade closed trades to execution/*_pre_upgrade_archive.json so that
active closed_trades and session PnL reflect the clean post-upgrade algorithmic performance.
Preserves all-time historical lifetime PnL and trades in the archive.
"""

import json
import time
from pathlib import Path

UPGRADE_TIMESTAMP = 1792460000.0  # Cutoff timestamp for the upgrade overhaul

DESK_SPECS = {
    "crypto_futures": {
        "state_file": "execution/crypto_futures_state.json",
        "archive_file": "execution/crypto_futures_pre_upgrade_archive.json",
        "base_capital": 50000.0,
    },
    "cme_futures": {
        "state_file": "execution/cme_futures_state.json",
        "archive_file": "execution/cme_futures_pre_upgrade_archive.json",
        "base_capital": 25000.0,
    },
    "forex": {
        "state_file": "execution/forex_state.json",
        "archive_file": "execution/forex_pre_upgrade_archive.json",
        "base_capital": 50000.0,
    },
}

def migrate_desk_state(name: str, spec: dict, root: Path):
    state_path = root / spec["state_file"]
    if not state_path.exists():
        print(f"[-] {name}: {state_path} does not exist, skipping.")
        return

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] {name}: Failed to read {state_path}: {e}")
        return

    closed = data.get("closed_trades", [])
    legacy = []
    post_upgrade = []

    for t in closed:
        ts = float(t.get("closed_at", 0) or 0)
        is_post = t.get("post_upgrade", False) or (ts >= UPGRADE_TIMESTAMP)
        if is_post:
            t["post_upgrade"] = True
            post_upgrade.append(t)
        else:
            legacy.append(t)

    # Archive legacy trades
    archive_path = root / spec["archive_file"]
    if legacy:
        existing_archive = []
        if archive_path.exists():
            try:
                existing_archive = json.loads(archive_path.read_text(encoding="utf-8"))
                if not isinstance(existing_archive, list):
                    existing_archive = []
            except Exception:
                existing_archive = []
        existing_archive.extend(legacy)
        archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
        print(f"[+] {name}: Archived {len(legacy)} pre-upgrade trades to {archive_path.name}")

    # Calculate post-upgrade metrics
    post_wins = sum(1 for t in post_upgrade if float(t.get("pnl", 0) or 0) > 0)
    post_wr = round(post_wins / len(post_upgrade) * 100, 1) if post_upgrade else 0.0
    post_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in post_upgrade), 2)

    # Lifetime preservation
    current_lifetime = data.get("lifetime_realized_pnl")
    if current_lifetime is None:
        current_lifetime = data.get("total_realized_pnl", 0.0)

    # Base fund capital
    base_cap = float(data.get("capital") or spec["base_capital"])
    open_positions = data.get("positions", {})
    unrealized_pnl = sum(float(p.get("unrealized_pnl", 0.0) or 0.0) for p in open_positions.values()) if isinstance(open_positions, dict) else 0.0
    
    # Calculate margin held
    if name == "forex":
        margin_held = sum(float(p.get("margin_reserved", 500.0) or 500.0) for p in open_positions.values()) if isinstance(open_positions, dict) else 0.0
    elif name == "cme_futures":
        margin_held = sum(float(p.get("margin_held", 1200.0) or 1200.0) for p in open_positions.values()) if isinstance(open_positions, dict) else 0.0
    else:
        margin_held = sum(float(p.get("contracts", 1) or 1) * float(p.get("entry_price", 0) or 0) / 3.0 for p in open_positions.values()) if isinstance(open_positions, dict) else 0.0

    new_equity = round(base_cap + post_pnl + unrealized_pnl, 2)
    new_cash = round(new_equity - margin_held, 2)

    data["closed_trades"] = post_upgrade
    data["after_change_pnl"] = post_pnl
    data["after_change_win_rate"] = post_wr
    data["after_change_trades_count"] = len(post_upgrade)
    data["after_change_wins"] = post_wins
    data["post_upgrade_pnl"] = post_pnl
    data["post_upgrade_win_rate"] = post_wr
    data["post_upgrade_trades_count"] = len(post_upgrade)
    data["total_realized_pnl"] = post_pnl
    data["lifetime_realized_pnl"] = round(float(current_lifetime), 2)
    data["capital"] = base_cap
    data["equity"] = new_equity
    data["cash"] = new_cash
    data["upgrade_timestamp"] = UPGRADE_TIMESTAMP

    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] {name}: Cleaned state -> {len(post_upgrade)} post-upgrade trades | After-Change PnL: ${post_pnl:+.2f} | Win Rate: {post_wr}% | Equity: ${new_equity:,.2f}")

def main():
    root = Path(__file__).resolve().parents[1]
    print("=== QUANT DESK: POST-UPGRADE TRADE MIGRATION & FUND RESET ===")
    print(f"Upgrade Cutoff Timestamp: {UPGRADE_TIMESTAMP} ({time.ctime(UPGRADE_TIMESTAMP)})")
    for name, spec in DESK_SPECS.items():
        migrate_desk_state(name, spec, root)
    print("=== MIGRATION COMPLETE ===")

if __name__ == "__main__":
    main()
