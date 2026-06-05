"""Tests para MED-8: procesar_csv_bank_feed separa log humano de return.

Bug: main.py:2792 — procesar_csv_bank_feed hace 20+ print() para
     progreso (líneas 2802-2884). Cuando se invoca como tool desde
     el LLM (vía tool_procesar_bank_feed_csv), los prints se mezclan
     con stdout, no se capturan en el dict, y el LLM no sabe qué
     depósito falló o por qué.

Fix: agregar parámetros `verbose: bool = True` y `log: list = None`.
     - verbose=True (default): imprime a stdout (uso CLI)
     - verbose=False: silencioso (uso tool)
     - log (list): si se pasa, cada mensaje se appendea al list
       (incluido en el return bajo 'log_lines')

     La tool wrapper pasa verbose=False, log=[] por defecto, y
     retorna {'success', 'total', 'success_count', 'errors',
     'details', 'log_lines'}.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestProcesarCsvBankFeedLog(unittest.TestCase):
    """MED-8: procesar_csv_bank_feed debe separar prints de returns."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_tool_wrapper_uses_verbose_false(self):
        """RED: tool_procesar_bank_feed_csv debe invocar con verbose=False."""
        from main import tool_procesar_bank_feed_csv
        with patch("main.procesar_csv_bank_feed", return_value={
            "success": True, "total": 0, "success_count": 0, "errors": 0,
            "details": [], "log_lines": []
        }) as mock_proc:
            tool_procesar_bank_feed_csv("dummy.csv")
            args, kwargs = mock_proc.call_args
            self.assertFalse(kwargs.get("verbose", True),
                             f"tool wrapper debe pasar verbose=False, got {kwargs}")

    def test_tool_wrapper_captures_log(self):
        """GREEN: tool wrapper debe capturar log_lines en el return."""
        from main import tool_procesar_bank_feed_csv
        captured = {
            "success": True, "total": 1, "success_count": 1, "errors": 0,
            "details": [{"deposit_id": "D1", "status": "success"}],
            "log_lines": ["📁 Procesando Bank Feed CSV: dummy.csv",
                          "✅ 1 depósito(s) encontrado(s) en el CSV",
                          "🔄 Procesando D1...",
                          "  ✓ Suma validada: $100.00",
                          "  ✅ Depósito creado (ID: 99)",
                          "     • 3 líneas procesadas",
                          "     • Monto total: $100.00",
                          "📊 RESUMEN DEL PROCESAMIENTO",
                          "Total depósitos: 1",
                          "✅ Exitosos: 1",
                          "❌ Errores: 0"]
        }
        with patch("main.procesar_csv_bank_feed", return_value=captured):
            result = tool_procesar_bank_feed_csv("dummy.csv")
            self.assertIn("log_lines", result)
            self.assertGreater(len(result["log_lines"]), 0)

    def test_verbose_false_suppresses_prints(self):
        """GREEN: con verbose=False, no se imprime a stdout."""
        from main import procesar_csv_bank_feed
        import io
        import sys
        captured_stdout = io.StringIO()
        with patch("main.agrupar_bank_feed_por_deposit_id", return_value={}):
            old_stdout = sys.stdout
            sys.stdout = captured_stdout
            try:
                result = procesar_csv_bank_feed("dummy.csv", verbose=False)
            finally:
                sys.stdout = old_stdout
            self.assertEqual(captured_stdout.getvalue(), "")

    def test_verbose_true_prints(self):
        """GREEN: con verbose=True (default), sí imprime a stdout."""
        from main import procesar_csv_bank_feed
        import io
        import sys
        captured_stdout = io.StringIO()
        with patch("main.agrupar_bank_feed_por_deposit_id", return_value={}):
            old_stdout = sys.stdout
            sys.stdout = captured_stdout
            try:
                procesar_csv_bank_feed("dummy.csv", verbose=True)
            finally:
                sys.stdout = old_stdout
            self.assertIn("Procesando Bank Feed CSV", captured_stdout.getvalue())

    def test_log_list_captures_messages(self):
        """GREEN: si se pasa log=[], cada print se appendea al list."""
        from main import procesar_csv_bank_feed
        log = []
        with patch("main.agrupar_bank_feed_por_deposit_id", return_value={}):
            procesar_csv_bank_feed("dummy.csv", verbose=False, log=log)
        self.assertGreater(len(log), 0)
        self.assertTrue(any("Procesando Bank Feed CSV" in line for line in log))

    def test_return_includes_log_lines(self):
        """GREEN: cuando log se pasa, return incluye 'log_lines'."""
        from main import procesar_csv_bank_feed
        log = []
        with patch("main.agrupar_bank_feed_por_deposit_id", return_value={}):
            result = procesar_csv_bank_feed("dummy.csv", verbose=False, log=log)
        self.assertIn("log_lines", result)
        self.assertEqual(result["log_lines"], log)


if __name__ == "__main__":
    unittest.main()
