# -*- coding: utf-8 -*-
"""
Tests para BatchEngine.
Ejecutar: python -m unittest tests.test_batch_engine
"""
import os
import shutil
import tempfile
import unittest

from dexter.core.batch.engine import BatchEngine, InvalidStateTransition
from dexter.core.batch.storage import BatchState, BatchStorage, ItemState


class TestEngineSetup(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))
        self.engine = BatchEngine(self.storage)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_batch(self, items=None, skill="test"):
        if items is None:
            items = [{"a": 1}, {"a": 2}]
        return self.engine.create_batch(skill, items)


class TestCreateBatch(TestEngineSetup):
    def test_create_batch_retorna_id(self):
        bid = self._make_batch()
        self.assertIsInstance(bid, str)

    def test_create_batch_persiste_items(self):
        bid = self._make_batch([{"x": 1}, {"x": 2}, {"x": 3}])
        items = self.storage.get_items(bid)
        self.assertEqual(len(items), 3)

    def test_create_batch_inicia_en_PENDING(self):
        bid = self._make_batch()
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.PENDING.value)

    def test_create_batch_persiste_skill(self):
        bid = self._make_batch(skill="deposits")
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["skill"], "deposits")


class TestValidate(TestEngineSetup):
    def test_validate_sin_validador_todo_es_valido(self):
        bid = self._make_batch()
        result = self.engine.validate(bid)
        self.assertEqual(result["valid"], 2)
        self.assertEqual(result["invalid"], 0)

    def test_validate_con_validador_acepta(self):
        bid = self._make_batch()
        validator = lambda item: (True, None)
        result = self.engine.validate(bid, validator=validator)
        self.assertEqual(result["valid"], 2)

    def test_validate_con_validador_rechaza(self):
        bid = self._make_batch([{"x": -10}, {"x": 20}, {"x": -5}])
        validator = lambda item: (item["x"] > 0, "x debe ser positivo")
        result = self.engine.validate(bid, validator=validator)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 2)

    def test_validate_marca_items_READY(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        items = self.storage.get_items(bid)
        for item in items:
            self.assertEqual(item["state"], ItemState.READY.value)

    def test_validate_marca_items_FAILED(self):
        bid = self._make_batch([{"x": -1}])
        validator = lambda item: (item["x"] > 0, "negativo")
        self.engine.validate(bid, validator=validator)
        items = self.storage.get_items(bid)
        self.assertEqual(items[0]["state"], ItemState.FAILED.value)
        self.assertEqual(items[0]["error"], "negativo")

    def test_validate_cambia_estado_a_VALIDATED(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.VALIDATED.value)


class TestStateTransitions(TestEngineSetup):
    def test_no_puede_ejecutar_sin_validar(self):
        bid = self._make_batch()
        with self.assertRaises(InvalidStateTransition):
            self.engine.execute(bid, lambda x: (x, None))

    def test_no_puede_dry_run_sin_validar(self):
        bid = self._make_batch()
        with self.assertRaises(InvalidStateTransition):
            self.engine.dry_run(bid)

    def test_no_puede_confirmar_sin_dry_run(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        with self.assertRaises(InvalidStateTransition):
            self.engine.confirm(bid)

    def test_no_puede_dry_run_dos_veces(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        with self.assertRaises(InvalidStateTransition):
            self.engine.dry_run(bid)

    def test_flujo_completo_funciona(self):
        bid = self._make_batch([{"x": 1}, {"x": 2}])
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.confirm(bid)
        result = self.engine.execute(bid, lambda x: ({"echo": x}, None))
        self.assertEqual(result["executed"], 2)
        self.assertEqual(result["failed"], 0)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.EXECUTED.value)


class TestCancel(TestEngineSetup):
    def test_cancelar_desde_PENDING(self):
        bid = self._make_batch()
        self.engine.cancel(bid)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.CANCELLED.value)

    def test_cancelar_desde_VALIDATED(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        self.engine.cancel(bid)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.CANCELLED.value)

    def test_cancelar_desde_DRY_RUN(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.cancel(bid)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.CANCELLED.value)

    def test_no_puede_cancelar_despues_de_ejecutar(self):
        bid = self._make_batch()
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.confirm(bid)
        self.engine.execute(bid, lambda x: (x, None))
        with self.assertRaises(InvalidStateTransition):
            self.engine.cancel(bid)


class TestExecute(TestEngineSetup):
    def test_execute_funcion_basica(self):
        bid = self._make_batch([{"n": 1}, {"n": 2}])
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.confirm(bid)
        result = self.engine.execute(bid, lambda x: ({"out": x["n"] * 2}, None))
        self.assertEqual(result["executed"], 2)
        items = self.storage.get_items(bid)
        self.assertEqual(items[0]["output"]["out"], 2)
        self.assertEqual(items[1]["output"]["out"], 4)

    def test_execute_con_fallos(self):
        bid = self._make_batch([{"n": 1}, {"n": 2}])
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.confirm(bid)

        def executor(item):
            if item["n"] == 1:
                return (None, "QBO error")
            return ({"out": item["n"]}, None)

        result = self.engine.execute(bid, executor)
        self.assertEqual(result["executed"], 1)
        self.assertEqual(result["failed"], 1)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.FAILED.value)

    def test_execute_salta_items_failed(self):
        bid = self._make_batch([{"n": 1}, {"n": 2}])
        self.engine.validate(bid, validator=lambda x: (x["n"] > 1, "n<=1"))
        self.engine.dry_run(bid)
        self.engine.confirm(bid)
        result = self.engine.execute(bid, lambda x: ({"ok": True}, None))
        self.assertEqual(result["executed"], 1)
        items = self.storage.get_items(bid)
        self.assertEqual(items[0]["state"], ItemState.FAILED.value)
        self.assertEqual(items[1]["state"], ItemState.EXECUTED.value)


class TestRetry(TestEngineSetup):
    def test_retry_crea_nuevo_batch(self):
        bid = self._make_batch([{"x": 1}, {"x": 2}])
        self.engine.validate(bid)
        self.engine.dry_run(bid)
        self.engine.confirm(bid)
        self.engine.execute(bid, lambda x: (None, "fail"))
        new_bid = self.engine.retry(bid)
        self.assertNotEqual(bid, new_bid)
        new_batch = self.storage.get_batch(new_bid)
        self.assertEqual(new_batch["state"], BatchState.PENDING.value)

    def test_retry_solo_desde_FAILED(self):
        bid = self._make_batch()
        with self.assertRaises(InvalidStateTransition):
            self.engine.retry(bid)


if __name__ == "__main__":
    unittest.main()
