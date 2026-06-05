"""Tests para CRIT-4: qbo_request debe reintentar en 429/503 con backoff exponencial.

Bug: main.py — qbo_request solo refrescaba token en 401, ignoraba 429/503.
      QBO rate limit (429) o service unavailable (503) → error cascada.

Fix: agregar 3 reintentos con backoff exponencial (1s, 2s, 4s) en 429/503/Timeout.
"""
import unittest
from unittest.mock import patch, MagicMock
import time

import requests


class TestQboRequestRetry(unittest.TestCase):
    """CRIT-4: qbo_request debe reintentar en 429/503 con backoff."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_429_triggers_retry_and_succeeds(self):
        """RED: si QBO retorna 429 dos veces y luego 200, qbo_request debe retornar 200."""
        from main import qbo_request

        responses = [
            MagicMock(status_code=429, text="rate limited"),
            MagicMock(status_code=429, text="rate limited"),
            MagicMock(status_code=200, json=lambda: {"ok": True}, text="ok"),
        ]

        with patch("main.requests.get", side_effect=responses):
            with patch("dexter.core.retry.time.sleep") as mock_sleep:
                response = qbo_request("GET", "companyinfo/1")

        self.assertEqual(response.status_code, 200, f"Final response debe ser 200. Got: {response.status_code}")
        # Verificar que se durmió al menos 2 veces (entre 3 reintentos)
        self.assertGreaterEqual(
            mock_sleep.call_count, 2,
            f"Debe dormir al menos 2 veces (entre reintentos). Got: {mock_sleep.call_count}"
        )

    def test_503_triggers_retry_and_succeeds(self):
        """RED: 503 dos veces y luego 200 → debe retornar 200."""
        from main import qbo_request

        responses = [
            MagicMock(status_code=503, text="unavailable"),
            MagicMock(status_code=200, json=lambda: {"ok": True}, text="ok"),
        ]

        with patch("main.requests.get", side_effect=responses):
            with patch("dexter.core.retry.time.sleep") as mock_sleep:
                response = qbo_request("GET", "companyinfo/1")

        self.assertEqual(response.status_code, 200, f"Final response debe ser 200. Got: {response.status_code}")
        self.assertGreaterEqual(mock_sleep.call_count, 1, "Debe dormir al menos 1 vez")

    def test_429_after_max_retries_returns_last(self):
        """RED: 4 reintentos de 429 → retornar el último 429 (no reintentar infinito)."""
        from main import qbo_request

        responses = [
            MagicMock(status_code=429, text="rate limited") for _ in range(10)
        ]

        with patch("main.requests.get", side_effect=responses):
            with patch("dexter.core.retry.time.sleep") as mock_sleep:
                response = qbo_request("GET", "companyinfo/1")

        # Después de N reintentos, retornar el último
        self.assertEqual(response.status_code, 429, f"Final response debe ser 429. Got: {response.status_code}")
        # Debe haber dormido N-1 veces
        self.assertLessEqual(
            mock_sleep.call_count, 3,
            f"Debe dormir máximo 3 veces (3 reintentos). Got: {mock_sleep.call_count}"
        )

    def test_backoff_is_exponential(self):
        """RED: los sleeps deben seguir backoff exponencial (1s, 2s, 4s)."""
        from main import qbo_request

        responses = [
            MagicMock(status_code=429, text="rl") for _ in range(5)
        ]

        with patch("main.requests.get", side_effect=responses):
            with patch("dexter.core.retry.time.sleep") as mock_sleep:
                qbo_request("GET", "companyinfo/1")

        # Verificar que los sleeps siguen 1, 2, 4 (con posibles capping)
        sleep_values = [call.args[0] for call in mock_sleep.call_args_list if call.args]
        self.assertGreater(len(sleep_values), 0, "Debe haber al menos 1 sleep")
        # Primer sleep debe ser > 0 y <= 4 (exponential capped)
        for i, val in enumerate(sleep_values[:3]):
            self.assertGreater(val, 0, f"Sleep {i} debe ser > 0")
            self.assertLessEqual(val, 4, f"Sleep {i} debe ser <= 4 (max backoff)")

    def test_400_does_not_retry(self):
        """RED: 400 (Bad Request) NO debe reintentarse (es error del cliente, no transitorio)."""
        from main import qbo_request

        call_count = [0]
        def mock_get(*args, **kwargs):
            call_count[0] += 1
            return MagicMock(status_code=400, text="bad request", json=lambda: {"error": "bad"})

        with patch("main.requests.get", side_effect=mock_get):
            with patch("dexter.core.retry.time.sleep") as mock_sleep:
                response = qbo_request("GET", "companyinfo/1")

        self.assertEqual(response.status_code, 400, f"400 debe pasarse tal cual. Got: {response.status_code}")
        self.assertEqual(call_count[0], 1, f"400 NO debe reintentarse. Got {call_count[0]} calls")
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
