"""Tests para LOW-7: generate_pl_report y generate_balance_sheet retornan
list[dict] en lugar de pd.DataFrame.

Bug: main.py:2489-2540 — generate_pl_report y generate_balance_sheet
     retornan pd.DataFrame. El wrapper tool_generar_reporte_pl (línea
     4534) hace .empty, .groupby, .to_dict() y .head(10), forzando
     dependencias pandas en el wrapper. Además: si un consumidor externo
     llama generate_pl_report (e.g., tests, scripts, integración), recibe
     un DataFrame y debe convertirlo. La función pública debería
     retornar datos nativos (list[dict]) que cualquier consumidor puede
     usar sin pandas.

Fix: cambiar return type a list[dict]. Wrapper hace su propia
     agregación con defaultdict/iter. Helper helper _rows_to_summary(rows)
     comparte lógica entre P&L y balance sheet. Error path retorna [].
"""
import unittest
from unittest.mock import patch, MagicMock


class TestGeneratePlReportReturnType(unittest.TestCase):
    """LOW-7: generate_pl_report retorna list[dict], no DataFrame."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _fake_qbo_response(self, payload, status=200):
        r = MagicMock()
        r.status_code = status
        r.text = "fake"
        r.json.return_value = payload
        return r

    def _sample_pl_payload(self):
        return {
            "Header": {"Time": "2026-01-01"},
            "Rows": {
                "Row": [
                    {
                        "type": "Section",
                        "Header": {"ColData": [{"value": "Income"}]},
                        "Rows": {
                            "Row": [
                                {
                                    "type": "Data",
                                    "ColData": [
                                        {"value": "Sales of Product Income"},
                                        {"value": "1000.00"},
                                    ],
                                }
                            ]
                        },
                    },
                    {
                        "type": "Section",
                        "Header": {"ColData": [{"value": "Expenses"}]},
                        "Rows": {
                            "Row": [
                                {
                                    "type": "Data",
                                    "ColData": [
                                        {"value": "Advertising"},
                                        {"value": "-200.00"},
                                    ],
                                }
                            ]
                        },
                    },
                ]
            },
        }

    def test_returns_list_not_dataframe(self):
        """RED: generate_pl_report retorna list, no DataFrame."""
        with patch("main.qbo_request", return_value=self._fake_qbo_response(self._sample_pl_payload())):
            from main import generate_pl_report
            result = generate_pl_report("2026-01-01", "2026-12-31")
            self.assertIsInstance(result, list)
            try:
                import pandas as pd
                self.assertNotIsInstance(result, pd.DataFrame)
            except ImportError:
                pass

    def test_returns_list_of_dicts_with_expected_keys(self):
        """GREEN: cada elemento es dict con cuenta/categoria/monto."""
        with patch("main.qbo_request", return_value=self._fake_qbo_response(self._sample_pl_payload())):
            from main import generate_pl_report
            result = generate_pl_report("2026-01-01", "2026-12-31")
            self.assertEqual(len(result), 2)
            self.assertEqual(
                sorted(result[0].keys()),
                ["categoria", "cuenta", "monto"],
            )
            sales = next(r for r in result if r["cuenta"] == "Sales of Product Income")
            self.assertEqual(sales["categoria"], "Income")
            self.assertEqual(sales["monto"], 1000.0)
            adv = next(r for r in result if r["cuenta"] == "Advertising")
            self.assertEqual(adv["categoria"], "Expenses")
            self.assertEqual(adv["monto"], -200.0)

    def test_returns_empty_list_on_error(self):
        """GREEN: status !=200 → []."""
        with patch("main.qbo_request", return_value=self._fake_qbo_response({}, status=500)):
            from main import generate_pl_report
            result = generate_pl_report("2026-01-01", "2026-12-31")
            self.assertIsInstance(result, list)
            self.assertEqual(result, [])


class TestGenerateBalanceSheetReturnType(unittest.TestCase):
    """LOW-7: generate_balance_sheet también retorna list[dict]."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _fake_qbo_response(self, payload, status=200):
        r = MagicMock()
        r.status_code = status
        r.text = "fake"
        r.json.return_value = payload
        return r

    def test_returns_list_not_dataframe(self):
        """RED: generate_balance_sheet retorna list, no DataFrame."""
        payload = {
            "Header": {"Time": "2026-01-01"},
            "Rows": {
                "Row": [
                    {
                        "type": "Section",
                        "Header": {"ColData": [{"value": "Assets"}]},
                        "Rows": {
                            "Row": [
                                {
                                    "type": "Data",
                                    "ColData": [
                                        {"value": "Checking"},
                                        {"value": "5000.00"},
                                    ],
                                }
                            ]
                        },
                    }
                ]
            },
        }
        with patch("main.qbo_request", return_value=self._fake_qbo_response(payload)):
            from main import generate_balance_sheet
            result = generate_balance_sheet("2026-01-01")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["cuenta"], "Checking")
            self.assertEqual(result[0]["categoria"], "Assets")
            self.assertEqual(result[0]["monto"], 5000.0)

    def test_returns_empty_list_on_error(self):
        """GREEN: status !=200 → []."""
        with patch("main.qbo_request", return_value=self._fake_qbo_response({}, status=500)):
            from main import generate_balance_sheet
            result = generate_balance_sheet("2026-01-01")
            self.assertEqual(result, [])


class TestToolWrapperStillWorks(unittest.TestCase):
    """LOW-7: tool_generar_reporte_pl sigue retornando dict (backward compat)."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_tool_generar_reporte_pl_returns_success(self):
        """GREEN: el wrapper sigue funcionando con la nueva API."""
        from unittest.mock import patch, MagicMock
        payload = {
            "Header": {"Time": "2026-01-01"},
            "Rows": {
                "Row": [
                    {
                        "type": "Section",
                        "Header": {"ColData": [{"value": "Income"}]},
                        "Rows": {
                            "Row": [
                                {
                                    "type": "Data",
                                    "ColData": [{"value": "Sales"}, {"value": "500"}],
                                }
                            ]
                        },
                    }
                ]
            },
        }
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = payload

        with patch("main.qbo_request", return_value=r):
            from main import tool_generar_reporte_pl
            result = tool_generar_reporte_pl("2026-01-01", "2026-12-31")
            self.assertTrue(result.get("success"))
            self.assertEqual(result["registros"], 1)
            self.assertIn("Income", result["resumen"])
            self.assertEqual(result["resumen"]["Income"], 500.0)

    def test_tool_generar_reporte_pl_error_path(self):
        """GREEN: el wrapper maneja [] como error."""
        r = MagicMock()
        r.status_code = 500
        r.text = "fail"

        with patch("main.qbo_request", return_value=r):
            from main import tool_generar_reporte_pl
            result = tool_generar_reporte_pl("2026-01-01", "2026-12-31")
            self.assertFalse(result.get("success"))
            self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
