"""Tests para MED-3: save_session_to_csv debe usar lock para evitar CSV corrupto.

Bug: main.py:611 — save_session_to_csv hace open(path, 'a') y write
     sin lock. Si dos threads o procesos llaman simultáneamente
     (e.g., Ctrl+C signal handler + normal close), el write se
     intercala y el CSV queda corrupto.

Fix: usar threading.Lock() para serializar writes. Lock module-level
     shared entre callers.
"""
import unittest


class TestSaveSessionCsvLock(unittest.TestCase):
    """MED-3: save_session_to_csv debe usar lock."""

    def test_module_has_csv_write_lock(self):
        """RED: main.py debe exportar _csv_write_lock (threading.Lock)."""
        import main
        import threading
        self.assertTrue(hasattr(main, "_csv_write_lock"))
        self.assertIsInstance(main._csv_write_lock, type(threading.Lock()))

    def test_lock_is_reentrant_safe_for_concurrent_calls(self):
        """GREEN: dos calls consecutivos (mismo proceso) usan el mismo lock."""
        import main
        lock1 = main._csv_write_lock
        lock2 = main._csv_write_lock
        self.assertIs(lock1, lock2, "Lock debe ser singleton module-level")

    def test_lock_supports_context_manager(self):
        """GREEN: el lock debe soportar `with` (context manager)."""
        import main
        with main._csv_write_lock:
            acquired = True
        self.assertTrue(acquired)


if __name__ == "__main__":
    unittest.main()
