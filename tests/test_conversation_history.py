"""Tests para R-5: dexter.core.conversation.ConversationHistory.

CRIT-2 ya usa deque(maxlen=N) en main.py:154. R-5 lo wrappea en una
clase con API limpia (append, clear, recent, to_list, __len__, __iter__)
que:
  - Encapsula el deque para que callers no manipulen el storage directo.
  - Permite re-uso fuera de main.py (e.g., tests, otros módulos).
  - Mantiene bounded behavior (no OOM en sesiones largas).

Backward compat: main.py NO se modifica. La clase es NUEVA en
dexter.core.conversation. El global conversation_history de main.py
sigue funcionando idéntico.
"""
import unittest


class TestConversationHistory(unittest.TestCase):
    """R-5: API limpia sobre deque(maxlen=N)."""

    def setUp(self):
        from dexter.core.conversation import ConversationHistory
        self.ConversationHistory = ConversationHistory

    def test_default_maxlen_is_200(self):
        """Default maxlen=200 (igual que main.py:153)."""
        h = self.ConversationHistory()
        self.assertEqual(h.maxlen, 200)

    def test_custom_maxlen(self):
        """Custom maxlen se respeta."""
        h = self.ConversationHistory(maxlen=5)
        self.assertEqual(h.maxlen, 5)

    def test_append_and_len(self):
        """append agrega mensaje, len() retorna count."""
        h = self.ConversationHistory()
        h.append({"role": "user", "content": "hola"})
        h.append({"role": "assistant", "content": "buenas"})
        self.assertEqual(len(h), 2)

    def test_bounded_maxlen_drops_oldest(self):
        """Cuando se excede maxlen, los más viejos se descartan."""
        h = self.ConversationHistory(maxlen=3)
        h.append("a")
        h.append("b")
        h.append("c")
        h.append("d")
        self.assertEqual(len(h), 3)
        self.assertEqual(h.to_list(), ["b", "c", "d"])

    def test_to_list_returns_list(self):
        """to_list() retorna copia como list."""
        h = self.ConversationHistory()
        h.append("a")
        h.append("b")
        lst = h.to_list()
        self.assertIsInstance(lst, list)
        self.assertEqual(lst, ["a", "b"])

    def test_recent_n_returns_last_n(self):
        """recent(n) retorna los últimos n mensajes."""
        h = self.ConversationHistory()
        for i in range(10):
            h.append(f"msg-{i}")
        self.assertEqual(h.recent(3), ["msg-7", "msg-8", "msg-9"])
        self.assertEqual(h.recent(1), ["msg-9"])
        self.assertEqual(h.recent(100), [f"msg-{i}" for i in range(10)])

    def test_recent_n_zero(self):
        """recent(0) retorna []."""
        h = self.ConversationHistory()
        h.append("a")
        self.assertEqual(h.recent(0), [])

    def test_recent_negative_raises(self):
        """recent(n<0) raise ValueError."""
        h = self.ConversationHistory()
        with self.assertRaises(ValueError):
            h.recent(-1)

    def test_clear_empties(self):
        """clear() vacía el historial."""
        h = self.ConversationHistory()
        h.append("a")
        h.append("b")
        h.clear()
        self.assertEqual(len(h), 0)
        self.assertEqual(h.to_list(), [])

    def test_iter_yields_messages(self):
        """__iter__ permite for msg in history."""
        h = self.ConversationHistory()
        h.append("a")
        h.append("b")
        result = list(h)
        self.assertEqual(result, ["a", "b"])

    def test_getitem_indexing(self):
        """h[0] retorna primer mensaje (oldest)."""
        h = self.ConversationHistory()
        h.append("a")
        h.append("b")
        h.append("c")
        self.assertEqual(h[0], "a")
        self.assertEqual(h[-1], "c")
        self.assertEqual(h[1], "b")

    def test_repr_does_not_leak_contents(self):
        """__repr__ muestra count + maxlen, NO mensajes (privacidad)."""
        h = self.ConversationHistory(maxlen=50)
        h.append({"role": "user", "content": "secret"})
        r = repr(h)
        self.assertIn("ConversationHistory", r)
        self.assertIn("len=1", r)
        self.assertIn("maxlen=50", r)
        self.assertNotIn("secret", r)

    def test_no_oom_on_million_appends(self):
        """Appending 1M mensajes NO causa OOM (bounded)."""
        h = self.ConversationHistory(maxlen=100)
        for i in range(1_000_000):
            h.append(i)
        self.assertEqual(len(h), 100)
        self.assertEqual(h.to_list()[0], 999_900)
        self.assertEqual(h.to_list()[-1], 999_999)


class TestConversationHistoryExports(unittest.TestCase):
    """R-5: la clase es importable desde dexter.core.conversation."""

    def test_importable(self):
        from dexter.core.conversation import ConversationHistory
        self.assertTrue(callable(ConversationHistory))


if __name__ == "__main__":
    unittest.main()
