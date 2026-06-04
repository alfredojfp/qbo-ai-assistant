# -*- coding: utf-8 -*-
"""
Tests para autonomia.dynamic_report_generator.
Ejecutar: python3 -m unittest tests.test_dynamic_report_generator
"""
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from autonomia.dynamic_report_generator import (
    DynamicReportGenerator,
    tool_generate_custom_report,
    tool_parse_date_expression,
)


class TestParseDateExpression(unittest.TestCase):
    def setUp(self):
        self.gen = DynamicReportGenerator()

    def test_este_mes(self):
        start, end = self.gen.parse_date_expression("este mes")
        today = datetime.now()
        self.assertEqual(start, today.replace(day=1).strftime('%Y-%m-%d'))
        last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day = last_day - timedelta(days=1)
        self.assertEqual(end, last_day.strftime('%Y-%m-%d'))

    def test_mes_pasado(self):
        start, end = self.gen.parse_date_expression("mes pasado")
        today = datetime.now()
        first_this = today.replace(day=1)
        first_prev = (first_this - timedelta(days=1)).replace(day=1)
        last_prev = first_this - timedelta(days=1)
        self.assertEqual(start, first_prev.strftime('%Y-%m-%d'))
        self.assertEqual(end, last_prev.strftime('%Y-%m-%d'))

    def test_este_año(self):
        start, end = self.gen.parse_date_expression("este año")
        today = datetime.now()
        self.assertEqual(start, today.replace(month=1, day=1).strftime('%Y-%m-%d'))
        self.assertEqual(end, today.replace(month=12, day=31).strftime('%Y-%m-%d'))

    def test_año_pasado(self):
        start, end = self.gen.parse_date_expression("año pasado")
        today = datetime.now()
        last_year = today.year - 1
        self.assertEqual(start, f"{last_year}-01-01")
        self.assertEqual(end, f"{last_year}-12-31")

    def test_este_trimestre(self):
        start, end = self.gen.parse_date_expression("este trimestre")
        today = datetime.now()
        q = (today.month - 1) // 3
        expected_start = today.replace(month=q * 3 + 1, day=1)
        expected_end_month = (q + 1) * 3
        if expected_end_month == 12:
            expected_end = today.replace(month=12, day=31)
        else:
            expected_end = today.replace(month=expected_end_month + 1, day=1) - timedelta(days=1)
        self.assertEqual(start, expected_start.strftime('%Y-%m-%d'))
        self.assertEqual(end, expected_end.strftime('%Y-%m-%d'))

    def test_ultimo_trimestre(self):
        start, end = self.gen.parse_date_expression("último trimestre")
        today = datetime.now()
        current_q = (today.month - 1) // 3
        prev_q = (current_q - 1) % 4
        year = today.year if current_q > 0 else today.year - 1
        expected_start_month = prev_q * 3 + 1
        expected_end_month = prev_q * 3 + 3
        expected_start = today.replace(year=year, month=expected_start_month, day=1)
        if expected_end_month == 12:
            expected_end = today.replace(year=year, month=12, day=31)
        else:
            expected_end = today.replace(year=year, month=expected_end_month + 1, day=1) - timedelta(days=1)
        self.assertEqual(start, expected_start.strftime('%Y-%m-%d'))
        self.assertEqual(end, expected_end.strftime('%Y-%m-%d'))

    def test_ultima_semana(self):
        start, end = self.gen.parse_date_expression("última semana")
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        self.assertEqual(start, last_monday.strftime('%Y-%m-%d'))
        self.assertEqual(end, last_sunday.strftime('%Y-%m-%d'))

    def test_ultimos_7_dias(self):
        start, end = self.gen.parse_date_expression("últimos 7 días")
        today = datetime.now()
        expected_start = today - timedelta(days=6)
        self.assertEqual(start, expected_start.strftime('%Y-%m-%d'))
        self.assertEqual(end, today.strftime('%Y-%m-%d'))

    def test_ultimos_30_dias(self):
        start, end = self.gen.parse_date_expression("últimos 30 días")
        today = datetime.now()
        expected_start = today - timedelta(days=29)
        self.assertEqual(start, expected_start.strftime('%Y-%m-%d'))
        self.assertEqual(end, today.strftime('%Y-%m-%d'))

    def test_ultimos_90_dias(self):
        start, end = self.gen.parse_date_expression("últimos 90 días")
        today = datetime.now()
        expected_start = today - timedelta(days=89)
        self.assertEqual(start, expected_start.strftime('%Y-%m-%d'))
        self.assertEqual(end, today.strftime('%Y-%m-%d'))

    def test_hoy(self):
        start, end = self.gen.parse_date_expression("hoy")
        today = datetime.now().strftime('%Y-%m-%d')
        self.assertEqual(start, today)
        self.assertEqual(end, today)

    def test_ayer(self):
        start, end = self.gen.parse_date_expression("ayer")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.assertEqual(start, yesterday)
        self.assertEqual(end, yesterday)

    def test_mes_especifico_enero_actual(self):
        start, end = self.gen.parse_date_expression("enero")
        today = datetime.now()
        self.assertEqual(start, f"{today.year}-01-01")
        self.assertEqual(end, f"{today.year}-01-31")

    def test_mes_especifico_diciembre_actual(self):
        start, end = self.gen.parse_date_expression("diciembre")
        today = datetime.now()
        self.assertEqual(start, f"{today.year}-12-01")
        self.assertEqual(end, f"{today.year}-12-31")

    def test_q1_sin_año(self):
        start, end = self.gen.parse_date_expression("Q1")
        today = datetime.now()
        self.assertEqual(start, f"{today.year}-01-01")
        self.assertEqual(end, f"{today.year}-03-31")

    def test_q3_2025(self):
        start, end = self.gen.parse_date_expression("Q3 2025")
        self.assertEqual(start, "2025-07-01")
        self.assertEqual(end, "2025-09-30")

    def test_año_especifico_2024(self):
        start, end = self.gen.parse_date_expression("2024")
        self.assertEqual(start, "2024-01-01")
        self.assertEqual(end, "2024-12-31")

    def test_mes_especifico_iso(self):
        start, end = self.gen.parse_date_expression("2026-03")
        self.assertEqual(start, "2026-03-01")
        self.assertEqual(end, "2026-03-31")

    def test_expresion_desconocida_retorna_mes_actual(self):
        start, end = self.gen.parse_date_expression("xyz abc")
        today = datetime.now()
        self.assertEqual(start, today.replace(day=1).strftime('%Y-%m-%d'))


class TestDetectReportType(unittest.TestCase):
    def setUp(self):
        self.gen = DynamicReportGenerator()

    def test_detecta_pl(self):
        self.assertEqual(self.gen.detect_report_type("dame el P&L de este mes"), "ProfitAndLoss")

    def test_detecta_pl_perdidas_ganancias(self):
        self.assertEqual(
            self.gen.detect_report_type("reporte de pérdidas y ganancias"),
            "ProfitAndLoss"
        )

    def test_detecta_balance_sheet(self):
        self.assertEqual(
            self.gen.detect_report_type("balance general"),
            "BalanceSheet"
        )

    def test_detecta_balance_ingles(self):
        self.assertEqual(
            self.gen.detect_report_type("balance sheet"),
            "BalanceSheet"
        )

    def test_detecta_cash_flow(self):
        self.assertEqual(
            self.gen.detect_report_type("flujo de caja"),
            "CashFlow"
        )

    def test_detecta_trial_balance(self):
        self.assertEqual(
            self.gen.detect_report_type("balance de comprobación"),
            "TrialBalance"
        )

    def test_default_es_pl(self):
        self.assertEqual(
            self.gen.detect_report_type("dame algo"),
            "ProfitAndLoss"
        )


class TestGenerateCustomReport(unittest.TestCase):
    def setUp(self):
        self.gen = DynamicReportGenerator()

    @patch("requests.get")
    def test_genera_pl_exitoso(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Header": {"Time": "2026-06-15"},
            "Rows": {"Row": [{"type": "Section", "group": "Income"}]},
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "test_token",
            "QB_REALM_ID": "test_realm",
        }):
            result = self.gen.generate_custom_report("P&L de este mes")

        self.assertTrue(result["success"])
        self.assertEqual(result["report_type"], "ProfitAndLoss")
        self.assertIn("period", result)
        self.assertIn("start_date", result)
        self.assertIn("end_date", result)

    @patch("requests.get")
    def test_genera_balance_sheet(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Header": {}, "Rows": {}}
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "test_token",
            "QB_REALM_ID": "test_realm",
        }):
            result = self.gen.generate_custom_report("balance general")

        self.assertTrue(result["success"])
        self.assertEqual(result["report_type"], "BalanceSheet")

    @patch("requests.get")
    def test_error_en_request(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "test_token",
            "QB_REALM_ID": "test_realm",
        }):
            result = self.gen.generate_custom_report("P&L")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_sin_token_retorna_error(self):
        with patch.dict(os.environ, {}, clear=True):
            result = self.gen.generate_custom_report("P&L")

        self.assertFalse(result["success"])
        self.assertIn("QB_ACCESS_TOKEN", result.get("error", ""))


class TestToolGenerateCustomReport(unittest.TestCase):
    @patch("autonomia.dynamic_report_generator.DynamicReportGenerator.generate_custom_report")
    def test_delega_al_generator(self, mock_gen):
        mock_gen.return_value = {"success": True, "report_type": "P&L"}
        result = tool_generate_custom_report("P&L de este mes")
        mock_gen.assert_called_once()
        self.assertTrue(result["success"])


class TestToolParseDateExpression(unittest.TestCase):
    def test_retorna_fechas(self):
        result = tool_parse_date_expression("este mes")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["start_date"]), 10)
        self.assertEqual(len(result["end_date"]), 10)


if __name__ == "__main__":
    unittest.main()
