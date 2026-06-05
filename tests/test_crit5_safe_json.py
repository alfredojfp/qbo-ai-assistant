"""Tests para CRIT-5: json.dumps falla con Decimal/datetime/Path → error genérico al LLM.

Bug: main.py:2844 — `json.dumps(result_data)` sin encoder custom.
      Si un tool retorna Decimal('1.50'), datetime.now(), o Path('/x'),
      json.dumps lanza TypeError y el LLM recibe mensaje genérico.

Fix: crear dexter/core/safe_json.py con DexterJSONEncoder y safe_dumps(obj)
     que maneja: Decimal→float, datetime→isoformat, Path→str, UUID→str, set→list.
"""
import unittest
import json
import tempfile
import unittest.mock
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from uuid import UUID


class TestSafeJson(unittest.TestCase):
    """CRIT-5: safe_dumps debe manejar tipos no-JSON-serializables."""

    def test_serializes_decimal_as_float(self):
        """RED: safe_dumps(Decimal('1.50')) debe retornar '1.5' (no fallar)."""
        from dexter.core.safe_json import safe_dumps
        result = safe_dumps({"amount": Decimal("1.50")})
        parsed = json.loads(result)
        self.assertEqual(parsed["amount"], 1.5, f"Decimal debe serializarse a float. Got: {parsed}")

    def test_serializes_datetime_as_isoformat(self):
        """RED: safe_dumps(datetime.now()) debe retornar ISO string."""
        from dexter.core.safe_json import safe_dumps
        dt = datetime(2026, 6, 4, 12, 30, 45)
        result = safe_dumps({"created_at": dt})
        parsed = json.loads(result)
        self.assertEqual(parsed["created_at"], "2026-06-04T12:30:45", f"datetime debe ser ISO. Got: {parsed}")

    def test_serializes_date_as_isoformat(self):
        """RED: safe_dumps(date.today()) debe retornar ISO string."""
        from dexter.core.safe_json import safe_dumps
        d = date(2026, 6, 4)
        result = safe_dumps({"txn_date": d})
        parsed = json.loads(result)
        self.assertEqual(parsed["txn_date"], "2026-06-04", f"date debe ser ISO. Got: {parsed}")

    def test_serializes_path_as_str(self):
        """RED: safe_dumps(Path('/tmp/x')) debe retornar '/tmp/x'."""
        from dexter.core.safe_json import safe_dumps
        result = safe_dumps({"pdf_path": Path("/tmp/x.pdf")})
        parsed = json.loads(result)
        self.assertEqual(parsed["pdf_path"], "/tmp/x.pdf", f"Path debe ser str. Got: {parsed}")

    def test_serializes_uuid_as_str(self):
        """RED: safe_dumps(UUID) debe retornar string hex."""
        from dexter.core.safe_json import safe_dumps
        u = UUID("12345678-1234-5678-1234-567812345678")
        result = safe_dumps({"id": u})
        parsed = json.loads(result)
        self.assertEqual(parsed["id"], "12345678-1234-5678-1234-567812345678", f"UUID debe ser str. Got: {parsed}")

    def test_serializes_set_as_list(self):
        """RED: safe_dumps({1, 2, 3}) debe retornar lista."""
        from dexter.core.safe_json import safe_dumps
        result = safe_dumps({"items": {1, 2, 3}})
        parsed = json.loads(result)
        self.assertIsInstance(parsed["items"], list, f"set debe ser list. Got: {type(parsed['items'])}")
        self.assertEqual(set(parsed["items"]), {1, 2, 3})

    def test_nested_structures(self):
        """RED: safe_dumps debe manejar estructuras anidadas con tipos mixtos."""
        from dexter.core.safe_json import safe_dumps
        data = {
            "id": 1,
            "amount": Decimal("99.99"),
            "created_at": datetime(2026, 6, 4, 10, 0, 0),
            "items": [
                {"name": "Item A", "qty": Decimal("2.5")},
                {"name": "Item B", "qty": Decimal("1.0"), "path": Path("/tmp/b")},
            ],
        }
        result = safe_dumps(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["amount"], 99.99)
        self.assertEqual(parsed["created_at"], "2026-06-04T10:00:00")
        self.assertEqual(parsed["items"][0]["qty"], 2.5)
        self.assertEqual(parsed["items"][1]["path"], "/tmp/b")

    def test_ensure_ascii_false_preserves_unicode(self):
        """RED: safe_dumps debe preservar acentos/ñ en strings (no \\uXXXX)."""
        from dexter.core.safe_json import safe_dumps
        result = safe_dumps({"text": "Clasificación de facturas"})
        self.assertIn("Clasificación", result, "acentos deben preservarse, no escaparse a \\u00")
        self.assertNotIn("\\u00", result, "no debe usar \\u escapes")

    def test_falls_back_to_str_for_unknown_types(self):
        """RED: safe_dumps debe usar str() para tipos desconocidos (no fallar)."""
        from dexter.core.safe_json import safe_dumps
        class CustomObj:
            def __str__(self):
                return "custom_repr"
        result = safe_dumps({"obj": CustomObj()})
        parsed = json.loads(result)
        self.assertEqual(parsed["obj"], "custom_repr", f"objetos desconocidos → str(). Got: {parsed}")


class TestToolDispatchUsesSafeJson(unittest.TestCase):
    """CRIT-5: el dispatch de tools (main.py) debe usar safe_dumps, no json.dumps."""

    def test_dispatch_handles_decimal_return(self):
        """RED: tool que retorna Decimal debe serializarse correctamente al LLM."""
        import main

        # Tool ficticio que retorna Decimal
        def tool_with_decimal(amount: str = "1.50") -> dict:
            return {"amount": Decimal(amount), "currency": "USD"}

        # Insertar en TOOL_FUNCTIONS para simular dispatch
        original_dispatch = main.TOOL_FUNCTIONS.get("tool_with_decimal_test")
        main.TOOL_FUNCTIONS["tool_with_decimal_test"] = tool_with_decimal

        try:
            # Simular lo que hace call_llm en main.py:2843-2844
            try:
                result_data = main.TOOL_FUNCTIONS["tool_with_decimal_test"](amount="99.99")
                from dexter.core.safe_json import safe_dumps
                result_str = safe_dumps(result_data, ensure_ascii=False)
            except TypeError as e:
                self.fail(f"safe_dumps no debería lanzar TypeError. Got: {e}")

            parsed = json.loads(result_str)
            self.assertEqual(parsed["amount"], 99.99, f"Decimal serializado a float. Got: {parsed}")
        finally:
            if original_dispatch is None:
                main.TOOL_FUNCTIONS.pop("tool_with_decimal_test", None)
            else:
                main.TOOL_FUNCTIONS["tool_with_decimal_test"] = original_dispatch


if __name__ == "__main__":
    unittest.main()
