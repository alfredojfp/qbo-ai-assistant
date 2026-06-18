"""Tests para dexter.core.memory — memoria persistente entre sesiones.

Inspirado en Hermes Agent: MEMORY.md (notas del agente) y USER.md
(perfil del usuario). El agente puede leer/escribir su memoria y
esta se inyecta en el system prompt al inicio de cada sesión.

Formato de las entradas: texto separado por § (section sign).
"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


class TestPersistentMemory(unittest.TestCase):
    """dexter.core.memory.PersistentMemory para notas del agente."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.memory_path = Path(self.tmp) / "MEMORY.md"
        self.user_path = Path(self.tmp) / "USER.md"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _fresh_memory(self):
        from dexter.core import memory
        import importlib
        importlib.reload(memory)
        return memory.PersistentMemory(
            memory_path=str(self.memory_path),
            user_path=str(self.user_path),
        )

    def test_empty_memory_on_first_load(self):
        """RED: primera carga con archivos inexistentes → memoria vacía."""
        mem = self._fresh_memory()
        self.assertEqual(mem.get_memory_entries(), [])
        self.assertEqual(mem.get_user_entries(), [])

    def test_add_and_read_entries(self):
        """GREEN: agregar entradas y leerlas."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(str(self.memory_path), str(self.user_path))
        mem.add("memory", "El cliente más frecuente es Prueba2 (ID 70)")
        mem.add("memory", "Usar sandbox realm 9341455870833544")
        mem.add("user", "Alfredo prefiere respuestas concisas en español")

        memory_entries = mem.get_memory_entries()
        user_entries = mem.get_user_entries()
        self.assertEqual(len(memory_entries), 2)
        self.assertIn("Prueba2", memory_entries[0])
        self.assertEqual(len(user_entries), 1)
        self.assertIn("Alfredo", user_entries[0])

    def test_entries_persist_to_disk(self):
        """GREEN: las entradas sobreviven a una recarga."""
        mem = self._fresh_memory()
        mem.add("memory", "Persistencia funciona")
        # Recargar desde disco — usar la MISMA ruta
        from dexter.core.memory import PersistentMemory
        mem2 = PersistentMemory(
            memory_path=str(self.memory_path),
            user_path=str(self.user_path),
        )
        self.assertIn("Persistencia funciona", mem2.get_memory_entries()[0])

    def test_remove_entry_by_substring(self):
        """GREEN: eliminar entrada por substring matching."""
        mem = self._fresh_memory()
        mem.add("memory", "Cliente X ID 100")
        mem.add("memory", "Cliente Z ID 200")
        mem.remove("memory", "X ID")
        self.assertEqual(len(mem.get_memory_entries()), 1)
        self.assertIn("Cliente Z", mem.get_memory_entries()[0])

    def test_format_for_system_prompt(self):
        """GREEN: formatear memoria para inyección en system prompt."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(
            memory_path=str(self.memory_path),
            user_path=str(self.user_path),
        )
        mem.add("memory", "Sandbox realm: 9341455870833544")
        mem.add("user", "Usuario: Alfredo, idioma: ES")
        formatted = mem.format_for_prompt()

        self.assertIn("MEMORY", formatted)
        self.assertIn("9341455870833544", formatted)
        self.assertIn("USER PROFILE", formatted)
        self.assertIn("Alfredo", formatted)
        # Con múltiples entradas, usa § como separador
        mem.add("memory", "Segunda entrada de prueba")
        formatted2 = mem.format_for_prompt()
        self.assertIn("§", formatted2)

    def test_format_shows_capacity(self):
        """GREEN: el formato muestra uso y capacidad."""
        mem = self._fresh_memory()
        mem.add("memory", "Test entry")
        formatted = mem.format_for_prompt()
        # Debe mostrar porcentaje o conteo de chars
        self.assertTrue("%" in formatted or "/" in formatted,
                        f"Expected capacity info in: {formatted[:100]}")

    def test_duplicate_prevention(self):
        """GREEN: entradas duplicadas no se agregan dos veces."""
        mem = self._fresh_memory()
        mem.add("memory", "Entry A")
        mem.add("memory", "Entry A")  # Duplicado
        self.assertEqual(len(mem.get_memory_entries()), 1)

    def test_char_limit_rejected_when_full(self):
        """GREEN: si ya hay entradas y nueva excede límite → rechazar."""
        mem = self._fresh_memory()
        # Llenar al 90% primero
        limit = mem.MEMORY_CHAR_LIMIT
        mem.add("memory", "A" * int(limit * 0.5))
        # Nueva entrada que excede el espacio restante
        big = "B" * int(limit * 0.7)
        result = mem.add("memory", big)
        self.assertFalse(result.get("success", True),
                         "Debe rechazar entrada que haría exceder el límite")

    def test_auto_consolidation_suggestion(self):
        """GREEN: cuando memoria está >80%, sugiere consolidar."""
        mem = self._fresh_memory()
        limit = mem.MEMORY_CHAR_LIMIT
        # Llenar al 85%
        chunk = "A" * (int(limit * 0.85 / 3))
        mem.add("memory", chunk + "1")
        mem.add("memory", chunk + "2")
        mem.add("memory", chunk + "3")
        usage = mem.usage_percent("memory")
        self.assertGreater(usage, 80,
                          f"Expected >80% usage, got {usage}%")


class TestParseDefaults(unittest.TestCase):
    """HIGH-2b: PersistentMemory.parse_defaults() con fuzzy key matching."""

    def setUp(self):
        from dexter.core.memory import PersistentMemory
        self.tmp = tempfile.mkdtemp()
        import os
        self.path = os.path.join(self.tmp, "MEMORY.md")
        self.PersistentMemory = PersistentMemory

    def test_parses_key_value_entries(self):
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "banco_default: 226")
        mem.add("memory", "deposito_default: 250")
        defaults = mem.parse_defaults(["banco_default", "deposito_default"])
        self.assertEqual(defaults.get("banco_default"), "226")
        self.assertEqual(defaults.get("deposito_default"), "250")

    def test_ignores_unstructured_entries(self):
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "El cliente John Smith paga puntual")
        mem.add("memory", "banco_default: 226")
        defaults = mem.parse_defaults(["banco_default"])
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults["banco_default"], "226")

    def test_empty_memory_returns_empty_dict(self):
        mem = self.PersistentMemory(memory_path=self.path)
        defaults = mem.parse_defaults(["banco_default"])
        self.assertEqual(defaults, {})

    def test_fuzzy_matches_natural_language(self):
        """'banco default para depositos: 226' → matchea con 'banco_default'."""
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "banco default para depositos: 226")
        defaults = mem.parse_defaults(["banco_default", "deposito_default"])
        self.assertEqual(defaults.get("banco_default"), "226")

    def test_fuzzy_deposito_default(self):
        """Natural language keys with colon match known keys."""
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "deposito_default: 250")
        mem.add("memory", "banco default para mi empresa: 92")
        defaults = mem.parse_defaults(["banco_default", "deposito_default"])
        self.assertEqual(defaults.get("banco_default"), "92")
        self.assertEqual(defaults.get("deposito_default"), "250")

    def test_mixed_language_defaults(self):
        """Claves con caracteres especiales se normalizan."""
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "Banco Default: 226")
        mem.add("memory", "cuenta_depósito: 250")
        defaults = mem.parse_defaults(["banco_default", "deposito_default"])
        self.assertEqual(defaults.get("banco_default"), "226")

    def test_no_known_keys_returns_all(self):
        mem = self.PersistentMemory(memory_path=self.path)
        mem.add("memory", "banco_default: 100")
        mem.add("memory", "vendor_preferido: Office Depot")
        defaults = mem.parse_defaults()
        self.assertIn("banco_default", defaults)
        self.assertIn("vendor_preferido", defaults)
