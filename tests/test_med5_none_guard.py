"""Tests para MED-5: find_account debe None-guard acc['name'] y acc['category'].

Bug: main.py:534, 543, 546 — find_account usa acc['category'] y
     acc['name'] directamente. Si el chart tiene cuentas con valores
     None (data malformada desde QBO o caché corrupto), TypeError en
     .lower() o .upper(). Crash silencioso o error genérico.

Fix: None-guard. Si acc['name'] o acc['category'] es None, skip la
     cuenta (no es match válido).
"""
import unittest
from unittest.mock import patch


class TestFindAccountNoneGuard(unittest.TestCase):
    """MED-5: find_account debe None-guard name y category."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_account_with_none_name_does_not_crash(self):
        """RED: acc con name=None no debe crashear (skip)."""
        from main import find_account

        chart = {
            "1": {"id": "1", "name": None, "number": "1000", "category": "ACTIVO"},
            "2": {"id": "2", "name": "Bank", "number": "1100", "category": "ACTIVO"},
        }

        with patch("main.session_state", {"chart_of_accounts": chart}):
            results = find_account("Bank")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["id"], "2")

    def test_account_with_none_category_does_not_crash(self):
        """RED: acc con category=None no debe crashear (skip en category filter)."""
        from main import find_account

        chart = {
            "1": {"id": "1", "name": "Bank", "number": "1000", "category": None},
        }

        with patch("main.session_state", {"chart_of_accounts": chart}):
            results = find_account("Bank", category="ACTIVO")
            self.assertEqual(results, [])

    def test_exact_match_with_none_name_returns_empty(self):
        """RED: exact match con name=None no debe crashear."""
        from main import find_account

        chart = {
            "1": {"id": "1", "name": None, "number": "1000", "category": "ACTIVO"},
        }

        with patch("main.session_state", {"chart_of_accounts": chart}):
            results = find_account("bank", exact=True)
            self.assertEqual(results, [])

    def test_mixed_chart_only_returns_valid_accounts(self):
        """GREEN: chart mixto (algunos None, otros válidos) solo retorna válidos."""
        from main import find_account

        chart = {
            "1": {"id": "1", "name": None, "number": "1000", "category": "ACTIVO"},
            "2": {"id": "2", "name": "Bank", "number": "1100", "category": "ACTIVO"},
            "3": {"id": "3", "name": "Cash", "number": None, "category": "ACTIVO"},
        }

        with patch("main.session_state", {"chart_of_accounts": chart}):
            results = find_account("bank")
            names = [r["name"] for r in results]
            self.assertIn("Bank", names)
            self.assertNotIn(None, names)


if __name__ == "__main__":
    unittest.main()
