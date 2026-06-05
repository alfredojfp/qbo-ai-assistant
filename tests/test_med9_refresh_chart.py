"""Tests para MED-9: cambiar empresa debe forzar refresh del Chart of Accounts.

Bug: main.py:4614 — Después de cambiar empresa, se carga el chart desde
     COMPANY_CONTEXT (cacheado al último switch). Si la nueva empresa
     agregó cuentas en QBO desde entonces, no se cargan. El usuario
     ve cuentas stale.

Fix: después de cargar el context, llamar load_chart_of_accounts(force_refresh=True)
     para traer el chart fresco desde QBO. Bypass del cache de 24h.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestCambiarEmpresaRefreshChart(unittest.TestCase):
    """MED-9: cambiar empresa debe forzar refresh del chart."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_cambiar_calls_load_chart_force_refresh(self):
        """RED: después de cambiar, load_chart_of_accounts(force_refresh=True) se llama."""
        from main import tool_gestionar_empresas

        target = {"name": "Otra", "realm_id": "999", "has_tokens": True}

        with patch("main.list_local_companies", return_value=[target]), \
             patch("main.reset_session_state"), \
             patch("main.save_company_context"), \
             patch("main.get_company_meta", return_value={
                 "access_token": "tok", "refresh_token": "ref"
             }), \
             patch("main.save_company_selection"), \
             patch("main.load_company_context", return_value={}), \
             patch("main.load_chart_of_accounts", return_value={"acc1": {"id": "1"}}) as mock_load, \
             patch("main.CURRENT_COMPANY", None), \
             patch("main.QB_ACCESS_TOKEN", "old"), \
             patch("main.QB_REFRESH_TOKEN", "old"):
            result = tool_gestionar_empresas("cambiar", nombre="Otra")

        mock_load.assert_called_once()
        self.assertTrue(mock_load.call_args.kwargs.get("force_refresh"),
                        "load_chart_of_accounts debe llamarse con force_refresh=True")
        self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()
