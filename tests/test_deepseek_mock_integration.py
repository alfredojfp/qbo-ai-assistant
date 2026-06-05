"""Integration tests: DeepseekMock + main.call_llm end-to-end.

Demuestra que DeepseekMock se integra correctamente con la función
call_llm de main.py:
  1. Patch requests.post con side_effect=mock
  2. call_llm(...) procesa el response y maneja tool calls
  3. call_llm maneja errores (rate limit, timeout, malformed JSON,
     hallucinated tool calls)
"""
import os
import unittest
from unittest.mock import patch, MagicMock


class TestCallLlmWithDeepseekMock(unittest.TestCase):
    """R-10.5: DeepseekMock se integra con call_llm."""

    def setUp(self):
        os.environ.setdefault("QB_ACCESS_TOKEN", "test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")
        os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

    def _fake_session_state(self):
        return {
            "language": "es",
            "chart_of_accounts": {},
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost": 0.0,
            "operations": {},
            "last_search_results": {},
            "saved_reports": {},
            "start_time": __import__("datetime").datetime.now(),
        }

    def test_text_response_flow(self):
        """Mock con text content → call_llm retorna el content."""
        from dexter.testing.llm_mock import DeepseekMock
        mock = DeepseekMock()
        mock.set_text("Hola, ¿en qué te ayudo?")

        import main
        with patch("main.requests.post", side_effect=mock), \
             patch("main.session_state", self._fake_session_state()), \
             patch("main.conversation_history", __import__("collections").deque(maxlen=200)):
            result = main.call_llm("hola", tools=[])
            self.assertIn("Hola", result)
            self.assertEqual(mock.call_count, 1)

    def test_tool_call_response_flow(self):
        """Mock con tool_call → call_llm ejecuta tool y retorna result."""
        from dexter.testing.llm_mock import DeepseekMock
        mock = DeepseekMock()
        mock.set_responses([
            {"tool_call": ("tool_buscar_cliente", {"nombre": "Test"})},
            {"text": "No encontré clientes."},
        ])

        import main
        with patch("main.requests.post", side_effect=mock), \
             patch("main.session_state", self._fake_session_state()), \
             patch("main.conversation_history", __import__("collections").deque(maxlen=200)):
            result = main.call_llm("buscar cliente Test", tools=[])
            self.assertIn("No encontré", result)
            self.assertEqual(mock.call_count, 2)

    def test_rate_limit_handled(self):
        """Mock con 429 → call_llm retorna mensaje de error gracefully."""
        from dexter.testing.llm_mock import DeepseekMock
        mock = DeepseekMock()
        mock.set_text("nunca debería llegar")
        mock.enable_rate_limit()

        import main
        with patch("main.requests.post", side_effect=mock), \
             patch("main.session_state", self._fake_session_state()), \
             patch("main.conversation_history", __import__("collections").deque(maxlen=200)):
            result = main.call_llm("test", tools=[])
            self.assertIn("Error", result)
            self.assertIn("429", result)

    def test_timeout_handled(self):
        """Mock con 408 → call_llm retorna mensaje de error gracefully."""
        from dexter.testing.llm_mock import DeepseekMock
        mock = DeepseekMock()
        mock.set_text("nunca")
        mock.enable_timeout()

        import main
        with patch("main.requests.post", side_effect=mock), \
             patch("main.session_state", self._fake_session_state()), \
             patch("main.conversation_history", __import__("collections").deque(maxlen=200)):
            result = main.call_llm("test", tools=[])
            self.assertIn("Error", result)
            self.assertIn("408", result)

    def test_hallucinated_tool_call_handled(self):
        """Mock con tool_call a fn inexistente → call_llm maneja gracefully."""
        from dexter.testing.llm_mock import DeepseekMock
        mock = DeepseekMock()
        mock.set_responses([
            {"tool_call": ("tool_que_no_existe_en_main", {})},
            {"text": "Lo siento, hubo un error."},
        ])

        import main
        with patch("main.requests.post", side_effect=mock), \
             patch("main.session_state", self._fake_session_state()), \
             patch("main.conversation_history", __import__("collections").deque(maxlen=200)):
            try:
                result = main.call_llm("test", tools=[])
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"call_llm raised: {type(e).__name__}: {e}")


if __name__ == "__main__":
    unittest.main()
