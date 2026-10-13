"""
AI Agent Trading Floor & Multi-Agent Council
=============================================
Specialized quantitative desks modeled after the 5-agent institutional virtual floor:
- Trend Desk (Macro trend alignment & Moving Average regimes)
- Breakout Desk (Bollinger band squeezes, RSI momentum, ATR breakouts)
- News & Sentiment Desk (FinBERT natural language catalyst scoring)
- Whale & Order Flow Desk (Volume ratio, OBV accumulation, institutional footprint)
- Risk Desk (The Gatekeeper: strict drawdown limit, stop-loss, position sizing, VETO power)
- Head CIO Agent (Synthesis, consensus scoring, and Human-in-the-Loop Yes/No safeguard)
"""

from .council import (
    AgentCouncil,
    CouncilMeetingResult,
    DeskAgent,
    convene_council_meeting,
    get_floor_status,
    get_recent_meetings,
    resolve_council_decision,
)

__all__ = [
    "AgentCouncil",
    "CouncilMeetingResult",
    "DeskAgent",
    "convene_council_meeting",
    "get_floor_status",
    "get_recent_meetings",
    "resolve_council_decision",
]
