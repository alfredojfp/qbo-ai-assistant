"""Tests para R-4: tool_procesar_csv_depositos debe retornar shape rico.

Estado actual (pre-R-4):
  - process_deposits_csv (main.py:2639) ya delega a tool_depositar_lote_csv
    (HIGH-4 fix). Mantiene return shape antiguo {success, total,
    success_count, errors} para backward compat con callers viejos.
  - tool_procesar_csv_depositos (main.py:4603) llama a process_deposits_csv
    y retorna su resultado (el shape antiguo, NO el rico).
  - tool_depositar_lote_csv retorna shape rico: {success, batch_id,
    executed, failed, errors}.

Refactor R-4:
  tool_procesar_csv_depositos debe llamar tool_depositar_lote_csv
  DIRECTAMENTE (no via process_deposits_csv) y retornar el shape rico
  {success, batch_id, executed, failed, errors}. Esto:
    - Da al LLM información útil (batch_id para auditar, executed/failed
      counts para resumir al usuario).
    - Elimina 1 nivel de indirección (3 wrappers → 2).
    - process_deposits_csv sigue existiendo como shim de backward compat
      (no se toca, HIGH-4 test sigue pasando).
"""
import os
import unittest
from unittest.mock import patch, MagicMock


class TestToolProcesarCsvDepositos(unittest.TestCase):
    """R-4: tool_procesar_csv_depositos retorna shape rico de tool_depositar_lote_csv."""

    def setUp(self):
        # Crear CSV temporal
        self.tmp_csv = "/tmp/r4_test_deposits.csv"
        with open(self.tmp_csv, "w") as f:
            f.write("date,client_name,amount\n")
            f.write("2026-01-15,Cliente 1,100.00\n")
            f.write("2026-01-16,Cliente 2,200.00\n")

    def tearDown(self):
        if os.path.exists(self.tmp_csv):
            os.remove(self.tmp_csv)

    def test_returns_batch_id_from_depositar_lote(self):
        """RED: tool_procesar_csv_depositos retorna batch_id del wrapper rico."""
        from main import tool_procesar_csv_depositos
        with patch("main.tool_depositar_lote_csv") as mock_lote:
            mock_lote.return_value = {
                "success": True,
                "batch_id": "BATCH_R4_TEST_123",
                "executed": 2,
                "failed": 0,
                "errors": [],
            }
            result = tool_procesar_csv_depositos(self.tmp_csv)
            self.assertEqual(result.get("batch_id"), "BATCH_R4_TEST_123")
            self.assertEqual(result.get("executed"), 2)
            self.assertEqual(result.get("failed"), 0)

    def test_delegates_directly_to_tool_depositar_lote_csv(self):
        """GREEN: tool_procesar_csv_depositos llama tool_depositar_lote_csv
        DIRECTAMENTE (no via process_deposits_csv)."""
        from main import tool_procesar_csv_depositos
        with patch("main.tool_depositar_lote_csv") as mock_lote:
            mock_lote.return_value = {
                "success": True,
                "batch_id": "BATCH_X",
                "executed": 1,
                "failed": 0,
                "errors": [],
            }
            tool_procesar_csv_depositos(self.tmp_csv)
            mock_lote.assert_called_once()
            args, kwargs = mock_lote.call_args
            self.assertEqual(kwargs.get("ruta_archivo"), self.tmp_csv)
            self.assertTrue(kwargs.get("confirmar", False))

    def test_does_not_call_process_deposits_csv(self):
        """GREEN: tool_procesar_csv_depositos bypassea process_deposits_csv."""
        from main import tool_procesar_csv_depositos
        with patch("main.tool_depositar_lote_csv") as mock_lote, \
             patch("main.process_deposits_csv") as mock_old:
            mock_lote.return_value = {
                "success": True, "batch_id": "B", "executed": 0,
                "failed": 0, "errors": [],
            }
            tool_procesar_csv_depositos(self.tmp_csv)
            mock_old.assert_not_called()

    def test_error_path_propagates(self):
        """GREEN: si tool_depositar_lote_csv retorna success=False,
        tool_procesar_csv_depositos propaga el error."""
        from main import tool_procesar_csv_depositos
        with patch("main.tool_depositar_lote_csv") as mock_lote:
            mock_lote.return_value = {
                "success": False,
                "error": "No se pudo identificar la cuenta bancaria",
            }
            result = tool_procesar_csv_depositos(self.tmp_csv)
            self.assertFalse(result.get("success"))
            self.assertIn("error", result)


class TestProcessDepositsCsvBackwardCompat(unittest.TestCase):
    """R-4 backward compat: process_deposits_csv sigue retornando shape antiguo."""

    def test_process_deposits_csv_still_returns_old_shape(self):
        """El shim process_deposits_csv NO se elimina — sigue retornando
        {success, total, success_count, errors} para callers existentes."""
        from main import process_deposits_csv
        tmp_csv = "/tmp/r4_test_compat.csv"
        with open(tmp_csv, "w") as f:
            f.write("date,client_name,amount\n")
            f.write("2026-01-15,Cliente,100\n")
        try:
            with patch("main.tool_depositar_lote_csv") as mock_lote:
                mock_lote.return_value = {
                    "success": True,
                    "batch_id": "B1",
                    "executed": 1,
                    "failed": 0,
                    "errors": [],
                }
                result = process_deposits_csv(tmp_csv)
                self.assertIn("success", result)
                self.assertIn("total", result)
                self.assertIn("success_count", result)
                self.assertIn("errors", result)
        finally:
            os.remove(tmp_csv)


if __name__ == "__main__":
    unittest.main()
