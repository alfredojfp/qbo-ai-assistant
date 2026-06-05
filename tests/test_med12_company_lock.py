"""Tests para MED-12: race condition en company switch mid-tool-call.

Bug: main.py:4706 — tool_gestionar_empresas modifica globales
     (QB_REALM_ID, QB_ACCESS_TOKEN, QB_BASE_URL, CURRENT_COMPANY)
     SIN lock. Si el usuario pide cambiar empresa mientras un tool
     largo está en flight (e.g., procesar_csv_banco con 5000
     transacciones), el tool completa con tokens/realm de la NUEVA
     empresa, pero el prompt original era para la VIEJA. Resultado:
     la factura/depósito se crea en la empresa equivocada sin error.

Fix: módulo-level _company_lock = threading.RLock() que:
     - El dispatcher adquiere durante tool execution (entry/exit)
     - tool_gestionar_empresas('cambiar') adquiere antes de mutar
     - Si el lock no está disponible, retorna error claro
       "No se puede cambiar de empresa mientras un tool está en
        ejecución; espera a que termine o cancela con Ctrl+C."

Approach TDD: en tests no podemos probar concurrencia real fácilmente,
pero podemos:
1. Verificar que _company_lock existe
2. Verificar que tool_gestionar_empresas('cambiar') lo adquiere
3. Verificar que si el lock está sostenido, retorna error
"""
import unittest
import threading
from unittest.mock import patch, MagicMock


class TestCompanySwitchLock(unittest.TestCase):
    """MED-12: tool_gestionar_empresas usa lock para evitar races."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")
        import main
        self._lock = main._company_lock

    def tearDown(self):
        import main
        try:
            if main._company_lock.acquire(blocking=False):
                main._company_lock.release()
        except Exception:
            pass

    def test_module_has_company_lock(self):
        """RED: main debe exportar _company_lock (Lock o RLock)."""
        import main
        self.assertTrue(hasattr(main, "_company_lock"))
        self.assertIsInstance(main._company_lock, type(threading.Lock()))

    def test_cambiar_empresa_succeeds_when_lock_free(self):
        """GREEN: con lock libre, el switch funciona normal."""
        import main
        with patch("main.list_local_companies", return_value=[
            {"name": "Empresa A", "realm_id": "111", "has_tokens": True},
        ]), \
             patch("main.get_company_meta", return_value={
                 "access_token": "tk", "refresh_token": "rt"
             }), \
             patch("main.reset_session_state"), \
             patch("main.save_company_context"), \
             patch("main.load_company_context", return_value={}), \
             patch("main.save_company_selection"), \
             patch("main.load_chart_of_accounts", return_value={}):
            result = main.tool_gestionar_empresas("cambiar", nombre="Empresa A")
        self.assertTrue(result["success"])

    def test_cambiar_empresa_returns_error_if_lock_busy(self):
        """GREEN: si el lock está sostenido (otro tool en flight),
           cambiar retorna error en lugar de mutar state."""
        import main
        acquired = main._company_lock.acquire(blocking=False)
        self.assertTrue(acquired, "Lock debería estar libre en setUp")
        try:
            with patch("main.list_local_companies", return_value=[
                {"name": "Empresa B", "realm_id": "222", "has_tokens": True},
            ]):
                result = main.tool_gestionar_empresas("cambiar", nombre="Empresa B")
            self.assertFalse(result["success"])
            self.assertTrue(result.get("lock_busy"))
            self.assertIn("ejecución", result.get("error", "").lower())
        finally:
            main._company_lock.release()

    def test_cambiar_empresa_error_from_other_thread(self):
        """GREEN: si OTRO thread sostiene el lock, retorna error."""
        import main
        held = threading.Event()
        release = threading.Event()
        container = {}

        def hold_lock():
            main._company_lock.acquire()
            held.set()
            release.wait(timeout=5)
            try:
                main._company_lock.release()
            except Exception:
                pass
            container["done"] = True

        t = threading.Thread(target=hold_lock, daemon=True)
        t.start()
        if not held.wait(timeout=2):
            self.skipTest("Otro thread no adquirió el lock (timing)")
        try:
            with patch("main.list_local_companies", return_value=[
                {"name": "Empresa B", "realm_id": "222", "has_tokens": True},
            ]):
                result = main.tool_gestionar_empresas("cambiar", nombre="Empresa B")
            self.assertFalse(result["success"])
            self.assertTrue(result.get("lock_busy"))
        finally:
            release.set()
            t.join(timeout=5)
            if not container.get("done"):
                self.skipTest("Thread no terminó limpio (timing)")

    def test_lock_held_during_cambiar_body(self):
        """GREEN: durante el body de cambiar, el lock está sostenido
        (verificable: otro thread no puede adquirirlo)."""
        import main
        state = {"held": None}
        acquire_ok = threading.Event()

        def check_from_thread():
            ok = main._company_lock.acquire(blocking=False)
            state["held"] = not ok
            if ok:
                try:
                    main._company_lock.release()
                except Exception:
                    pass

        def spy_load_chart(force_refresh=False):
            t = threading.Thread(target=check_from_thread)
            t.start()
            t.join(timeout=2)
            return {}

        with patch("main.list_local_companies", return_value=[
            {"name": "Empresa A", "realm_id": "111", "has_tokens": True},
        ]), \
             patch("main.get_company_meta", return_value={
                 "access_token": "tk", "refresh_token": "rt"
             }), \
             patch("main.reset_session_state"), \
             patch("main.save_company_context"), \
             patch("main.load_company_context", return_value={}), \
             patch("main.save_company_selection"), \
             patch("main.load_chart_of_accounts", side_effect=spy_load_chart):
            main.tool_gestionar_empresas("cambiar", nombre="Empresa A")
        self.assertTrue(state["held"],
                        "Lock debería estar sostenido durante el switch")


if __name__ == "__main__":
    unittest.main()
