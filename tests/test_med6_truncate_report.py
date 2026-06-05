"""Tests para MED-6: _fetch_report trunca si payload es gigante.

Bug: main.py:1659 — _fetch_report retorna el JSON completo de QBO.
     Reportes grandes (ProfitAndLossDetail, GeneralLedger, TransactionList)
     pueden ser 5-50MB de JSON. Esto revienta el context window del LLM
     (200K tokens, ~800KB) y la respuesta de la tool se trunca o
     el LLM ignora datos importantes.

Fix: agregar _truncate_report_data(report_name, data, max_bytes) helper
     que trunca 'Rows.Row' (estructura típica de QBO reports) si excede
     max_bytes, agregando aviso "_truncated": True. Configurable via
     env MAX_REPORT_BYTES (default 250_000 = 250KB ≈ 60K tokens).
"""
import json
import unittest
from unittest.mock import patch, MagicMock


class TestFetchReportTruncation(unittest.TestCase):
    """MED-6: _fetch_report debe truncar reportes grandes."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_truncation_helper_exists(self):
        """RED: debe existir _truncate_report_data en main."""
        import main
        self.assertTrue(callable(getattr(main, "_truncate_report_data", None)))

    def test_small_report_passes_through(self):
        """GREEN: reportes < max_bytes se devuelven intactos."""
        from main import _truncate_report_data
        small = {
            "Header": {"Time": "2026-06-04", "ReportName": "TrialBalance"},
            "Rows": {"Row": [{"ColData": [{"value": "100"}]}]},
        }
        out = _truncate_report_data("TrialBalance", small, max_bytes=10000)
        self.assertNotIn("_truncated", out)
        self.assertEqual(out, small)

    def test_huge_report_truncated(self):
        """GREEN: reportes > max_bytes se truncan y marcan _truncated=True."""
        from main import _truncate_report_data
        huge = {
            "Header": {"Time": "2026-06-04", "ReportName": "GeneralLedger"},
            "Rows": {"Row": [{"ColData": [{"value": f"line-{i:06d}"}]} for i in range(5000)]},
        }
        out = _truncate_report_data("GeneralLedger", huge, max_bytes=5000)
        self.assertTrue(out.get("_truncated"))
        self.assertIn("Rows", out)
        self.assertLess(len(out["Rows"].get("Row", [])), 5000)

    def test_truncation_preserves_header(self):
        """GREEN: header siempre se preserva (Time, ReportName, etc)."""
        from main import _truncate_report_data
        huge = {
            "Header": {"Time": "2026-06-04", "ReportName": "ProfitAndLossDetail",
                       "StartPeriod": "2026-01-01", "EndPeriod": "2026-06-30"},
            "Rows": {"Row": [{"ColData": [{"value": str(i)}]} for i in range(10000)]},
        }
        out = _truncate_report_data("ProfitAndLossDetail", huge, max_bytes=2000)
        self.assertEqual(out["Header"]["ReportName"], "ProfitAndLossDetail")
        self.assertTrue(out.get("_truncated"))

    def test_truncation_includes_summary(self):
        """GREEN: el dict truncado incluye _truncation_summary con conteo."""
        from main import _truncate_report_data
        huge = {
            "Header": {"ReportName": "X"},
            "Rows": {"Row": [{"ColData": [{"value": str(i)}]} for i in range(1000)]},
        }
        out = _truncate_report_data("X", huge, max_bytes=2000)
        self.assertIn("_truncation_summary", out)
        self.assertIn("original_rows", out["_truncation_summary"])
        self.assertIn("kept_rows", out["_truncation_summary"])
        self.assertEqual(out["_truncation_summary"]["original_rows"], 1000)

    def test_fetch_report_uses_truncation(self):
        """GREEN: _fetch_report llama al helper antes de retornar."""
        from main import _fetch_report
        with patch("main.qbo_request") as mock_req, \
             patch("main._truncate_report_data", side_effect=lambda name, data, **kw: {**data, "_truncated": True}) as mock_trunc:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"Header": {}, "Rows": {}}
            mock_req.return_value = mock_resp
            result = _fetch_report("TrialBalance", {})
            mock_trunc.assert_called_once()
            self.assertTrue(result.get("data", {}).get("_truncated"))


if __name__ == "__main__":
    unittest.main()
