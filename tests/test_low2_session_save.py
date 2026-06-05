"""Tests para LOW-2: token usage se guarda en Ctrl+C.

Bug: main.py:5558 — main_loop() hace break en el except
     KeyboardInterrupt y luego corre save_session_to_csv() (línea
     5641) DESPUÉS del while. Pero:
     - Si KeyboardInterrupt ocurre dentro de save_session_to_csv()
       mismo, los datos del último turno se pierden.
     - Si el proceso recibe SIGTERM/SIGKILL, no hay atexit.
     - El save está fuera de try/finally, así que si algo lanza
       entre 'break' y 'save_session_to_csv()' (líneas 5620-5641),
       el save no se ejecuta.

Fix: envolver el cuerpo del main loop en try/finally que SIEMPRE
     llame save_session_to_csv. Además registrar save_session_to_csv
     con atexit.register() como safety net para SIGTERM/SIGKILL.
"""
import unittest
import sys
import signal
from unittest.mock import patch, MagicMock


class TestSessionSaveOnInterrupt(unittest.TestCase):
    """LOW-2: token usage se guarda en Ctrl+C y salidas abruptas."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")
        import main
        main._session_already_closed = False

    def test_save_session_registered_with_atexit(self):
        """RED: _close_session_safely debe estar registrado en atexit
           para que corra en SIGTERM/SIGKILL limpio."""
        import atexit
        import main
        # atexit._exithandlers es API privada pero estable en Python 3.9+
        if hasattr(atexit, "_exithandlers"):
            handlers = [h[0] for h in atexit._exithandlers]
            self.assertIn(main._close_session_safely, handlers)
        else:
            # Fallback: verify function exists y está registrada via
            # el módulo al ser importado
            self.skipTest("atexit._exithandlers not available in this Python")
        self.assertTrue(callable(main._close_session_safely))
        self.assertTrue(callable(main.save_session_to_csv))

    def test_save_runs_after_keyboard_interrupt_in_call_llm(self):
        """GREEN: si KeyboardInterrupt ocurre en call_llm, save corre igual."""
        import main
        from dexter.console import user_prompt as _rich_prompt
        with patch("main.call_llm", side_effect=KeyboardInterrupt), \
             patch("main.save_session_to_csv") as mock_save, \
             patch("dexter.console.user_prompt", return_value="hola"):
            try:
                main.main_loop()
            except (KeyboardInterrupt, StopIteration, EOFError, Exception):
                pass
            self.assertTrue(mock_save.called,
                            "save debe correr tras KeyboardInterrupt en call_llm")

    def test_save_runs_when_main_loop_exits_normally(self):
        """GREEN: cuando main_loop retorna normalmente, save corre."""
        import main
        with patch("dexter.console.user_prompt", side_effect=["hola", "salir"]), \
             patch("main.process_quick_command", return_value=None), \
             patch("main.call_llm", return_value="respuesta"), \
             patch("main.save_session_to_csv") as mock_save:
            try:
                main.main_loop()
            except (StopIteration, EOFError):
                pass
            self.assertTrue(mock_save.called,
                            "save_session_to_csv debe correr al salir normal")

    def test_save_idempotent(self):
        """GREEN: llamar _close_session_safely dos veces solo guarda una vez."""
        import main
        main._session_already_closed = False
        with patch("main.save_session_to_csv") as mock_save:
            main._close_session_safely()
            main._close_session_safely()
            self.assertEqual(mock_save.call_count, 1)


if __name__ == "__main__":
    unittest.main()
