"""Tests para HIGH-9: create_customer debe soportar deduplicación opcional.

Bug: `create_customer(display_name, ...)` siempre hace POST. Si el
     cliente ya existe, QBO retorna 409 Conflict. No hay búsqueda
     previa. Mismo patrón aplica a create_vendor/create_account/create_item
     y otros 5+ create_* master data (18 en total).

Fix: agregar parámetro opcional `deduplicate: bool = False`. Si es True,
     hacer `search_customer(exact=True)` antes del POST; si hay match
     exacto por DisplayName, retornar el ID existente sin crear.
     Default False para backward compat (0 líneas removidas).

Scope del commit: patrón de ejemplo en create_customer. Se replica a
los otros 5+ master data en commits subsiguientes (HIGH-9a, HIGH-9b...).
"""
import unittest
from unittest.mock import patch, MagicMock


class TestCreateCustomerIdempotency(unittest.TestCase):
    """HIGH-9: create_customer debe poder ser idempotente vía deduplicate=True."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_deduplicate_true_returns_existing_when_found(self):
        """RED: deduplicate=True + display_name existente → retorna existing, NO POST."""
        from main import create_customer

        existing = [{
            "id": "42",
            "name": "Acme Corp",
            "company": "Acme Holdings",
            "balance": 100.0,
            "active": True,
        }]

        with patch("main.search_customer", return_value=existing) as mock_search, \
             patch("main.qbo_request") as mock_qbo:
            result = create_customer(
                display_name="Acme Corp",
                deduplicate=True,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["customer_id"], "42")
            self.assertTrue(result.get("idempotent_reused"))
            self.assertEqual(result["display_name"], "Acme Corp")
            mock_search.assert_called_once_with("Acme Corp", exact=True)
            mock_qbo.assert_not_called()

    def test_deduplicate_true_creates_when_not_found(self):
        """RED: deduplicate=True + display_name nuevo → comportamiento normal de create."""
        from main import create_customer

        with patch("main.search_customer", return_value=[]) as mock_search, \
             patch("main.qbo_request") as mock_qbo:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "Customer": {
                    "Id": "99",
                    "DisplayName": "New Customer",
                    "CompanyName": None,
                    "Balance": 0,
                    "Active": True,
                }
            }
            mock_qbo.return_value = mock_response

            result = create_customer(
                display_name="New Customer",
                email="new@example.com",
                deduplicate=True,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["customer_id"], "99")
            self.assertFalse(result.get("idempotent_reused", False))
            mock_search.assert_called_once_with("New Customer", exact=True)
            mock_qbo.assert_called_once()
            sent_data = mock_qbo.call_args.kwargs.get("data") or mock_qbo.call_args[1].get("data")
            self.assertEqual(sent_data["DisplayName"], "New Customer")
            self.assertEqual(sent_data["PrimaryEmailAddr"]["Address"], "new@example.com")

    def test_deduplicate_false_skips_search_backward_compat(self):
        """GREEN: deduplicate=False (default) → comportamiento actual, no search."""
        from main import create_customer

        with patch("main.search_customer") as mock_search, \
             patch("main.qbo_request") as mock_qbo:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "Customer": {
                    "Id": "100",
                    "DisplayName": "Legacy",
                    "CompanyName": None,
                    "Balance": 0,
                    "Active": True,
                }
            }
            mock_qbo.return_value = mock_response

            result = create_customer(display_name="Legacy")

            self.assertTrue(result["success"])
            self.assertEqual(result["customer_id"], "100")
            self.assertNotIn("idempotent_reused", result)
            mock_search.assert_not_called()
            mock_qbo.assert_called_once()

    def test_deduplicate_true_uses_exact_match_not_fuzzy(self):
        """RED: la búsqueda pre-check debe ser exacta (no fuzzy) para evitar falsos positivos."""
        from main import create_customer

        with patch("main.search_customer", return_value=[]) as mock_search, \
             patch("main.qbo_request") as mock_qbo:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "Customer": {"Id": "1", "DisplayName": "Acme", "Active": True}
            }
            mock_qbo.return_value = mock_response

            create_customer(display_name="Acme Co", deduplicate=True)

            self.assertEqual(mock_search.call_args.kwargs.get("exact"), True)


if __name__ == "__main__":
    unittest.main()
