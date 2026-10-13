"""
Quant Desk Dashboard — one-command HTML report
==============================================
Generates a single self-contained dashboard.html (no web framework, no
external JS) showing:

    • Account snapshot          (Alpaca paper equity / positions)
    • Journal analytics         (win rate, R:R, grade/session breakdowns)
    • Recent trades ledger      (last 50 with grades & reasons)
    • Market leaderboard        (live sector-ranked top candidates)
    • Tuning suggestions        (the auto-balance output)

Usage:
    python -m reports.dashboard                 # real data
    python -m reports.dashboard --demo          # seeded sample data
    python -m reports.dashboard --serve         # also serve on :8999
"""

import argparse
import contextlib
import html
import io
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

OUT_PATH = Path("reports/dashboard.html")

CSS = """
body{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;background:#0b1220;
     color:#e6edf3;margin:0;padding:24px}
h1{margin:0 0 4px} h2{margin-top:28px;border-bottom:1px solid #22304a;
   padding-bottom:6px;color:#8ab4ff}
.sub{color:#7d8590;margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
      gap:14px}
.card{background:#111a2c;border:1px solid #22304a;border-radius:12px;
      padding:16px}
.card .k{color:#7d8590;font-size:12px;text-transform:uppercase;letter-spacing:.08em}
.card .v{font-size:26px;font-weight:700;margin-top:6px}
.good{color:#3fb950}.bad{color:#f85149}.warn{color:#d29922}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}
th{text-align:left;color:#7d8590;border-bottom:1px solid #22304a;padding:6px}
td{padding:6px;border-bottom:1px solid #16213a}
.pos{color:#3fb950}.neg{color:#f85149}
.sugg{background:#1c1633;border-left:4px solid #d29922;padding:10px 14px;
      margin:8px 0;border-radius:6px}
.pill{display:inline-block;background:#1c2536;border:1px solid #2c3a55;
      border-radius:999px;padding:2px 10px;margin:2px;font-size:12px}
.bar-bg{background:#1b2740;border-radius:4px;height:10px;width:100%}
.bar-fg{height:10px;border-radius:4px}
footer{margin-top:30px;color:#7d8590;font-size:12px}
"""


def _fmt_ts(ts) -> str:
    if not ts:
        return "—"
    return datetime.fromtimestamp(float(ts)).strftime("%m-%d %H:%M")


def _wr_color(wr) -> str:
    if wr is None:
        return ""
    return "good" if wr >= 55 else ("warn" if wr >= 40 else "bad")


# ------------------------------------------------------------- data loaders -
def load_journal(db_override=None):
    """Returns (analytics dict, recent trades list)."""
    import execution.trade_journal as tj
    if db_override:
        tj.DB_PATH = Path(db_override)
    j = tj.TradeJournal(tj.DB_PATH)

    conn = j._conn()
    rows = conn.execute(
        """SELECT ticker, opened_at, closed_at, qty, entry, exit,
                  reason, pnl, grade, score
           FROM trades ORDER BY id DESC LIMIT 50""").fetchall()
    conn.close()

    trades = [{
        "ticker": t, "opened": _fmt_ts(o), "closed": _fmt_ts(c),
        "qty": q, "entry": e, "exit": x,
        "reason": r or "", "pnl": float(p or 0.0),
        "grade": g or "—", "score": s,
    } for t, o, c, q, e, x, r, p, g, s in rows]
    return j.analytics(), trades


def load_leaderboard(top: int = 10):
    """Live market ranking; scanner prints verbosely -> silence it."""
    try:
        from backtest.market_scanner import rank_market
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rows = rank_market(top_n=top)
        return rows, None
    except Exception as e:                                # noqa: BLE001
        return [], f"scanner unavailable: {e}"


def load_account() -> dict:
    try:
        from execution import client
        acct = client.get_account()
        positions = [{"symbol": p.symbol, "qty": p.qty,
                      "avg": float(p.avg_entry_price),
                      "now": float(p.current_price),
                      "pnl_pct": float(p.unrealized_pl)}
                     for p in client.get_all_positions()]
        return {"equity": float(acct.equity), "cash": float(acct.cash),
                "positions": positions}
    except Exception as e:                                # noqa: BLE001
        return {"error": str(e)}


# --------------------------------------------------------------- rendering --
def _esc(s) -> str:
    return html.escape(str(s))


def render_page(analytics: dict, trades: list, board: list,
                scan_note: str, account: dict, demo: bool,
                refresh_seconds: int = 0) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = []
    a = parts.append

    refresh_meta = (f"<meta http-equiv='refresh' content='{refresh_seconds}'>"
                    if refresh_seconds else "")
    a(f"<!doctype html><html><head><meta charset='utf-8'>{refresh_meta}"
      f"<title>Quant Desk</title><style>{CSS}</style></head><body>")
    a("<h1>📈 Quant Desk — Scenario C Command Center</h1>"
      f"<div class='sub'>generated {now}"
      f"{' · DEMO DATA' if demo else ''} · refresh: "
      f"<code>python -m reports.dashboard{' --demo' if demo else ''}</code></div>")

    ov = analytics.get("overall", {})
    wr = ov.get("win_rate")
    wr_cls = _wr_color(wr)
    eq = account.get("equity")

    a("<div class='grid'>")
    if eq is not None:
        a(f"<div class='card'><div class='k'>Account Equity (paper)</div>"
          f"<div class='v'>${eq:,.2f}</div></div>")
    else:
        a("<div class='card'><div class='k'>Account Equity</div>"
          "<div class='v warn'>offline</div></div>")
    a(f"<div class='card'><div class='k'>Closed Trades</div>"
      f"<div class='v'>{ov.get('n', 0)}</div></div>")
    a(f"<div class='card'><div class='k'>Win Rate</div>"
      f"<div class='v {wr_cls}'>{wr if wr is not None else '—'}"
      f"{'%' if wr is not None else ''}</div></div>")
    rr = analytics.get("reward_risk")
    a(f"<div class='card'><div class='k'>Reward : Risk</div>"
      f"<div class='v'>{rr if rr is not None else '—'}</div></div>")
    tot = ov.get("total", 0.0)
    cls_tot = "pos" if tot >= 0 else "neg"
    a(f"<div class='card'><div class='k'>Journal P&L</div>"
      f"<div class='v {cls_tot}'>${tot:,.2f}</div></div>")
    a("</div>")

    a("<h2>🧠 Auto-Balance Suggestions</h2>")
    suggs = analytics.get("suggestions") or []
    if suggs:
        for s in suggs:
            a(f"<div class='sugg'>⚖️ {_esc(s)}</div>")
    else:
        a("<div class='sugg'>✅ No adjustments suggested — keep executing.</div>")

    # ---- grade breakdown with mini bars ------------------------------------
    a("<h2>Performance by Grade</h2><table><tr><th>Grade</th><th>Trades</th>"
      "<th>Win rate</th><th>Avg P&L</th><th>Total</th><th></th></tr>")
    grade_items = sorted(analytics.get("by_grade", {}).items())
    max_abs = max([abs(v.get("total") or 0) for _, v in grade_items] or [1])
    for g, st in grade_items:
        wr_g = st.get("win_rate")
        cls = _wr_color(wr_g)
        total = st.get("total") or 0
        width = min(100.0, abs(total) / max_abs * 100) if max_abs else 0
        color = "#3fb950" if total >= 0 else "#f85149"
        tcls = "pos" if total >= 0 else "neg"
        a(f"<tr><td><b>{_esc(g)}</b></td><td>{st['n']}</td>"
          f"<td class='{cls}'>{wr_g if wr_g is not None else '—'}"
          f"{'%' if wr_g is not None else ''}</td>"
          f"<td>${st.get('avg_pnl', 0):,.2f}</td>"
          f"<td class='{tcls}'>${total:,.2f}</td>"
          f"<td><div class='bar-bg'><div class='bar-fg' "
          f"style='width:{width:.0f}%;background:{color}'></div></div></td></tr>")
    a("</table>")

    # ---- session timing -----------------------------------------------------
    a("<h2>Session Timing (US/Eastern entry hour)</h2>"
      "<table><tr><th>Session</th><th>Trades</th><th>Win rate</th>"
      "<th>Total P&L</th></tr>")
    for b, st in sorted(analytics.get("by_session", {}).items()):
        cls = _wr_color(st.get("win_rate"))
        total = st.get("total") or 0
        tcls = "pos" if total >= 0 else "neg"
        wr_s = st.get("win_rate")
        a(f"<tr><td>{_esc(b)}</td><td>{st['n']}</td>"
          f"<td class='{cls}'>{wr_s if wr_s is not None else '—'}%</td>"
          f"<td class='{tcls}'>${total:,.2f}</td></tr>")
    a("</table>")

    # ---- leaderboard --------------------------------------------------------
    a("<h2>🔎 Market Leaderboard (live)</h2>")
    if scan_note:
        a(f"<div class='sugg'>{_esc(scan_note)}</div>")
    for i, r in enumerate(board[:10], 1):
        a(f"<span class='pill'>#{i} <b>{_esc(r['ticker'])}</b> "
          f"[{_esc(r['sector'])}] {r['score']}/100</span>")

    # ---- open positions ------------------------------------------------------
    if account.get("positions"):
        a("<h2>💼 Open Positions (Alpaca paper)</h2><table>"
          "<tr><th>Symbol</th><th>Qty</th><th>Avg</th><th>Now</th>"
          "<th>P&L %</th></tr>")
        for p in account["positions"]:
            cls = "pos" if p["pnl_pct"] >= 0 else "neg"
            a(f"<tr><td><b>{_esc(p['symbol'])}</b></td><td>{p['qty']}</td>"
              f"<td>${p['avg']:,.2f}</td><td>${p['now']:,.2f}</td>"
              f"<td class='{cls}'>{p['pnl_pct']:+.2f}%</td></tr>")
        a("</table>")

    # ---- trade ledger ---------------------------------------------------------
    a(f"<h2>📒 Recent Trades (last {len(trades)})</h2>")
    if trades:
        a("<table><tr><th>Ticker</th><th>Opened</th><th>Closed</th>"
          "<th>Qty</th><th>Entry</th><th>Exit</th><th>Reason</th>"
          "<th>Grade</th><th>P&L</th></tr>")
        for t in trades:
            cls = "pos" if t["pnl"] >= 0 else "neg"
            closed = t["closed"] if t["closed"] != "—" else "OPEN"
            a(f"<tr><td><b>{_esc(t['ticker'])}</b></td>"
              f"<td>{t['opened']}</td><td>{closed}</td><td>{t['qty']}</td>"
              f"<td>${t['entry']:,.2f}</td><td>${t['exit']:,.2f}</td>"
              f"<td>{_esc(t['reason'])}</td><td>{_esc(t['grade'])}</td>"
              f"<td class='{cls}'>${t['pnl']:,.2f}</td></tr>")
        a("</table>")
    else:
        a("<div class='sugg'>No trades yet — the journal fills as Scenario C "
          "executes.</div>")

    a("<footer>Stock Signal Engine · Quant Desk · paper trading only · "
      "not financial advice</footer></body></html>")
    return "".join(parts)


# ------------------------------------------------------------------ demo ----
def seed_demo(db_path: Path) -> None:
    """Populates a throwaway DB so the layout can be previewed."""
    import execution.trade_journal as tj
    tj.DB_PATH = db_path
    if db_path.exists():
        db_path.unlink()
    j = tj.TradeJournal(db_path)

    samples = [
        ("FCX", 30, 79.0, 84.0, "A", 88), ("FCX", 25, 82.0, 88.5, "A", 91),
        ("V",   12, 384.0, 391.0, "B", 72),
        ("META", 5, 300.0, 296.0, "B", 58), ("META", 5, 296.0, 291.0, "B", 55),
        ("TSLA", 4, 350.0, 348.0, "C", 61), ("MSFT", 6, 488.0, 497.0, "B", 67),
    ]
    for ticker, qty, entry, exitp, grade, score in samples:
        j.record_open(ticker, qty, entry,
                      hedge="SH x10", grade=grade,
                      regime="BULL_MOMENTUM", score=score)
        j.record_close(ticker, exitp, "stop")


# -------------------------------------------------------------------- CLI ---
def main() -> None:
    parser = argparse.ArgumentParser(description="Quant Desk HTML Dashboard")
    parser.add_argument("--demo", action="store_true",
                        help="render with seeded sample trades")
    parser.add_argument("--top", type=int, default=10,
                        help="leaderboard depth")
    parser.add_argument("--watch", type=int, default=0, metavar="SECONDS",
                        help="LIVE mode: regenerate + auto-refresh browser "
                             "every N seconds (e.g. --watch 60)")
    parser.add_argument("--serve", action="store_true",
                        help="also serve the report at http://localhost:8999")
    args = parser.parse_args()

    demo = args.demo
    tmp_db = None
    if demo:
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp(prefix="quantdesk_demo_"))
        tmp_db = tmp_dir / "demo.db"
        seed_demo(tmp_db)

    def generate_once() -> None:
        analytics, trades = load_journal(tmp_db)
        board, scan_note = load_leaderboard(top=args.top)
        account = {"equity": None, "cash": None, "positions": []} \
            if demo else load_account()
        if demo:
            account.update({"equity": 112.40, "cash": 12.40,
                            "positions": [
                                {"symbol": "FCX", "qty": "9", "avg": 79.0,
                                 "now": 84.2, "pnl_pct": 6.58},
                                {"symbol": "SH", "qty": "40", "avg": 12.1,
                                 "now": 11.8, "pnl_pct": -2.48}]})
        page = render_page(analytics, trades, board, scan_note, account,
                           demo, refresh_seconds=args.watch)
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(page, encoding="utf-8")

    generate_once()
    print(f"✅ dashboard written -> {OUT_PATH.resolve()}")

    if args.watch:
        print(f"🔴 LIVE MODE: regenerating every {args.watch}s "
              f"(Ctrl+C to stop). Keep the page open — it self-refreshes.")
        try:
            while True:
                time.sleep(args.watch)
                try:
                    generate_once()
                    stamp = datetime.now().strftime("%H:%M:%S")
                    print(f"  [{stamp}] refreshed")
                except Exception as e:                    # noqa: BLE001
                    print(f"  refresh error: {e}")
        except KeyboardInterrupt:
            print("\ndashboard stopped.")
            return

    if args.serve:
        import http.server
        import webbrowser

        handler = lambda *ar, **kw: http.server.SimpleHTTPRequestHandler(
            *ar, directory=str(OUT_PATH.parent.resolve()), **kw)
        print("serving at http://localhost:8999/dashboard.html (Ctrl+C to stop)")
        webbrowser.open("http://localhost:8999/dashboard.html")
        http.server.HTTPServer(("127.0.0.1", 8999), handler).serve_forever()


if __name__ == "__main__":
    main()