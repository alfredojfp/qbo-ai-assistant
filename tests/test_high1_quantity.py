"""Tests para HIGH-1: create_invoice debe rechazar quantity <= 0 con error claro.

Bug: main.py:710 — `item["amount"] / item.get("quantity", 1)` lanza
      ZeroDivisionError silencioso si quantity=0 explícito. El default
      `or 1` solo se aplica si la clave está ausente; no si está presente
      con valor 0.

Fix: validar line_items al inicio de la función, raise ValueError con
     índice de línea y valor problemático antes de tocar QBO.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestCreateInvoiceQuantityValidation(unittest.TestCase):
    """HIGH-1: create_invoice debe validar quantity > 0 antes de calcular UnitPrice."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_quantity_zero_raises_value_error(self):
        """RED: quantity=0 debe levantar ValueError con mensaje claro, no ZeroDivisionError."""
        from main import create_invoice

        line_items = [
            {"item_id": "1", "amount": 100.0, "quantity": 0}
        ]

        with patch("main.qbo_request") as mock_qbo:
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items=line_items)

            self.assertIn("quantity", str(ctx.exception).lower())
            self.assertIn("0", str(ctx.exception))
            mock_qbo.assert_not_called()

    def test_quantity_negative_raises_value_error(self):
        """RED: quantity<0 no tiene sentido en una venta; debe rechazarse."""
        from main import create_invoice

        line_items = [
            {"item_id": "1", "amount": 100.0, "quantity": -5}
        ]

        with patch("main.qbo_request") as mock_qbo:
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items=line_items)

            self.assertIn("quantity", str(ctx.exception).lower())
            mock_qbo.assert_not_called()

    def test_quantity_error_includes_line_index(self):
        """RED: el error debe indicar qué línea del array falla (idx 1-based)."""
        from main import create_invoice

        line_items = [
            {"item_id": "1", "amount": 50.0, "quantity": 2},
            {"item_id": "2", "amount": 75.0, "quantity": 0},
        ]

        with patch("main.qbo_request"):
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items=line_items)

            self.assertIn("2", str(ctx.exception))

    def test_missing_quantity_uses_default_one(self):
        """GREEN: si la clave quantity está ausente, default 1 (sin error)."""
        from main import create_invoice

        line_items = [
            {"item_id": "1", "amount": 100.0}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Invoice": {
                "Id": "999",
                "DocNumber": "INV-001",
                "TotalAmt": 100.0,
            }
        }

        with patch("main.qbo_request", return_value=mock_response) as mock_qbo:
            result = create_invoice(customer_id="42", line_items=line_items)
            self.assertTrue(result["success"])
            call_args = mock_qbo.call_args
            sent_data = call_args.kwargs.get("data") or call_args[1].get("data")
            line0 = sent_data["Line"][0]
            self.assertEqual(line0["SalesItemLineDetail"]["Qty"], 1)
            self.assertEqual(line0["SalesItemLineDetail"]["UnitPrice"], 100.0)

    def test_valid_quantity_proceeds_to_qbo(self):
        """GREEN: quantity>0 válido deja pasar a la llamada real a QBO."""
        from main import create_invoice

        line_items = [
            {"item_id": "1", "amount": 50.0, "quantity": 2}
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Invoice": {
                "Id": "1001",
                "DocNumber": "INV-002",
                "TotalAmt": 50.0,
            }
        }

        with patch("main.qbo_request", return_value=mock_response) as mock_qbo:
            result = create_invoice(customer_id="42", line_items=line_items)
            self.assertTrue(result["success"])
            self.assertEqual(result["invoice_id"], "1001")
            call_args = mock_qbo.call_args
            sent_data = call_args.kwargs.get("data") or call_args[1].get("data")
            self.assertEqual(
                sent_data["Line"][0]["SalesItemLineDetail"]["UnitPrice"], 25.0
            )


if __name__ == "__main__":
    unittest.main()
