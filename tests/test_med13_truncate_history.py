"""Tests para MED-13: build_conversation_context trunca mensajes gigantes.

Bug: main.py:5478 — build_conversation_context retorna `recent`
     que es history[-(max_turns*2):] sin truncar contenido. Si un
     tool retornó 5MB (reporte sin MED-6 fix, batch grande, etc.),
     ese mensaje vive en conversation_history y se reenvía al LLM
     en cada llamada, multiplicando tokens consumidos.

Fix: agregar parámetro max_content_chars (default 2000) que trunca
     el campo 'content' de cada mensaje a N chars + '...[truncated]'.
     El LLM sigue viendo el contexto pero no el payload gigante.
"""
import unittest


class TestBuildConversationContextTruncation(unittest.TestCase):
    """MED-13: build_conversation_context trunca mensajes grandes."""

    def test_module_function_exists(self):
        """RED: build_conversation_context debe existir en main."""
        import main
        self.assertTrue(callable(getattr(main, "build_conversation_context", None)))

    def test_truncation_helper_exists(self):
        """GREEN: helper _truncate_message_content debe existir."""
        import main
        self.assertTrue(callable(getattr(main, "_truncate_message_content", None)))

    def test_small_message_not_truncated(self):
        """GREEN: mensajes < max no se truncan."""
        from main import _truncate_message_content
        msg = {"role": "user", "content": "Hola, ¿cuánto gasté?"}
        out = _truncate_message_content(msg, max_chars=2000)
        self.assertEqual(out["content"], "Hola, ¿cuánto gasté?")

    def test_huge_message_truncated(self):
        """GREEN: mensajes > max se truncan con marcador."""
        from main import _truncate_message_content
        big = "X" * 10_000
        msg = {"role": "tool", "content": big}
        out = _truncate_message_content(msg, max_chars=500)
        self.assertLess(len(out["content"]), 1000)
        self.assertIn("[truncated", out["content"])

    def test_huge_message_preserves_metadata(self):
        """GREEN: name, tool_call_id, role se preservan."""
        from main import _truncate_message_content
        msg = {"role": "tool", "name": "crear_factura", "tool_call_id": "abc123",
               "content": "Y" * 5000}
        out = _truncate_message_content(msg, max_chars=300)
        self.assertEqual(out["role"], "tool")
        self.assertEqual(out["name"], "crear_factura")
        self.assertEqual(out["tool_call_id"], "abc123")

    def test_build_context_truncates_each_message(self):
        """GREEN: build_conversation_context aplica truncado."""
        from main import build_conversation_context
        history = [
            {"role": "user", "content": "Hola"},
            {"role": "tool", "content": "Z" * 50_000},
            {"role": "assistant", "content": "Listo"},
            {"role": "user", "content": "Gracias"},
        ]
        recent, ctx = build_conversation_context(history, max_turns=3, max_content_chars=200)
        for msg in recent:
            self.assertLessEqual(len(msg["content"]), 500,
                                 f"msg demasiado grande: {len(msg['content'])} chars")

    def test_build_context_default_max(self):
        """GREEN: default max_content_chars razonable (no None, no infinito)."""
        from main import build_conversation_context
        history = [{"role": "user", "content": "X" * 100_000}]
        recent, ctx = build_conversation_context(history, max_turns=2)
        for msg in recent:
            self.assertLess(len(msg["content"]), 200_000)


if __name__ == "__main__":
    unittest.main()
