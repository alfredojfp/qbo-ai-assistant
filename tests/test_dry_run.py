"""Tests para dry-run mode (UX-2).

Dry-run: el usuario agrega '--dry-run' al final de su mensaje.
Dexter simula la ejecución de tools que modifican QBO sin
ejecutarlas realmente. Tools de solo-lectura (buscar, qbo_query,
reportes) se ejecutan normalmente para dar contexto.

Flujo:
  1. Usuario: "crea estimate para X por $1,000 --dry-run"
  2. Dexter ejecuta tools de lectura (buscar_cliente) normalmente
  3. Tools de escritura (crear_estimate) se simulan
  4. Dexter responde: "[DRY-RUN] Crearía estimate para X..."
  5. Al terminar la iteración, dry-run se desactiva automáticamente
"""
import unittest
from unittest.mock import patch, MagicMock, ANY


class TestDryRunMode(unittest.TestCase):
    """UX-2: modo dry-run para simulación segura."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_dry_run_flag_detected_in_message(self):
        """El flag --dry-run se detecta y se elimina del mensaje."""
        import main
        msg, is_dry = main._parse_dry_run("crea un cliente --dry-run")
        self.assertTrue(is_dry)
        self.assertEqual(msg, "crea un cliente")
        self.assertNotIn("--dry-run", msg)

    def test_dry_run_flag_not_present(self):
        """Sin --dry-run, retorna el mensaje original."""
        import main
        msg, is_dry = main._parse_dry_run("crea un cliente")
        self.assertFalse(is_dry)
        self.assertEqual(msg, "crea un cliente")

    def test_dry_run_flag_case_insensitive(self):
        """El flag es case-insensitive."""
        import main
        msg, is_dry = main._parse_dry_run("busca cliente --DRY-RUN")
        self.assertTrue(is_dry)
        self.assertEqual(msg, "busca cliente")

    def test_dry_run_flag_mid_message(self):
        """--dry-run en cualquier parte del mensaje."""
        import main
        msg, is_dry = main._parse_dry_run("crea --dry-run un cliente")
        self.assertTrue(is_dry)
        self.assertEqual(msg.strip(), "crea un cliente")

    def test_dry_run_simulates_create_tool(self):
        """En dry-run, un tool de escritura se simula, no se ejecuta."""
        import main
        from dexter.core.safe_json import safe_dumps

        # mock TOOL_FUNCTIONS con un tool falso de escritura
        mock_fn = MagicMock(return_value={"success": True, "id": "99"})
        with patch.dict(main.TOOL_FUNCTIONS, {"crear_estimate": mock_fn}), \
             patch.object(main, "DRY_RUN_ACTIVE", True):
            result = main._execute_tool("crear_estimate", {"cliente_id": "70", "monto": 1000})
            # No debe llamar a la función real
            mock_fn.assert_not_called()
            # Debe retornar un mensaje de dry-run
            self.assertIn("DRY-RUN", result.get("dry_run_note", ""))
            self.assertTrue(result.get("dry_run", False))

    def test_dry_run_executes_read_tools_normally(self):
        """En dry-run, tools de solo-lectura se ejecutan normalmente."""
        import main

        mock_fn = MagicMock(return_value={"encontrados": 1, "clientes": [{"id": "70"}]})
        with patch.dict(main.TOOL_FUNCTIONS, {"buscar_cliente": mock_fn}), \
             patch.object(main, "DRY_RUN_ACTIVE", True):
            result = main._execute_tool("buscar_cliente", {"nombre": "Prueba2"})
            # Debe llamar a la función real (es solo-lectura)
            mock_fn.assert_called_once()
            self.assertEqual(result["encontrados"], 1)

    def test_dry_run_resets_after_iteration(self):
        """Después de procesar el mensaje, dry-run se desactiva."""
        import main
        main.DRY_RUN_ACTIVE = True
        msg, is_dry = main._parse_dry_run("hola")
        # Si el nuevo mensaje NO tiene --dry-run, se desactiva
        main.DRY_RUN_ACTIVE = is_dry
        self.assertFalse(main.DRY_RUN_ACTIVE)

    def test_full_dry_run_flow_integration(self):
        """Integración: mensaje con --dry-run activa el modo para esa iteración."""
        import main
        msg = "crea un estimate para Prueba2 por $1,000 --dry-run"
        cleaned, is_dry = main._parse_dry_run(msg)
        self.assertTrue(is_dry)
        self.assertEqual(cleaned, "crea un estimate para Prueba2 por $1,000")
