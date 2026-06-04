# -*- coding: utf-8 -*-
"""
Tests para Disambiguator (con input/output mockeados).
Ejecutar: python -m unittest tests.test_batch_disambiguator
"""
import unittest

from dexter.core.batch.disambiguator import Disambiguator


class MockIO:
    """Captura output y simula input."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.outputs = []

    def __call__(self, prompt=""):
        self.outputs.append(prompt)
        if not self.responses:
            raise AssertionError(f"No more responses for: {prompt!r}")
        return self.responses.pop(0)

    def output(self, msg):
        self.outputs.append(msg)

    def get_outputs(self):
        return self.outputs


def make_disambiguator(responses):
    io = MockIO(responses)
    return Disambiguator(input_func=io, output_func=io.output), io


class TestAskChoice(unittest.TestCase):
    def test_selecciona_primera_opcion(self):
        d, io = make_disambiguator(["1"])
        result = d.ask_choice("¿Cuál?", ["A", "B", "C"], allow_new=False)
        self.assertEqual(result, "A")

    def test_selecciona_tercera_opcion(self):
        d, io = make_disambiguator(["3"])
        result = d.ask_choice("¿Cuál?", ["A", "B", "C"], allow_new=False)
        self.assertEqual(result, "C")

    def test_skip_retorna_none(self):
        d, io = make_disambiguator(["s"])
        result = d.ask_choice("¿Cuál?", ["A", "B"])
        self.assertIsNone(result)

    def test_new_retorna_marcador(self):
        d, io = make_disambiguator(["n"])
        result = d.ask_choice("¿Cuál?", ["A", "B"], allow_new=True)
        self.assertEqual(result, "__NEW__")

    def test_input_invalido_re_pregunta(self):
        d, io = make_disambiguator(["xyz", "999", "1"])
        result = d.ask_choice("¿Cuál?", ["A", "B"], allow_new=False)
        self.assertEqual(result, "A")
        # Verifica que mostró el mensaje de error
        outputs = io.get_outputs()
        self.assertTrue(any("inválida" in str(o).lower() for o in outputs))


class TestAskNewCustomer(unittest.TestCase):
    def test_datos_minimos_email_y_terms(self):
        d, io = make_disambiguator(["", "maria@x.com", "Net 30", "", ""])
        result = d.ask_new_customer("Maria Rodriguez")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Maria Rodriguez")
        self.assertEqual(result["email"], "maria@x.com")
        self.assertEqual(result["terms"], "Net 30")

    def test_email_vacio_retorna_none(self):
        d, io = make_disambiguator(["", "", ""])
        result = d.ask_new_customer("Maria")
        self.assertIsNone(result)

    def test_usuario_rechaza_crear(self):
        d, io = make_disambiguator(["n"])
        result = d.ask_new_customer("Maria")
        self.assertIsNone(result)

    def test_datos_completos_incluye_telefono_y_empresa(self):
        d, io = make_disambiguator(["", "j@x.com", "Net 15", "555-1234", "Acme"])
        result = d.ask_new_customer("Jose")
        self.assertEqual(result["phone"], "555-1234")
        self.assertEqual(result["company"], "Acme")

    def test_terms_default_si_vacio(self):
        d, io = make_disambiguator(["", "a@b.com", "", "", ""])
        result = d.ask_new_customer("Test")
        self.assertEqual(result["terms"], "Net 30")


class TestAskAccount(unittest.TestCase):
    def test_selecciona_cuenta(self):
        d, io = make_disambiguator(["2"])
        result = d.ask_account("Gasto X", [
            {"id": "acc_1", "name": "Office"},
            {"id": "acc_2", "name": "Meals"}
        ])
        self.assertEqual(result, "acc_2")

    def test_no_clasificar_retorna_none(self):
        d, io = make_disambiguator(["n"])
        result = d.ask_account("Gasto X", [{"id": "a1", "name": "X"}])
        self.assertIsNone(result)


class TestConfirmBatch(unittest.TestCase):
    def test_confirmar_con_s(self):
        d, io = make_disambiguator(["s"])
        result = d.confirm_batch({"total": 3, "ready_to_execute": 3, "skipped": 0, "items": []})
        self.assertTrue(result)

    def test_confirmar_con_si(self):
        d, io = make_disambiguator(["si"])
        result = d.confirm_batch({"total": 1, "ready_to_execute": 1, "skipped": 0, "items": []})
        self.assertTrue(result)

    def test_confirmar_con_yes(self):
        d, io = make_disambiguator(["yes"])
        result = d.confirm_batch({"total": 1, "ready_to_execute": 1, "skipped": 0, "items": []})
        self.assertTrue(result)

    def test_confirmar_con_enter_vacio(self):
        d, io = make_disambiguator([""])
        result = d.confirm_batch({"total": 1, "ready_to_execute": 1, "skipped": 0, "items": []})
        self.assertTrue(result)

    def test_rechazar_con_n(self):
        d, io = make_disambiguator(["n"])
        result = d.confirm_batch({"total": 1, "ready_to_execute": 1, "skipped": 0, "items": []})
        self.assertFalse(result)

    def test_muestra_items_en_resumen(self):
        d, io = make_disambiguator(["s"])
        d.confirm_batch({
            "total": 2,
            "ready_to_execute": 2,
            "skipped": 0,
            "items": [
                {"index": 0, "state": "READY", "input": {"name": "A"}},
                {"index": 1, "state": "READY", "input": {"name": "B"}},
            ]
        })
        outputs = io.get_outputs()
        joined = " ".join(str(o) for o in outputs)
        self.assertIn("A", joined)
        self.assertIn("B", joined)


if __name__ == "__main__":
    unittest.main()
