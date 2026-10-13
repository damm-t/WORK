"""
Factor DAG Pipeline Engine (Inspired by Qanat & Agent-Native Quant Systems)
===========================================================================
Defines quantitative alpha factors and data processing stages as a
Directed Acyclic Graph (DAG) for autonomous AI agents and quant researchers.

Features:
  - Topological Dependency Ordering (Kahn's algorithm).
  - Strict Point-in-Time session alignment node to eliminate lookahead bias.
  - Composable nodes: Price Ingestion, News Ingestion, Sentiment, Technicals, Alpha Blending.
  - Dual Backtesting Execution: Leak-Free Point-in-Time vs. Naive Leaked.
  - Self-documenting Mermaid diagram generation.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

from data.point_in_time import (
    align_timestamp_point_in_time,
    enrich_article_point_in_time,
    validate_anti_leakage,
)
from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DAG Nodes Base
# ---------------------------------------------------------------------------
class Node:
    """Base class for every computation node in the factor DAG."""

    def __init__(self, name: str, inputs: Optional[List[str]] = None):
        self.name = name
        self.inputs = inputs or []

    def compute(self, context: Dict[str, Any]) -> Any:
        raise NotImplementedError("Subclasses must implement compute()")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', inputs={self.inputs})"


# ---------------------------------------------------------------------------
# Concrete Pipeline Nodes
# ---------------------------------------------------------------------------
class PriceSourceNode(Node):
    """Ingests OHLCV market bars for the target ticker."""

    def __init__(self, name: str = "price_source", ticker: str = "NVDA", period: str = "1y"):
        super().__init__(name=name, inputs=[])
        self.ticker = ticker.upper()
        self.period = period

    def compute(self, context: Dict[str, Any]) -> pd.DataFrame:
        ticker = context.get("ticker", self.ticker)
        period = context.get("period", self.period)
        df = fetch_prices(ticker, period=period)
        if df.empty:
            raise ValueError(f"No price data available for {ticker} ({period})")
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        return df


class NewsSourceNode(Node):
    """
    Ingests financial news headlines with publication timestamps.
    Can use live ingestion or provided historical news datasets.
    """

    def __init__(self, name: str = "news_source", ticker: str = "NVDA", fallback_live: bool = True):
        super().__init__(name=name, inputs=[])
        self.ticker = ticker.upper()
        self.fallback_live = fallback_live

    def compute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        if "news_articles" in context:
            return context["news_articles"]

        ticker = context.get("ticker", self.ticker)
        if self.fallback_live:
            try:
                from ingestion import fetch_all
                articles = fetch_all(ticker)
                return articles or []
            except Exception as e:
                logger.warning(f"Live news fetch failed: {e}")
        return []


class PointInTimeAlignmentNode(Node):
    """
    Maps every news headline to its FIRST viable regular trading session,
    strictly eliminating after-hours / weekend lookahead bias.
    """

    def __init__(self, name: str = "pit_aligner", news_input: str = "news_source"):
        super().__init__(name=name, inputs=[news_input])
        self.news_input = news_input

    def compute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_news: List[Dict[str, Any]] = context[self.news_input]
        aligned_articles = []
        for a in raw_news:
            enriched = enrich_article_point_in_time(a)
            aligned_articles.append(enriched)
        return aligned_articles


class SentimentAggregatorNode(Node):
    """
    Aggregates news sentiment by trading day using either:
      - 'point_in_time': groups by effective_trade_date (leak-free)
      - 'naive_leaked': groups by printed calendar_date (contains lookahead leakage)
    """

    def __init__(
        self,
        name: str = "sentiment_factor",
        news_input: str = "pit_aligner",
        mode: str = "point_in_time",
    ):
        super().__init__(name=name, inputs=[news_input])
        self.news_input = news_input
        self.mode = mode

    def compute(self, context: Dict[str, Any]) -> pd.DataFrame:
        mode = context.get("execution_mode", self.mode)
        articles: List[Dict[str, Any]] = context[self.news_input]

        if not articles:
            return pd.DataFrame(columns=["date", "sentiment_score", "article_count"])

        date_key = "effective_trade_date" if mode == "point_in_time" else "calendar_date"

        daily_groups: Dict[str, List[float]] = defaultdict(list)
        for a in articles:
            d = a.get(date_key)
            if not d:
                continue

            # Retrieve score or fallback to sentiment polarity
            score = float(a.get("sentiment_score", 0.0) or 0.0)
            if score == 0.0:
                sentiment = str(a.get("sentiment", "neutral")).lower()
                if "pos" in sentiment:
                    score = 0.75
                elif "neg" in sentiment:
                    score = -0.75
                else:
                    score = 0.0

            daily_groups[d].append(score)

        rows = []
        for d_str, scores in sorted(daily_groups.items()):
            avg_score = float(np.mean(scores))
            rows.append({
                "date": pd.to_datetime(d_str),
                "sentiment_score": round(avg_score, 4),
                "article_count": len(scores),
            })

        df_sent = pd.DataFrame(rows)
        if not df_sent.empty:
            df_sent.set_index("date", inplace=True)
        return df_sent


class TechnicalFeaturesNode(Node):
    """Computes technical indicator factors (RSI, MACD, ATR, Bollinger Bands)."""

    def __init__(self, name: str = "technicals", price_input: str = "price_source"):
        super().__init__(name=name, inputs=[price_input])
        self.price_input = price_input

    def compute(self, context: Dict[str, Any]) -> pd.DataFrame:
        df: pd.DataFrame = context[self.price_input].copy()
        close = df["Close"]

        df["RSI"] = TI.rsi(close)
        df["MACD"], df["MACD_Signal"] = TI.macd(close)
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
        df["ATR"] = TI.atr(df)
        df["SMA20"] = TI.sma(close, 20)
        df["SMA50"] = TI.sma(close, 50)
        return df


class AlphaCompositeNode(Node):
    """
    Merges technical indicators with point-in-time sentiment factors into
    a normalized composite alpha signal S_t in [-1.0, 1.0].
    """

    def __init__(
        self,
        name: str = "alpha_composite",
        price_tech_input: str = "technicals",
        sentiment_input: str = "sentiment_factor",
        weight_tech: float = 0.40,
        weight_sent: float = 0.60,
    ):
        super().__init__(name=name, inputs=[price_tech_input, sentiment_input])
        self.price_tech_input = price_tech_input
        self.sentiment_input = sentiment_input
        self.weight_tech = weight_tech
        self.weight_sent = weight_sent

    def compute(self, context: Dict[str, Any]) -> pd.DataFrame:
        df_tech: pd.DataFrame = context[self.price_tech_input].copy()
        df_sent: pd.DataFrame = context[self.sentiment_input].copy()

        # Ensure indices match timezone-naive dates
        if hasattr(df_tech.index, "tz") and df_tech.index.tz is not None:
            df_tech.index = df_tech.index.tz_localize(None)
        df_tech.index = pd.to_datetime(df_tech.index).normalize()

        if hasattr(df_sent.index, "tz") and df_sent.index.tz is not None:
            df_sent.index = df_sent.index.tz_localize(None)
        df_sent.index = pd.to_datetime(df_sent.index).normalize()

        # Merge on date index
        df = df_tech.join(df_sent, how="left")
        df["sentiment_score"] = df["sentiment_score"].fillna(0.0)
        df["article_count"] = df["article_count"].fillna(0)

        # Technical Score in [-1, 1]:
        # Positive if RSI 35-65 & MACD_Hist > 0 & Close > SMA50
        rsi = df["RSI"].fillna(50.0)
        macd_h = df["MACD_Hist"].fillna(0.0)
        sma50 = df["SMA50"].fillna(df["Close"])

        tech_signal = np.zeros(len(df))
        tech_signal += np.where((rsi > 40.0) & (rsi < 70.0), 0.35, -0.2)
        tech_signal += np.where(macd_h > 0, 0.35, -0.35)
        tech_signal += np.where(df["Close"] > sma50, 0.30, -0.30)
        tech_signal = np.clip(tech_signal, -1.0, 1.0)

        df["tech_signal"] = tech_signal

        # Composite Alpha = weight_tech * tech_signal + weight_sent * sentiment_score
        alpha = self.weight_tech * df["tech_signal"] + self.weight_sent * df["sentiment_score"]
        df["alpha_signal"] = np.clip(alpha, -1.0, 1.0)
        return df


# ---------------------------------------------------------------------------
# DAG Engine & Backtester
# ---------------------------------------------------------------------------
class FactorDAG:
    """
    Agent-native workflow engine orchestrating alpha factor nodes
    with topological dependency execution.
    """

    def __init__(self, name: str = "FactorPipeline"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.execution_order: List[str] = []

    def add_node(self, node: Node) -> FactorDAG:
        self.nodes[node.name] = node
        self.execution_order = self._topological_sort()
        return self

    def _topological_sort(self) -> List[str]:
        in_degree = {name: 0 for name in self.nodes}
        graph = defaultdict(list)

        for name, node in self.nodes.items():
            for inp in node.inputs:
                if inp not in self.nodes:
                    raise ValueError(f"Node '{name}' references unknown input node '{inp}'")
                graph[inp].append(name)
                in_degree[name] += 1

        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("Cycle detected in Factor DAG! Nodes must form a directed acyclic graph.")

        return order

    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs the DAG in topological order, passing outputs along the context."""
        context = dict(initial_context or {})
        for node_name in self.execution_order:
            node = self.nodes[node_name]
            logger.debug(f"Executing DAG node: {node_name}")
            output = node.compute(context)
            context[node_name] = output
        return context

    def to_mermaid(self) -> str:
        """Renders the DAG as a GitHub-flavored Mermaid graph."""
        lines = ["```mermaid", "graph TD"]
        for node_name in self.execution_order:
            node = self.nodes[node_name]
            node_label = f'{node_name}["{node.__class__.__name__}<br/>({node_name})"]'
            for inp in node.inputs:
                lines.append(f"    {inp} --> {node_name}")
        lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def simulate_strategy(
        df_alpha: pd.DataFrame,
        mode: str = "point_in_time",
        threshold: float = 0.20,
        cost_bps: float = 5.0,  # 5 bps transaction friction
    ) -> Dict[str, Any]:
        """
        Simulates strategy returns.
          - 'point_in_time': Signal generated at close of day T executes at Open of day T+1.
          - 'naive_leaked': Signal generated on calendar date T executes at Open of day T
                            (Lookahead leakage: trades today using tonight's after-hours news!)
        """
        df = df_alpha.copy().sort_index()
        n = len(df)
        if n < 5:
            return {"error": "Insufficient data"}

        closes = df["Close"].values
        opens = df["Open"].values if "Open" in df.columns else closes
        signals = df["alpha_signal"].values

        positions = np.zeros(n)
        returns = np.zeros(n)

        # In Point-in-Time: Signal at i-1 dictates position held on day i
        # In Naive Leaked: Signal at i dictates position on day i (lookahead!)
        for i in range(1, n):
            if mode == "point_in_time":
                # Decision made with information available up to close of bar i-1
                sig = signals[i - 1]
                pos = 1.0 if sig >= threshold else (-1.0 if sig <= -threshold else 0.0)
                positions[i] = pos
                # Return from Open of day i to Close of day i (or Close to Close)
                day_ret = (closes[i] - opens[i]) / opens[i]
                returns[i] = pos * day_ret
            else:
                # Naive Leaked: uses signal of day i (which naively grouped after-hours news)
                # to trade the full day i return (Open to Close)
                sig = signals[i]
                pos = 1.0 if sig >= threshold else (-1.0 if sig <= -threshold else 0.0)
                positions[i] = pos
                day_ret = (closes[i] - opens[i]) / opens[i]
                returns[i] = pos * day_ret

            # Transaction cost deduction on position change
            if positions[i] != positions[i - 1]:
                returns[i] -= cost_bps / 10000.0

        cum_equity = np.cumprod(1.0 + returns)
        total_return = float(cum_equity[-1] - 1.0)
        daily_vol = float(np.std(returns))
        ann_vol = daily_vol * np.sqrt(252) if daily_vol > 0 else 1e-6
        ann_ret = float(np.mean(returns)) * 252
        sharpe = round(ann_ret / ann_vol, 2)

        peak = np.maximum.accumulate(cum_equity)
        drawdown = (cum_equity - peak) / peak
        max_dd = round(float(np.min(drawdown)) * 100.0, 2)

        trades_count = int(np.count_nonzero(np.diff(positions)))
        win_trades = int(np.count_nonzero(returns > 0))
        loss_trades = int(np.count_nonzero(returns < 0))
        win_rate = round(win_trades / max(1, (win_trades + loss_trades)) * 100.0, 1)

        return {
            "mode": mode,
            "total_return_pct": round(total_return * 100.0, 2),
            "annualized_return_pct": round(ann_ret * 100.0, 2),
            "annualized_vol_pct": round(ann_vol * 100.0, 2),
            "sharpe_ratio": sharpe,
            "max_drawdown_pct": max_dd,
            "win_rate_pct": win_rate,
            "total_rebalances": trades_count,
            "bars_evaluated": n,
        }
