"""Tests para HIGH-7: find_bank_account_id debe usar category='ACTIVO'.

Bug: dexter/core/qbo_client.py:274 — find_bank_account_id pasa
     category='BANK' a find_account. Pero find_account (main.py:426-453)
     filtra por categorías en ESPAÑOL: 'ACTIVO', 'PASIVO', 'INGRESO', 'GASTO'.
     'BANK' nunca matchea → siempre retorna ''.

Fix: cambiar a category='ACTIVO' (bank accounts son Asset type).
     Agregar fallback: si no encuentra con category, intentar sin
     filter (search-wide) para casos donde la cuenta no esté categorizada.
"""
import unittest
from unittest.mock import MagicMock


class TestFindBankAccountIdCategory(unittest.TestCase):
    """HIGH-7: find_bank_account_id debe usar 'ACTIVO' como category."""

    def test_finds_bank_account_using_activo_category(self):
        """RED: con cuentas Asset, debe usar category='ACTIVO' y retornar ID."""
        from dexter.core.qbo_client import find_bank_account_id

        activo_bank = {
            "id": "bank_1",
            "name": "Bank of America",
            "category": "ACTIVO",
        }
        activo_other = {
            "id": "asset_2",
            "name": "Accounts Receivable",
            "category": "ACTIVO",
        }
        chart = {
            "bank_1": activo_bank,
            "asset_2": activo_other,
        }

        def fake_find_account(term, exact=False, category=None):
            if category is None:
                return []
            return [a for a in chart.values() if a["category"] == category]

        result = find_bank_account_id(fake_find_account, search_terms=["bank"])
        self.assertEqual(result, "bank_1")

    def test_falls_back_to_search_wide_if_no_match(self):
        """GREEN: si no hay cuentas con 'ACTIVO', intentar sin filter."""
        from dexter.core.qbo_client import find_bank_account_id

        chart = {
            "bank_1": {"id": "bank_1", "name": "Bank", "category": "OTRO"},
        }

        calls = []

        def fake_find_account(term, exact=False, category=None):
            calls.append(category)
            if category == "ACTIVO":
                return []
            return [a for a in chart.values() if term.lower() in a["name"].lower()]

        result = find_bank_account_id(fake_find_account, search_terms=["bank"])
        self.assertEqual(result, "bank_1")
        self.assertIn("ACTIVO", calls)

    def test_returns_empty_string_when_no_bank_found(self):
        """GREEN: si no hay match, retorna '' (no raise)."""
        from dexter.core.qbo_client import find_bank_account_id

        def fake_find_account(term, exact=False, category=None):
            return []

        result = find_bank_account_id(fake_find_account, search_terms=["bank"])
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
