"""Tests para CRIT-3: state global no se limpia al cambiar empresa → data leak.

Bug: main.py:4388-4422 — tool_gestionar_empresas("cambiar") solo actualiza
      QB_BASE_URL y chart, no limpia conversation_history ni last_search_results.
      → Cambio de empresa → tool results stale → invoice en empresa equivocada.

Fix: crear reset_session_state() que limpia globals, llamar desde "cambiar"
     branch ANTES de cargar el contexto de la nueva empresa.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestResetSessionState(unittest.TestCase):
    """CRIT-3: reset_session_state() debe limpiar state inter-company."""

    def test_reset_clears_conversation_history(self):
        """RED: reset_session_state() debe vaciar conversation_history."""
        import main
        # Poblar history con datos de empresa A
        main.conversation_history.append({"role": "user", "content": "A: cliente 1"})
        main.conversation_history.append({"role": "assistant", "content": "A: encontré cliente 1"})

        self.assertGreater(len(main.conversation_history), 0)

        main.reset_session_state()

        self.assertEqual(
            len(main.conversation_history), 0,
            f"conversation_history debe quedar vacía. Got: {len(main.conversation_history)} items"
        )

    def test_reset_clears_last_search_results(self):
        """RED: reset_session_state() debe vaciar last_search_results."""
        import main
        # Poblar last_search_results
        main.session_state["last_search_results"]["customers"] = [
            {"id": "1", "name": "Cliente A", "balance": 100.0}
        ]
        main.session_state["last_search_results"]["accounts"] = [
            {"id": "10", "name": "Cuenta A", "balance": 500.0}
        ]

        self.assertGreater(len(main.session_state["last_search_results"]), 0)

        main.reset_session_state()

        self.assertEqual(
            len(main.session_state["last_search_results"]), 0,
            f"last_search_results debe quedar vacío. Got: {main.session_state['last_search_results']}"
        )

    def test_reset_preserves_token_counters(self):
        """RED: reset NO debe tocar input_tokens, output_tokens, total_cost."""
        import main
        main.session_state["input_tokens"] = 5000
        main.session_state["output_tokens"] = 2000
        main.session_state["total_cost"] = 0.42

        main.reset_session_state()

        self.assertEqual(main.session_state["input_tokens"], 5000, "input_tokens preservado")
        self.assertEqual(main.session_state["output_tokens"], 2000, "output_tokens preservado")
        self.assertEqual(main.session_state["total_cost"], 0.42, "total_cost preservado")

    def test_reset_preserves_operations_counters(self):
        """RED: reset NO debe tocar counters de operations (searches, deposits, etc.)."""
        import main
        main.session_state["operations"]["searches"] = 5
        main.session_state["operations"]["invoices"] = 2

        main.reset_session_state()

        self.assertEqual(main.session_state["operations"]["searches"], 5, "searches preservado")
        self.assertEqual(main.session_state["operations"]["invoices"], 2, "invoices preservado")


class TestGestionarEmpresasCambiarClears(unittest.TestCase):
    """CRIT-3: tool_gestionar_empresas('cambiar') debe llamar reset_session_state."""

    def test_cambiar_calls_reset_session_state(self):
        """RED: al cambiar de empresa, reset_session_state debe ser llamado."""
        import main

        # Set up state preexistente de empresa A
        main.conversation_history.append({"role": "user", "content": "A: search customer"})
        main.session_state["last_search_results"]["customers"] = [
            {"id": "1", "name": "Cliente A"}
        ]

        # Mock list_local_companies para retornar empresa B
        target_company = {
            "name": "Sandbox_B",
            "realm_id": "1111111111111111",
        }
        target_meta = {
            "access_token": "fake-token-b",
            "refresh_token": "fake-refresh-b",
        }

        with patch("main.list_local_companies", return_value=[target_company]), \
             patch("main.get_company_meta", return_value=target_meta), \
             patch("main.save_company_context"), \
             patch("main.save_company_selection"), \
             patch("main.load_company_context", return_value={}), \
             patch("main.reset_session_state") as mock_reset:
            result = main.tool_gestionar_empresas("cambiar", nombre="Sandbox_B")

        self.assertTrue(result.get("success"), f"Cambio debe ser exitoso. Got: {result}")
        mock_reset.assert_called_once(), "reset_session_state debe ser llamado una vez"

    def test_cambiar_actually_clears_state(self):
        """RED: después de cambiar, conversation_history y last_search_results están vacíos."""
        import main

        # Pre-poblar con datos de empresa A
        main.conversation_history.append({"role": "user", "content": "A: cliente 1"})
        main.conversation_history.append({"role": "tool", "content": "A: cliente id=1"})
        main.session_state["last_search_results"]["customers"] = [{"id": "1", "name": "Cliente A"}]

        target_company = {
            "name": "Sandbox_B",
            "realm_id": "1111111111111111",
        }
        target_meta = {
            "access_token": "fake-token-b",
            "refresh_token": "fake-refresh-b",
        }

        with patch("main.list_local_companies", return_value=[target_company]), \
             patch("main.get_company_meta", return_value=target_meta), \
             patch("main.save_company_context"), \
             patch("main.save_company_selection"), \
             patch("main.load_company_context", return_value={}):
            main.tool_gestionar_empresas("cambiar", nombre="Sandbox_B")

        # Verificar que se limpió
        self.assertEqual(
            len(main.conversation_history), 0,
            f"history debe estar vacía. Got: {len(main.conversation_history)}"
        )
        self.assertEqual(
            len(main.session_state["last_search_results"]), 0,
            f"last_search_results debe estar vacío. Got: {main.session_state['last_search_results']}"
        )


if __name__ == "__main__":
    unittest.main()
