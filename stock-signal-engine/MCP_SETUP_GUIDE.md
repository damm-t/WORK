# 🔌 Universal MCP Server Setup Guide for All AI Builders

Connect your Stock Signal Engine directly into any AI assistant or agentic builder (**Claude Desktop**, **Claude Code**, **Cursor**, **Windsurf**, **Cline**, **Antigravity**).

Once connected, your AI agents can query live market prices, compute technical indicators, run FinBERT sentiment analysis, inspect account balances, check multi-desk positions, and evaluate Factor DAG pipelines in real time.

---

## 🛠️ The 9 Live MCP Tools Exposed

1. `fetch_stock_prices`: Real-time OHLCV candles, daily % change, and recent history.
2. `get_technical_indicators`: RSI-14, MACD, Bollinger Bands, ATR.
3. `analyze_financial_sentiment`: FinBERT neural NLP sentiment analysis on headlines/text.
4. `check_alpaca_account`: Portfolio equity, buying power, cash, and open stock positions.
5. `align_event_point_in_time`: Eliminates lookahead bias by calculating strict point-in-time session execution.
6. `evaluate_factor_dag`: Runs the leak-free topological DAG alpha pipeline.
7. `get_engine_health`: Real-time autopilot heartbeat age, liveness status, and watchdog diagnostics.
8. `get_multi_desk_status`: Equity, cash, and open position details across Stocks, Crypto, Futures, and Forex.
9. `get_trade_journal_stats`: Cross-desk win rates, total realized PnL, and dynamic Reward:Risk ratio.

---

## 1. Claude Desktop (macOS)

Open or edit:
```bash
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add the `stock-signal-engine` entry under `mcpServers`:
```json
{
  "mcpServers": {
    "stock-signal-engine": {
      "command": "/Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python",
      "args": [
        "/Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```
*Restart Claude Desktop to activate the hammer icon 🔨 with all 9 tools.*

---

## 2. Claude Code CLI

Run this one-liner in your terminal:
```bash
claude mcp add stock-signal-engine /Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python /Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py
```

---

## 3. Cursor IDE

1. Open **Cursor Settings** (`Cmd + ,`).
2. Navigate to **Features** -> **MCP**.
3. Click **+ Add New MCP Server**.
   - **Name:** `stock-signal-engine`
   - **Type:** `command`
   - **Command:** `/Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python /Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py`

Or add directly to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "stock-signal-engine": {
      "command": "/Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python",
      "args": [
        "/Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py"
      ]
    }
  }
}
```

---

## 4. Windsurf / Codeium

Add to `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "stock-signal-engine": {
      "command": "/Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python",
      "args": [
        "/Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py"
      ]
    }
  }
}
```

---

## 5. VS Code (Cline / Roo Code / Continue)

Open **Cline Settings** -> **MCP Servers** -> **Edit in settings.json**:
```json
{
  "mcpServers": {
    "stock-signal-engine": {
      "command": "/Users/voonfamily/Desktop/WORK/stock-signal-engine/.venv/bin/python",
      "args": [
        "/Users/voonfamily/Desktop/WORK/stock-signal-engine/mcp_server.py"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```
