# QuantDesk Project & Deployment Architecture

## 1. Executive Summary & Host Topography

QuantDesk is an institutional-grade, multi-desk autonomous trading system. The system runs 24/7 continuously on a dedicated host machine.

### Critical Infrastructure Topology

* **24/7 Primary Host Engine (Production Server)**:
  * **Machine**: `seesharpwin1` (Dedicated Windows Machine)
  * **Tailscale Static IP**: `100.105.70.120`
  * **Web & API Port**: `8080` (FastAPI + Uvicorn)
  * **Active Desks Running 24/7**:
    * Desk 1: **Stocks** (Alpaca Paper, 15-min momentum cycle, Ross Cameron 5-pillars, JEV scooper)
    * Desk 2: **Crypto** (24/7 perpetual futures, capitulation scoopers, trap defense)
    * Desk 3: **Futures** (CME micro indices, dynamic trailing brackets)
    * Desk 4: **Forex** (Session-based FX pairs)
  * **Access URLs**:
    * Dashboard: `http://100.105.70.120:8080`
    * Mobile HUD Widget: `http://100.105.70.120:8080/widget`
    * Health Telemetry: `http://100.105.70.120:8080/health`

* **Local Mac Client (Development & Management Machine)**:
  * **Machine**: `macbook-pro` (macOS)
  * **Tailscale IP**: `100.77.178.28`
  * **Role**: Code editing, testing, model research, and git version control.
  * **Important**: This Mac is **NOT** the 24/7 trading server. The Mac can be closed, put to sleep, or shut down at any time without interrupting active trading.
  * **Avoid Duplicate Autopilot**: Do not leave `./quant start` or `execution.autopilot` running locally on the Mac to prevent duplicate trade submissions against the live broker account.

* **Mobile Devices (iPhone / iPad)**:
  * Connected via Tailscale mesh VPN.
  * Accesses `http://100.105.70.120:8080/widget` to monitor portfolio equity and desk status in real-time.

---

## 2. Remote Access & Tailscale Networking Rules

1. **Host Tailscale**: The Windows machine (`seesharpwin1`) must keep Tailscale active in the background so it can receive connections from phone and client devices.
2. **Client Tailscale**: Phones or laptops only need Tailscale active when opening the dashboard or widget remotely.
3. **Backup Cloudflare Tunnel**: If Tailscale is unavailable, the webapp also supports dynamic Cloudflare Quick Tunnels via `webapp/tunnel_manager.py`.

---

## 3. Core Desks & Automation Components

* **Autopilot Runner**: `execution/autopilot.py`
* **Web & Telemetry Hub**: `webapp/app.py`
* **One-Command CLI**: `./quant status`, `./quant stop`, `./quant logs`
* **SQLite Ledgers**:
  * `data/trade_journal.db` (Master trade ledger)
  * `data/compliance_audit.db` (Rule compliance ledger)
