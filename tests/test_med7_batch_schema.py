"""Tests para MED-7: execute_batch valida schema de items antes de POST.

Bug: main.py:2088 — execute_batch hace:
     if len(operations) > 30: return error
     y luego POST directo. NO valida:
     - operations es list no-vacía
     - cada item es dict
     - cada item tiene 'bId' único
     - cada item tiene 'operation' válida (create/update/delete/query)
     - max 30 (ya validado, OK)

     Si el caller pasa None, [], [{}], [{'bId': 1}, {'bId': 1}], QBO
     responde 400 con mensaje críptico. Mejor fallar con mensaje claro.

Fix: helper _validate_batch_schema(operations) que retorna (ok, error_msg).
     execute_batch lo llama antes del POST. Si no OK, return
     {"success": False, "error": error_msg, "validation_error": True}.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestExecuteBatchSchemaValidation(unittest.TestCase):
    """MED-7: execute_batch debe validar schema de items."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_validation_helper_exists(self):
        """RED: _validate_batch_schema debe existir en main."""
        import main
        self.assertTrue(callable(getattr(main, "_validate_batch_schema", None)))

    def test_empty_operations_rejected(self):
        """GREEN: lista vacía debe rechazarse con mensaje claro."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([])
        self.assertFalse(ok)
        self.assertIn("vacía", msg.lower())

    def test_none_operations_rejected(self):
        """GREEN: None debe rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema(None)
        self.assertFalse(ok)
        self.assertIn("lista", msg.lower())

    def test_non_list_operations_rejected(self):
        """GREEN: dict en lugar de list debe rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema({"bId": "1", "operation": "create"})
        self.assertFalse(ok)

    def test_item_missing_bId_rejected(self):
        """GREEN: item sin 'bId' debe rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([{"operation": "create", "Customer": {}}])
        self.assertFalse(ok)
        self.assertIn("bId", msg)

    def test_item_missing_operation_rejected(self):
        """GREEN: item sin 'operation' debe rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([{"bId": "1", "Customer": {}}])
        self.assertFalse(ok)
        self.assertIn("operation", msg)

    def test_duplicate_bId_rejected(self):
        """GREEN: bIds duplicados deben rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([
            {"bId": "1", "operation": "create", "Customer": {}},
            {"bId": "1", "operation": "create", "Vendor": {}},
        ])
        self.assertFalse(ok)
        self.assertIn("duplicado", msg.lower())

    def test_invalid_operation_value_rejected(self):
        """GREEN: operation no en {create,update,delete,query} debe rechazarse."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([
            {"bId": "1", "operation": "patch", "Customer": {}},
        ])
        self.assertFalse(ok)

    def test_valid_batch_passes(self):
        """GREEN: batch válido pasa sin error."""
        from main import _validate_batch_schema
        ok, msg = _validate_batch_schema([
            {"bId": "1", "operation": "create", "Customer": {"DisplayName": "X"}},
            {"bId": "2", "operation": "update", "Vendor": {"Id": "99", "DisplayName": "Y"}},
            {"bId": "3", "operation": "query", "Query": "select * from Invoice"},
            {"bId": "4", "operation": "delete", "Invoice": {"Id": "55", "SyncToken": "0"}},
        ])
        self.assertTrue(ok, msg=msg)

    def test_execute_batch_validates_before_post(self):
        """GREEN: execute_batch valida antes de hacer POST a QBO."""
        from main import execute_batch
        with patch("main.qbo_request") as mock_req:
            result = execute_batch([])
            self.assertFalse(result["success"])
            self.assertTrue(result.get("validation_error"))
            mock_req.assert_not_called()

    def test_execute_batch_does_not_post_on_invalid(self):
        """GREEN: si validación falla, NO se llama qbo_request."""
        from main import execute_batch
        with patch("main.qbo_request") as mock_req:
            execute_batch([{"operation": "create"}])
            mock_req.assert_not_called()


if __name__ == "__main__":
    unittest.main()
