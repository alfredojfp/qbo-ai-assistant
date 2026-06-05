"""Tests para LOW-5: EntityRef NO debe incluir 'name' (QBO rechaza).

Bug: main.py:2780 — En crear_deposito_bank_feed se construye:
     'Entity': {'EntityRef': {'value': customer_id, 'name': customer_name},
                'Type': 'Customer'}
     QBO es estricto: si 'name' no coincide exactamente con el
     nombre actual del Customer en QBO (cambios de DisplayName,
     case, acentos), responde 400 con error 'Invalid Name'.
     Convención QBO: enviar SOLO 'value' (el ID) y dejar que
     QBO resuelva el name server-side.

Fix: helper _build_entity_ref(entity_id, entity_type, name=None)
     que retorna SOLO {'value': entity_id, 'type': entity_type}.
     El parámetro 'name' se acepta pero se IGNORA (deprecation
     warning en logs). Si el caller necesita enviar name por
     backward compat con QBO idiosyncrasies, puede pasarlo
     explícitamente con include_name=True.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestEntityRefNoName(unittest.TestCase):
    """LOW-5: EntityRef no debe incluir 'name' (QBO rechaza)."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_helper_exists(self):
        """RED: _build_entity_ref debe existir en main."""
        import main
        self.assertTrue(callable(getattr(main, "_build_entity_ref", None)))

    def test_default_omits_name(self):
        """GREEN: por default, EntityRef NO incluye 'name'."""
        from main import _build_entity_ref
        ref = _build_entity_ref("42", "Customer")
        self.assertEqual(ref, {"value": "42", "type": "Customer"})
        self.assertNotIn("name", ref)

    def test_name_passed_but_ignored_by_default(self):
        """GREEN: aunque pases name, se ignora por default."""
        from main import _build_entity_ref
        ref = _build_entity_ref("42", "Customer", name="ACME Corp")
        self.assertNotIn("name", ref)

    def test_explicit_include_name(self):
        """GREEN: con include_name=True, sí incluye name."""
        from main import _build_entity_ref
        ref = _build_entity_ref("42", "Customer", name="ACME Corp",
                                include_name=True)
        self.assertEqual(ref["name"], "ACME Corp")
        self.assertEqual(ref["value"], "42")

    def test_type_optional(self):
        """GREEN: type es opcional (algunos endpoints no lo requieren)."""
        from main import _build_entity_ref
        ref = _build_entity_ref("42")
        self.assertEqual(ref, {"value": "42"})

    def test_value_required(self):
        """GREEN: sin value, lanza ValueError."""
        from main import _build_entity_ref
        with self.assertRaises(ValueError):
            _build_entity_ref("", "Customer")
        with self.assertRaises(ValueError):
            _build_entity_ref(None, "Customer")


if __name__ == "__main__":
    unittest.main()
