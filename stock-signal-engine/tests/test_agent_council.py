"""
Unit Tests for AI Agent Council & Virtual Trading Floor
=======================================================
Validates:
1. 5 Specialist Desks (Trend, Breakout, Sentiment, Whale, Risk Gatekeeper) & Head CIO
2. 7-Tier Institutional Pipeline Execution & Consensus Scoring
3. Sarah Connor's Risk Gatekeeper Approval / Veto Logic
4. Human-in-the-Loop Yes/No Decision Authorization
5. Web API endpoints (/office, /api/council/status, /api/council/convene, /api/council/decision)
6. MCP Server Registered Tools
"""

import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from agents.council import (
    DESK_ROSTER,
    convene_council_meeting,
    get_floor_status,
    get_recent_meetings,
    resolve_council_decision,
)
from webapp.app import app
from mcp_server import (
    convene_agent_council_meeting,
    get_virtual_office_status,
    submit_human_decision,
)


class TestAgentCouncilArchitecture(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_desk_roster_composition(self):
        """Verify all 5 specialized agent desks and CIO orchestrator are present."""
        self.assertIn("trend", DESK_ROSTER)
        self.assertIn("breakout", DESK_ROSTER)
        self.assertIn("sentiment", DESK_ROSTER)
        self.assertIn("whale", DESK_ROSTER)
        self.assertIn("risk", DESK_ROSTER)
        self.assertIn("cio", DESK_ROSTER)

        # Check key attributes
        trend = DESK_ROSTER["trend"]
        self.assertEqual(trend.name, "Alex 'Macro' Vance")
        risk = DESK_ROSTER["risk"]
        self.assertEqual(risk.name, "Sarah 'Ironclad' Connor")
        self.assertIn("VETO", risk.motto.upper())

    def test_convene_council_meeting_pipeline(self):
        """Verify the 7-tier pipeline runs and produces turns, votes, and risk evaluation."""
        meeting = convene_council_meeting(ticker="AAPL")
        self.assertTrue(meeting["meeting_id"].startswith("mtg_"))
        self.assertEqual(meeting["ticker"], "AAPL")
        self.assertIn(meeting["recommendation"], ["STRONG_BUY", "BUY", "HOLD", "CAUTION", "REJECT"])
        self.assertIn(meeting["risk_status"], ["APPROVED", "VETOED"])
        self.assertGreaterEqual(meeting["consensus_score"], 0)
        self.assertLessEqual(meeting["consensus_score"], 100)

        # Ensure all 6 turns are recorded (Trend, Breakout, Sentiment, Whale, Risk, CIO)
        self.assertEqual(len(meeting["turns"]), 6)
        agent_turns = [t["agent_id"] for t in meeting["turns"]]
        self.assertEqual(agent_turns, ["trend", "breakout", "sentiment", "whale", "risk", "cio"])

        # Check votes
        self.assertIn("trend", meeting["votes"])
        self.assertIn("breakout", meeting["votes"])
        self.assertIn("sentiment", meeting["votes"])
        self.assertIn("whale", meeting["votes"])
        self.assertIn("risk", meeting["votes"])

        # Check 7 tiers in pipeline
        self.assertEqual(len(meeting["pipeline_tiers"]), 7)

    def test_human_in_the_loop_approval_lifecycle(self):
        """Test human authorization: APPROVE routes execution, REJECT preserves capital."""
        # 1. Convene meeting
        meeting = convene_council_meeting(ticker="NVDA")
        mtg_id = meeting["meeting_id"]
        self.assertEqual(meeting["status"], "PENDING_HUMAN_APPROVAL")

        # 2. Reject flow
        rejected = resolve_council_decision(mtg_id, "REJECT")
        self.assertEqual(rejected["status"], "success")
        self.assertEqual(rejected["meeting"]["status"], "REJECTED_BY_HUMAN")
        self.assertEqual(rejected["meeting"]["human_decision"], "REJECT")

        # 3. Approve flow on fresh meeting
        m2 = convene_council_meeting(ticker="MSFT")
        m2_id = m2["meeting_id"]
        approved = resolve_council_decision(m2_id, "APPROVE")
        self.assertEqual(approved["status"], "success")
        self.assertIn(approved["meeting"]["status"], ["APPROVED", "EXECUTED"])
        self.assertIsNotNone(approved["meeting"]["execution_result"])

    def test_floor_status_and_leaderboard(self):
        """Test virtual floor telemetry, fund capital, and live chatter."""
        status = get_floor_status()
        self.assertEqual(status["status"], "success")
        self.assertGreater(status["fund_equity"], 0)
        self.assertEqual(status["desks_online"], 5)
        self.assertEqual(status["sub_bots_connected"], 300)
        self.assertEqual(len(status["agents"]), 6)

        # Check leaderboard metrics as shown in the video
        lb = status["leaderboard"]
        self.assertIn("human_coaches", lb)
        self.assertIn("ai_desks", lb)
        self.assertIn("fund_total", lb)
        self.assertEqual(lb["human_coaches"]["return_pct"], "+1.43%")
        self.assertEqual(lb["ai_desks"]["return_pct"], "+2.84%")

        # Floor chatter should have entries
        self.assertGreater(len(status["floor_chatter"]), 0)

    def test_webapp_council_api_endpoints(self):
        """Test FastAPI webapp endpoints for Virtual Floor and Council."""
        # GET /office
        resp_office = self.client.get("/office")
        self.assertEqual(resp_office.status_code, 200)
        self.assertIn("Quant Desk AI Trading Floor", resp_office.text)

        # GET /api/council/status
        resp_status = self.client.get("/api/council/status")
        self.assertEqual(resp_status.status_code, 200)
        data = resp_status.json()
        self.assertEqual(data["status"], "success")

        # POST /api/council/convene
        resp_convene = self.client.post("/api/council/convene", json={"ticker": "TSLA"})
        self.assertEqual(resp_convene.status_code, 200)
        m_data = resp_convene.json()
        self.assertEqual(m_data["ticker"], "TSLA")
        mtg_id = m_data["meeting_id"]

        # POST /api/council/decision
        resp_dec = self.client.post("/api/council/decision", json={"meeting_id": mtg_id, "decision": "APPROVE"})
        self.assertEqual(resp_dec.status_code, 200)
        self.assertEqual(resp_dec.json()["status"], "success")

        # GET /api/council/recent
        resp_rec = self.client.get("/api/council/recent?limit=5")
        self.assertEqual(resp_rec.status_code, 200)
        self.assertGreater(len(resp_rec.json()["meetings"]), 0)

    def test_mcp_council_tools(self):
        """Test that MCP tools can be invoked directly by external AI builders."""
        # Tool 1: convene_agent_council_meeting
        mcp_mtg = convene_agent_council_meeting(ticker="AMD")
        self.assertEqual(mcp_mtg["status"], "success")
        self.assertEqual(mcp_mtg["ticker"], "AMD")
        self.assertIn("turns_summary", mcp_mtg)
        self.assertEqual(len(mcp_mtg["turns_summary"]), 6)

        # Tool 2: get_virtual_office_status
        mcp_status = get_virtual_office_status()
        self.assertEqual(mcp_status["status"], "success")
        self.assertEqual(mcp_status["sub_bots_connected"], 300)

        # Tool 3: submit_human_decision
        mcp_res = submit_human_decision(meeting_id=mcp_mtg["meeting_id"], decision="REJECT")
        self.assertEqual(mcp_res["status"], "success")
        self.assertEqual(mcp_res["meeting"]["status"], "REJECTED_BY_HUMAN")


if __name__ == "__main__":
    unittest.main()
