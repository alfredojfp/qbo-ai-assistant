"""Tests para fuzzy matching de clientes ≥85% (HIGH-1).

HIGH-1: La lógica vive en dexter.skills.search.fuzzy.
main.py tiene wrappers finos que delegan + log_operation.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dexter.skills.search.fuzzy as fuzzy


class TestFuzzyCustomerSearch(unittest.TestCase):
    """HIGH-1: dexter.skills.search.fuzzy (search_customer con fuzzy fallback)."""

    def setUp(self):
        self._orig_customer_cache = fuzzy._customer_cache
        self._orig_vendor_cache = fuzzy._vendor_cache
        fuzzy._customer_cache = None
        fuzzy._customer_cache_time = 0.0
        fuzzy._vendor_cache = None
        fuzzy._vendor_cache_time = 0.0

    def tearDown(self):
        fuzzy._customer_cache = self._orig_customer_cache
        fuzzy._vendor_cache = self._orig_vendor_cache

    def test_search_customer_qbo_finds_exact_no_fuzzy(self):
        """Cuando QBO encuentra resultados, no activa fuzzy fallback."""
        mock_qbo_result = {
            "QueryResponse": {
                "Customer": [
                    {"Id": "1", "DisplayName": "John Smith", "Active": True, "Balance": 100}
                ]
            }
        }
        with patch.object(fuzzy, "_qbo", return_value=lambda sql: mock_qbo_result):
            result = fuzzy.search_customer("John", exact=False, fuzzy_fallback=True)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], "1")
            self.assertEqual(result[0]["name"], "John Smith")
            self.assertNotIn("_fuzzy_score", result[0])

    def test_search_customer_exact_disables_fuzzy(self):
        """exact=True nunca activa fuzzy fallback."""
        mock_qbo_result = {"error": "not found"}
        with patch.object(fuzzy, "_qbo", return_value=lambda sql: mock_qbo_result):
            result = fuzzy.search_customer("Nobody", exact=True, fuzzy_fallback=True)
            self.assertEqual(result, [])

    def test_find_similar_customers_above_threshold(self):
        """Clientes con ≥85% similitud se retornan ordenados por score."""
        fuzzy._customer_cache = [
            {"id": "1", "name": "John Smith", "balance": 0, "active": True, "company": ""},
            {"id": "2", "name": "Joan Smith", "balance": 0, "active": True, "company": ""},
            {"id": "3", "name": "Jon Smitt", "balance": 0, "active": True, "company": ""},
            {"id": "4", "name": "XYZ Corporation", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._customer_cache_time = float("inf")
        results = fuzzy.find_similar_customers("John Smith", threshold=0.85)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("_fuzzy_score", results[0])
        self.assertEqual(results[0]["name"], "John Smith")
        self.assertAlmostEqual(results[0]["_fuzzy_score"], 1.0)

    def test_find_similar_customers_below_threshold_excluded(self):
        """Clientes con <85% se excluyen."""
        fuzzy._customer_cache = [
            {"id": "1", "name": "XYZ Corporation", "balance": 0, "active": True, "company": ""},
            {"id": "2", "name": "ABC Holdings", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._customer_cache_time = float("inf")
        results = fuzzy.find_similar_customers("John Smith", threshold=0.85)
        self.assertEqual(results, [])

    def test_find_similar_customers_respects_max_results(self):
        """Respeta el límite max_results."""
        fuzzy._customer_cache = [
            {"id": str(i), "name": f"John Smith Variant {i}", "balance": 0, "active": True, "company": ""}
            for i in range(10)
        ]
        fuzzy._customer_cache_time = float("inf")
        results = fuzzy.find_similar_customers("John Smith", threshold=0.0, max_results=3)
        self.assertEqual(len(results), 3)

    def test_search_customer_integration_fuzzy_fallback(self):
        """Integración: QBO no encuentra, fuzzy fallback sí."""
        fuzzy._customer_cache = [
            {"id": "10", "name": "Joan Smith", "balance": 0, "active": True, "company": ""},
            {"id": "20", "name": "John Smith Jr", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._customer_cache_time = float("inf")

        mock_qbo_empty = {"QueryResponse": {}}
        with patch.object(fuzzy, "_qbo", return_value=lambda sql: mock_qbo_empty):
            result = fuzzy.search_customer("John Smith", exact=False, fuzzy_fallback=True)
            self.assertGreaterEqual(len(result), 1)
            self.assertIn("_fuzzy_score", result[0])

    def test_cache_invalidation_on_create(self):
        """Crear cliente invalida el caché."""
        fuzzy._customer_cache = [{"id": "old", "name": "Old", "balance": 0, "active": True, "company": ""}]
        fuzzy._customer_cache_time = float("inf")
        self.assertIsNotNone(fuzzy._customer_cache)
        fuzzy.invalidate_customer_cache()
        self.assertIsNone(fuzzy._customer_cache)

    def test_search_vendor_fuzzy_fallback(self):
        """search_vendor también tiene fuzzy fallback."""
        fuzzy._vendor_cache = [
            {"id": "50", "name": "Acme Supply Co", "balance": 0, "active": True, "company": ""},
            {"id": "60", "name": "XYZ Corp", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._vendor_cache_time = float("inf")

        mock_qbo_empty = {"QueryResponse": {}}
        with patch.object(fuzzy, "_qbo", return_value=lambda sql: mock_qbo_empty):
            result = fuzzy.search_vendor("Acme Supply", exact=False, fuzzy_fallback=True)
            self.assertGreaterEqual(len(result), 1)
            self.assertIn("_fuzzy_score", result[0])

    def test_fuzzy_fallback_disabled_flag(self):
        """fuzzy_fallback=False evita el fallback."""
        fuzzy._customer_cache = [
            {"id": "1", "name": "John Smith", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._customer_cache_time = float("inf")

        mock_qbo_empty = {"QueryResponse": {}}
        with patch.object(fuzzy, "_qbo", return_value=lambda sql: mock_qbo_empty):
            result = fuzzy.search_customer("John", exact=False, fuzzy_fallback=False)
            self.assertEqual(result, [])


class TestAskFuzzyCustomerMatch(unittest.TestCase):
    """HIGH-1: Disambiguator.ask_fuzzy_customer_match()."""

    def setUp(self):
        from dexter.core.batch.disambiguator import Disambiguator
        self.inputs = []
        self.outputs = []
        self.d = Disambiguator(
            input_func=lambda _: self.inputs.pop(0) if self.inputs else "",
            output_func=lambda s: self.outputs.append(s),
        )

    def test_selecciona_fuzzy_match(self):
        """Usuario selecciona una de las opciones fuzzy."""
        self.inputs = ["1"]
        candidates = [
            {"id": "50", "name": "Joan Smith", "_fuzzy_score": 0.89},
            {"id": "60", "name": "John Smitt", "_fuzzy_score": 0.85},
        ]
        result = self.d.ask_fuzzy_customer_match("John Smith", candidates)
        self.assertEqual(result, "50")
        output_text = "\n".join(self.outputs)
        self.assertIn("89%", output_text)
        self.assertIn("85%", output_text)
        self.assertIn("John Smith", output_text)

    def test_crear_nuevo_desde_fuzzy(self):
        """Usuario elige N para crear nuevo cliente."""
        self.inputs = ["n"]
        candidates = [{"id": "99", "name": "Similar Name", "_fuzzy_score": 0.87}]
        result = self.d.ask_fuzzy_customer_match("Unique Name", candidates)
        self.assertEqual(result, "__NEW__")

    def test_saltar_fuzzy(self):
        """Usuario elige S para saltar."""
        self.inputs = ["s"]
        candidates = [{"id": "99", "name": "Similar Name", "_fuzzy_score": 0.87}]
        result = self.d.ask_fuzzy_customer_match("Unique Name", candidates)
        self.assertIsNone(result)

    def test_opcion_invalida_re_pregunta(self):
        """Opción inválida → vuelve a preguntar."""
        self.inputs = ["999", "1"]
        candidates = [
            {"id": "10", "name": "Match", "_fuzzy_score": 0.90},
        ]
        result = self.d.ask_fuzzy_customer_match("Name", candidates)
        self.assertEqual(result, "10")
        self.assertTrue(len(self.inputs) == 0)


class TestTokenBasedFuzzyMatching(unittest.TestCase):
    """HIGH-1b: token-based fuzzy matching con prefijos."""

    def test_ben_haselman_vs_benjamin_haselman(self):
        score = fuzzy._name_similarity("Ben Haselman", "Benjamin Haselman")
        self.assertGreaterEqual(score, 0.85)

    def test_ben_haselman_vs_benjamin_haselman_score(self):
        score = fuzzy._name_similarity("Ben Haselman", "Benjamin Haselman")
        # token-based: "ben" → prefix "benjamin" (0.90), "haselman" → exact (1.0) → avg 0.95
        self.assertAlmostEqual(score, 0.95, delta=0.05)

    def test_exact_match_is_perfect(self):
        self.assertEqual(fuzzy._name_similarity("John Smith", "John Smith"), 1.0)

    def test_prefix_ben_vs_benjamin_detected(self):
        self.assertGreaterEqual(fuzzy._token_similarity("Ben", "Benjamin"), 0.85)

    def test_prefix_mike_vs_michael(self):
        """Mike no es prefijo de Michael (m-i-k-e vs m-i-c-h-a-e-l)."""
        score = fuzzy._token_similarity("Mike", "Michael")
        self.assertLess(score, 0.85)

    def test_prefix_pat_vs_patrick(self):
        """Pat sí es prefijo de Patrick."""
        self.assertGreaterEqual(fuzzy._token_similarity("Pat", "Patrick"), 0.85)

    def test_last_name_match_first_name_prefix(self):
        score = fuzzy._name_similarity("Bob Johnson", "Robert Johnson")
        self.assertGreaterEqual(score, 0.80)

    def test_different_last_names_rejected(self):
        score = fuzzy._name_similarity("Ben Smith", "Benjamin Jones")
        self.assertLess(score, 0.85)

    def test_find_similar_uses_token_matching(self):
        fuzzy._customer_cache = [
            {"id": "1", "name": "Benjamin Haselman", "balance": 0, "active": True, "company": ""},
            {"id": "2", "name": "XYZ Corp", "balance": 0, "active": True, "company": ""},
        ]
        fuzzy._customer_cache_time = float("inf")
        results = fuzzy.find_similar_customers("Ben Haselman", threshold=0.85)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Benjamin Haselman")

    def test_single_token_query_vs_multi_token_candidate(self):
        score = fuzzy._name_similarity("Benjamin", "Benjamin Franklin Haselman")
        self.assertGreaterEqual(score, 0.85)

    def test_string_similarity_still_works_as_fallback(self):
        score = fuzzy._name_similarity("Jon Smith", "John Smith")
        self.assertGreaterEqual(score, 0.85)


if __name__ == "__main__":
    unittest.main()
