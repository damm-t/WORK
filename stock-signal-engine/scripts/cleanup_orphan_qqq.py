"""
Script to liquidate and clean up the 2-week orphan QQQ position on Alpaca Paper.
Records the close cleanly in SQLite trade_journal.db and purges stale state from autopilot_state.json.
"""

import sys
import time
from pathlib import Path

# Add repo root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from execution.alpha_client import get_client, submit_market_order
from execution.json_state import atomic_json_read, atomic_json_write
from execution.trade_journal import journal

STATE_PATH = Path("execution/autopilot_state.json")


def main():
    client = get_client()
    print("=" * 60)
    print("   DESK 1: ORPHAN QQQ CLEANUP & PORTFOLIO RECONCILIATION")
    print("=" * 60)

    account = client.get_account()
    print(f"Current Equity: ${float(account.equity):,.2f}")

    positions = client.get_all_positions()
    qqq_pos = None
    for p in positions:
        if str(p.symbol).upper() == "QQQ":
            qqq_pos = p
            break

    if not qqq_pos:
        print("✅ No open QQQ position found in Alpaca account. Already clean!")
    else:
        qty = int(abs(float(qqq_pos.qty)))
        entry_px = float(qqq_pos.avg_entry_price)
        curr_px = float(qqq_pos.current_price)
        unrealized = float(qqq_pos.unrealized_pl)
        print(f"⚠️ Found Orphan QQQ Position:")
        print(f"   Quantity     : {qty} shares")
        print(f"   Entry Price  : ${entry_px:.2f}")
        print(f"   Current Price: ${curr_px:.2f}")
        print(f"   Unrealized PL: ${unrealized:,.2f}")

        print("Executing Market Order to liquidate orphan QQQ...")
        res = submit_market_order(client, "QQQ", qty, side="SELL")
        print(f"Order Result: {res}")

        # Record close in trade journal
        try:
            journal.record_close("QQQ", curr_px, "orphan_cleanup", pnl=unrealized)
            print(f"✅ Recorded QQQ close in execution/trade_journal.db (PnL ${unrealized:,.2f})")
        except Exception as e:
            print(f"Note recording to journal: {e}")

    # Reconcile autopilot_state.json
    state = atomic_json_read(STATE_PATH, default={})
    stale_keys = [k for k in state.keys() if not str(k).startswith("_")]
    if stale_keys:
        print(f"Cleaning {len(stale_keys)} stale symbols from autopilot_state.json: {stale_keys}")
        for k in stale_keys:
            state.pop(k, None)
        atomic_json_write(STATE_PATH, state)
        print("✅ autopilot_state.json reconciled successfully.")

    time.sleep(2)
    post_account = client.get_account()
    remaining = client.get_all_positions()
    print("-" * 60)
    print(f"Post-cleanup Equity : ${float(post_account.equity):,.2f}")
    print(f"Post-cleanup Cash   : ${float(post_account.cash):,.2f}")
    print(f"Remaining Positions : {len(remaining)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
