"""Tests para MED-10: create_invoice debe rechazar line_items=[] o None.

Bug: main.py:801-816 — create_invoice no valida que line_items tenga
     contenido. Si se llama con [] o None, el loop no itera y se
     envía a QBO un Invoice sin Line → QBO rechaza con 400 confuso.
     Mismo riesgo en 6+ create_* tools.

Fix: validar al inicio de la función. Si line_items is None o [] o
     no es list, raise ValueError con mensaje claro. Esto es un
     patrón a aplicar también a create_bill, create_estimate, etc.
     (iteración 3b: extender a las otras 6 tools en commits separados).
"""
import unittest
from unittest.mock import patch


class TestCreateInvoiceEmptyLineItems(unittest.TestCase):
    """MED-10: create_invoice debe rechazar line_items=[] o None."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_empty_list_raises_value_error(self):
        """RED: line_items=[] debe raise ValueError antes de llamar QBO."""
        from main import create_invoice

        with patch("main.qbo_request") as mock_qbo:
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items=[])
            self.assertIn("line_items", str(ctx.exception).lower())
            self.assertIn("empty", str(ctx.exception).lower())
            mock_qbo.assert_not_called()

    def test_none_raises_value_error(self):
        """RED: line_items=None debe raise ValueError."""
        from main import create_invoice

        with patch("main.qbo_request") as mock_qbo:
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items=None)
            self.assertIn("line_items", str(ctx.exception).lower())
            mock_qbo.assert_not_called()

    def test_non_list_raises_value_error(self):
        """RED: line_items='not a list' (string) debe raise ValueError."""
        from main import create_invoice

        with patch("main.qbo_request") as mock_qbo:
            with self.assertRaises(ValueError) as ctx:
                create_invoice(customer_id="42", line_items="oops")
            self.assertIn("line_items", str(ctx.exception).lower())
            mock_qbo.assert_not_called()

    def test_valid_list_proceeds(self):
        """GREEN: line_items con contenido se procesa normalmente."""
        from main import create_invoice
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Invoice": {"Id": "1", "DocNumber": "INV-1", "TotalAmt": 100.0}
        }

        with patch("main.qbo_request", return_value=mock_response) as mock_qbo:
            result = create_invoice(
                customer_id="42",
                line_items=[{"item_id": "1", "amount": 100.0, "quantity": 1}],
            )
            self.assertTrue(result["success"])
            mock_qbo.assert_called_once()


if __name__ == "__main__":
    unittest.main()
