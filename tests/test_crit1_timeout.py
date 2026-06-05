"""Tests para CRIT-1: qbo_request() debe tener timeout + retry on Timeout/ConnectionError.

Bug: main.py:280,282,292,294 — `requests.get/post(...)` sin timeout
      → proceso puede colgarse indefinidamente.

Fix: agregar timeout configurable (default 30s) y reintentar 1× en Timeout/ConnectionError.
"""
import unittest
from unittest.mock import patch, MagicMock

import requests


class TestQboRequestTimeout(unittest.TestCase):
    """CRIT-1: qbo_request debe tener timeout y manejar Timeout/ConnectionError."""

    def setUp(self):
        """Patch QB_BASE_URL/QB_ACCESS_TOKEN antes de importar."""
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_get_request_uses_timeout(self):
        """RED: qbo_request GET debe pasar timeout a requests.get (no None)."""
        from main import qbo_request

        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_get.return_value = mock_response

            qbo_request("GET", "companyinfo/1")

            self.assertTrue(mock_get.called, "requests.get debe ser llamado")
            call_kwargs = mock_get.call_args.kwargs
            self.assertIn(
                "timeout", call_kwargs,
                f"requests.get debe recibir timeout, no colgar. Got kwargs: {call_kwargs}"
            )
            self.assertIsNotNone(
                call_kwargs.get("timeout"),
                f"timeout no debe ser None. Got: {call_kwargs.get('timeout')}"
            )

    def test_post_request_uses_timeout(self):
        """RED: qbo_request POST debe pasar timeout a requests.post."""
        from main import qbo_request

        with patch("main.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response

            qbo_request("POST", "customer", data={"DisplayName": "Test"})

            self.assertTrue(mock_post.called)
            call_kwargs = mock_post.call_args.kwargs
            self.assertIn(
                "timeout", call_kwargs,
                f"requests.post debe recibir timeout. Got: {call_kwargs}"
            )
            self.assertIsNotNone(
                call_kwargs.get("timeout"),
                f"timeout no debe ser None. Got: {call_kwargs.get('timeout')}"
            )

    def test_timeout_raises_within_bounded_time(self):
        """RED: si QBO no responde, qbo_request debe lanzar Timeout, no colgar."""
        from main import qbo_request

        with patch("main.requests.get", side_effect=requests.exceptions.Timeout("slow")):
            with self.assertRaises(requests.exceptions.Timeout):
                qbo_request("GET", "companyinfo/1")

    def test_connection_error_raises(self):
        """RED: ConnectionError no debe matar el proceso silenciosamente."""
        from main import qbo_request

        with patch("main.requests.get", side_effect=requests.exceptions.ConnectionError("net down")):
            with self.assertRaises(requests.exceptions.ConnectionError):
                qbo_request("GET", "companyinfo/1")


if __name__ == "__main__":
    unittest.main()
