"""Tests para MED-2: parse_date debe raise en fecha inválida (no fallback silencioso).

Bug: main.py:212 — parse_date cae silenciosamente a 'today' con un print
     si la fecha no matchea ningún formato. Para operaciones batch,
     esto significa que fechas inválidas se convierten en 'today' en
     silencio — mal para auditoría.

Fix: diferenciar entre:
     - date_str vacía/None → usar today (backward compat para callers
       que no pasan fecha)
     - date_str con formato inválido → raise ValueError con mensaje claro
"""
import unittest
from datetime import datetime
from unittest.mock import patch


class TestParseDateStrict(unittest.TestCase):
    """MED-2: parse_date debe raise en fecha inválida."""

    def setUp(self):
        from main import parse_date
        self.parse_date = parse_date

    def test_empty_string_returns_today(self):
        """GREEN: date_str vacía → today (backward compat)."""
        result = self.parse_date("")
        expected = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(result, expected)

    def test_valid_iso_format_unchanged(self):
        """GREEN: formato ISO YYYY-MM-DD → se retorna igual."""
        self.assertEqual(self.parse_date("2026-06-15"), "2026-06-15")

    def test_valid_dmy_format_parsed(self):
        """GREEN: DD/MM/YYYY se parsea correctamente."""
        self.assertEqual(self.parse_date("15/06/2026"), "2026-06-15")

    def test_valid_long_format_parsed(self):
        """GREEN: '15 June 2026' se parsea correctamente."""
        self.assertEqual(self.parse_date("15 June 2026"), "2026-06-15")

    def test_invalid_format_raises_value_error(self):
        """RED: fecha inválida ('foo', '32/13/2026') debe raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.parse_date("not-a-date")
        self.assertIn("not-a-date", str(ctx.exception))

    def test_invalid_day_month_raises(self):
        """RED: '32/13/2026' (día/mes inválido) debe raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.parse_date("32/13/2026")
        self.assertIn("32/13/2026", str(ctx.exception))

    def test_invalid_garbage_does_not_silently_use_today(self):
        """RED: 'xxxxxxxx' NO debe caer a today silenciosamente."""
        today = datetime.now().strftime("%Y-%m-%d")
        with self.assertRaises(ValueError):
            self.parse_date("xxxxxxxx")
        # Comprobar que no se retornó today
        try:
            result = self.parse_date("xxx")
        except ValueError:
            result = None
        self.assertNotEqual(result, today)


if __name__ == "__main__":
    unittest.main()
