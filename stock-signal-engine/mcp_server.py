"""
Stock Signal Engine - Custom Model Context Protocol (MCP) Server
Exposes stock price fetching, technical indicators, financial sentiment analysis,
and Alpaca paper trading operations as standardized tools for AI agents.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure workspace root is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from mcp.server.mcpserver import MCPServer

# Initialize MCP server
mcp = MCPServer("stock-signal-engine")


@mcp.tool()
def fetch_stock_prices(ticker: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
    """Fetch historical and latest stock price data (OHLCV) for a given ticker.

    Args:
        ticker: Stock symbol (e.g. 'AAPL', 'NVDA', 'TSLA').
        period: Data range (e.g. '1d', '5d', '1mo', '3mo', '6mo', '1y').
        interval: Bar interval (e.g. '1d', '1h', '5m').
    """
    from market.price_fetcher import fetch_prices

    df = fetch_prices(ticker=ticker.upper().strip(), period=period, interval=interval)
    if df.empty:
        return {"status": "error", "message": f"No price data found for {ticker}"}

    latest = df.iloc[-1]
    prev_close = df.iloc[-2]["Close"] if len(df) > 1 else latest["Close"]
    pct_change = ((latest["Close"] - prev_close) / prev_close) * 100

    # Format recent history (last 5 rows)
    recent_history = []
    for idx, row in df.tail(5).iterrows():
        recent_history.append({
            "date": str(idx),
            "open": round(float(row.get("Open", 0)), 2),
            "high": round(float(row.get("High", 0)), 2),
            "low": round(float(row.get("Low", 0)), 2),
            "close": round(float(row.get("Close", 0)), 2),
            "volume": int(row.get("Volume", 0)),
        })

    return {
        "status": "success",
        "ticker": ticker.upper().strip(),
        "latest_close": round(float(latest.get("Close", 0)), 2),
        "latest_date": str(df.index[-1]),
        "change_pct": round(float(pct_change), 2),
        "total_candles": len(df),
        "recent_history": recent_history,
    }


@mcp.tool()
def get_technical_indicators(ticker: str, period: str = "6mo") -> Dict[str, Any]:
    """Compute technical indicators (RSI, MACD, Bollinger Bands, ATR) for a ticker.

    Args:
        ticker: Stock symbol (e.g. 'AAPL', 'MSFT', 'SPY').
        period: Historical period to calculate indicators over (default: '6mo').
    """
    from market.price_fetcher import fetch_prices
    from market.indicators import add_indicators

    df = fetch_prices(ticker=ticker.upper().strip(), period=period, interval="1d")
    if df.empty or len(df) < 30:
        return {
            "status": "error",
            "message": f"Insufficient data for {ticker} (need at least 30 trading days).",
        }

    try:
        df_ind = add_indicators(df)
        latest = df_ind.iloc[-1]

        return {
            "status": "success",
            "ticker": ticker.upper().strip(),
            "latest_date": str(df_ind.index[-1]),
            "latest_close": round(float(latest.get("Close", 0)), 2),
            "rsi_14": round(float(latest.get("RSI", 0)), 2) if "RSI" in latest else None,
            "macd": round(float(latest.get("MACD", 0)), 4) if "MACD" in latest else None,
            "macd_signal": round(float(latest.get("MACD_Signal", 0)), 4) if "MACD_Signal" in latest else None,
            "macd_histogram": round(float(latest.get("MACD_Histogram", 0)), 4) if "MACD_Histogram" in latest else None,
            "bollinger_upper": round(float(latest.get("BB_Upper", 0)), 2) if "BB_Upper" in latest else None,
            "bollinger_middle": round(float(latest.get("BB_Middle", 0)), 2) if "BB_Middle" in latest else None,
            "bollinger_lower": round(float(latest.get("BB_Lower", 0)), 2) if "BB_Lower" in latest else None,
            "atr_14": round(float(latest.get("ATR", 0)), 2) if "ATR" in latest else None,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def analyze_financial_sentiment(text: str) -> Dict[str, Any]:
    """Analyze the financial market sentiment (positive, negative, neutral) of a news headline or text using FinBERT.

    Args:
        text: Financial news headline, article snippet, or market commentary.
    """
    from nlp.finbert import analyze_sentiment

    res = analyze_sentiment({"clean_text": text})
    return {
        "status": "success",
        "input_text": text,
        "sentiment": res.get("sentiment", "neutral"),
        "sentiment_score": res.get("sentiment_score", 0.0),
    }


@mcp.tool()
def check_alpaca_account() -> Dict[str, Any]:
    """Check the connected Alpaca paper trading account balance, cash, buying power, and active positions."""
    try:
        from execution.alpha_client import get_client, get_portfolio_value, get_current_exposure

        client = get_client()
        account = client.get_account()
        positions = client.get_all_positions()

        pos_list = []
        for p in positions:
            pos_list.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "market_value": float(p.market_value),
                "current_price": float(p.current_price),
                "unrealized_pl": float(p.unrealized_pl),
            })

        return {
            "status": "success",
            "account_status": account.status,
            "currency": account.currency,
            "portfolio_value": round(float(account.portfolio_value), 2),
            "cash": round(float(account.cash), 2),
            "buying_power": round(float(account.buying_power), 2),
            "current_exposure": round(get_current_exposure(client), 2),
            "positions": pos_list,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not connect to Alpaca: {e}. Check APCA_API_KEY_ID in .env",
        }


@mcp.tool()
def align_event_point_in_time(timestamp: str) -> Dict[str, Any]:
    """Calculate the point-in-time trading session and effective execution date for an event timestamp to eliminate lookahead leakage.

    Args:
        timestamp: ISO timestamp or date string of news release or catalyst (e.g. '2026-10-05T16:30:00Z').
    """
    from data.point_in_time import align_timestamp_point_in_time

    try:
        session = align_timestamp_point_in_time(timestamp)
        return {
            "status": "success",
            "session": session.to_dict(),
            "explanation": (
                f"Published {session.market_phase.lower().replace('_', ' ')} on {session.calendar_date}. "
                f"First tradable on regular market hours: {session.effective_trade_date} ({session.execution_bar}). "
                f"Leakage risk: {session.leakage_risk}."
            ),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def evaluate_factor_dag(ticker: str = "NVDA", period: str = "6mo", mode: str = "point_in_time") -> Dict[str, Any]:
    """Run an agent-native Factor DAG pipeline (Qanat architecture) to compute alpha signals and backtest returns without leakage.

    Args:
        ticker: Stock symbol (e.g. 'NVDA', 'AAPL', 'TSLA').
        period: Historical lookback period ('3mo', '6mo', '1y').
        mode: 'point_in_time' (strictly leak-free) or 'naive_leaked' (for research comparison).
    """
    from data.factor_dag import (
        FactorDAG, PriceSourceNode, NewsSourceNode,
        PointInTimeAlignmentNode, SentimentAggregatorNode,
        TechnicalFeaturesNode, AlphaCompositeNode
    )

    try:
        dag = FactorDAG("AgentFactorPipeline")
        dag.add_node(PriceSourceNode(ticker=ticker, period=period))
        dag.add_node(NewsSourceNode(ticker=ticker))
        dag.add_node(PointInTimeAlignmentNode())
        dag.add_node(SentimentAggregatorNode(mode=mode))
        dag.add_node(TechnicalFeaturesNode())
        dag.add_node(AlphaCompositeNode())

        ctx = dag.execute({
            "ticker": ticker,
            "period": period,
            "execution_mode": mode,
        })
        df_alpha = ctx["alpha_composite"]
        stats = FactorDAG.simulate_strategy(df_alpha, mode=mode)

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "period": period,
            "mode": mode,
            "execution_order": dag.execution_order,
            "mermaid_graph": dag.to_mermaid(),
            "performance": stats,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_engine_health() -> Dict[str, Any]:
    """Check the real-time health and heartbeat of the trading engine, autopilot, and watchdog."""
    import time
    from execution.json_state import atomic_json_read

    hb = atomic_json_read(WORKSPACE_DIR / ".run/autopilot_heartbeat.json", default={})
    now = time.time()
    hb_ts = float(hb.get("timestamp", 0.0) or 0.0)
    hb_age = round(now - hb_ts, 1) if hb_ts > 0 else None

    return {
        "status": "healthy" if (hb_age and hb_age < 600) else "idle_or_restarting",
        "autopilot_alive": bool(hb_age and hb_age < 360),
        "heartbeat_age_seconds": hb_age,
        "last_cycle": hb.get("cycle", 0),
        "autopilot_status": hb.get("status", "unknown"),
    }


@mcp.tool()
def get_multi_desk_status() -> Dict[str, Any]:
    """Retrieve equity, open positions, and telemetry across all 4 desks (Stocks, Crypto, CME Futures, Forex)."""
    from execution.json_state import atomic_json_read

    desks = {}
    for desk_name, fname in [
        ("crypto", "crypto_futures_state.json"),
        ("futures", "cme_futures_state.json"),
        ("forex", "forex_state.json"),
    ]:
        st = atomic_json_read(WORKSPACE_DIR / "execution" / fname, default={})
        desks[desk_name] = {
            "equity": st.get("equity", 0.0),
            "cash": st.get("cash", 0.0),
            "open_positions_count": len(st.get("positions", {})),
            "positions": st.get("positions", {}),
            "total_realized_pnl": st.get("total_realized_pnl", 0.0),
        }

    try:
        from execution.alpha_client import get_client
        c = get_client()
        acc = c.get_account()
        pos = c.get_all_positions()
        desks["stocks"] = {
            "equity": float(acc.equity),
            "cash": float(acc.cash),
            "open_positions_count": len(pos),
            "positions": {p.symbol: {"qty": float(p.qty), "entry_price": float(p.avg_entry_price), "current_price": float(p.current_price), "unrealized_pnl": float(p.unrealized_pl or 0.0)} for p in pos},
        }
    except Exception as e:
        desks["stocks"] = {"error": str(e)}

    self_learning = {}
    try:
        from strategy.equities_strategy import equities_strategy
        self_learning["equities"] = equities_strategy.learner.get_performance_summary()
    except Exception:
        pass
    try:
        from strategy.crypto_perp_strategy import crypto_strategy
        self_learning["crypto_perp"] = crypto_strategy.learner.get_performance_summary()
    except Exception:
        pass
    try:
        from strategy.cme_futures_strategy import cme_strategy
        self_learning["cme_futures"] = cme_strategy.learner.get_performance_summary()
    except Exception:
        pass
    try:
        from strategy.forex_strategy import forex_strategy
        self_learning["forex"] = forex_strategy.learner.get_performance_summary()
    except Exception:
        pass

    return {"status": "success", "desks": desks, "self_learning": self_learning}


@mcp.tool()
def get_trade_journal_stats(desk: str = "stocks") -> Dict[str, Any]:
    """Get trade journal metrics including win rate, total PnL, trades count, and reward-to-risk ratio.

    Args:
        desk: Target desk ('stocks', 'crypto', 'futures', 'forex', or 'overall').
    """
    from execution.trade_journal import journal

    stats = journal.stats()
    summary = journal.summary()
    return {
        "status": "success",
        "desk": desk,
        "stats": stats,
        "summary": summary,
    }


@mcp.tool()
def convene_agent_council_meeting(ticker: str = "NVDA", topic: str = "") -> Dict[str, Any]:
    """Convene a formal strategy meeting with all 5 specialized AI agent desks
    (Trend Desk, Breakout Desk, News/Sentiment Desk, Whale/Order Flow Desk, and Risk Gatekeeper)
    to debate an asset across the 7-tier institutional pipeline and produce a consensus trade proposal.

    Args:
        ticker: Asset symbol to evaluate (e.g. 'NVDA', 'AAPL', 'BTC', 'SPY').
        topic: Optional custom meeting topic or hypothesis to test.
    """
    from agents.council import convene_council_meeting

    meeting = convene_council_meeting(ticker=ticker, topic=topic if topic else None)
    return {
        "status": "success",
        "meeting_id": meeting["meeting_id"],
        "ticker": meeting["ticker"],
        "consensus_score": meeting["consensus_score"],
        "recommendation": meeting["recommendation"],
        "risk_status": meeting["risk_status"],
        "proposed_allocation_usd": meeting["proposed_allocation_usd"],
        "stop_loss_pct": meeting["stop_loss_pct"],
        "votes": meeting["votes"],
        "turns_summary": [
            f"[{t['name']} - {t['role']} ({t['stance']})]: {t['message']}" for t in meeting.get("turns", [])
        ],
        "human_decision_status": meeting["status"],
    }


@mcp.tool()
def get_virtual_office_status() -> Dict[str, Any]:
    """Retrieve the live status of the 3D Virtual Trading Floor, all 5 specialist agent desks,
    300 connected sub-bots, combined hedge fund capital, and 24/7 floor chatter notes.
    """
    from agents.council import get_floor_status

    return get_floor_status()


@mcp.tool()
def submit_human_decision(meeting_id: str, decision: str = "APPROVE") -> Dict[str, Any]:
    """Submit a Human-in-the-Loop decision ('APPROVE' or 'REJECT') on a pending council trade recommendation.

    Args:
        meeting_id: ID of the council meeting (e.g. 'mtg_69fa7bad11').
        decision: Human choice ('APPROVE' / 'YES' to route order, 'REJECT' / 'NO' to abort).
    """
    from agents.council import resolve_council_decision

    return resolve_council_decision(meeting_id=meeting_id, decision=decision)


@mcp.tool()
def query_knowledge_graph(query: str, budget: int = 2000) -> Dict[str, Any]:
    """Query the codebase knowledge graph (1,950+ nodes, 4,480+ edges) for architectural context,
    symbol definitions, call paths, data flow, or module dependencies.

    Args:
        query: Natural language question or symbol name (e.g. 'crypto execution', 'risk sizing', 'compliance gate').
        budget: Maximum token budget for the BFS subgraph traversal (default 2000).
    """
    import subprocess
    res = subprocess.run(
        ["graphify", "query", query, "--budget", str(budget)],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(WORKSPACE_DIR),
    )
    return {
        "status": "success" if res.returncode == 0 else "error",
        "query": query,
        "result": res.stdout or res.stderr,
    }


@mcp.tool()
def find_codebase_path(source_symbol: str, target_symbol: str, undirected: bool = True) -> Dict[str, Any]:
    """Find the shortest dependency or call path between two concepts or symbols in the codebase.

    Args:
        source_symbol: Starting symbol or module (e.g. 'CryptoFuturesAutopilot').
        target_symbol: Destination symbol or module (e.g. 'compliance_checker').
        undirected: Whether to ignore edge direction when finding relationships (default True).
    """
    import subprocess
    cmd = ["graphify", "path", source_symbol, target_symbol]
    if undirected:
        cmd.append("--undirected")
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(WORKSPACE_DIR),
    )
    return {
        "status": "success" if res.returncode == 0 else "error",
        "source": source_symbol,
        "target": target_symbol,
        "path": res.stdout or res.stderr,
    }


@mcp.tool()
def get_codebase_graph_summary() -> Dict[str, Any]:
    """Retrieve high-level summary of the codebase knowledge graph, total symbols,
    top communities, and graph metrics.
    """
    import json
    report_path = WORKSPACE_DIR / "graphify-out" / "GRAPH_REPORT.md"
    analysis_path = WORKSPACE_DIR / "graphify-out" / ".graphify_analysis.json"
    analysis = {}
    if analysis_path.exists():
        try:
            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    report_excerpt = ""
    if report_path.exists():
        report_excerpt = report_path.read_text(encoding="utf-8")[:1500]

    return {
        "status": "success",
        "nodes": analysis.get("nodes_count", 1955),
        "edges": analysis.get("edges_count", 4485),
        "communities": analysis.get("communities_count", 94),
        "visualization_url": "http://localhost:8080/graph",
        "report_excerpt": report_excerpt,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")



