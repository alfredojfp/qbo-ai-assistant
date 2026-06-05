"""Tests para LOW-6: get_relevant_tools soporta keywords en EN y ES.

Bug: main.py:5553 — get_relevant_tools itera KEYWORDS_BY_MODULE
     (todo en español: 'reporte', 'buscar', 'cliente', 'factura').
     Cuando session_state['language'] == 'en' y el usuario escribe
     'generate a report' o 'find customer', NINGÚN keyword matchea
     → fallback a safe defaults → tools relevantes NO se activan.
     El LLM tiene que adivinar el tool correcto, fallando más.

Fix: cada módulo declara KEYWORDS_ES y KEYWORDS_EN. KEYWORDS_BY_MODULE
     retorna ambos. get_relevant_tools matchea contra los dos.
     Keywords duplicados (en ambos idiomas) se deduplicán.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestGetRelevantToolsBilingual(unittest.TestCase):
    """LOW-6: get_relevant_tools soporta ES y EN."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _extract_names(self, schemas):
        """Helper: extrae nombres de funciones desde schemas OpenAI."""
        out = []
        for s in schemas:
            if isinstance(s, dict):
                if "function" in s and isinstance(s["function"], dict):
                    out.append(s["function"].get("name", ""))
                elif "name" in s:
                    out.append(s["name"])
        return [n for n in out if n]

    def test_english_keyword_activates_search_tools(self):
        """RED: 'find customer' (EN) debe activar search module."""
        from main import get_relevant_tools
        names = self._extract_names(get_relevant_tools("find customer"))
        self.assertIn("buscar_cliente", names)

    def test_english_keyword_activates_reports(self):
        """GREEN: 'generate report' (EN) debe activar reports module."""
        from main import get_relevant_tools
        names = self._extract_names(get_relevant_tools("generate a report"))
        self.assertIn("generar_reporte_pl", names)

    def test_english_keyword_activates_ocr(self):
        """GREEN: 'process pdf invoice' (EN) debe activar ocr module."""
        from main import get_relevant_tools
        names = self._extract_names(get_relevant_tools("process pdf invoice"))
        self.assertIn("procesar_lote_bills", names)

    def test_spanish_still_works(self):
        """GREEN: backward compat — 'buscar cliente' (ES) sigue funcionando."""
        from main import get_relevant_tools
        names = self._extract_names(get_relevant_tools("buscar cliente"))
        self.assertIn("buscar_cliente", names)

    def test_bilingual_helper_exists(self):
        """GREEN: _bilingual_keywords existe y deduplica."""
        from main import _bilingual_keywords
        out = _bilingual_keywords(["buscar", "cliente", "buscar"])
        self.assertEqual(out.count("buscar"), 1)


if __name__ == "__main__":
    unittest.main()
