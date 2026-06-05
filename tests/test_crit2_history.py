"""Tests para CRIT-2: conversation_history debe tener tamaño máximo.

Bug: main.py:141 — `conversation_history = []` crece sin límite.
      → sesión larga (cientos de turnos) → OOM al construir payload LLM.

Fix: reemplazar `list` por `collections.deque(maxlen=200)` (auto-truncado al append).
"""
import unittest
from collections import deque


class TestConversationHistoryBounded(unittest.TestCase):
    """CRIT-2: conversation_history no debe crecer más allá de MAX_HISTORY."""

    def test_conversation_history_is_bounded_deque(self):
        """RED: conversation_history debe ser un deque con maxlen."""
        import main
        # Re-evaluar el import por si la implementación cachea el módulo
        from collections import deque
        # Si es un list, falla. Si es un deque(maxlen=N), pasa.
        self.assertIsInstance(
            main.conversation_history, deque,
            f"conversation_history debe ser deque, no list. Got: {type(main.conversation_history)}"
        )
        self.assertIsNotNone(
            main.conversation_history.maxlen,
            f"deque debe tener maxlen configurado. Got maxlen: {main.conversation_history.maxlen}"
        )
        self.assertEqual(
            main.conversation_history.maxlen, 200,
            f"maxlen debe ser 200 (suficiente para ~50 turnos). Got: {main.conversation_history.maxlen}"
        )

    def test_append_beyond_maxlen_drops_oldest(self):
        """RED: append 250 mensajes → solo los últimos 200 deben quedar."""
        import main
        # Limpiar y poblar
        main.conversation_history.clear()
        for i in range(250):
            main.conversation_history.append({"role": "user", "content": f"msg-{i}"})

        self.assertEqual(
            len(main.conversation_history), 200,
            f"history debe estar cap a 200, no 250. Got: {len(main.conversation_history)}"
        )
        # El más reciente (msg-249) debe estar presente
        self.assertEqual(
            main.conversation_history[-1]["content"], "msg-249",
            f"el mensaje más reciente debe preservarse. Got: {main.conversation_history[-1]['content']}"
        )
        # El más antiguo (msg-0) debe haberse caído
        self.assertNotEqual(
            main.conversation_history[0]["content"], "msg-0",
            f"los primeros 50 deben haberse caído. Got primero: {main.conversation_history[0]['content']}"
        )
        # El primer mensaje presente debe ser msg-50
        self.assertEqual(
            main.conversation_history[0]["content"], "msg-50",
            f"el primer mensaje presente debe ser msg-50. Got: {main.conversation_history[0]['content']}"
        )

    def test_slice_in_call_llm_works_with_deque(self):
        """RED: el patrón de slicing `list(history)[-N:]` debe seguir funcionando con deque."""
        import main
        main.conversation_history.clear()
        for i in range(100):
            main.conversation_history.append({"role": "user", "content": f"msg-{i}"})

        # call_llm usa esto: list(conversation_history)[-(max_iterations*4+10):]
        sliced = list(main.conversation_history)[-(5 * 4 + 10):]
        self.assertEqual(
            len(sliced), min(30, len(main.conversation_history)),
            f"slicing debe funcionar. Got {len(sliced)} items"
        )
        # El último elemento del slice debe ser el más reciente
        self.assertEqual(
            sliced[-1]["content"], "msg-99",
            f"slicing debe preservar el orden. Got: {sliced[-1]['content']}"
        )


if __name__ == "__main__":
    unittest.main()
