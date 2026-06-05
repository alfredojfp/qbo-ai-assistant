"""Tests para R-8: dexter.core.session_state.SessionState.

main.py:132 tiene un global `session_state = {...}` con 56+ usos.
R-8 wrappea este patrón en una clase tipada para callers nuevos.

API:
  SessionState()           # default state con campos tipados
  .chart_of_accounts       # dict (Chart)
  .language                # str ('es' | 'en')
  .input_tokens, .output_tokens, .total_cost
  .start_time              # datetime
  .operations              # dict[str, int] (contadores por tipo)
  .last_search_results     # dict
  .saved_reports           # dict
  .current_company         # str|None
  .to_dict() / .reset() / .get(key) / .set(key, value)

Backward compat: main.py NO se modifica. La clase es NUEVA.
"""
import unittest
from datetime import datetime


class TestSessionStateDefaults(unittest.TestCase):
    """R-8: defaults coinciden con main.py:132-150."""

    def setUp(self):
        from dexter.core.session_state import SessionState
        self.SessionState = SessionState

    def test_default_language_is_es(self):
        s = self.SessionState()
        self.assertEqual(s.language, "es")

    def test_default_chart_empty_dict(self):
        s = self.SessionState()
        self.assertEqual(s.chart_of_accounts, {})

    def test_default_tokens_zero(self):
        s = self.SessionState()
        self.assertEqual(s.input_tokens, 0)
        self.assertEqual(s.output_tokens, 0)
        self.assertEqual(s.total_cost, 0.0)

    def test_default_operations_empty_dict(self):
        s = self.SessionState()
        self.assertEqual(s.operations, {})

    def test_default_start_time_is_datetime(self):
        s = self.SessionState()
        self.assertIsInstance(s.start_time, datetime)

    def test_default_current_company_none(self):
        s = self.SessionState()
        self.assertIsNone(s.current_company)

    def test_default_last_search_results_empty(self):
        s = self.SessionState()
        self.assertEqual(s.last_search_results, {})

    def test_default_saved_reports_empty(self):
        s = self.SessionState()
        self.assertEqual(s.saved_reports, {})


class TestSessionStateMutations(unittest.TestCase):
    """R-8: setters mutan state correctamente."""

    def setUp(self):
        from dexter.core.session_state import SessionState
        self.s = self.SessionState = SessionState()

    def test_set_language(self):
        self.s.language = "en"
        self.assertEqual(self.s.language, "en")

    def test_add_tokens(self):
        self.s.input_tokens += 100
        self.s.output_tokens += 50
        self.assertEqual(self.s.input_tokens, 100)
        self.assertEqual(self.s.output_tokens, 50)

    def test_increment_operation(self):
        self.s.operations["searches"] = self.s.operations.get("searches", 0) + 1
        self.s.operations["searches"] += 1
        self.assertEqual(self.s.operations["searches"], 2)

    def test_set_chart(self):
        self.s.chart_of_accounts = {"1": {"name": "Checking"}}
        self.assertEqual(len(self.s.chart_of_accounts), 1)

    def test_set_current_company(self):
        self.s.current_company = "Sandbox Company_US_1"
        self.assertEqual(self.s.current_company, "Sandbox Company_US_1")


class TestSessionStateDictAPI(unittest.TestCase):
    """R-8: to_dict() y get/set compatibles con patrón dict."""

    def test_to_dict_returns_all_fields(self):
        from dexter.core.session_state import SessionState
        s = SessionState()
        s.input_tokens = 50
        s.operations["searches"] = 3
        d = s.to_dict()
        self.assertEqual(d["input_tokens"], 50)
        self.assertEqual(d["output_tokens"], 0)
        self.assertEqual(d["language"], "es")
        self.assertEqual(d["operations"]["searches"], 3)
        self.assertIn("start_time", d)
        self.assertIn("chart_of_accounts", d)
        self.assertIn("last_search_results", d)
        self.assertIn("saved_reports", d)
        self.assertIn("current_company", d)
        self.assertIn("total_cost", d)

    def test_get_with_default(self):
        from dexter.core.session_state import SessionState
        s = SessionState()
        self.assertEqual(s.get("language", "es"), "es")
        self.assertEqual(s.get("input_tokens", 0), 0)
        self.assertEqual(s.get("nonexistent_key", "fallback"), "fallback")
        self.assertIsNone(s.get("nonexistent_key"))

    def test_set_key_value(self):
        from dexter.core.session_state import SessionState
        s = SessionState()
        s.set("language", "en")
        s.set("input_tokens", 100)
        self.assertEqual(s.language, "en")
        self.assertEqual(s.input_tokens, 100)

    def test_reset_returns_to_defaults(self):
        from dexter.core.session_state import SessionState
        s = SessionState()
        s.input_tokens = 500
        s.language = "en"
        s.operations["searches"] = 5
        s.reset()
        self.assertEqual(s.input_tokens, 0)
        self.assertEqual(s.language, "es")
        self.assertEqual(s.operations, {})


class TestSessionStateExport(unittest.TestCase):
    """R-8: importable desde dexter.core.session_state."""

    def test_importable(self):
        from dexter.core.session_state import SessionState
        self.assertTrue(callable(SessionState))


if __name__ == "__main__":
    unittest.main()
