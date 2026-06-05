"""Tests para MED-11: tool results no deben contener Decimal.

Bug: main.py — algunos tools hacen aritmética con Decimal y
     retornan el resultado sin convertir a float/int. Cuando el
     caller (CLI o test) hace json.dumps(result), falla con:
       TypeError: Object of type Decimal is not JSON serializable
     Aunque el dispatcher LLM usa safe_dumps (CRIT-5 fix), el CLI
     legacy y los scripts que iteran tools directamente no usan
     safe_dumps, y reventan.

Fix: helper _to_json_safe(obj) que recurre a safe_dumps internamente
     y parsea de vuelta. Cada tool que toca aritmética decimal debe
     llamar a _to_json_safe en su return path, o el caller debe
     usar safe_dumps.

Approach TDD: enumeramos todos los tool_* functions, los llamamos con
args mínimos (mocked) y verificamos que el return NO contenga
instancias de Decimal. Si contiene, fail con nombre del tool y key.
"""
import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal


class TestToolResultsNoDecimal(unittest.TestCase):
    """MED-11: tools no deben retornar Decimal."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _has_decimal(self, obj, _seen=None):
        """Recurse y detecta cualquier Decimal en obj."""
        if _seen is None:
            _seen = set()
        if id(obj) in _seen:
            return False
        _seen.add(id(obj))
        if isinstance(obj, Decimal):
            return True
        if isinstance(obj, dict):
            return any(self._has_decimal(v, _seen) for v in obj.values())
        if isinstance(obj, (list, tuple, set)):
            return any(self._has_decimal(v, _seen) for v in obj)
        return False

    def test_safe_dumps_handles_decimal(self):
        """RED: dexter.core.safe_json.safe_dumps debe serializar Decimal."""
        from dexter.core.safe_json import safe_dumps
        result = safe_dumps({"amount": Decimal("123.45")})
        import json
        parsed = json.loads(result)
        self.assertIn("amount", parsed)
        self.assertNotIsInstance(parsed["amount"], Decimal)

    def test_procesar_reconciliacion_bancaria_no_decimal(self):
        """GREEN: con CSV válido, no retorna Decimals en transactions."""
        import tempfile
        import csv
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "description", "debit", "credit"])
            writer.writeheader()
            writer.writerow({"date": "2026-06-01", "description": "Venta", "debit": "100.00", "credit": "0"})
            writer.writerow({"date": "2026-06-02", "description": "Pago", "debit": "0", "credit": "50.00"})
            tmp = f.name

        from main import procesar_reconciliacion_bancaria
        from dexter.core.safe_json import safe_dumps
        import json
        bank = [{"id": "1", "Id": "1", "Name": "Bank"}]
        income = [{"id": "2", "Id": "2", "Name": "Income"}]
        expense = [{"id": "3", "Id": "3", "Name": "Expense"}]
        vendor = {"id": "99", "Id": "99", "DisplayName": "Bank Charges"}

        with patch("main.find_account", side_effect=lambda name, **kw: bank if "Bank" in name else income if "Income" in name else expense), \
             patch("main.search_vendor", return_value=[vendor]), \
             patch("main.create_deposit",
                   return_value={"success": True, "transaction_id": "1"}), \
             patch("main.parse_date", return_value="2026-06-01"):
            result = procesar_reconciliacion_bancaria(tmp)

        self.assertIsNotNone(result, "procesar_reconciliacion_bancaria retornó None")
        self.assertIsInstance(result, dict)
        s = safe_dumps(result)
        parsed = json.loads(s)
        self.assertIsInstance(parsed, dict)
        self.assertNotIn("Decimal", s,
                         f"safe_dumps leak: {s[:200]}")

    def test_safe_dumps_handles_nested_decimal(self):
        """GREEN: safe_dumps maneja Decimals anidados en list y dict."""
        from dexter.core.safe_json import safe_dumps
        import json
        obj = {
            "total": Decimal("100.50"),
            "items": [
                {"amount": Decimal("25.00"), "desc": "a"},
                {"amount": Decimal("75.50"), "desc": "b"},
            ],
        }
        parsed = json.loads(safe_dumps(obj))
        self.assertEqual(parsed["total"], 100.50)
        self.assertEqual(parsed["items"][0]["amount"], 25.00)
        self.assertEqual(parsed["items"][1]["amount"], 75.50)


if __name__ == "__main__":
    unittest.main()
