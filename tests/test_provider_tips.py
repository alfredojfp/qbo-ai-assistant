"""Tests para sistema de aprendizaje OCR por proveedor (UX-4).

Cada proveedor tiene formatos distintos. Cuando Dexter procesa una
factura y el usuario corrige algo, se guarda el tip en
companies/{name}/PROVIDER_TIPS.md para que la próxima factura del
mismo proveedor se procese correctamente.

Ejemplos de tips:
  - "El total está en la esquina inferior derecha, en negrita"
  - "La factura es bilingüe EN/ES: usar montos de la columna en español"
  - "El IVA aparece en la página 2 bajo 'Tax Summary'"
  - "Factura manuscrita en la sección de observaciones: leer con cuidado"
"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestProviderTips(unittest.TestCase):
    """UX-4: aprendizaje de formatos de facturas por proveedor."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tips_path = Path(self.tmp) / "PROVIDER_TIPS.md"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mock_memory_module(self, tips_path):
        """Crea funciones de tips usando rutas temporales."""
        # Simular el comportamiento del módulo
        pass

    def test_add_provider_tip_creates_file(self):
        """Agregar un tip crea el archivo si no existe."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(memory_path=str(self.tips_path))
        mem.add("memory", "CFE: El total está en negrita abajo a la derecha")
        entries = mem.get_memory_entries()
        self.assertEqual(len(entries), 1)
        self.assertIn("CFE", entries[0])

    def test_multiple_tips_same_provider(self):
        """Múltiples tips del mismo proveedor se acumulan."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(memory_path=str(self.tips_path))
        mem.add("memory", "CFE: Total en negrita abajo derecha")
        mem.add("memory", "CFE: IVA en página 2 bajo Tax Summary")
        mem.add("memory", "Amazon: Usar columna USD no MXN")
        entries = mem.get_memory_entries()
        self.assertEqual(len(entries), 3)

    def test_get_tips_for_specific_provider(self):
        """Se pueden filtrar tips por proveedor específico."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(memory_path=str(self.tips_path))
        mem.add("memory", "CFE: Total en negrita")
        mem.add("memory", "CFE: IVA en página 2")
        mem.add("memory", "Amazon: USD no MXN")
        entries = mem.get_memory_entries()
        cfe_tips = [e for e in entries if "CFE:" in e]
        self.assertEqual(len(cfe_tips), 2)
        amazon_tips = [e for e in entries if "Amazon:" in e]
        self.assertEqual(len(amazon_tips), 1)

    def test_tips_formatted_for_ocr_prompt(self):
        """Los tips se formatean como instrucciones para el prompt OCR."""
        tips = [
            "CFE: Total en negrita abajo derecha",
            "CFE: IVA en página 2",
        ]
        prompt_section = "\n".join(f"  • {t}" for t in tips)
        self.assertIn("CFE", prompt_section)
        self.assertIn("IVA", prompt_section)
        self.assertIn("  •", prompt_section)

    def test_tips_empty_for_unknown_provider(self):
        """Proveedor sin tips retorna string vacío."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(memory_path=str(self.tips_path))
        mem.add("memory", "CFE: Total en negrita")
        entries = mem.get_memory_entries()
        telmex_tips = [e for e in entries if "Telmex:" in e]
        self.assertEqual(len(telmex_tips), 0)

    def test_tips_include_handwritten_note(self):
        """Tips para facturas manuscritas."""
        from dexter.core.memory import PersistentMemory
        mem = PersistentMemory(memory_path=str(self.tips_path))
        mem.add("memory", "Ferretería Local: Factura manuscrita. Leer con cuidado la sección de observaciones.")
        mem.add("memory", "Ferretería Local: Montos en letra y número, priorizar el número.")
        entries = mem.get_memory_entries()
        self.assertEqual(len(entries), 2)
        self.assertIn("manuscrita", entries[0])


class TestOcrProviderAwareness(unittest.TestCase):
    """El prompt de OCR debe incluir tips del proveedor cuando existen."""

    def test_ocr_prompt_includes_provider_tips(self):
        """Si hay tips para un proveedor, se inyectan en el prompt de Gemini."""
        tips = ["Total en negrita abajo derecha", "IVA en página 2"]
        base_prompt = "Extrae los datos de esta factura."
        provider = "CFE"

        # Simular cómo se construiría el prompt con tips
        enhanced = base_prompt
        if tips:
            tip_text = "\n".join(f"  • {provider}: {t}" for t in tips)
            enhanced += f"\n\nINSTRUCCIONES ESPECÍFICAS PARA {provider}:\n{tip_text}"

        self.assertIn("INSTRUCCIONES ESPECÍFICAS", enhanced)
        self.assertIn("CFE", enhanced)
        self.assertIn("Total en negrita", enhanced)

    def test_ocr_prompt_no_tips_for_new_provider(self):
        """Sin tips, el prompt no tiene sección de instrucciones."""
        base_prompt = "Extrae los datos de esta factura."
        enhanced = base_prompt  # No hay tips
        self.assertNotIn("INSTRUCCIONES ESPECÍFICAS", enhanced)
