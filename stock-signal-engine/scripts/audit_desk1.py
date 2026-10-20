import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.alpha_client import get_client, get_portfolio_value
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

def main():
    client = get_client()
    account = client.get_account()
    print("=" * 60)
    print("   DESK 1: US EQUITIES (ALPACA PAPER) AUDIT REPORT")
    print("=" * 60)
    print(f"Equity       : ${float(account.equity):,.2f}")
    print(f"Cash         : ${float(account.cash):,.2f}")
    print(f"Buying Power : ${float(account.buying_power):,.2f}")
    print(f"Portfolio Val: ${get_portfolio_value(client):,.2f}")
    print(f"Status       : {account.status}")
    print("-" * 60)

    # Active positions
    positions = client.get_all_positions()
    print(f"Active Positions ({len(positions)}):")
    for p in positions:
        cost = float(p.cost_basis)
        market_val = float(p.market_value)
        unrealized_pl = float(p.unrealized_pl)
        unrealized_plpc = float(p.unrealized_plpc) * 100
        print(f"  • {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f}")
        print(f"    Current Price: ${float(p.current_price):.2f}")
        print(f"    Market Value : ${market_val:,.2f} (Cost Basis: ${cost:,.2f})")
        print(f"    Unrealized PL: ${unrealized_pl:,.2f} ({unrealized_plpc:+.2f}%)")

    print("-" * 60)
    # Closed orders
    orders = client.get_orders(GetOrdersRequest(status=QueryOrderStatus.CLOSED, limit=40))
    print(f"Recent Closed Orders ({len(orders)}):")
    for o in orders:
        filled_price = float(o.filled_avg_price) if o.filled_avg_price else 0.0
        submitted = o.submitted_at.strftime("%Y-%m-%d %H:%M") if o.submitted_at else "N/A"
        filled_at = o.filled_at.strftime("%Y-%m-%d %H:%M") if o.filled_at else "N/A"
        print(f"  [{submitted}] {o.side.value.upper():4s} {float(o.qty):6.1f} {o.symbol:5s} @ ${filled_price:7.2f} | Status: {o.status.value} (Filled: {filled_at})")

    print("-" * 60)
    # Search all orders for QQQ
    qqq_orders = client.get_orders(GetOrdersRequest(status=QueryOrderStatus.ALL, symbols=["QQQ"], limit=50))
    print(f"QQQ Order History ({len(qqq_orders)}):")
    for o in qqq_orders:
        filled_price = float(o.filled_avg_price) if o.filled_avg_price else 0.0
        submitted = o.submitted_at.strftime("%Y-%m-%d %H:%M") if o.submitted_at else "N/A"
        filled_at = o.filled_at.strftime("%Y-%m-%d %H:%M") if o.filled_at else "N/A"
        print(f"  [{submitted}] {o.side.value.upper():4s} {float(o.qty):6.1f} {o.symbol} @ ${filled_price:.2f} | Status: {o.status.value} (Filled: {filled_at})")

    print("-" * 60)
    # SQLite Trade Journal Audit
    import sqlite3
    db_path = "execution/trade_journal.db"
    p = Path(db_path)
    if p.exists():
        print(f"Trade Journal ({db_path}):")
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT id, ticker, entry, exit, pnl, reason, grade, style, book, hedge FROM trades WHERE closed_at IS NOT NULL ORDER BY id ASC")
        rows = cur.fetchall()
        print(f"  Total Closed Trades: {len(rows)}")
        wins = [r for r in rows if (r[4] or 0.0) > 0]
        losses = [r for r in rows if (r[4] or 0.0) < 0]
        tot_pnl = sum(r[4] or 0.0 for r in rows)
        avg_w = (sum(r[4] for r in wins) / len(wins)) if wins else 0.0
        avg_l = (sum(r[4] for r in losses) / len(losses)) if losses else 0.0
        print(f"  Total Realized PnL : ${tot_pnl:,.2f}")
        print(f"  Wins: {len(wins)} (Avg: +${avg_w:.2f})")
        print(f"  Losses: {len(losses)} (Avg: -${abs(avg_l):.2f})")
        print(f"  Realized Win/Loss Ratio: {avg_w / abs(avg_l) if avg_l != 0 else 0:.2f} : 1.0")

        print("  All Closed Trades:")
        for r in rows:
            print(f"    #{r[0]:2d} {r[1]:5s} entry=${r[2] or 0:7.2f} exit=${r[3] or 0:7.2f} pnl=${r[4] or 0:8.2f} | Reason: {r[5]} (Grade: {r[6]}, Style: {r[7]}, Book: {r[8]}, Hedge: {r[9]})")
        conn.close()



if __name__ == "__main__":
    main()
