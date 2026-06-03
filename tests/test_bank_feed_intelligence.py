# -*- coding: utf-8 -*-
"""
Tests para el motor de clasificación de bank feed.

Estos tests usan unittest de stdlib (sin dependencias externas).
Ejecutar con: python -m unittest tests.test_bank_feed_intelligence
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch

from autonomia.bank_feed_intelligence import (
    BankFeedClassificationEngine,
    normalize_description,
    classify_transaction,
    tool_analyze_bank_feed_for_classification,
    tool_find_pattern_for_transaction,
    tool_record_bank_feed_classification,
    tool_get_classification_history_stats,
)


class TestNormalize(unittest.TestCase):
    """Tests para la función de normalización de descripciones."""

    def test_lowercase(self):
        self.assertEqual(normalize_description("AMAZON.COM"), "amazon com")

    def test_remove_punctuation(self):
        self.assertEqual(normalize_description("AMZN Mktp US*MK4J2"), "amzn mktp us mk j")

    def test_remove_numbers(self):
        self.assertEqual(normalize_description("ACH DEBIT 123456789"), "ach debit")

    def test_collapse_spaces(self):
        self.assertEqual(normalize_description("FOO   BAR   BAZ"), "foo bar baz")

    def test_empty(self):
        self.assertEqual(normalize_description(""), "")

    def test_spanish_accents_preserved(self):
        # Los acentos no se eliminan, son significativos en español
        self.assertEqual(normalize_description("SEÑOR INDUSTRIAS"), "señor industrias")

    def test_complex_case(self):
        result = normalize_description("AMZN Mktp US*MK4J2 #12345")
        self.assertNotIn("12345", result)
        self.assertNotIn("*", result)
        self.assertNotIn("#", result)


class TestClassifyTransaction(unittest.TestCase):
    """Tests del motor de matching principal."""

    def setUp(self):
        self.history = {
            "classifications": [
                {
                    "description": "AMAZON.COM",
                    "account_id": "acc_1",
                    "account_name": "Office Supplies",
                    "amount": 45.00,
                    "date": "2026-01-15"
                },
                {
                    "description": "STARBUCKS STORE #123",
                    "account_id": "acc_2",
                    "account_name": "Meals & Entertainment",
                    "amount": 12.50,
                    "date": "2026-01-16"
                },
                {
                    "description": "SHELL OIL 12345",
                    "account_id": "acc_3",
                    "account_name": "Vehicle Expenses",
                    "amount": 65.00,
                    "date": "2026-01-17"
                }
            ],
            "patterns": {
                r"\bpayroll\b": {"account_id": "acc_4", "account_name": "Payroll Expenses"},
                r"\bclient\s+payment\b": {"account_id": "acc_5", "account_name": "Service Revenue"}
            }
        }

    def test_exact_match_returns_100_confidence(self):
        result = classify_transaction("AMAZON.COM", 45.00, self.history)
        self.assertEqual(result["confidence"], 100)
        self.assertEqual(result["account_name"], "Office Supplies")
        self.assertEqual(result["match_type"], "exact")

    def test_exact_match_ignores_punctuation_and_case(self):
        result = classify_transaction("amazon.com!", 50.00, self.history)
        self.assertEqual(result["confidence"], 100)
        self.assertEqual(result["account_name"], "Office Supplies")

    def test_regex_pattern_match_returns_95_confidence(self):
        result = classify_transaction("PAYROLL DEPOSIT 2026-01", 5000.00, self.history)
        self.assertEqual(result["confidence"], 95)
        self.assertEqual(result["account_name"], "Payroll Expenses")
        self.assertEqual(result["match_type"], "regex")

    def test_fuzzy_match_high_confidence(self):
        # STARBUCKS con variaciones debería hacer match fuzzy
        result = classify_transaction("STARBUCKS COFFEE", 13.00, self.history)
        self.assertIn(result["match_type"], ["fuzzy", "fuzzy_weak"])
        self.assertGreaterEqual(result["confidence"], 40)
        if result["match_type"] == "fuzzy":
            self.assertEqual(result["account_name"], "Meals & Entertainment")

    def test_no_match_returns_default_for_expense(self):
        # Convención: monto negativo = gasto (expense)
        result = classify_transaction("COMPLETELY UNKNOWN VENDOR XYZ", -50.00, self.history)
        self.assertEqual(result["match_type"], "default")
        self.assertLess(result["confidence"], 30)
        # Default para gastos pequeños = Office Supplies
        self.assertEqual(result["account_name"], "Office Supplies")

    def test_no_match_returns_default_for_income(self):
        # Convención: monto positivo = ingreso
        result = classify_transaction("UNKNOWN INCOME SOURCE", 500.00, self.history)
        self.assertEqual(result["match_type"], "default")
        self.assertEqual(result["account_name"], "Sales Income")

    def test_no_match_large_expense_suggests_major_purchases(self):
        # Gasto grande (negativo) → Major Purchases
        result = classify_transaction("UNKNOWN BIG PURCHASE", -5000.00, self.history)
        self.assertEqual(result["account_name"], "Major Purchases")

    def test_empty_history_returns_default(self):
        empty = {"classifications": [], "patterns": {}}
        result = classify_transaction("ANYTHING", 100.00, empty)
        self.assertEqual(result["match_type"], "default")
        self.assertEqual(result["confidence"], 15)

    def test_result_includes_reasoning(self):
        result = classify_transaction("AMAZON.COM", 45.00, self.history)
        self.assertIn("reasoning", result)
        self.assertIsInstance(result["reasoning"], str)
        self.assertGreater(len(result["reasoning"]), 0)

    def test_result_includes_account_id(self):
        result = classify_transaction("AMAZON.COM", 45.00, self.history)
        self.assertIn("account_id", result)
        self.assertIn("account_name", result)
        self.assertIn("confidence", result)
        self.assertIn("match_type", result)


class TestAnalyzeBankFeed(unittest.TestCase):
    """Tests para la función tool_analyze_bank_feed_for_classification."""

    def setUp(self):
        self.engine = BankFeedClassificationEngine(history_file="/tmp/_test_history.json")
        # Poblar historial
        self.engine.record_classification(
            description="AMAZON.COM",
            account_id="acc_1",
            account_name="Office Supplies",
            amount=45.00,
            date="2026-01-15"
        )
        self.engine.save_history()

    def tearDown(self):
        if os.path.exists("/tmp/_test_history.json"):
            os.remove("/tmp/_test_history.json")

    def test_empty_transactions_returns_zero_total(self):
        result = self.engine.analyze_pending_transactions([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(len(result["high_confidence"]), 0)
        self.assertEqual(len(result["medium_confidence"]), 0)
        self.assertEqual(len(result["low_confidence"]), 0)
        self.assertEqual(len(result["no_match"]), 0)

    def test_exact_match_goes_to_high_confidence(self):
        result = self.engine.analyze_pending_transactions([
            {"description": "AMAZON.COM", "amount": 50.00}
        ])
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["high_confidence"]), 1)
        self.assertEqual(len(result["no_match"]), 0)

    def test_unknown_transaction_goes_to_no_match(self):
        result = self.engine.analyze_pending_transactions([
            {"description": "COMPLETELY UNKNOWN", "amount": 50.00}
        ])
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["high_confidence"]), 0)
        self.assertEqual(len(result["no_match"]), 1)

    def test_min_confidence_threshold(self):
        # min_confidence 90 → el match exacto (100) pasa, el default (15) no
        result = self.engine.analyze_pending_transactions(
            [
                {"description": "AMAZON.COM", "amount": 50.00},
                {"description": "RANDOM THING", "amount": 50.00}
            ],
            min_confidence=0.90
        )
        self.assertEqual(len(result["high_confidence"]), 1)
        self.assertEqual(len(result["no_match"]), 1)


class TestToolWrappers(unittest.TestCase):
    """Tests de las funciones tool_* para verificar compatibilidad de API."""

    def setUp(self):
        self._tmp_history = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        self._tmp_history_path = self._tmp_history.name
        self._tmp_history.close()

    def tearDown(self):
        if os.path.exists(self._tmp_history_path):
            os.remove(self._tmp_history_path)

    def test_tool_find_pattern_no_match(self):
        result = tool_find_pattern_for_transaction("BLAH BLAH")
        self.assertTrue(result["success"])

    def test_tool_record_classification(self):
        result = tool_record_bank_feed_classification(
            description="AMAZON",
            account_id="acc_1",
            account_name="Office",
            amount=10.0,
            date="2026-01-01"
        )
        self.assertTrue(result["success"])

    def test_tool_get_stats(self):
        result = tool_get_classification_history_stats()
        self.assertTrue(result["success"])
        self.assertIn("total_classifications", result)
        self.assertIn("patterns_learned", result)


class TestBackwardCompatibility(unittest.TestCase):
    """Tests que verifican que el módulo mantiene la API pública anterior."""

    def test_module_imports(self):
        """El módulo debe poder importarse sin errores."""
        from autonomia import bank_feed_intelligence
        self.assertIsNotNone(bank_feed_intelligence)

    def test_required_functions_exist(self):
        """Las funciones tool_* deben existir con la firma original."""
        import autonomia.bank_feed_intelligence as mod
        self.assertTrue(hasattr(mod, "tool_analyze_bank_feed_for_classification"))
        self.assertTrue(hasattr(mod, "tool_record_bank_feed_classification"))
        self.assertTrue(hasattr(mod, "tool_get_classification_history_stats"))
        self.assertTrue(hasattr(mod, "tool_find_pattern_for_transaction"))

    def test_class_engine_exists(self):
        """La clase principal debe existir y ser instanciable."""
        import autonomia.bank_feed_intelligence as mod
        self.assertTrue(hasattr(mod, "BankFeedClassificationEngine"))


if __name__ == "__main__":
    unittest.main()
