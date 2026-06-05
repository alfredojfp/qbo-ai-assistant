"""Tests para LOW-3: process_quick_command usa word boundaries.

Bug: main.py:5345 — process_quick_command usa `in` para matching:
     if "refrescar" in input_lower
     if "template" in input_lower
     if "recon" in input_lower
     Esto matchea substrings falsos:
       - "refrescar" matchea en "refrescante", "refrescamiento"
       - "template" matchea en "templated", "templater"
       - "recon" matchea en "reconocer", "reconciliación" (acceptable
         aquí porque el intent es recon)
       - "listar" matchea en "sublistar"
       - "manual" matchea en "manualmente", "manualidad"

Fix: helper _quick_match(input_lower, keyword) que usa regex con
     word boundaries \\b. process_quick_command usa el helper.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestQuickCommandWordBoundaries(unittest.TestCase):
    """LOW-3: process_quick_command usa word boundaries."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_helper_exists(self):
        """RED: _quick_match debe existir en main."""
        import main
        self.assertTrue(callable(getattr(main, "_quick_match", None)))

    def test_exact_word_matches(self):
        """GREEN: 'refrescar chart' matchea 'refrescar' con word boundary."""
        from main import _quick_match
        self.assertTrue(_quick_match("refrescar chart", "refrescar"))
        self.assertTrue(_quick_match("refrescar", "refrescar"))

    def test_substring_does_not_match(self):
        """GREEN: palabras con el keyword como prefijo+letra adicional
        NO deben matchear (refrescante ≠ refrescar)."""
        from main import _quick_match
        self.assertFalse(_quick_match("refrescante de menta", "refrescar"))
        self.assertFalse(_quick_match("templater pro", "template"))

    def test_case_insensitive(self):
        """GREEN: matching es case-insensitive."""
        from main import _quick_match
        self.assertTrue(_quick_match("REFRESCAR chart", "refrescar"))
        self.assertTrue(_quick_match("Refrescar Chart", "refrescar"))

    def test_stem_matches(self):
        """GREEN: _quick_match_stem es alias de _quick_match (decisión
        de diseño: stems complejos son demasiado riesgosos)."""
        from main import _quick_match_stem
        # _quick_match_stem es alias - no usamos stems (demasiado riesgo)
        # de falsos positivos (recon → reconciliación, refrescar → refresca)
        self.assertTrue(_quick_match_stem("refrescar", "refrescar"))
        self.assertTrue(_quick_match_stem("reconocer", "reconocer"))

    def test_stem_helper_exists(self):
        """GREEN: _quick_match_stem existe como helper complementario."""
        import main
        self.assertTrue(callable(getattr(main, "_quick_match_stem", None)))

    def test_substring_blocked_within_word(self):
        """GREEN: 'listar' NO debe matchear 'sublistar'."""
        from main import _quick_match
        self.assertFalse(_quick_match("sublistar items", "listar"))
        self.assertFalse(_quick_match("manualidad creativa", "manual"))

    def test_process_quick_uses_helper(self):
        """GREEN: process_quick_command usa _quick_match internamente."""
        import main
        with patch("main._quick_match", wraps=main._quick_match) as spy:
            main.process_quick_command("refrescar chart")
            self.assertGreater(spy.call_count, 0)


if __name__ == "__main__":
    unittest.main()
