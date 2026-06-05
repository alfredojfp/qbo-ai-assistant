"""Tests para R-10: dexter.testing.llm_mock.DeepseekMock.

Mock realista del LLM deepseek para tests de conversación. Los mocks
actuales en los tests (return_value=...) son demasiado simples y no
detectan bugs relacionados a peculiaridades del LLM real:
  - JSON malformado en tool_call.arguments
  - Tool calls a funciones inexistentes (alucinaciones)
  - Timeouts intermitentes
  - Rate limits (429)
  - Respuestas con contenido vacío
  - Truncamiento de tool calls a mitad

R-10 fix: helper DeepseekMock que simula deepseek via OpenRouter API,
con API para tests de configurar respuestas, errores, y validar que
call_llm() maneja correctamente cada quirk.

Diseño: DeepseekMock es un callable que se inyecta via patch en lugar
de requests.post. Retorna un objeto con status_code + .json() + .text
(mismo shape que requests.Response).
"""
import json
import unittest
from unittest.mock import patch, MagicMock


class TestDeepseekMockBasics(unittest.TestCase):
    """R-10.1: DeepseekMock basics."""

    def test_mock_importable(self):
        from dexter.testing.llm_mock import DeepseekMock
        self.assertTrue(callable(DeepseekMock))

    def test_default_response_is_text(self):
        """Mock default retorna text content sin tool calls."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        response = m(messages=[{"role": "user", "content": "hola"}])
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["choices"][0]["message"]["role"], "assistant")
        self.assertIn("content", body["choices"][0]["message"])

    def test_set_text_response(self):
        """set_text() configura el content a retornar."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_text("Hola, ¿en qué te ayudo?")
        response = m(messages=[])
        self.assertEqual(
            response.json()["choices"][0]["message"]["content"],
            "Hola, ¿en qué te ayudo?",
        )


class TestDeepseekMockToolCalls(unittest.TestCase):
    """R-10.2: DeepseekMock simula tool calls correctamente."""

    def test_add_tool_call(self):
        """add_tool_call() configura el tool call a retornar."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.add_tool_call("tool_buscar_cliente", {"nombre": "AlfredoTPM"})
        response = m(messages=[])
        msg = response.json()["choices"][0]["message"]
        self.assertIn("tool_calls", msg)
        self.assertEqual(len(msg["tool_calls"]), 1)
        self.assertEqual(msg["tool_calls"][0]["function"]["name"], "tool_buscar_cliente")
        args = json.loads(msg["tool_calls"][0]["function"]["arguments"])
        self.assertEqual(args["nombre"], "AlfredoTPM")

    def test_multiple_tool_calls(self):
        """add_tool_call() múltiples veces retorna N tool calls."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.add_tool_call("tool_a", {})
        m.add_tool_call("tool_b", {"x": 1})
        m.add_tool_call("tool_c", {"y": 2})
        response = m(messages=[])
        msg = response.json()["choices"][0]["message"]
        self.assertEqual(len(msg["tool_calls"]), 3)


class TestDeepseekMockQuirks(unittest.TestCase):
    """R-10.3: DeepseekMock simula peculiaridades del LLM real."""

    def test_malformed_json_arguments(self):
        """enable_malformed_json() hace que arguments sea JSON inválido."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.add_tool_call("tool_x", {"y": 1})
        m.enable_malformed_json()
        response = m(messages=[])
        msg = response.json()["choices"][0]["message"]
        args_str = msg["tool_calls"][0]["function"]["arguments"]
        with self.assertRaises(json.JSONDecodeError):
            json.loads(args_str)

    def test_hallucinated_function_name(self):
        """add_hallucinated_tool_call() simula tool call a función inexistente."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.add_hallucinated_tool_call("tool_que_no_existe", {})
        response = m(messages=[])
        msg = response.json()["choices"][0]["message"]
        self.assertEqual(
            msg["tool_calls"][0]["function"]["name"],
            "tool_que_no_existe",
        )

    def test_rate_limit_429(self):
        """enable_rate_limit() hace que retorne 429 la próxima llamada."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_text("hola")
        m.enable_rate_limit()
        response = m(messages=[])
        self.assertEqual(response.status_code, 429)
        self.assertIn("rate limit", response.text.lower())

    def test_timeout_raises(self):
        """enable_timeout() hace que retorne response con status 408 (timeout)."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_text("hola")
        m.enable_timeout()
        response = m(messages=[])
        self.assertEqual(response.status_code, 408)
        self.assertIn("timeout", response.text.lower())

    def test_empty_content(self):
        """set_text('') produce mensaje con content vacío."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_text("")
        response = m(messages=[])
        self.assertEqual(response.json()["choices"][0]["message"]["content"], "")

    def test_call_count(self):
        """call_count incrementa cada invocación."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        self.assertEqual(m.call_count, 0)
        m(messages=[])
        m(messages=[])
        m(messages=[])
        self.assertEqual(m.call_count, 3)

    def test_captured_messages(self):
        """captured_messages guarda los mensajes enviados."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        msgs = [{"role": "user", "content": "test"}]
        m(messages=msgs)
        self.assertEqual(m.captured_messages, [msgs])


class TestDeepseekMockScripted(unittest.TestCase):
    """R-10.4: DeepseekMock con respuestas scripted por call #."""

    def test_responses_per_call(self):
        """set_responses() configura respuestas para cada llamada."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_responses([
            {"text": "primera respuesta"},
            {"text": "segunda respuesta"},
            {"text": "tercera respuesta"},
        ])
        r1 = m(messages=[])
        r2 = m(messages=[])
        r3 = m(messages=[])
        self.assertEqual(r1.json()["choices"][0]["message"]["content"], "primera respuesta")
        self.assertEqual(r2.json()["choices"][0]["message"]["content"], "segunda respuesta")
        self.assertEqual(r3.json()["choices"][0]["message"]["content"], "tercera respuesta")

    def test_tool_call_then_text_response(self):
        """Script: 1er call tool_call, 2do call text response."""
        from dexter.testing.llm_mock import DeepseekMock
        m = DeepseekMock()
        m.set_responses([
            {"tool_call": ("tool_x", {"a": 1})},
            {"text": "Listo, terminé."},
        ])
        r1 = m(messages=[])
        msg1 = r1.json()["choices"][0]["message"]
        self.assertIn("tool_calls", msg1)

        r2 = m(messages=[])
        msg2 = r2.json()["choices"][0]["message"]
        self.assertEqual(msg2["content"], "Listo, terminé.")


if __name__ == "__main__":
    unittest.main()
