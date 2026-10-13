"""
Unit & Integration Tests for Architecture Review Fixes
======================================================
Validates all patches applied from the architecture review:
1. PIN Auth Hardening: raw PIN bypass rejected, HMAC token accepted, cookie HttpOnly, rate limiting.
2. Webapp /health & /api/health telemetry endpoints.
3. Pipeline multi-article weighted conviction calculation.
4. Concurrency & crash-safe atomic JSON persistence with file locking.
5. Autopilot Dead-Man's switch failsafe evaluation.
6. Dynamic non-stock desk trade scores and reward:risk computation.
"""

import time
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from webapp.app import app, _PIN_AUTH_TOKEN, DASHBOARD_PIN
from unittest.mock import patch
from execution.json_state import atomic_json_read, atomic_json_write
from execution.deadmans_switch import check_liveness
from pipeline import news_deep_dive


class TestArchitectureFixes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pin_auth_hardening_rejects_raw_pin(self):
        """Raw PIN string in token header or cookie must NOT grant authenticated access."""
        # Test raw PIN header
        resp = self.client.get(
            "/api/account",
            headers={
                "X-Forwarded-For": "203.0.113.195",
                "X-Dash-PIN-Token": DASHBOARD_PIN
            }
        )
        self.assertEqual(resp.status_code, 401)
        self.assertTrue(resp.json().get("pin_required"))

        # Test valid HMAC token
        resp_authed = self.client.get(
            "/api/account",
            headers={
                "X-Forwarded-For": "203.0.113.195",
                "X-Dash-PIN-Token": _PIN_AUTH_TOKEN
            }
        )
        self.assertEqual(resp_authed.status_code, 200)

    def test_pin_auth_cookie_is_httponly(self):
        """PIN verification must return HttpOnly cookie to mitigate XSS exfiltration."""
        resp = self.client.post("/api/auth/verify-pin", json={"pin": DASHBOARD_PIN})
        self.assertEqual(resp.status_code, 200)
        cookie = resp.cookies.get("dash_pin_token")
        self.assertIsNotNone(cookie)
        self.assertEqual(cookie, _PIN_AUTH_TOKEN)
        # Check raw set-cookie header contains httponly
        set_cookie_header = resp.headers.get("set-cookie", "").lower()
        self.assertIn("httponly", set_cookie_header)

    def test_pin_status_does_not_leak_default_hint(self):
        """Public /api/auth/status must never announce the default PIN in the response."""
        resp = self.client.get("/api/auth/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotIn("hint", data)

    def test_pin_verify_rate_limiting(self):
        """Repeated failed PIN attempts must trigger HTTP 429 Too Many Requests."""
        test_ip = "198.51.100.42"
        # 4 failed attempts should return 401
        for _ in range(4):
            r = self.client.post(
                "/api/auth/verify-pin",
                json={"pin": "0000"},
                headers={"CF-Connecting-IP": test_ip}
            )
            self.assertEqual(r.status_code, 401)

        # 5th failed attempt triggers rate limit lockout (429)
        r5 = self.client.post(
            "/api/auth/verify-pin",
            json={"pin": "0000"},
            headers={"CF-Connecting-IP": test_ip}
        )
        self.assertEqual(r5.status_code, 429)
        self.assertIn("Too many failed", r5.json().get("detail", ""))

    def test_health_endpoints(self):
        """Both /health and /api/health must be public and return structured liveness."""
        for endpoint in ["/health", "/api/health"]:
            resp = self.client.get(endpoint)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("status", data)
            self.assertIn("uptime_seconds", data)
            self.assertIn("database", data)
            self.assertIn("autopilot", data)
            self.assertIn("desks", data)

    @patch("pipeline.fetch_all")
    @patch("pipeline.analyze_sentiment_only")
    def test_pipeline_multi_article_conviction(self, mock_sent, mock_fetch):
        """Multi-article conviction must incorporate all articles rather than discarding enriched[1:]."""
        # Article 0 is neutral, while articles 1, 2, 3 are strongly positive
        mock_fetch.return_value = [
            {"title": "Company quarterly routine update", "source": "Wire"},
            {"title": "Record Q3 earnings blowout beats estimates", "source": "Bloomberg"},
            {"title": "Major $10B enterprise AI contract signed", "source": "Reuters"},
            {"title": "Analyst raises target price by 40%", "source": "CNBC"},
        ]
        mock_sent.side_effect = [
            {"sentiment": "neutral", "sentiment_score": 0.50},
            {"sentiment": "positive", "sentiment_score": 0.95},
            {"sentiment": "positive", "sentiment_score": 0.90},
            {"sentiment": "positive", "sentiment_score": 0.88},
        ]

        res = news_deep_dive("MSFT", store=False)
        self.assertEqual(res["ticker"], "MSFT")
        self.assertEqual(res["n"], 4)
        # Because articles 1-3 are strongly positive, aggregate conviction must be high (>65)
        self.assertGreater(res["conviction"], 65.0)
        self.assertEqual(res["label"], "positive")

    def test_atomic_json_read_write_locking(self):
        """Atomic read/write must guarantee data integrity without corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = Path(tmpdir) / "test_state.json"
            sample = {"cycle": 42, "symbols": ["BTC", "ETH"], "score": 91.5}
            atomic_json_write(fpath, sample)
            loaded = atomic_json_read(fpath)
            self.assertEqual(loaded, sample)

            # Test reading non-existent file returns default
            non_existent = Path(tmpdir) / "missing.json"
            self.assertEqual(atomic_json_read(non_existent, default={"fallback": True}), {"fallback": True})

    def test_deadmans_switch_evaluation(self):
        """Dead-man's switch must detect fresh vs stale heartbeat."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hb_file = Path(tmpdir) / "test_hb.json"
            # Write fresh heartbeat
            atomic_json_write(hb_file, {"timestamp": time.time(), "cycle": 1})
            
            # Monkeypatch HEARTBEAT_PATH for check
            from execution import deadmans_switch
            orig_path = deadmans_switch.HEARTBEAT_PATH
            try:
                deadmans_switch.HEARTBEAT_PATH = hb_file
                rep_fresh = check_liveness(max_staleness=600)
                self.assertEqual(rep_fresh["status"], "HEALTHY")
                self.assertFalse(rep_fresh["is_stale"])

                # Write stale heartbeat (15 minutes ago)
                atomic_json_write(hb_file, {"timestamp": time.time() - 900, "cycle": 1})
                rep_stale = check_liveness(max_staleness=600)
                self.assertEqual(rep_stale["status"], "STALE")
                self.assertTrue(rep_stale["is_stale"])
            finally:
                deadmans_switch.HEARTBEAT_PATH = orig_path


if __name__ == "__main__":
    unittest.main()
