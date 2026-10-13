"""
Quant Desk Live — True Web App (FastAPI + polling SPA)
======================================================
Run:  ./run_webapp.sh          (http://localhost:8081)

Read APIs (no auth, localhost):
    GET /api/account            equity, cash, open positions
    GET /api/journal/summary    stats + analytics + suggestions
    GET /api/journal/trades     last N ledger rows
    GET /api/scan?top=N         market leaderboard (5-min TTL cache)
    GET /api/regime             SPY regime snapshot
Action API (requires X-Dash-Token: INTERNAL_API_KEY):
    POST /api/actions/flatten   {"ticker": "NVDA"}  -> market-exit + cancel stops
    POST /api/actions/rescan    force leaderboard refresh
"""

import contextlib
import io
import json
import logging
import os
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

import hashlib
import hmac
import uvicorn
from fastapi import Body, FastAPI, Header, HTTPException, Request, Query
from fastapi.responses import FileResponse, Response, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_settings                       # noqa: E402
from execution.trade_journal import journal           # noqa: E402
from execution.json_state import atomic_json_read     # noqa: E402

settings = get_settings()
logger = logging.getLogger("uvicorn.error")
STATIC_DIR = Path(__file__).resolve().parent / "static"

_APP_START_TIME = time.time()

# Configure log rotation for webapp.log and logs/webapp.log (50MB, max 5 backups)
for log_filename in ["webapp.log", "logs/webapp.log"]:
    try:
        Path(log_filename).parent.mkdir(parents=True, exist_ok=True)
        rf_handler = RotatingFileHandler(
            log_filename, maxBytes=50 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        rf_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(rf_handler)
        logging.getLogger("uvicorn.error").addHandler(rf_handler)
    except Exception:
        pass

try:
    from loguru import logger as loguru_logger
    loguru_logger.add("webapp.log", rotation="50 MB", retention="7 days", enqueue=True)
    loguru_logger.add("logs/webapp.log", rotation="50 MB", retention="7 days", enqueue=True)
except Exception:
    pass

DASHBOARD_PIN = str(getattr(settings, "DASHBOARD_PIN", "8888") or "8888").strip()
_PIN_AUTH_TOKEN = hmac.new(
    (getattr(settings, "INTERNAL_API_KEY", "") or "quantdesk_secure_salt").encode(),
    f"pin_auth_{DASHBOARD_PIN}".encode(),
    hashlib.sha256,
).hexdigest()

# Sliding-window IP rate limiting for PIN verification brute-force defense
_pin_attempt_history: Dict[str, List[float]] = defaultdict(list)
_pin_lockout_until: Dict[str, float] = {}
_MAX_PIN_ATTEMPTS = 5
_PIN_WINDOW_SECONDS = 60
_PIN_LOCKOUT_SECONDS = 300

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quant Desk Live", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _is_request_authenticated(request: Request) -> bool:
    """Check if request is authorized via PIN HMAC token cookie, header, or localhost loopback."""
    client_host = request.client.host if request.client else ""
    has_proxy_header = bool(
        request.headers.get("x-forwarded-for") or
        request.headers.get("cf-connecting-ip") or
        request.headers.get("cf-ray") or
        request.headers.get("x-real-ip")
    )

    token = (
        request.cookies.get("dash_pin_token") or
        request.headers.get("x-dash-pin-token")
    )
    if token and hmac.compare_digest(str(token), _PIN_AUTH_TOKEN):
        return True

    # Permit direct loopback (localhost/testclient) when not arriving from a public tunnel/proxy
    if (client_host in ("127.0.0.1", "::1", "localhost", "testclient")) and not has_proxy_header:
        return True

    return False


@app.middleware("http")
async def pin_auth_middleware(request: Request, call_next):
    path = request.url.path
    is_public = (
        path in ("/", "/widget", "/overview", "/terminal", "/legacy", "/office", "/graph", "/manifest.json", "/favicon.ico", "/health", "/api/health") or
        path.startswith("/static") or
        path.startswith("/api/auth") or
        path.startswith("/api/remote-access") or
        path.startswith("/api/graphify") or
        path.startswith("/docs") or
        path.startswith("/openapi")
    )
    if is_public:
        return await call_next(request)

    if path.startswith("/api/"):
        if not _is_request_authenticated(request):
            return JSONResponse(
                status_code=401,
                content={"detail": "PIN authentication required", "pin_required": True}
            )

    return await call_next(request)


class PinVerifyRequest(BaseModel):
    pin: str


@app.post("/api/auth/verify-pin")
def api_verify_pin(body: PinVerifyRequest, request: Request, response: Response) -> dict:
    client_ip = (
        request.headers.get("cf-connecting-ip") or
        request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
        (request.client.host if request.client else "unknown")
    )
    now = time.time()

    # Check active lockout
    locked_until = _pin_lockout_until.get(client_ip, 0.0)
    if now < locked_until:
        rem_seconds = int(locked_until - now)
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed PIN attempts. Locked out for {rem_seconds} more seconds."
        )

    pin = str(body.pin).strip()
    if pin == DASHBOARD_PIN:
        _pin_attempt_history.pop(client_ip, None)
        _pin_lockout_until.pop(client_ip, None)
        response.set_cookie(
            key="dash_pin_token",
            value=_PIN_AUTH_TOKEN,
            max_age=30 * 86400,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return {"success": True, "token": _PIN_AUTH_TOKEN, "detail": "PIN verified successfully"}

    history = [t for t in _pin_attempt_history[client_ip] if now - t < _PIN_WINDOW_SECONDS]
    history.append(now)
    _pin_attempt_history[client_ip] = history

    if len(history) >= _MAX_PIN_ATTEMPTS:
        _pin_lockout_until[client_ip] = now + _PIN_LOCKOUT_SECONDS
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed PIN attempts ({len(history)}). Locked out for 5 minutes."
        )

    remaining = _MAX_PIN_ATTEMPTS - len(history)
    raise HTTPException(status_code=401, detail=f"Incorrect PIN code ({remaining} attempts remaining)")


@app.get("/api/auth/status")
def api_auth_status(request: Request) -> dict:
    is_authed = _is_request_authenticated(request)
    return {
        "authenticated": is_authed,
        "pin_required": True,
    }


@app.post("/api/auth/logout")
def api_auth_logout(response: Response) -> dict:
    response.delete_cookie(key="dash_pin_token", path="/")
    return {"success": True, "detail": "Logged out successfully"}

# --------------------------------------------------------- scan TTL cache ---
_scan_cache = {"ts": 0.0, "rows": [], "note": None}
SCAN_TTL_SECONDS = 300


def _leaderboard(top: int = 10, force: bool = False) -> list:
    from backtest.market_scanner import rank_market

    now = time.time()
    stale = (now - _scan_cache["ts"]) > SCAN_TTL_SECONDS
    if force or stale or len(_scan_cache["rows"]) < top:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rows = rank_market(top_n=max(top, 10))
            _scan_cache.update(ts=time.time(), rows=rows, note=None)
        except Exception as e:                            # noqa: BLE001
            _scan_cache["note"] = f"scan error: {e}"
    return _scan_cache["rows"][:top]


def _account_snapshot() -> dict:
    from execution import client
    from risk.book_allocator import get_book_allocations, classify_position_book

    acct = client.get_account()
    positions = []
    for p in client.get_all_positions():
        entry = float(p.avg_entry_price)
        now_px = float(p.current_price)
        b = classify_position_book(p.symbol)
        positions.append({
            "symbol": p.symbol,
            "book": b,
            "qty": abs(float(p.qty)),
            "avg_entry": round(entry, 2),
            "now": round(now_px, 2),
            "pnl_dollars": round(float(p.unrealized_pl or 0.0), 2),
            "pnl_pct": round(float(p.unrealized_plpc or 0.0) * 100.0, 2),
        })
    book_alloc = get_book_allocations(client=client)
    return {
        "equity": round(float(acct.equity), 2),
        "cash": round(float(acct.cash), 2),
        "buying_power": round(float(acct.buying_power), 2),
        "market_open": bool(client.get_clock().is_open),
        "positions": positions,
        "book_allocation": book_alloc,
    }


def _require_token(token_header: str) -> None:
    if token_header != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="invalid X-Dash-Token")


# ------------------------------------------------------------- read routes --
@app.get("/api/account")
def api_account() -> dict:
    return _account_snapshot()


@app.get("/api/book/allocation")
def api_book_allocation() -> dict:
    """🏛️ Returns live 95% Core and 5% Momentum capital architecture breakdown."""
    from execution import client
    from risk.book_allocator import get_book_allocations
    return get_book_allocations(client=client)


def _get_desk_state_file(desk_key: str) -> Optional[dict]:
    d = str(desk_key or "").lower().strip()
    fname_map = {
        "crypto": "crypto_futures_state.json",
        "futures": "cme_futures_state.json",
        "cme": "cme_futures_state.json",
        "forex": "forex_state.json",
    }
    fname = fname_map.get(d)
    if not fname:
        return None
    for cand in [
        os.path.join(os.path.dirname(__file__), "..", "execution", fname),
        os.path.join(os.path.dirname(__file__), fname),
        os.path.join("execution", fname),
    ]:
        if os.path.exists(cand):
            data = atomic_json_read(cand)
            if data:
                return data
    return None


@app.get("/health")
@app.get("/api/health")
def api_health() -> dict:
    """Liveness, database, desks, and autopilot heartbeat health check."""
    now = time.time()
    uptime = round(now - _APP_START_TIME, 1)

    # Check autopilot heartbeat
    hb_path = Path(".run/autopilot_heartbeat.json")
    hb_data = atomic_json_read(hb_path, default={})
    hb_ts = float(hb_data.get("timestamp", 0.0) or 0.0)
    hb_age = round(now - hb_ts, 1) if hb_ts > 0 else None
    hb_alive = bool(hb_age is not None and hb_age < 360.0)

    # Check database
    db_ok = False
    trade_count = 0
    try:
        conn = journal._conn()
        row = conn.execute("SELECT count(*) FROM trades").fetchone()
        trade_count = int(row[0]) if row else 0
        conn.close()
        db_ok = True
    except Exception:
        pass

    # Check desk states
    desks_status = {}
    for dk in ["stocks", "crypto", "futures", "forex"]:
        if dk == "stocks":
            desks_status["stocks"] = {"configured": True, "trade_count": trade_count}
        else:
            st = _get_desk_state_file(dk) or {}
            desks_status[dk] = {
                "configured": bool(st),
                "open_positions": len(st.get("positions", {})),
                "equity": st.get("equity", 0.0),
            }

    status_str = "healthy" if db_ok else "degraded"

    return {
        "status": status_str,
        "uptime_seconds": uptime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {"ok": db_ok, "trade_count": trade_count},
        "autopilot": {
            "alive": hb_alive,
            "heartbeat_age_seconds": hb_age,
            "status": hb_data.get("status", "unknown"),
            "cycle": hb_data.get("cycle", 0),
        },
        "desks": desks_status,
    }


@app.get("/api/journal/summary")
def api_journal_summary(desk: str = "stocks") -> dict:
    d = str(desk or "stocks").lower().strip()
    if d == "stocks":
        return {
            "stats": journal.stats(),
            "core_stats": journal.stats(book="core"),
            "momentum_stats": journal.stats(book="momentum"),
            "analytics": journal.analytics(),
            "desk": "stocks",
        }

    from datetime import datetime

    if d in ("crypto", "futures", "cme", "forex"):
        state = _get_desk_state_file(d) or {}
        closed = state.get("closed_trades", [])
        open_pos = state.get("positions", [])
        n = len(closed)
        wins = [float(t.get("pnl", 0.0)) for t in closed if float(t.get("pnl", 0.0)) > 0]
        losses = [float(t.get("pnl", 0.0)) for t in closed if float(t.get("pnl", 0.0)) < 0]
        wr = round(100.0 * len(wins) / n, 1) if n > 0 else 0.0
        tot = round(sum(float(t.get("pnl", 0.0)) for t in closed), 2)
        avg_pnl = round(tot / n, 2) if n > 0 else 0.0
        avg_win = round(sum(wins) / len(wins), 2) if wins else 0.0
        avg_loss = round(abs(sum(losses) / len(losses)), 2) if losses else 0.0
        rr = round(avg_win / avg_loss, 2) if avg_loss > 0 else (1.5 if wins else None)

        by_strat: Dict[str, List[float]] = {}
        for t in closed:
            strat = t.get("strategy") or t.get("side") or "SCALP"
            by_strat.setdefault(strat, []).append(float(t.get("pnl", 0.0)))
        by_grade = {k: journal._wr(v) for k, v in sorted(by_strat.items())}

        by_sym: Dict[str, List[float]] = {}
        for t in closed:
            sym = t.get("symbol", "ASSET")
            by_sym.setdefault(sym, []).append(float(t.get("pnl", 0.0)))
        by_session = {k: journal._wr(v) for k, v in sorted(by_sym.items())}

        desk_title = "Crypto 3x Perps" if d == "crypto" else ("CME Micro Futures" if d in ("futures", "cme") else "Forex 24/5")
        suggestions = []
        if tot >= 0:
            suggestions.append(f"🟢 {desk_title} desk generated +${tot:,.2f} net realized alpha across {n} closed cycles (Win Rate: {wr}%).")
        else:
            suggestions.append(f"⚠️ {desk_title} experiencing drawdowns of -${abs(tot):,.2f} over {n} trades. Stop brackets active.")
        if rr is not None:
            suggestions.append(f"⚖️ Payoff Asymmetry: {rr} Reward:Risk (${avg_win:.2f} avg win vs -${avg_loss:.2f} avg loss).")
        if open_pos:
            suggestions.append(f"🎯 {len(open_pos)} active live position(s) being managed by trailing brackets.")

        return {
            "stats": {"n": n, "win_rate": wr, "avg_pnl": avg_pnl, "total": tot, "closed_trades": n, "open_trades": len(open_pos)},
            "reward_risk": rr,
            "analytics": {
                "by_grade": by_grade,
                "by_session": by_session,
                "suggestions": suggestions,
            },
            "desk": d,
        }

    # overall / all 4 desks
    conn = journal._conn()
    stock_rows = conn.execute("SELECT pnl FROM trades WHERE closed_at IS NOT NULL").fetchall()
    conn.close()
    stock_pnls = [float(r[0]) for r in stock_rows]

    c_state = _get_desk_state_file("crypto") or {}
    f_state = _get_desk_state_file("futures") or {}
    x_state = _get_desk_state_file("forex") or {}

    c_trades = c_state.get("closed_trades", [])
    f_trades = f_state.get("closed_trades", [])
    x_trades = x_state.get("closed_trades", [])

    c_pnls = [float(t.get("pnl", 0.0)) for t in c_trades]
    f_pnls = [float(t.get("pnl", 0.0)) for t in f_trades]
    x_pnls = [float(t.get("pnl", 0.0)) for t in x_trades]

    all_pnls = stock_pnls + c_pnls + f_pnls + x_pnls
    n_all = len(all_pnls)
    wins_all = [p for p in all_pnls if p > 0]
    wr_all = round(100.0 * len(wins_all) / n_all, 1) if n_all > 0 else 0.0
    tot_all = round(sum(all_pnls), 2)
    avg_pnl_all = round(tot_all / n_all, 2) if n_all > 0 else 0.0

    by_grade = {
        "🏛️ Equities (Alpaca)": journal._wr(stock_pnls),
        "⚡ Crypto Perps (3x)": journal._wr(c_pnls),
        "📈 CME Futures": journal._wr(f_pnls),
        "💱 Forex 24/5": journal._wr(x_pnls),
    }

    by_session = {
        "US Megacap Stocks": journal._wr(stock_pnls),
        "Perpetual Derivatives": journal._wr(c_pnls),
        "Index & Commodity Micro": journal._wr(f_pnls),
        "Macro FX Currencies": journal._wr(x_pnls),
    }

    wins = [p for p in all_pnls if p > 0]
    losses = [p for p in all_pnls if p < 0]
    aw = sum(wins) / len(wins) if wins else 0.0
    al = abs(sum(losses) / len(losses)) if losses else 0.0
    computed_rr = round(aw / al, 2) if al > 0 else (round(aw, 2) if wins else 0.0)

    suggestions = [
        f"🌐 4-Desk Multi-Asset Portfolio: +${tot_all:,.2f} combined realized P&L across {n_all} executions.",
        f"📊 Cross-desk win rate is {wr_all}% with diversified uncorrelated market regimes.",
        "⚡ Crypto desk providing 24/7 continuous alpha generation alongside US Equities intraday sniping.",
    ]

    return {
        "stats": {"n": n_all, "win_rate": wr_all, "avg_pnl": avg_pnl_all, "total": tot_all, "closed_trades": n_all},
        "reward_risk": computed_rr,
        "analytics": {
            "by_grade": by_grade,
            "by_session": by_session,
            "suggestions": suggestions,
        },
        "desk": "overall",
    }


@app.get("/api/journal/trades")
def api_journal_trades(limit: int = 50, book: str = "all", desk: str = "stocks") -> dict:
    d = str(desk or "stocks").lower().strip()
    from datetime import datetime

    if d == "stocks":
        conn = journal._conn()
        if book and book.lower() in {"core", "momentum"}:
            rows = conn.execute(
                """SELECT id, ticker, opened_at, closed_at, qty, entry, exit,
                          reason, pnl, grade, score, actual_entry, slippage_bps, book, order_id
                   FROM trades WHERE book = ? ORDER BY id DESC LIMIT ?""",
                (book.lower(), int(limit))).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, ticker, opened_at, closed_at, qty, entry, exit,
                          reason, pnl, grade, score, actual_entry, slippage_bps, book, order_id
                   FROM trades ORDER BY id DESC LIMIT ?""", (int(limit),)).fetchall()
        conn.close()
        trades = [{
            "id": tid,
            "ticker": t,
            "opened_at": o, "closed_at": c,
            "qty": q, "entry": e, "exit": x,
            "reason": r or "", "pnl": float(p or 0.0),
            "grade": g, "score": s,
            "actual_entry": a, "slippage_bps": sl,
            "book": bk or ("momentum" if (r and "ross" in str(r).lower()) else "core"),
            "order_id": oid,
        } for tid, t, o, c, q, e, x, r, p, g, s, a, sl, bk, oid in rows]
        return {"trades": trades}

    if d in ("crypto", "futures", "cme", "forex"):
        state = _get_desk_state_file(d) or {}
        closed = state.get("closed_trades", [])
        trades = []
        n = len(closed)
        for i, t in enumerate(reversed(closed[-int(limit):])):
            ts = t.get("closed_at")
            dt_str = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M") if ts else "—"
            trades.append({
                "id": f"{d[:3].upper()}-{n - i}",
                "ticker": t.get("symbol", "ASSET"),
                "opened_at": dt_str,
                "closed_at": dt_str,
                "qty": float(t.get("contracts") or t.get("lots") or 1.0),
                "entry": float(t.get("entry_price") or 0.0),
                "exit": float(t.get("exit_price") or 0.0),
                "reason": t.get("reason", "Harvester Exit"),
                "pnl": round(float(t.get("pnl", 0.0)), 2),
                "grade": t.get("strategy") or ("3x Perp" if d == "crypto" else "Micro"),
                "score": round(float(t.get("score") or t.get("confidence") or (82.0 if d == "crypto" else 80.0)), 1),
                "actual_entry": float(t.get("entry_price") or 0.0),
                "slippage_bps": 0.0,
                "book": d,
                "order_id": f"desk-{d}-{n - i}",
            })
        return {"trades": trades}

    # Overall / all desks
    all_raw = []
    # stocks
    conn = journal._conn()
    rows = conn.execute(
        """SELECT id, ticker, opened_at, closed_at, qty, entry, exit,
                  reason, pnl, grade, score, actual_entry, slippage_bps, book, order_id
           FROM trades WHERE closed_at IS NOT NULL ORDER BY id DESC LIMIT ?""", (int(limit),)).fetchall()
    conn.close()
    for tid, t, o, c, q, e, x, r, p, g, s, a, sl, bk, oid in rows:
        ts_val = float(c or o or 0)
        all_raw.append({
            "ts": ts_val,
            "id": f"STK-{tid}",
            "ticker": t,
            "opened_at": str(o), "closed_at": str(c),
            "qty": q, "entry": e, "exit": x,
            "reason": r or "", "pnl": float(p or 0.0),
            "grade": g or "Stock", "score": s or 75,
            "actual_entry": a, "slippage_bps": sl or 0.0,
            "book": "stocks", "order_id": oid,
        })
    # other desks
    for dk in ("crypto", "futures", "forex"):
        st = _get_desk_state_file(dk) or {}
        for ct in st.get("closed_trades", [])[-int(limit):]:
            ts_val = float(ct.get("closed_at") or 0)
            dt_str = datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M") if ts_val > 0 else "—"
            all_raw.append({
                "ts": ts_val,
                "id": f"{dk[:3].upper()}",
                "ticker": ct.get("symbol", "ASSET"),
                "opened_at": dt_str, "closed_at": dt_str,
                "qty": float(ct.get("contracts") or ct.get("lots") or 1.0),
                "entry": float(ct.get("entry_price") or 0.0),
                "exit": float(ct.get("exit_price") or 0.0),
                "reason": f"[{dk.upper()}] {ct.get('reason', '')}",
                "pnl": round(float(ct.get("pnl", 0.0)), 2),
                "grade": ct.get("strategy") or dk,
                "score": round(float(ct.get("score") or ct.get("confidence") or (82.0 if dk == "crypto" else 80.0)), 1),
                "actual_entry": float(ct.get("entry_price") or 0.0),
                "slippage_bps": 0.0,
                "book": dk,
                "order_id": f"{dk}-trade",
            })
    all_raw.sort(key=lambda x: x["ts"], reverse=True)
    return {"trades": all_raw[:int(limit)]}


@app.get("/api/journal/exits")
def api_journal_exits(limit: int = 50) -> dict:
    return {"exits": journal.get_exits(limit=limit), "summary": journal.stats()}


@app.get("/api/journal/equity_curve")
def api_equity_curve(desk: str = "stocks") -> dict:
    d = str(desk or "stocks").lower().strip()
    from datetime import datetime

    if d == "stocks":
        pts = journal.equity_curve()
        last = pts[-1]["cum_pnl"] if pts else 0.0
        return {"points": pts, "cum_pnl": last, "desk": "stocks"}

    if d in ("crypto", "futures", "cme", "forex"):
        state = _get_desk_state_file(d) or {}
        closed = state.get("closed_trades", [])
        cum = 0.0
        pts = []
        for i, t in enumerate(closed):
            pnl = float(t.get("pnl", 0.0))
            cum += pnl
            ts = t.get("closed_at")
            t_str = datetime.fromtimestamp(float(ts)).strftime("%d/%m %H:%M") if ts else f"#{i+1}"
            pts.append({
                "t": t_str,
                "ticker": t.get("symbol", "ASSET"),
                "pnl": round(pnl, 2),
                "cum_pnl": round(cum, 2),
                "reason": t.get("reason", "Take Profit"),
                "qty": float(t.get("contracts") or t.get("lots") or 1.0),
                "entry": round(float(t.get("entry_price") or 0.0), 2),
                "exit": round(float(t.get("exit_price") or 0.0), 2),
                "grade": t.get("strategy", d.upper()),
            })
        last = pts[-1]["cum_pnl"] if pts else 0.0
        return {"points": pts, "cum_pnl": last, "desk": d}

    # overall / all desks combined
    all_events = []
    # stocks
    conn = journal._conn()
    rows = conn.execute(
        "SELECT closed_at, pnl, ticker, reason, qty, entry, exit, grade FROM trades WHERE closed_at IS NOT NULL"
    ).fetchall()
    conn.close()
    for ts, pnl, sym, reason, qty, entry, exit_px, grade in rows:
        all_events.append({
            "ts": float(ts or 0),
            "ticker": sym,
            "desk": "🏛️ Stocks",
            "pnl": float(pnl or 0),
            "reason": reason,
            "qty": qty,
            "entry": entry,
            "exit": exit_px,
            "grade": grade,
        })
    # other desks
    for dk, name in [("crypto", "⚡ Crypto"), ("futures", "📈 Futures"), ("forex", "💱 Forex")]:
        st = _get_desk_state_file(dk) or {}
        for t in st.get("closed_trades", []):
            all_events.append({
                "ts": float(t.get("closed_at") or 0),
                "ticker": t.get("symbol", dk.upper()),
                "desk": name,
                "pnl": float(t.get("pnl", 0)),
                "reason": t.get("reason", ""),
                "qty": t.get("contracts") or t.get("lots") or 1.0,
                "entry": t.get("entry_price", 0),
                "exit": t.get("exit_price", 0),
                "grade": t.get("strategy", dk.upper()),
            })
    all_events.sort(key=lambda x: x["ts"])
    cum = 0.0
    pts = []
    for i, ev in enumerate(all_events):
        cum += ev["pnl"]
        ts_val = ev["ts"]
        t_str = datetime.fromtimestamp(ts_val).strftime("%d/%m %H:%M") if ts_val > 0 else f"#{i+1}"
        pts.append({
            "t": t_str,
            "ticker": ev["ticker"],
            "pnl": round(ev["pnl"], 2),
            "cum_pnl": round(cum, 2),
            "reason": f"[{ev['desk']}] {ev.get('reason', '')}",
            "qty": float(ev["qty"] or 1.0),
            "entry": round(float(ev["entry"] or 0), 2),
            "exit": round(float(ev["exit"] or 0), 2),
            "grade": ev["grade"] or "Asset",
        })
    last = pts[-1]["cum_pnl"] if pts else 0.0
    return {"points": pts, "cum_pnl": last, "desk": "overall"}


@app.get("/api/purchases")
def api_purchases(limit: int = 50) -> dict:
    from execution.purchase_logger import get_purchase_logs, get_purchase_log_text
    return {
        "purchases": get_purchase_logs(limit=limit),
        "raw_text": get_purchase_log_text(),
    }


@app.get("/api/scan")
def api_scan(top: int = 10) -> dict:
    rows = _leaderboard(top=top)
    age = round(time.time() - _scan_cache["ts"], 1)
    return {"rows": rows, "cache_age_seconds": age, "note": _scan_cache["note"]}


@app.post("/api/actions/rescan")
def api_rescan(x_dash_token: str = Header(default="", alias="X-Dash-Token")) -> dict:
    _require_token(x_dash_token)
    _leaderboard(top=10, force=True)
    return {"status": "rescanned", "rows": len(_scan_cache["rows"])}


@app.get("/api/regime")
def api_regime() -> dict:
    from market.beta_calculator import detect_market_regime
    return detect_market_regime("SPY")


@app.get("/api/advisor/exit")
def api_advisor_exit(ticker: str, entry: float, shares: float = 0) -> dict:
    """🧭 Exit Advisor — personalised exit analysis for a user's position across all 4 asset classes."""
    from risk.exit_advisor import analyze_exit
    t_clean = ticker.upper().strip()

    # 1. Forex Currency Pair Check
    if "/" in t_clean or t_clean.endswith("=X") or t_clean in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF"]:
        from strategy.forex_strategy import forex_strategy
        from market.price_fetcher import fetch_prices
        norm = forex_strategy.normalize_symbol(t_clean)
        yf = forex_strategy.get_yahoo_ticker(norm)
        df = fetch_prices(yf, period="5d", interval="1h")
        if not df.empty:
            curr_px = float(df["Close"].iloc[-1])
            cfg = forex_strategy.PAIR_CONFIG.get(norm, {"pip": 0.0001, "pip_val_usd": 10.0})
            pip_size = cfg["pip"]
            pip_val = cfg.get("pip_val_usd", 10.0)
            sig = forex_strategy.evaluate(norm, df)
            pips_gain = (curr_px - float(entry)) / pip_size
            sl = sig.stop_loss if sig.stop_loss > 0 else (entry - (20.0 * pip_size))
            tp = sig.take_profit if sig.take_profit > 0 else (entry + (40.0 * pip_size))
            return {
                "ticker": norm,
                "asset_class": "FOREX",
                "entry_price": float(entry),
                "current_price": curr_px,
                "pnl_pct": round(((curr_px - entry) / entry) * 100.0, 2),
                "pip_size": pip_size,
                "pips_gain": round(pips_gain, 1),
                "session": sig.session,
                "ladder": {
                    "hard_stop_price": round(sl, 5 if pip_size == 0.0001 else 3),
                    "take_profit_1_price": round(tp, 5 if pip_size == 0.0001 else 3),
                    "take_profit_2_trigger": round(tp + (20.0 * pip_size), 5 if pip_size == 0.0001 else 3),
                },
                "verdict": "IN_PROFIT" if pips_gain > 5 else ("DRAWDOWN" if pips_gain < -5 else "NEAR_ENTRY"),
                "notes": f"Forex {norm} position. Current session: {sig.session}. Trailing pips active.",
            }

    # 2. Crypto 3x Perpetual Futures Check
    if "USDT" in t_clean or "BTC" in t_clean or "ETH" in t_clean or "SOL" in t_clean:
        from strategy.crypto_perp_strategy import crypto_strategy
        from market.price_fetcher import fetch_prices
        yf_sym = t_clean.replace("/USDT", "-USD").replace("/USD", "-USD")
        if not "-" in yf_sym and not yf_sym.endswith("-USD"):
            yf_sym = f"{yf_sym}-USD"
        df = fetch_prices(yf_sym, period="5d", interval="1h")
        if not df.empty:
            curr_px = float(df["Close"].iloc[-1])
            sig = crypto_strategy.evaluate(t_clean, df)
            pnl_pct = ((curr_px - entry) / entry) * 100.0
            sl = sig.stop_loss if sig.stop_loss > 0 else (entry * 0.96)
            tp = sig.take_profit if sig.take_profit > 0 else (entry * 1.08)
            liq_buffer = ((entry - (entry * 0.67)) / entry) * 100.0
            return {
                "ticker": t_clean,
                "asset_class": "CRYPTO",
                "entry_price": float(entry),
                "current_price": curr_px,
                "pnl_pct": round(pnl_pct, 2),
                "leverage": "3x",
                "liquidation_buffer_pct": round(liq_buffer, 1),
                "ladder": {
                    "hard_stop_price": round(sl, 2),
                    "take_profit_1_price": round(tp, 2),
                    "take_profit_2_trigger": round(tp * 1.04, 2),
                },
                "verdict": "IN_PROFIT" if pnl_pct > 2 else ("DRAWDOWN" if pnl_pct < -2 else "NEAR_ENTRY"),
                "notes": f"Crypto 3x Perp position. {sig.rationale}",
            }

    # 3. CME Micro Futures Check
    if t_clean in ["MES", "MNQ", "MCL", "MGC", "ES", "NQ", "CL", "GC", "ES=F", "NQ=F"]:
        from strategy.cme_futures_strategy import cme_strategy
        from market.price_fetcher import fetch_prices
        sym = t_clean.replace("=F", "")
        if sym in ["ES", "NQ", "CL", "GC"]: sym = f"M{sym}"
        proxy_map = {"MES": "SPY", "MNQ": "QQQ", "MCL": "USO", "MGC": "GLD"}
        df = fetch_prices(proxy_map.get(sym, "SPY"), period="5d", interval="1h")
        if not df.empty:
            curr_px = float(df["Close"].iloc[-1])
            sig = cme_strategy.evaluate(sym, df)
            sl = sig.stop_loss if sig.stop_loss > 0 else (entry * 0.985)
            tp = sig.take_profit if sig.take_profit > 0 else (entry * 1.03)
            return {
                "ticker": sym,
                "asset_class": "FUTURES",
                "entry_price": float(entry),
                "current_price": curr_px,
                "pnl_pct": round(((curr_px - entry) / entry) * 100.0, 2),
                "tick_size": sig.tick_size,
                "point_value": sig.point_value,
                "ladder": {
                    "hard_stop_price": round(sl, 2),
                    "take_profit_1_price": round(tp, 2),
                    "take_profit_2_trigger": round(tp * 1.02, 2),
                },
                "verdict": "IN_PROFIT" if curr_px > entry else "DRAWDOWN",
                "notes": f"CME Micro Futures {sym}. Point value ${sig.point_value}/pt.",
            }

    # 4. Default US Equities
    res = analyze_exit(ticker.upper(), float(entry))
    if shares > 0 and "current_price" in res:
        res["shares"] = shares
        res["position_pnl_dollars"] = round(
            (res["current_price"] - float(entry)) * shares, 2)
        res["pnl_at_tp1_dollars"] = round(
            ((res.get("ladder") or {}).get("take_profit_1_price", 0.0)
             - float(entry)) * shares, 2)
        res["pnl_at_sl_dollars"] = round(
            ((res.get("ladder") or {}).get("hard_stop_price", 0.0)
             - float(entry)) * shares, 2)
    return res


@app.get("/api/evaluate/{ticker}")
def api_evaluate(ticker: str) -> dict:
    """Validate candidate trade (README Step 2): FinBERT sentiment + model signal + risk decision + beta hedge plan + grade."""
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("USE_LGBM_RUNTIME", "0")
    from api import services
    try:
        return services.get_hedge_evaluation(ticker.upper().strip())
    except Exception as e:
        logger.warning(f"api_evaluate {ticker} error: {e}")
        return {"error": str(e), "ticker": ticker.upper()}



# ----------------------------------------------------------- action routes --
class FlattenRequest(BaseModel):
    ticker: str


def _cancel_open_orders(ticker: str) -> int:
    """Cancels protective/GTC stops so flattening doesn't leave orphans."""
    from alpaca.trading.requests import CancelOrderRequest  # noqa: E402

    cancelled = 0
    try:
        from execution import client
        client.cancel_orders(filter=CancelOrderRequest(symbols=[ticker.upper()]))
        cancelled += 1
    except Exception as e:                                # noqa: BLE001
        logger.warning(f"cancel orders {ticker}: {e}")
    return cancelled


@app.post("/api/actions/flatten")
def api_flatten(body: FlattenRequest,
                x_dash_token: str = Header(default="", alias="X-Dash-Token")) -> dict:
    _require_token(x_dash_token)
    ticker = body.ticker.upper().strip()

    from execution import client, submit_market_order

    qty = None
    entry = None
    for p in client.get_all_positions():
        if p.symbol.upper() == ticker:
            qty = int(abs(float(p.qty)))
            entry = float(p.avg_entry_price)
            break
    if not qty:
        # Check Desk 2: Crypto Perpetual Futures
        crypto_state_path = Path("execution/crypto_futures_state.json")
        if crypto_state_path.exists():
            try:
                cdata = json.loads(crypto_state_path.read_text())
                cpos = cdata.get("positions", {})
                for sym, pos in list(cpos.items()):
                    if sym.upper() == ticker or sym.replace("/", "").upper() == ticker.replace("/", ""):
                        closed_p = cpos.pop(sym)
                        pnl = float(closed_p.get("unrealized_pnl", 0.0))
                        cdata["cash"] = float(cdata.get("cash", 0.0)) + float(closed_p.get("notional_margin", 0.0)) + pnl
                        cdata["total_realized_pnl"] = float(cdata.get("total_realized_pnl", 0.0)) + pnl
                        cdata["closed_trades"] = cdata.get("closed_trades", [])
                        cdata["closed_trades"].append({
                            "symbol": sym,
                            "side": closed_p.get("side", "LONG"),
                            "entry_price": closed_p.get("entry_price"),
                            "exit_price": closed_p.get("current_price"),
                            "contracts": closed_p.get("contracts"),
                            "pnl": pnl,
                            "reason": "manual_flatten",
                            "closed_at": time.time(),
                        })
                        crypto_state_path.write_text(json.dumps(cdata, indent=2))
                        return {"status": "submitted", "ticker": sym, "qty": closed_p.get("contracts", 1), "desk": "crypto", "pnl": pnl}
            except Exception as e:
                logger.debug(f"Crypto flatten check: {e}")

        # Check Desk 3: CME Micro Futures
        cme_state_path = Path("execution/cme_futures_state.json")
        if cme_state_path.exists():
            try:
                mdata = json.loads(cme_state_path.read_text())
                mpos = mdata.get("positions", {})
                for sym, pos in list(mpos.items()):
                    if sym.upper() == ticker:
                        closed_p = mpos.pop(sym)
                        pnl = float(closed_p.get("unrealized_pnl", 0.0))
                        mdata["cash"] = float(mdata.get("cash", 0.0)) + float(closed_p.get("margin_held", 2500.0)) + pnl
                        mdata["total_realized_pnl"] = float(mdata.get("total_realized_pnl", 0.0)) + pnl
                        mdata["closed_trades"] = mdata.get("closed_trades", [])
                        mdata["closed_trades"].append({
                            "symbol": sym,
                            "side": closed_p.get("side", "LONG"),
                            "entry_price": closed_p.get("entry_price"),
                            "exit_price": closed_p.get("current_price"),
                            "contracts": closed_p.get("contracts"),
                            "pnl": pnl,
                            "reason": "manual_flatten",
                            "closed_at": time.time(),
                        })
                        cme_state_path.write_text(json.dumps(mdata, indent=2))
                        return {"status": "submitted", "ticker": sym, "qty": closed_p.get("contracts", 1), "desk": "cme_futures", "pnl": pnl}
            except Exception as e:
                logger.debug(f"CME flatten check: {e}")

        # Check Desk 4: Forex 24/5 Macro
        forex_state_path = Path("execution/forex_state.json")
        if forex_state_path.exists():
            try:
                fdata = json.loads(forex_state_path.read_text())
                fpos = fdata.get("positions", {})
                for sym, pos in list(fpos.items()):
                    if sym.upper() == ticker or sym.replace("/", "").upper() == ticker.replace("/", ""):
                        closed_p = fpos.pop(sym)
                        pnl = float(closed_p.get("unrealized_pnl", 0.0))
                        fdata["cash"] = float(fdata.get("cash", 0.0)) + float(closed_p.get("margin_reserved", 10000.0)) + pnl
                        fdata["total_realized_pnl"] = float(fdata.get("total_realized_pnl", 0.0)) + pnl
                        fdata["closed_trades"] = fdata.get("closed_trades", [])
                        fdata["closed_trades"].append({
                            "symbol": sym,
                            "side": closed_p.get("side", "LONG"),
                            "entry_price": closed_p.get("entry_price"),
                            "exit_price": closed_p.get("current_price"),
                            "lots": closed_p.get("lots", 2.0),
                            "pnl": pnl,
                            "reason": "manual_flatten",
                            "closed_at": time.time(),
                        })
                        forex_state_path.write_text(json.dumps(fdata, indent=2))
                        return {"status": "submitted", "ticker": sym, "qty": closed_p.get("lots", 2.0), "desk": "forex", "pnl": pnl}
            except Exception as e:
                logger.debug(f"Forex flatten check: {e}")

        raise HTTPException(status_code=404, detail=f"no open position in {ticker}")

    now_px = None
    for p in client.get_all_positions():
        if p.symbol.upper() == ticker:
            now_px = float(p.current_price)
            break

    _cancel_open_orders(ticker)
    order = submit_market_order(client, ticker, qty, side="SELL")

    try:
        journal.record_close(ticker, float(now_px or 0.0), "manual_flatten",
                             pnl=(float(now_px or 0.0) - float(entry or 0.0)) * qty)
    except Exception as e:                                # noqa: BLE001
        logger.warning(f"journal close failed: {e}")

    # Unwind paired inverse hedge if this was an alpha position
    try:
        from execution.autopilot import unwind_paired_hedge, load_state, save_state
        _st = load_state()
        unwind_paired_hedge(ticker, client, _st)
        _st.pop(ticker, None)
        save_state(_st)
    except Exception as h_err:
        logger.debug(f"Hedge unwind on flatten failed: {h_err}")

    return {"status": "submitted", "ticker": ticker, "qty": qty,
            "order": order, "cancelled_stops": True}


@app.get("/api/ross/session")
def api_ross_session(capital: float = 2500.0, risk: float = 50.0, scenario: str = "", persist: bool = False) -> dict:
    """⚡ Executes the Ross Cameron momentum playbook simulation without polluting live trade journal."""
    from backtest.ross_momentum_sim import mock_ross_session
    return mock_ross_session(account_risk_dollars=risk, capital=capital, scenario_override=scenario or None, persist=persist)


@app.post("/api/journal/purge_mocks")
def api_purge_mock_trades() -> dict:
    """Cleans up mock simulation runs from trade journal so overall metrics are not distorted."""
    deleted = journal.purge_mock_trades()
    return {"status": "success", "deleted_rows": deleted}


@app.post("/api/journal/reconcile")
def api_reconcile_broker() -> dict:
    """🔄 Performs 2-way broker reconciliation between SQLite trade journal and Alpaca."""
    from execution import client
    res = journal.reconcile_with_broker(client=client)
    return {"status": "success", "result": res}


class RossExecuteRequest(BaseModel):
    ticker: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    hod_target: Optional[float] = None
    max_risk: Optional[float] = 50.0
    dry_run: bool = False


@app.post("/api/ross/execute")
def api_ross_execute(body: RossExecuteRequest) -> dict:
    """⚡ Executes an atomic bracket order on Alpaca within the 5% Satellite Momentum Sandbox."""
    from execution.ross_execution import execute_ross_bracket_trade
    return execute_ross_bracket_trade(
        ticker=body.ticker,
        entry_price=body.entry_price,
        stop_loss=body.stop_loss,
        hod_target=body.hod_target,
        max_risk=body.max_risk or 50.0,
        dry_run=body.dry_run,
    )


_ROSS_CACHE = {"ts": 0, "data": []}


@app.get("/api/ross/window")
def api_ross_window() -> dict:
    from market.low_float_scanner import check_trading_window
    return check_trading_window()


@app.get("/api/ross/runners")
def api_ross_runners(top: int = 5, whole_market: bool = False) -> dict:
    """🔎 Returns morning low-float momentum runners, bracket geometry, and satellite budget."""
    from market.low_float_scanner import scan_momentum_market, check_trading_window, MOMENTUM_WATCHLIST
    from risk.book_allocator import get_book_allocations
    now = time.time()
    if now - _ROSS_CACHE["ts"] < 180 and _ROSS_CACHE["data"]:
        runners = _ROSS_CACHE["data"][:top]
    else:
        runners = scan_momentum_market(watchlist=MOMENTUM_WATCHLIST[:6], top_n=top)
        _ROSS_CACHE["ts"] = now
        _ROSS_CACHE["data"] = runners

    for r in runners:
        price = float(r.get("price", 5.0) or 5.0)
        stop_dist = max(0.15, round(price * 0.04, 2))
        stop_px = round(price - stop_dist, 2)
        risk_per_share = round(price - stop_px, 2)
        hod_px = round(price + (risk_per_share * 1.5), 2)
        shares_50 = int(50.0 / risk_per_share) if risk_per_share > 0 else 0
        r["setup"] = {
            "entry_price": price,
            "stop_loss": stop_px,
            "hod_target": hod_px,
            "risk_per_share": risk_per_share,
            "shares_for_50_risk": shares_50,
            "notional_for_50_risk": round(shares_50 * price, 2),
            "rr_ratio": 1.5,
        }

    return {
        "window": check_trading_window(),
        "runners": runners,
        "momentum_book": get_book_allocations().get("momentum", {}),
    }


# ------------------------------------------------- bayesian confidence & anti-volatility --
class ConfidenceEvaluateRequest(BaseModel):
    ticker: Optional[str] = None
    cost_basis: Optional[float] = None


@app.get("/api/model/confidence")
def api_model_confidence(ticker: Optional[str] = None) -> dict:
    """🧠 Returns current Bayesian confidence pointers, thesis statements, and statement verification."""
    from model.bayesian_confidence import belief_engine
    from execution import client
    from risk.book_allocator import classify_position_book

    results = []
    # If specific ticker requested
    if ticker:
        sym = ticker.upper().strip()
        stmt = belief_engine.get_latest_statement(sym)
        if not stmt:
            stmt = belief_engine.run_daily_cycle(sym)
        hist = belief_engine.get_history(sym, limit=10)
        return {"current": stmt.__dict__, "history": hist}

    # Otherwise return for all open positions + top core holdings
    try:
        positions = client.get_all_positions()
    except Exception:
        positions = []

    seen = set()
    for p in positions:
        sym = p.symbol.upper()
        if sym in {"SH", "SPY", "QQQ"} or sym in seen:
            continue
        seen.add(sym)
        basis = float(p.avg_entry_price)
        stmt = belief_engine.get_latest_statement(sym)
        if not stmt:
            try:
                stmt = belief_engine.run_daily_cycle(sym, cost_basis=basis)
            except Exception as e:
                logger.warning(f"confidence cycle failed for {sym}: {e}")
                continue
        if stmt:
            d = stmt.__dict__.copy()
            d["book"] = classify_position_book(sym)
            d["current_shares"] = abs(float(p.qty))
            results.append(d)

    # If no positions, add META as baseline
    if not results:
        stmt = belief_engine.get_latest_statement("META")
        if not stmt:
            stmt = belief_engine.run_daily_cycle("META", cost_basis=730.0)
        d = stmt.__dict__.copy()
        d["book"] = "core"
        results.append(d)

    return {
        "confidence_pointers": results,
        "learned_rules": [r.__dict__ for r in belief_engine.get_learned_rules(limit=10)],
    }


@app.post("/api/model/confidence/evaluate")
def api_model_confidence_evaluate(body: ConfidenceEvaluateRequest) -> dict:
    """🔄 Executes the Two-Worker daily belief cycle: Worker 1 harvests, Worker 2 updates Bayesian belief."""
    from model.bayesian_confidence import belief_engine
    sym = (body.ticker or "META").upper().strip()
    stmt = belief_engine.run_daily_cycle(sym, cost_basis=body.cost_basis)
    return {
        "status": "success",
        "ticker": sym,
        "statement": stmt.__dict__,
        "learned_rules": [r.__dict__ for r in belief_engine.get_learned_rules(limit=5)],
    }


@app.get("/api/model/stabilized_price/{ticker}")
def api_model_stabilized_price(ticker: str) -> dict:
    """🛡️ Anti-Volatility Model: calculates latent stabilized fair price and Price Stability Index."""
    from market.anti_volatility import anti_volatility_model
    sym = ticker.upper().strip()
    try:
        res = anti_volatility_model.evaluate_ticker(sym)
        hist = []
        if res.history is not None:
            # Return last 30 bars for UI charting
            tail = res.history.tail(30)
            for idx, row in tail.iterrows():
                hist.append({
                    "date": str(idx)[:10],
                    "raw_price": round(float(row["raw_price"]), 2),
                    "stabilized_price": round(float(row["stabilized_price"]), 2),
                    "upper_band": round(float(row["upper_band"]), 2),
                    "lower_band": round(float(row["lower_band"]), 2),
                    "psi": round(float(row["price_stability_index"]), 1),
                })
        return {
            "ticker": res.ticker,
            "current_raw_price": res.current_raw_price,
            "stabilized_price": res.stabilized_price,
            "velocity": res.velocity,
            "volatility_residual": res.volatility_residual,
            "residual_zscore": res.residual_zscore,
            "price_stability_index": res.price_stability_index,
            "upper_band": res.upper_band,
            "lower_band": res.lower_band,
            "regime": res.regime,
            "history": hist,
        }
    except Exception as e:
        logger.warning(f"stabilized_price error for {sym}: {e}")
        return {"error": str(e), "ticker": sym}


@app.get("/api/model/learning_log")
def api_model_learning_log(limit: int = 25) -> dict:
    """📖 Returns the self-improving knowledge ledger written down by Worker 2."""
    from model.bayesian_confidence import belief_engine
    rules = belief_engine.get_learned_rules(limit=limit)
    return {"rules": [r.__dict__ for r in rules]}


# --------------------------------------------------------- jev liquidity scooper --
class JevExecuteRequest(BaseModel):
    ticker: str
    entry_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    max_risk: Optional[float] = 50.0
    dry_run: bool = False


@app.get("/api/jev/opportunities")
def api_jev_opportunities(top: int = 6) -> dict:
    """🎯 Scans market/watchlist for Joint Expected Value (JEV) liquidity dislocation scoops."""
    from strategy.jev_scooper import jev_scooper
    opps = jev_scooper.scan_market(top_n=top)
    return {"opportunities": [o.__dict__ for o in opps]}


@app.post("/api/jev/execute")
def api_jev_execute(body: JevExecuteRequest) -> dict:
    """⚡ Executes a JEV liquidity scoop order onto Alpaca Paper/Live within the allocated book."""
    from execution.jev_execution import execute_jev_scoop_trade
    return execute_jev_scoop_trade(
        ticker=body.ticker,
        entry_price=body.entry_price,
        take_profit=body.take_profit,
        stop_loss=body.stop_loss,
        max_risk=body.max_risk or 50.0,
        dry_run=body.dry_run,
    )


class AIReviewRequest(BaseModel):
    ticker: str
    strategy: str = "core_swing"
    price: float = 100.0
    rvol: float = 1.0
    momentum_5d_pct: float = 0.0
    sentiment_score: float = 0.0
    price_stability_index: float = 50.0
    dislocation_zscore: float = 0.0
    notes: str = ""


@app.get("/api/compliance/report")
def api_compliance_report() -> Dict[str, Any]:
    """Returns dynamic strategy weights, praises/punishments, and recent AI auditor reviews."""
    from compliance.autonomous_checker import compliance_checker
    return compliance_checker.generate_ai_compliance_report()


@app.get("/api/confluence/evaluate/{ticker}")
def api_confluence_evaluate(ticker: str) -> Dict[str, Any]:
    """Evaluates ticker through 100-pt Tri-Confluence Matrix with Whale Trap filter."""
    from dataclasses import asdict
    from strategy.confluence_matrix import confluence_matrix
    decision = confluence_matrix.evaluate_candidate(ticker)
    return asdict(decision)


@app.post("/api/compliance/ai-review")
def api_compliance_ai_review(body: AIReviewRequest) -> Dict[str, Any]:
    """On-demand AI Model review and parameter revision."""
    from dataclasses import asdict
    from compliance.ai_revision_checker import TradeReviewPacket, ai_reviewer
    packet = TradeReviewPacket(
        ticker=body.ticker,
        strategy=body.strategy,
        action="PRE_TRADE_PROPOSAL",
        price=body.price,
        rvol=body.rvol,
        momentum_5d_pct=body.momentum_5d_pct,
        sentiment_score=body.sentiment_score,
        price_stability_index=body.price_stability_index,
        dislocation_zscore=body.dislocation_zscore,
        notes=body.notes,
    )
    res = ai_reviewer.evaluate_pre_trade(packet)
    return asdict(res)


class SubscriberRegisterRequest(BaseModel):
    user_id: str
    tier: str = "PREMIUM_VIP"
    broker_type: str = "alpaca_paper"
    api_key: str = ""
    secret_key: str = ""
    base_url: str = "https://paper-api.alpaca.markets"
    risk_pct_per_trade: float = 0.015
    max_portfolio_heat: float = 0.45
    max_daily_loss_pct: float = -0.03
    is_active: bool = True
    notes: str = ""


class MirrorSignalRequest(BaseModel):
    ticker: str
    side: str = "buy"
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy_name: str = "core_swing"
    grade: str = "A"
    rationale: str = ""


@app.get("/api/benchmark/summary")
def api_benchmark_summary(benchmark: str = "SPY", period: str = "1y") -> Dict[str, Any]:
    """Returns institutional benchmark metrics (Sharpe > 2.0, Sortino, Calmar, MDD vs SPY/QQQ)."""
    from dataclasses import asdict
    from benchmark.institutional_benchmark import benchmark_engine
    metrics = benchmark_engine.calculate_metrics(benchmark=benchmark, period=period)
    return asdict(metrics)


@app.post("/api/gateway/subscribers/register")
def api_gateway_register_subscriber(body: SubscriberRegisterRequest) -> Dict[str, Any]:
    """Registers or updates a premium subscriber broker connection and personalized risk settings."""
    from gateway.subscriber_registry import SubscriberProfile, subscriber_registry
    prof = SubscriberProfile(
        user_id=body.user_id,
        tier=body.tier,
        broker_type=body.broker_type,
        api_key=body.api_key,
        secret_key=body.secret_key,
        base_url=body.base_url,
        risk_pct_per_trade=body.risk_pct_per_trade,
        max_portfolio_heat=body.max_portfolio_heat,
        max_daily_loss_pct=body.max_daily_loss_pct,
        is_active=body.is_active,
        notes=body.notes,
    )
    subscriber_registry.register_or_update(prof)
    return {"status": "registered", "user_id": body.user_id, "tier": body.tier, "broker": body.broker_type}


@app.get("/api/gateway/subscribers/list")
def api_gateway_list_subscribers(active_only: bool = False) -> List[Dict[str, Any]]:
    """Lists connected subscribers with masked credentials and live broker connectivity status."""
    from gateway.subscriber_registry import subscriber_registry
    from gateway.broker_client import broker_factory
    subs = subscriber_registry.list_all(active_only=active_only)
    out = []
    for s in subs:
        masked_key = (s.api_key[:4] + "..." + s.api_key[-3:]) if len(s.api_key) > 8 else "***"
        acc = broker_factory.get_account(s)
        out.append({
            "user_id": s.user_id,
            "tier": s.tier,
            "broker_type": s.broker_type,
            "api_key_masked": masked_key,
            "risk_pct_per_trade": s.risk_pct_per_trade,
            "max_portfolio_heat": s.max_portfolio_heat,
            "is_active": s.is_active,
            "live_equity": acc.get("equity", s.last_equity),
            "live_buying_power": acc.get("buying_power", s.last_buying_power),
            "connection_status": acc.get("status", "unknown"),
            "last_sync": s.last_sync_at,
        })
    return out


@app.post("/api/gateway/mirror/replicate")
def api_gateway_replicate(body: MirrorSignalRequest) -> Dict[str, Any]:
    """Replicates a master signal proportionally across all active subscriber accounts."""
    from dataclasses import asdict
    from gateway.mirror_dispatcher import MirrorTradeSignal, mirror_dispatcher
    sig = MirrorTradeSignal(
        ticker=body.ticker,
        side=body.side,
        entry_price=body.entry_price,
        stop_loss=body.stop_loss,
        take_profit=body.take_profit,
        strategy_name=body.strategy_name,
        grade=body.grade,
        rationale=body.rationale,
    )
    res = mirror_dispatcher.replicate_signal(sig)
    return asdict(res)


@app.get("/api/gateway/mirror/history")
def api_gateway_mirror_history(limit: int = 25) -> List[Dict[str, Any]]:
    """Returns recent replicated trade executions."""
    from gateway.mirror_dispatcher import mirror_dispatcher
    return mirror_dispatcher.get_recent_replications(limit=limit)


def _is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError, ValueError):
        return False


def _find_process_pid(module_name: str) -> Optional[int]:
    try:
        import subprocess
        res = subprocess.run(["pgrep", "-f", module_name], capture_output=True, text=True, timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            pids = [int(p) for p in res.stdout.strip().splitlines() if p.isdigit()]
            for p in pids:
                if p != os.getpid() and _is_pid_alive(p):
                    return p
    except Exception:
        pass
    return None


def _read_pid(pid_path: Path, module_name: Optional[str] = None) -> Optional[int]:
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text().strip())
            if _is_pid_alive(pid):
                return pid
        except Exception:
            pass
    if module_name:
        live_pid = _find_process_pid(module_name)
        if live_pid:
            try:
                pid_path.parent.mkdir(parents=True, exist_ok=True)
                pid_path.write_text(str(live_pid))
            except Exception:
                pass
            return live_pid
    return None


@app.get("/api/desks/status")
def api_desks_status() -> Dict[str, Any]:
    """Returns real-time status, PIDs, equity, and positions for all 3 concurrent trading desks."""
    root_dir = Path(__file__).resolve().parents[1]

    # 1. Stocks Desk (Alpaca)
    stocks_pid = _read_pid(root_dir / ".run" / "autopilot.pid", module_name="execution.autopilot")
    stocks_status = "RUNNING" if stocks_pid else "STOPPED"
    stocks_data: Dict[str, Any] = {
        "desk_id": "stocks",
        "display_name": "US Equities & Macro Desk",
        "pid": stocks_pid,
        "status": stocks_status,
        "broker": "Alpaca Markets Paper",
        "mode": "Live Paper Execution",
        "trading_hours": "09:30 - 16:00 ET (US Equities)",
        "equity": 0.0,
        "cash": 0.0,
        "buying_power": 0.0,
        "positions_count": 0,
        "positions": [],
    }
    try:
        from execution import client
        acc = client.get_account()
        stocks_data["equity"] = round(float(acc.equity), 2)
        stocks_data["cash"] = round(float(acc.cash), 2)
        stocks_data["buying_power"] = round(float(acc.buying_power), 2)
        pos_list = client.get_all_positions()
        stocks_data["positions_count"] = len(pos_list)
        stocks_data["positions"] = [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": "LONG" if float(p.qty) > 0 else "SHORT",
                "avg_entry": round(float(p.avg_entry_price), 2),
                "current_price": round(float(p.current_price), 2),
                "unrealized_pnl": round(float(p.unrealized_pl or 0.0), 2),
            }
            for p in pos_list
        ]
    except Exception as e:
        stocks_data["error"] = str(e)

    # 2. Crypto Perpetual Futures Desk (24/7 CCXT)
    crypto_pid = _read_pid(root_dir / ".run" / "crypto_futures.pid", module_name="execution.crypto_futures_autopilot")
    crypto_status = "RUNNING" if crypto_pid else "STOPPED"
    crypto_state_file = root_dir / "execution" / "crypto_futures_state.json"
    crypto_state: Dict[str, Any] = {}
    if crypto_state_file.exists():
        try:
            crypto_state = json.loads(crypto_state_file.read_text())
        except Exception:
            pass

    all_closed_crypto = crypto_state.get("closed_trades", [])
    crypto_wins = sum(1 for t in all_closed_crypto if float(t.get("pnl", 0) or 0) > 0)
    crypto_wr = round(crypto_wins / len(all_closed_crypto) * 100, 1) if all_closed_crypto else 0.0
    session_crypto_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in all_closed_crypto), 2)

    crypto_data = {
        "desk_id": "crypto_perp",
        "display_name": "Crypto Perpetual Futures Desk",
        "pid": crypto_pid,
        "status": crypto_status,
        "broker": "CCXT Demo (Binance/OKX)",
        "mode": "24/7/365 Autonomous Perpetual Futures",
        "trading_hours": "24/7/365 Continuous",
        "leverage": "3x Cross-Margin",
        "capital": crypto_state.get("capital", 50000.0),
        "equity": crypto_state.get("equity", 50000.0),
        "cash": crypto_state.get("cash", 50000.0),
        "positions_count": len(crypto_state.get("positions", {})),
        "positions": [
            {"symbol": k, **v} for k, v in crypto_state.get("positions", {}).items()
        ],
        "closed_trades": all_closed_crypto[-10:],
        "total_closed_count": len(all_closed_crypto),
        "win_rate": crypto_wr,
        "wins_count": crypto_wins,
        "traps_avoided": crypto_state.get("traps_avoided", 0),
        "session_realized_pnl": session_crypto_pnl,
        "total_realized_pnl": crypto_state.get("total_realized_pnl", 0.0),
        "lifetime_realized_pnl": crypto_state.get("total_realized_pnl", 0.0),
    }

    # 3. CME Micro Index Futures Desk (23h)
    cme_pid = _read_pid(root_dir / ".run" / "cme_futures.pid", module_name="execution.cme_futures_autopilot")
    cme_status = "RUNNING" if cme_pid else "STOPPED"
    cme_state_file = root_dir / "execution" / "cme_futures_state.json"
    cme_state: Dict[str, Any] = {}
    if cme_state_file.exists():
        try:
            cme_state = json.loads(cme_state_file.read_text())
        except Exception:
            pass

    all_closed_cme = cme_state.get("closed_trades", [])
    cme_wins = sum(1 for t in all_closed_cme if float(t.get("pnl", 0) or 0) > 0)
    cme_wr = round(cme_wins / len(all_closed_cme) * 100, 1) if all_closed_cme else 0.0
    session_cme_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in all_closed_cme), 2)

    cme_data = {
        "desk_id": "cme_futures",
        "display_name": "CME Micro Index Futures Desk",
        "pid": cme_pid,
        "status": cme_status,
        "broker": "CME Simulated Feed (MES, MNQ, MCL, MGC)",
        "mode": "23h Micro Futures Bracket Execution",
        "trading_hours": "Sun 18:00 - Fri 17:00 ET (23h/day)",
        "capital": cme_state.get("capital", 25000.0),
        "equity": cme_state.get("equity", 25000.0),
        "cash": cme_state.get("cash", 25000.0),
        "positions_count": len(cme_state.get("positions", {})),
        "positions": [
            {"symbol": k, **v} for k, v in cme_state.get("positions", {}).items()
        ],
        "closed_trades": all_closed_cme[-10:],
        "total_closed_count": len(all_closed_cme),
        "win_rate": cme_wr,
        "wins_count": cme_wins,
        "session_realized_pnl": session_cme_pnl,
        "total_realized_pnl": cme_state.get("total_realized_pnl", 0.0),
        "lifetime_realized_pnl": cme_state.get("total_realized_pnl", 0.0),
    }

    # 4. Forex 24/5 Macro Desk
    forex_pid = _read_pid(root_dir / ".run" / "forex.pid", module_name="execution.forex_autopilot")
    forex_status = "RUNNING" if forex_pid else "STOPPED"
    forex_state_file = root_dir / "execution" / "forex_state.json"
    forex_state: Dict[str, Any] = {}
    if forex_state_file.exists():
        try:
            forex_state = json.loads(forex_state_file.read_text())
        except Exception:
            pass

    all_closed_fx = forex_state.get("closed_trades", [])
    fx_wins = sum(1 for t in all_closed_fx if float(t.get("pnl", 0) or 0) > 0)
    fx_wr = round(fx_wins / len(all_closed_fx) * 100, 1) if all_closed_fx else 0.0
    session_forex_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in all_closed_fx), 2)

    forex_data = {
        "desk_id": "forex",
        "display_name": "Forex 24/5 Macro Desk",
        "pid": forex_pid,
        "status": forex_status,
        "broker": "Interbank FX Demo (20:1 Margin)",
        "mode": "24/5 Continuous Macro Currencies",
        "trading_hours": "Sun 17:00 - Fri 17:00 ET (24/5)",
        "capital": forex_state.get("capital", 50000.0),
        "equity": forex_state.get("equity", 50000.0),
        "cash": forex_state.get("cash", 50000.0),
        "positions_count": len(forex_state.get("positions", {})),
        "positions": [
            {"symbol": k, **v} for k, v in forex_state.get("positions", {}).items()
        ],
        "closed_trades": all_closed_fx[-10:],
        "total_closed_count": len(all_closed_fx),
        "win_rate": fx_wr,
        "wins_count": fx_wins,
        "session_realized_pnl": session_forex_pnl,
        "total_realized_pnl": forex_state.get("total_realized_pnl", 0.0),
        "lifetime_realized_pnl": forex_state.get("total_realized_pnl", 0.0),
        "total_pips_won": forex_state.get("total_pips_won", 0.0),
    }

    total_equity = stocks_data["equity"] + crypto_data["equity"] + cme_data["equity"] + forex_data["equity"]
    running_count = sum(1 for d in [stocks_status, crypto_status, cme_status, forex_status] if d == "RUNNING")

    return {
        "timestamp": time.time(),
        "summary": {
            "total_desks": 4,
            "running_desks": running_count,
            "combined_portfolio_equity": round(total_equity, 2),
            "combined_portfolio_session_pnl": round(
                float(stocks_data.get("realized_pl", 0.0)) + session_crypto_pnl + session_cme_pnl + session_forex_pnl, 2
            ),
            "combined_portfolio_lifetime_pnl": round(
                float(stocks_data.get("realized_pl", 0.0))
                + float(crypto_data.get("total_realized_pnl", 0.0))
                + float(cme_data.get("total_realized_pnl", 0.0))
                + float(forex_data.get("total_realized_pnl", 0.0)),
                2,
            ),
        },
        "desks": {
            "stocks": stocks_data,
            "crypto_perp": crypto_data,
            "cme_futures": cme_data,
            "forex": forex_data,
        },
    }


@app.get("/api/desks/benchmark")
def api_desks_benchmark(force: bool = False) -> Dict[str, Any]:
    """Returns the multi-asset comparative benchmark report (Stocks vs Crypto vs Futures vs Forex)."""
    report_file = Path(__file__).resolve().parents[1] / "reports" / "multi_asset_comparison.json"
    if report_file.exists() and not force:
        try:
            return json.loads(report_file.read_text())
        except Exception:
            pass
    from backtest.multi_asset_benchmark import run_multi_asset_benchmark
    return run_multi_asset_benchmark(period="6mo")


_DESK_SCAN_CACHE: Dict[str, Any] = {}
_DESK_SCAN_CACHE_TS: Dict[str, float] = {}
_DESK_SCAN_TTL = 30.0


@app.get("/api/desks/scan")
def api_desks_scan(desk: str = "all") -> Dict[str, Any]:
    """Scans and ranks trade candidates across individual or all 4 desks (cached 30s)."""
    d = desk.lower().strip()
    now = time.time()
    if d in _DESK_SCAN_CACHE and (now - _DESK_SCAN_CACHE_TS.get(d, 0.0) < _DESK_SCAN_TTL):
        return _DESK_SCAN_CACHE[d]

    out: Dict[str, Any] = {}

    if d in ("stocks", "all"):
        out["stocks"] = _leaderboard(top=8)

    if d in ("crypto", "all"):
        from strategy.crypto_perp_strategy import crypto_strategy
        from market.price_fetcher import fetch_prices
        crypto_items = []
        for pair in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT", "BNB/USDT"]:
            yf_sym = pair.replace("/USDT", "-USD")
            df = fetch_prices(yf_sym, period="5d", interval="1h")
            if not df.empty:
                sig = crypto_strategy.evaluate(pair, df)
                curr_px = float(df["Close"].iloc[-1])
                p_24h = ((curr_px - float(df["Close"].iloc[-24])) / float(df["Close"].iloc[-24]) * 100.0) if len(df) >= 25 else 0.0
                crypto_items.append({
                    "symbol": pair,
                    "price": curr_px,
                    "change_24h": round(p_24h, 2),
                    "side": sig.side,
                    "confidence": sig.confidence_score,
                    "stop_loss": sig.stop_loss,
                    "take_profit": sig.take_profit,
                    "leverage": "3x",
                    "setup": sig.strategy_type,
                    "rationale": sig.rationale,
                })
        out["crypto"] = sorted(crypto_items, key=lambda x: x["confidence"], reverse=True)

    if d in ("futures", "all"):
        from strategy.cme_futures_strategy import cme_strategy
        from market.price_fetcher import fetch_prices
        futures_items = []
        for sym in ["MES", "MNQ", "MCL", "MGC"]:
            proxy_map = {"MES": "SPY", "MNQ": "QQQ", "MCL": "USO", "MGC": "GLD"}
            df = fetch_prices(proxy_map.get(sym, "SPY"), period="5d", interval="1h")
            if not df.empty:
                sig = cme_strategy.evaluate(sym, df)
                curr_px = float(df["Close"].iloc[-1])
                futures_items.append({
                    "symbol": sym,
                    "name": cme_strategy.TICK_CONFIG.get(sym, {}).get("name", sym),
                    "price": curr_px,
                    "side": sig.side,
                    "confidence": sig.confidence_score,
                    "stop_loss": sig.stop_loss,
                    "take_profit": sig.take_profit,
                    "tick_size": sig.tick_size,
                    "point_val": sig.point_value,
                    "setup": sig.setup_name,
                    "rationale": sig.rationale,
                })
        out["futures"] = sorted(futures_items, key=lambda x: x["confidence"], reverse=True)

    if d in ("forex", "all"):
        from strategy.forex_strategy import forex_strategy
        from market.price_fetcher import fetch_prices
        forex_items = []
        for pair in ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF"]:
            yf_ticker = forex_strategy.get_yahoo_ticker(pair)
            df = fetch_prices(yf_ticker, period="5d", interval="1h")
            if not df.empty:
                sig = forex_strategy.evaluate(pair, df)
                curr_px = float(df["Close"].iloc[-1])
                forex_items.append({
                    "symbol": pair,
                    "price": curr_px,
                    "side": sig.side,
                    "confidence": sig.confidence_score,
                    "stop_loss": sig.stop_loss,
                    "take_profit": sig.take_profit,
                    "pips_sl": sig.pips_sl,
                    "pips_tp": sig.pips_tp,
                    "session": sig.session,
                    "setup": sig.strategy_type,
                    "rationale": sig.rationale,
                })
        out["forex"] = sorted(forex_items, key=lambda x: x["confidence"], reverse=True)

    _DESK_SCAN_CACHE[d] = out
    _DESK_SCAN_CACHE_TS[d] = now
    return out


@app.get("/")
def index() -> FileResponse:
    """Primary Master Cockpit on Port 8080."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/overview")
def overview() -> FileResponse:
    return FileResponse(STATIC_DIR / "overview.html")


@app.get("/terminal")
@app.get("/legacy")
def terminal() -> FileResponse:
    """Deep Equities Single-Asset Terminal."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/widget")
def widget() -> FileResponse:
    """Glanceable Mobile & HUD Widget."""
    return FileResponse(STATIC_DIR / "widget.html")


@app.get("/manifest.json")
def manifest() -> FileResponse:
    """PWA web application manifest for mobile installation."""
    return FileResponse(STATIC_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/api/remote-access")
def api_remote_access() -> dict:
    """Return local Wi-Fi, remote Cloudflare Tunnel URL, QR code info and status."""
    from webapp.tunnel_manager import get_remote_status
    return get_remote_status(port=8080)


@app.get("/api/remote-access/qr.svg")
def api_remote_qr_svg(type: str = "auto") -> Response:
    """Generate dynamic SVG QR code for mobile phone camera scanning."""
    from webapp.tunnel_manager import get_remote_status, get_qr_svg
    status = get_remote_status(port=8080)
    if type == "local":
        url = status.get("local_url") or "http://127.0.0.1:8080"
    elif type == "widget":
        url = status.get("tunnel_widget_url") or status.get("local_widget_url") or "http://127.0.0.1:8080/widget"
    else:
        url = status.get("tunnel_url") or status.get("local_url") or "http://127.0.0.1:8080"
    svg = get_qr_svg(url)
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/api/remote-access/restart")
def api_remote_restart() -> dict:
    """Cleanly restarts the Cloudflare tunnel (intermediate middle server) and generates a fresh URL."""
    from webapp.tunnel_manager import restart_tunnel
    return restart_tunnel(port=8080)


# ------------------------------------------------------- Virtual Trading Floor & Agent Council ----
@app.get("/office")
def office_view() -> FileResponse:
    """Virtual 3D Isometric Trading Floor & Multi-Agent Council Office."""
    return FileResponse(STATIC_DIR / "office.html")


@app.get("/api/council/status")
def api_council_status() -> Dict[str, Any]:
    """Returns real-time status of the 5-Agent Trading Floor, roster, and live chatter."""
    from agents.council import get_floor_status
    return get_floor_status()


@app.post("/api/council/convene")
def api_council_convene(payload: Dict[str, Any] = Body(default={})) -> Dict[str, Any]:
    """Convenes the 7-tier multi-agent strategy council on any ticker."""
    from agents.council import convene_council_meeting
    ticker = payload.get("ticker", "NVDA")
    topic = payload.get("topic")
    return convene_council_meeting(ticker=ticker, topic=topic)


@app.get("/api/council/recent")
def api_council_recent(limit: int = 10) -> Dict[str, Any]:
    """Returns recent council meetings and consensus verdicts."""
    from agents.council import get_recent_meetings
    return {"status": "success", "meetings": get_recent_meetings(limit=limit)}


@app.post("/api/council/decision")
def api_council_decision(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Human-in-the-Loop authorization gate: APPROVE or REJECT a council recommendation."""
    from agents.council import resolve_council_decision
    meeting_id = payload.get("meeting_id", "")
    decision = payload.get("decision", "REJECT")
    return resolve_council_decision(meeting_id=meeting_id, decision=decision)


# ------------------------------------------------------- Knowledge Graph (Graphify) ----
@app.get("/graph")
def graph_view() -> Response:
    """Interactive Knowledge Graph HTML visualization generated by Graphify."""
    graph_html_path = Path(__file__).resolve().parents[1] / "graphify-out" / "graph.html"
    if not graph_html_path.exists():
        return HTMLResponse("<h1>Graphify graph has not been generated yet. Run ./quant graphify</h1>", status_code=404)
    return FileResponse(graph_html_path)


@app.get("/graph/tree")
def graph_tree_view() -> Response:
    """Collapsible D3 hierarchy tree visualization generated by Graphify."""
    tree_path = Path(__file__).resolve().parents[1] / "graphify-out" / "GRAPH_TREE.html"
    if not tree_path.exists():
        return HTMLResponse("<h1>Tree view not generated yet. Run ./quant graphify tree</h1>", status_code=404)
    return FileResponse(tree_path)


@app.get("/api/graphify/status")
def api_graphify_status() -> Dict[str, Any]:
    """Returns metadata and statistics for the codebase knowledge graph."""
    graph_path = Path(__file__).resolve().parents[1] / "graphify-out" / "graph.json"
    if not graph_path.exists():
        return {"status": "error", "message": "graphify-out/graph.json not found"}
    try:
        import json
        data = json.loads(graph_path.read_text(encoding="utf-8"))
        nodes = data.get("nodes", [])
        edges = data.get("links", data.get("edges", []))
        communities = {n.get("community") for n in nodes if n.get("community")}
        return {
            "status": "success",
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "communities_count": len(communities),
            "graph_file": str(graph_path),
            "visualization_url": "/graph",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/graphify/query")
def api_graphify_query(q: str = Query(..., description="Query terms to search knowledge graph")) -> Dict[str, Any]:
    """Queries the graphify knowledge graph for relevant components and relationships."""
    import subprocess
    try:
        res = subprocess.run(
            ["graphify", "query", q],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(Path(__file__).resolve().parents[1])
        )
        return {
            "status": "success",
            "query": q,
            "output": res.stdout,
            "error": res.stderr if res.returncode != 0 else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _start_port_8081_forwarder() -> None:
    """
    Transparently forwards connections on port 8081 to port 8080.
    Ensures macOS menu bar widget and existing links continue working without disruption.
    """
    import socket
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 8081))
        srv.listen(10)
    except Exception as e:
        logger.debug(f"[proxy] Port 8081 forwarder skipped or already bound: {e}")
        return

    def forward_stream(src: socket.socket, dst: socket.socket) -> None:
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        finally:
            with contextlib.suppress(Exception):
                src.close()
            with contextlib.suppress(Exception):
                dst.close()

    def accept_loop() -> None:
        while True:
            try:
                client_sock, _ = srv.accept()
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_sock.connect(("127.0.0.1", 8080))
                threading.Thread(target=forward_stream, args=(client_sock, target_sock), daemon=True).start()
                threading.Thread(target=forward_stream, args=(target_sock, client_sock), daemon=True).start()
            except Exception:
                pass

    threading.Thread(target=accept_loop, daemon=True).start()
    logger.info("[proxy] Port 8081 backwards-compatibility forwarder active -> 8080")


# ------------------------------------------------------- startup warm-up ----
@app.on_event("startup")
def warm_cache() -> None:
    _start_port_8081_forwarder()

    def _warm() -> None:
        try:
            _leaderboard(top=10)
        except Exception as e:                            # noqa: BLE001
            logger.warning(f"warm scan failed: {e}")

    def _tunnel() -> None:
        try:
            from webapp.tunnel_manager import start_tunnel
            start_tunnel(port=8080)
        except Exception as e:
            logger.warning(f"remote tunnel init error: {e}")

    threading.Thread(target=_warm, daemon=True).start()
    threading.Thread(target=_tunnel, daemon=True).start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)