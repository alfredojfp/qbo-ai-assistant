"""Tests para UX-1: cuando el refresh token de QBO expira, ofrecer
re-autenticar vía OAuth flow en vez de salir silenciosamente.

Bug: main.py:5982-5993 — el bloque de verificación de QBO al
inicio hace `exit(1)` si `refresh_qb_token()` falla con
`invalid_grant` (refresh token expiró). El usuario ve un mensaje
críptico y la app muere sin ofrecer solución.

Fix: extraer la verificación a `_verify_qbo_connection_or_offer_reauth()`
que:
  1. Llama `qbo_query()` para verificar.
  2. Si falla, intenta `refresh_qb_token()`.
  3. Si refresh falla (cualquier razón), pregunta al usuario si
     quiere lanzar `scripts/oauth_flow.py` (OAuth interactivo).
  4. Si dice sí: lanza el script, recarga .env, re-verifica.
  5. Si dice no: retorna False (caller decide qué hacer).
"""
import unittest
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock, call


class TestReloadEnvAfterOauth(unittest.TestCase):
    """Unit tests para _reload_env_after_oauth (UX-1 helper)."""

    def test_reload_updates_qb_globals_from_dotenv(self):
        """GREEN: _reload_env_after_oauth recarga los tokens desde .env."""
        import main
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "new-at-from-env",
            "QB_REFRESH_TOKEN": "new-rt-from-env",
            "QB_REALM_ID": "9341455870833544",
        }), patch("dotenv.load_dotenv", return_value=None), \
           patch("main.CURRENT_COMPANY", None):
            main._reload_env_after_oauth()
        self.assertEqual(main.QB_ACCESS_TOKEN, "new-at-from-env")
        self.assertEqual(main.QB_REFRESH_TOKEN, "new-rt-from-env")
        self.assertEqual(main.QB_REALM_ID, "9341455870833544")

    def test_reload_saves_meta_json_when_company_set(self):
        """GREEN: si CURRENT_COMPANY está seteado, actualiza su meta.json."""
        import main
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "at-sync-test",
            "QB_REFRESH_TOKEN": "rt-sync-test",
            "QB_REALM_ID": "9341455870833544",
        }), patch("dotenv.load_dotenv", return_value=None), \
           patch("main.CURRENT_COMPANY", {
            "name": "Sandbox Company_US_1",
            "realm_id": "9341455870833544",
        }), patch("company_manager.save_company_meta") as mock_save:
            main._reload_env_after_oauth()
        mock_save.assert_called_once_with(
            "Sandbox Company_US_1", "9341455870833544",
            access_token="at-sync-test",
            refresh_token="rt-sync-test",
        )

    def test_reload_skips_meta_json_when_company_none(self):
        """GREEN: si CURRENT_COMPANY es None, no llama save_company_meta."""
        import main
        from company_manager import save_company_meta
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "at-no-company",
        }), patch("dotenv.load_dotenv", return_value=None), \
           patch("main.CURRENT_COMPANY", None), \
           patch("company_manager.save_company_meta") as mock_save:
            main._reload_env_after_oauth()
        mock_save.assert_not_called()


class TestVerifyQboConnectionWithReauth(unittest.TestCase):
    """UX-1: verificación de QBO al iniciar con oferta de re-auth."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")
        import main
        # Asegurar que el helper existe (RED: debería no existir)
        self.assertTrue(
            hasattr(main, "_verify_qbo_connection_or_offer_reauth"),
            "RED: _verify_qbo_connection_or_offer_reauth debe existir en main",
        )

    def test_qbo_reachable_returns_true_without_prompt(self):
        """GREEN: si qbo_query() funciona, retorna True sin preguntar nada."""
        import main
        with patch("main.qbo_query", return_value={"QueryResponse": {"totalCount": 5}}), \
             patch("main.refresh_qb_token") as mock_refresh, \
             patch("main.input") as mock_input, \
             patch("main.subprocess.run") as mock_subproc:
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertTrue(result)
        mock_refresh.assert_not_called()
        mock_input.assert_not_called()
        mock_subproc.assert_not_called()

    def test_qbo_unreachable_refresh_fails_user_says_yes_launches_oauth(self):
        """GREEN: si QBO no responde y refresh falla, y user dice 's',
           se lanza scripts/oauth_flow.py y se re-verifica."""
        import main
        # Primer qbo_query: error. Refresh: falla.
        # subprocess.run (oauth flow): éxito simulado.
        # Tras oauth, .env se recarga; segundo qbo_query: éxito.
        with patch("main.qbo_query") as mock_qbo, \
             patch("main.refresh_qb_token", return_value=False), \
             patch("main.input", return_value="s"), \
             patch("main.subprocess.run", return_value=MagicMock(returncode=0)) as mock_subproc, \
             patch("main._reload_env_after_oauth") as mock_reload, \
             patch.object(main.sys.stdin, "isatty", return_value=True):
            # Primera llamada: error; segunda llamada (post-OAuth): éxito
            mock_qbo.side_effect = [
                {"error": "Token revoked"},
                {"QueryResponse": {"totalCount": 5}},
            ]
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertTrue(result)
        mock_qbo.assert_called()
        self.assertEqual(mock_qbo.call_count, 2)
        # Verificar que se llamó al OAuth flow con la empresa actual
        self.assertTrue(mock_subproc.called)
        cmd = mock_subproc.call_args[0][0]
        self.assertIn("oauth_flow.py", " ".join(cmd))
        mock_reload.assert_called_once()

    def test_qbo_unreachable_refresh_fails_user_says_no_returns_false(self):
        """GREEN: si user dice 'n' a re-autenticar, retorna False (caller decide)."""
        import main
        with patch("main.qbo_query", return_value={"error": "Token revoked"}), \
             patch("main.refresh_qb_token", return_value=False), \
             patch("main.input", return_value="n"), \
             patch("main.subprocess.run") as mock_subproc:
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertFalse(result)
        mock_subproc.assert_not_called()

    def test_qbo_unreachable_refresh_succeeds_returns_true_without_prompt(self):
        """GREEN: si refresh tiene éxito, retorna True sin preguntar."""
        import main
        with patch("main.qbo_query") as mock_qbo, \
             patch("main.refresh_qb_token", return_value=True), \
             patch("main.input") as mock_input, \
             patch("main.subprocess.run") as mock_subproc:
            # 1ra qbo_query: error; 2da (post-refresh): éxito
            mock_qbo.side_effect = [
                {"error": "Token revoked"},
                {"QueryResponse": {"totalCount": 5}},
            ]
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertTrue(result)
        mock_input.assert_not_called()
        mock_subproc.assert_not_called()

    def test_qbo_unreachable_user_says_yes_but_oauth_fails_returns_false(self):
        """GREEN: si user dice sí pero OAuth flow falla, retorna False."""
        import main
        with patch("main.qbo_query", return_value={"error": "Token revoked"}), \
             patch("main.refresh_qb_token", return_value=False), \
             patch("main.input", return_value="s"), \
             patch("main.subprocess.run", return_value=MagicMock(returncode=1)) as mock_subproc, \
             patch("main._reload_env_after_oauth"), \
             patch.object(main.sys.stdin, "isatty", return_value=True):
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertFalse(result)
        self.assertTrue(mock_subproc.called)

    def test_eoferror_on_input_returns_false(self):
        """GREEN: si input() lanza EOFError (entrada no interactiva),
           retorna False sin intentar OAuth."""
        import main
        with patch("main.qbo_query", return_value={"error": "Token revoked"}), \
             patch("main.refresh_qb_token", return_value=False), \
             patch("main.input", side_effect=EOFError), \
             patch("main.subprocess.run") as mock_subproc, \
             patch.object(main.sys.stdin, "isatty", return_value=True):
            result = main._verify_qbo_connection_or_offer_reauth()
        self.assertFalse(result)
        mock_subproc.assert_not_called()
