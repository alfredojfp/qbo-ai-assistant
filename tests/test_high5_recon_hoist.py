"""Tests para HIGH-5: procesar_reconciliacion_bancaria hoist vendor lookup.

Bug: main.py:2825 — `search_vendor("Bank Charges")` se llama INSIDE el
     loop, una vez por cada debit transaction. Con 100 debits, son 100
     lookups. Cada uno hace una SQL query a QBO. Performance N+1 clásico.

Fix: hoist el lookup fuera del loop. Buscar "Bank Charges" una vez antes
     del loop, reusar el ID. Si no se encuentra, fail rápido antes
     de crear cualquier transacción.

Bonus (HIGH-5b, scope separate): partial writes sin rollback se
atiende refactorizando a usar tool_depositar_lote_csv pattern (como HIGH-4).
Ese cambio es de mayor scope; HIGH-5a solo arregla N+1.
"""
import io
import unittest
from unittest.mock import patch, MagicMock


def _csv_text(rows):
    """Genera CSV con header estándar."""
    lines = ["date,description,debit,credit,reference"]
    for r in rows:
        lines.append(",".join([
            r["date"], r["description"], r["debit"], r["credit"], r.get("reference", "")
        ]))
    return "\n".join(lines) + "\n"


class TestReconciliationHoistVendorLookup(unittest.TestCase):
    """HIGH-5: vendor lookup debe hoist fuera del loop."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _mock_open_with(self, csv_text):
        return patch("builtins.open", return_value=io.StringIO(csv_text))

    def test_vendor_lookup_called_once_not_per_row(self):
        """RED: search_vendor se llama 1 vez, no N veces para N debits."""
        from main import procesar_reconciliacion_bancaria

        csv_text = _csv_text([
            {"date": "2026-06-01", "description": "DEBIT 1", "debit": "100", "credit": "", "reference": "R1"},
            {"date": "2026-06-02", "description": "DEBIT 2", "debit": "200", "credit": "", "reference": "R2"},
            {"date": "2026-06-03", "description": "DEBIT 3", "debit": "300", "credit": "", "reference": "R3"},
        ])

        vendor = {"id": "v_bank_charges", "name": "Bank Charges", "balance": 0, "active": True}
        bank_acc = {"id": "bank_1", "name": "Checking", "category": "ACTIVO"}
        expense = {"id": "exp_1", "name": "Expense", "category": "GASTO"}
        bill_ok = {"success": True, "bill_id": "B1"}

        with patch("os.path.exists", return_value=True), \
             self._mock_open_with(csv_text), \
             patch("main.find_account", side_effect=[
                 [bank_acc],      # Checking
                 [bank_acc],      # Bank fallback
                 [expense],       # Expense
             ]), \
             patch("main.search_vendor", return_value=[vendor]) as mock_search_vendor, \
             patch("main.create_bill", return_value=bill_ok) as mock_bill, \
             patch("main.parse_date", return_value="2026-06-01"), \
             patch("main.log_operation"):
            result = procesar_reconciliacion_bancaria("/tmp/test.csv")

        self.assertEqual(mock_search_vendor.call_count, 1,
                         f"Vendor lookup debe ser 1 vez, fue {mock_search_vendor.call_count}")
        self.assertEqual(mock_bill.call_count, 3)

    def test_fails_fast_when_no_vendor_found(self):
        """GREEN: si no hay Bank Charges vendor, fail antes de crear nada."""
        from main import procesar_reconciliacion_bancaria

        csv_text = _csv_text([
            {"date": "2026-06-01", "description": "DEBIT", "debit": "100", "credit": "", "reference": "R1"},
        ])

        bank_acc = {"id": "bank_1", "name": "Checking", "category": "ACTIVO"}
        expense = {"id": "exp_1", "name": "Expense", "category": "GASTO"}

        with patch("os.path.exists", return_value=True), \
             self._mock_open_with(csv_text), \
             patch("main.find_account", side_effect=[
                 [bank_acc],
                 [bank_acc],
                 [expense],
             ]), \
             patch("main.search_vendor", return_value=[]) as mock_search_vendor, \
             patch("main.create_bill") as mock_bill, \
             patch("main.parse_date", return_value="2026-06-01"), \
             patch("main.log_operation"):
            result = procesar_reconciliacion_bancaria("/tmp/test.csv")

        mock_search_vendor.assert_called_once()
        mock_bill.assert_not_called()
        self.assertFalse(result["success"])
        self.assertIn("vendor", result["error"].lower())


if __name__ == "__main__":
    unittest.main()
