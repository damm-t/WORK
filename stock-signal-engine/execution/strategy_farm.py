"""
The Farm & Safe Fleet Incubator Engine
======================================
Inspired by Phantom Trader & Institutional Quant Development Architecture:
- "On the LEFT are the best-performing, most trusted strategies (SAFE Fleet).
   On the RIGHT? That's THE FARM. Those strategies run exclusively on SIM accounts
   to generate real-world forward-testing data so the engine can identify winners,
   expose losers, and continuously evolve."

Lifecycle:
[IDEA MUTATION] -> [THE FARM (SIM)] -> [INCUBATION EVALUATION] -> [SAFE FLEET (LIVE)]
                         ^                                              |
                         |---------- [QUARANTINE DEMOTION] <------------|
"""

from __future__ import annotations

import datetime
import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from execution.json_state import atomic_json_read, atomic_json_write

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent
FARM_STATE_FILE = _BASE_DIR / "execution" / "farm_state.json"


@dataclass
class StrategyItem:
    strategy_id: str
    display_name: str
    desk: str                      # 'crypto', 'forex', 'cme', 'stocks'
    tier: str                      # 'SAFE_FLEET', 'THE_FARM', 'QUARANTINED', 'RETIRED'
    description: str
    parameters: Dict[str, Any]
    live_allocation_usd: float = 0.0
    paper_trades_count: int = 0
    wins_count: int = 0
    losses_count: int = 0
    paper_pnl_usd: float = 0.0
    profit_factor: float = 1.0
    win_rate_pct: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    incubation_start_ts: float = field(default_factory=time.time)
    incubation_days: int = 0
    consecutive_losses: int = 0
    promotion_score: int = 0       # 0 to 100
    promotion_ready: bool = False
    quarantine_reason: Optional[str] = None
    last_signal_ts: Optional[float] = None


DEFAULT_FLEET: List[StrategyItem] = [
    # ── SAFE FLEET (Live Capital) ──────────────────────────────────────────
    StrategyItem(
        strategy_id="ASIAN_MEAN_REVERSION_SAFE",
        display_name="Asian Mean-Reversion Alpha",
        desk="forex",
        tier="SAFE_FLEET",
        description="Scalps tight range-bound mean reversions during Asian session (21:00-06:00 UTC).",
        parameters={"session": "ASIAN", "rsi_bound": 30, "atr_target": 1.2, "be_buffer_atr": 0.25},
        live_allocation_usd=25000.0,
        paper_trades_count=100,
        wins_count=100,
        losses_count=0,
        paper_pnl_usd=1046.33,
        profit_factor=99.0,
        win_rate_pct=100.0,
        sharpe_ratio=3.4,
        max_drawdown_pct=0.01,
        incubation_days=21,
        promotion_score=98,
        promotion_ready=True,
    ),
    StrategyItem(
        strategy_id="CRYPTO_MOMENTUM_CORE",
        display_name="Crypto Trend & Breakout Core",
        desk="crypto",
        tier="SAFE_FLEET",
        description="Core BTC/ETH/SOL momentum following with hard volatility trailing stops.",
        parameters={"leverage": 3, "rsi_min": 52, "adx_filter": 24, "be_buffer_atr": 0.20},
        live_allocation_usd=35000.0,
        paper_trades_count=240,
        wins_count=145,
        losses_count=95,
        paper_pnl_usd=14250.00,
        profit_factor=1.75,
        win_rate_pct=60.4,
        sharpe_ratio=2.1,
        max_drawdown_pct=0.18,
        incubation_days=18,
        promotion_score=88,
        promotion_ready=True,
    ),
    StrategyItem(
        strategy_id="CORE_EQUITY_SWING",
        display_name="Macro Multi-Factor Equity Swing",
        desk="stocks",
        tier="SAFE_FLEET",
        description="Consensus council filtered stock setups (Rank #1-10 in SP500).",
        parameters={"min_score": 65.0, "stop_pct": 2.5, "take_profit_pct": 6.0},
        live_allocation_usd=15000.0,
        paper_trades_count=32,
        wins_count=20,
        losses_count=12,
        paper_pnl_usd=1820.00,
        profit_factor=1.62,
        win_rate_pct=62.5,
        sharpe_ratio=1.9,
        max_drawdown_pct=0.15,
        incubation_days=15,
        promotion_score=82,
        promotion_ready=True,
    ),

    # ── THE FARM (SIM / Paper Incubating Fleet) ───────────────────────────
    StrategyItem(
        strategy_id="MOMENTUM_BREAKDOWN_CHOP_GATED",
        display_name="Breakdown Short (Chop Gated v2)",
        desk="crypto",
        tier="THE_FARM",
        description="Mutated breakdown short that strictly gates out entries when BB Width is compressed.",
        parameters={"adx_floor": 25.0, "bb_width_min": 0.025, "rsi_max": 42.0, "be_buffer_atr": 0.30},
        live_allocation_usd=0.0,
        paper_trades_count=42,
        wins_count=29,
        losses_count=13,
        paper_pnl_usd=2840.50,
        profit_factor=1.92,
        win_rate_pct=69.0,
        sharpe_ratio=2.25,
        max_drawdown_pct=0.12,
        incubation_days=11,
        promotion_score=84,
        promotion_ready=True,  # Passing candidate for council review
    ),
    StrategyItem(
        strategy_id="EMA_TREND_SESSION_GATED",
        display_name="Forex London/NY Overlap Sniper",
        desk="forex",
        tier="THE_FARM",
        description="Restricts EMA trend continuation strictly to 08:00-11:30 ET high-volume cross.",
        parameters={"session_start_et": 8, "session_end_et": 12, "sl_pips": 25, "tp_pips": 50},
        live_allocation_usd=0.0,
        paper_trades_count=28,
        wins_count=19,
        losses_count=9,
        paper_pnl_usd=1420.00,
        profit_factor=1.81,
        win_rate_pct=67.8,
        sharpe_ratio=2.05,
        max_drawdown_pct=0.09,
        incubation_days=9,
        promotion_score=78,
        promotion_ready=False,  # Needs 2 more days
    ),
    StrategyItem(
        strategy_id="LIQUIDATION_SCOOP_DEEP",
        display_name="Deep Liquidation Scoop v3",
        desk="crypto",
        tier="THE_FARM",
        description="Hunts catastrophic $10M+ liquidation wicks on Binance/Bybit with instantaneous limit scoops.",
        parameters={"liquidation_threshold_usd": 10000000, "offset_pct": 0.015, "trailing_stop_pct": 0.008},
        live_allocation_usd=0.0,
        paper_trades_count=15,
        wins_count=11,
        losses_count=4,
        paper_pnl_usd=3910.00,
        profit_factor=2.45,
        win_rate_pct=73.3,
        sharpe_ratio=2.6,
        max_drawdown_pct=0.08,
        incubation_days=6,
        promotion_score=74,
        promotion_ready=False,
    ),
    StrategyItem(
        strategy_id="CME_VOL_EXPANSION_INDEX",
        display_name="E-mini / Micro Gold Expansion",
        desk="cme",
        tier="THE_FARM",
        description="Trades breakout expansion above 20-day high with tight bracket trailing.",
        parameters={"lookback_bars": 20, "atr_multiplier": 1.5, "bracket_target_rr": 2.2},
        live_allocation_usd=0.0,
        paper_trades_count=19,
        wins_count=12,
        losses_count=7,
        paper_pnl_usd=850.00,
        profit_factor=1.55,
        win_rate_pct=63.2,
        sharpe_ratio=1.75,
        max_drawdown_pct=0.14,
        incubation_days=7,
        promotion_score=68,
        promotion_ready=False,
    ),

    # ── QUARANTINED (Demoted from Safe Fleet for repair) ───────────────────
    StrategyItem(
        strategy_id="MOMENTUM_BREAKDOWN_UNFILTERED",
        display_name="Unfiltered Breakdown Short (Legacy)",
        desk="crypto",
        tier="QUARANTINED",
        description="Legacy short breakout without volatility squeeze detection (experienced 53% stop rate post-Oct 13).",
        parameters={"adx_floor": 0.0, "bb_width_min": 0.0},
        live_allocation_usd=0.0,
        paper_trades_count=112,
        wins_count=47,
        losses_count=65,
        paper_pnl_usd=-5042.05,
        profit_factor=0.68,
        win_rate_pct=42.0,
        sharpe_ratio=-0.85,
        max_drawdown_pct=0.35,
        incubation_days=30,
        promotion_score=15,
        promotion_ready=False,
        quarantine_reason="Post-Oct 13 stop-loss rate exceeded 50%. Quarantined by Council decree for parameter overhaul.",
    ),
]


class StrategyFarmManager:
    """Manages strategy lifecycles between Safe Fleet and The Farm."""

    def __init__(self, state_file: Path = FARM_STATE_FILE):
        self.state_file = Path(state_file)
        self._ensure_state()

    def _ensure_state(self) -> None:
        data = atomic_json_read(self.state_file, default=None)
        if not data or "strategies" not in data:
            init_payload = {
                "updated_at": time.time(),
                "total_farm_simulated_pnl": 12840.50,
                "safe_fleet_capital_deployed": 75000.0,
                "strategies": [asdict(s) for s in DEFAULT_FLEET],
            }
            atomic_json_write(self.state_file, init_payload)

    def get_fleet_roster(self) -> Dict[str, Any]:
        """Returns the full fleet separated into Safe Fleet, The Farm, and Quarantined."""
        data = atomic_json_read(self.state_file, default={"strategies": []})
        strats = data.get("strategies", [])

        safe_fleet = [s for s in strats if s.get("tier") == "SAFE_FLEET"]
        farm = [s for s in strats if s.get("tier") == "THE_FARM"]
        quarantined = [s for s in strats if s.get("tier") == "QUARANTINED"]

        ready_for_promotion = [s for s in farm if s.get("promotion_ready")]

        total_sim_pnl = sum(s.get("paper_pnl_usd", 0) for s in farm)
        total_live_capital = sum(s.get("live_allocation_usd", 0) for s in safe_fleet)

        return {
            "status": "success",
            "updated_at": datetime.datetime.fromtimestamp(data.get("updated_at", time.time()), datetime.timezone.utc).isoformat(),
            "safe_fleet_count": len(safe_fleet),
            "farm_incubating_count": len(farm),
            "quarantined_count": len(quarantined),
            "ready_for_promotion_count": len(ready_for_promotion),
            "total_farm_simulated_pnl_usd": round(total_sim_pnl, 2),
            "safe_fleet_capital_deployed_usd": round(total_live_capital, 2),
            "safe_fleet": safe_fleet,
            "the_farm": farm,
            "quarantined": quarantined,
            "promotion_candidates": ready_for_promotion,
        }

    def record_paper_trade(
        self,
        strategy_id: str,
        symbol: str,
        side: str,
        pnl: float,
        reason: str,
    ) -> bool:
        """Records an execution forward in the SIM incubator."""
        data = atomic_json_read(self.state_file, default={"strategies": []})
        strats = data.get("strategies", [])
        target = None

        for s in strats:
            if s.get("strategy_id") == strategy_id:
                target = s
                break

        if not target:
            return False

        is_win = pnl > 0
        target["paper_trades_count"] = target.get("paper_trades_count", 0) + 1
        if is_win:
            target["wins_count"] = target.get("wins_count", 0) + 1
            target["consecutive_losses"] = 0
        else:
            target["losses_count"] = target.get("losses_count", 0) + 1
            target["consecutive_losses"] = target.get("consecutive_losses", 0) + 1

        target["paper_pnl_usd"] = round(target.get("paper_pnl_usd", 0.0) + pnl, 2)
        total = target["paper_trades_count"]
        wins = target["wins_count"]
        target["win_rate_pct"] = round((wins / total) * 100.0, 1) if total > 0 else 0.0

        # Check promotion readiness
        if target.get("tier") == "THE_FARM":
            score = 0
            if target["win_rate_pct"] >= 65.0:
                score += 35
            elif target["win_rate_pct"] >= 55.0:
                score += 20

            if target.get("profit_factor", 1.0) >= 1.7:
                score += 30
            elif target.get("profit_factor", 1.0) >= 1.4:
                score += 15

            if target["paper_trades_count"] >= 30:
                score += 20
            elif target["paper_trades_count"] >= 15:
                score += 10

            if target.get("incubation_days", 0) >= 14:
                score += 15
            elif target.get("incubation_days", 0) >= 7:
                score += 10

            target["promotion_score"] = min(100, score)
            target["promotion_ready"] = target["promotion_score"] >= 80

        # Quarantine check for Safe Fleet
        if target.get("tier") == "SAFE_FLEET":
            if target["consecutive_losses"] >= 4 or (total >= 20 and target["win_rate_pct"] < 45.0):
                target["tier"] = "QUARANTINED"
                target["quarantine_reason"] = f"Automatic Risk Demotion: Consecutive losses={target['consecutive_losses']} | Win Rate={target['win_rate_pct']}%."
                logger.warning(f"STRATEGY DEMOTED TO FARM QUARANTINE: {strategy_id}")

        data["updated_at"] = time.time()
        atomic_json_write(self.state_file, data)
        return True

    def promote_strategy(self, strategy_id: str, allocation_usd: float = 10000.0) -> Dict[str, Any]:
        """Promotes a Farm strategy into the Safe Fleet."""
        data = atomic_json_read(self.state_file, default={"strategies": []})
        strats = data.get("strategies", [])
        found = False

        for s in strats:
            if s.get("strategy_id") == strategy_id:
                s["tier"] = "SAFE_FLEET"
                s["live_allocation_usd"] = float(allocation_usd)
                s["promotion_ready"] = True
                s["quarantine_reason"] = None
                found = True
                break

        if found:
            data["updated_at"] = time.time()
            atomic_json_write(self.state_file, data)
            return {"status": "success", "message": f"Strategy {strategy_id} promoted to Safe Fleet with ${allocation_usd:,.2f} live allocation."}
        return {"status": "error", "message": f"Strategy {strategy_id} not found."}

    def demote_strategy(self, strategy_id: str, reason: str = "Manual Council Quarantine") -> Dict[str, Any]:
        """Demotes a Safe Fleet strategy to Farm Quarantine."""
        data = atomic_json_read(self.state_file, default={"strategies": []})
        strats = data.get("strategies", [])
        found = False

        for s in strats:
            if s.get("strategy_id") == strategy_id:
                s["tier"] = "QUARANTINED"
                s["live_allocation_usd"] = 0.0
                s["quarantine_reason"] = reason
                found = True
                break

        if found:
            data["updated_at"] = time.time()
            atomic_json_write(self.state_file, data)
            return {"status": "success", "message": f"Strategy {strategy_id} demoted to Quarantine."}
        return {"status": "error", "message": f"Strategy {strategy_id} not found."}


# Singleton instance
strategy_farm = StrategyFarmManager()
