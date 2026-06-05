"""Tests para HIGH-4: process_deposits_csv debe usar batch engine, no crear QBO directo.

Bug: main.py:2312-2373 — process_deposits_csv itera el CSV y llama
     create_deposit() directamente. Sin dry-run obligatorio, sin rollback
     si falla una fila intermedia. Si fila 5/10 falla, filas 1-4 ya están
     en QBO. No hay forma de rollback.

Fix: delegar a tool_depositar_lote_csv(confirmar=True) que usa el
     Sprint 2 BatchEngine con state machine, dry-run obligatorio, y
     rollback seguro via storage. La función vieja se mantiene como
     wrapper de compat con la misma return shape.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestProcessDepositsCsvUsesBatchEngine(unittest.TestCase):
    """HIGH-4: process_deposits_csv debe delegar a tool_depositar_lote_csv."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_does_not_call_create_deposit_directly(self):
        """RED: process_deposits_csv NO debe llamar create_deposit directamente."""
        from main import process_deposits_csv

        with patch("os.path.exists", return_value=True), \
             patch("main.pd.read_csv") as mock_read, \
             patch("main.create_deposit") as mock_create, \
             patch("main.tool_depositar_lote_csv", return_value={
                 "success": True,
                 "batch_id": "B1",
                 "dry_run": False,
                 "results": {"success": 2, "errors": []},
             }) as mock_batch:
            import pandas as pd
            mock_read.return_value = pd.DataFrame([
                {
                    "customer_name": "Alice",
                    "amount": 100.0,
                    "from_account": "Bank",
                    "to_account": "Sales",
                    "date": "2026-06-01",
                },
                {
                    "customer_name": "Bob",
                    "amount": 200.0,
                    "from_account": "Bank",
                    "to_account": "Sales",
                    "date": "2026-06-02",
                },
            ])

            result = process_deposits_csv("/tmp/test.csv")

            mock_create.assert_not_called()
            mock_batch.assert_called_once()
            self.assertIn("success", result)
            self.assertIn("total", result)
            self.assertIn("errors", result)

    def test_partial_failure_does_not_leave_orphan_deposits(self):
        """RED: si batch reporta errores, return shape lo refleja, no se hizo rollback manual."""
        from main import process_deposits_csv

        with patch("os.path.exists", return_value=True), \
             patch("main.pd.read_csv") as mock_read, \
             patch("main.tool_depositar_lote_csv", return_value={
                 "success": False,
                 "batch_id": "B1",
                 "errors": ["Fila 2: cliente no encontrado"],
             }) as mock_batch:
            import pandas as pd
            mock_read.return_value = pd.DataFrame([
                {"customer_name": "Alice", "amount": 100.0,
                 "from_account": "Bank", "to_account": "Sales", "date": "2026-06-01"},
                {"customer_name": "Missing", "amount": 200.0,
                 "from_account": "Bank", "to_account": "Sales", "date": "2026-06-02"},
            ])

            result = process_deposits_csv("/tmp/test.csv")

            mock_batch.assert_called_once()
            self.assertFalse(result["success"])
            self.assertEqual(result["success_count"], 0)
            self.assertIn("Fila 2", str(result["errors"]))

    def test_missing_file_returns_error(self):
        """GREEN: archivo no encontrado → return sin llamar batch engine."""
        from main import process_deposits_csv

        with patch("os.path.exists", return_value=False), \
             patch("main.tool_depositar_lote_csv") as mock_batch:
            result = process_deposits_csv("/tmp/nonexistent.csv")

            self.assertFalse(result["success"])
            self.assertIn("no encontrado", result["error"].lower())
            mock_batch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
