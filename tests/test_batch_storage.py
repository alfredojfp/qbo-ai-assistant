# -*- coding: utf-8 -*-
"""
Tests para BatchStorage.
Ejecutar: python -m unittest tests.test_batch_storage
"""
import os
import tempfile
import unittest

from dexter.core.batch.storage import (
    BatchState, ItemState, BatchStorage
)


class TestBatchStorageInit(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_storage_crea_archivo_db(self):
        BatchStorage(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))

    def test_storage_crea_directorio_si_no_existe(self):
        nested = os.path.join(self.tmpdir, "subdir", "deep", "test.db")
        BatchStorage(nested)
        self.assertTrue(os.path.exists(nested))

    def test_storage_puede_inicializarse_dos_veces(self):
        s1 = BatchStorage(self.db_path)
        s2 = BatchStorage(self.db_path)
        self.assertEqual(s1.db_path, s2.db_path)


class TestCreateBatch(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_crear_batch_retorna_id(self):
        bid = self.storage.create_batch("test_skill")
        self.assertIsInstance(bid, str)
        self.assertGreater(len(bid), 0)

    def test_crear_batch_con_id_explicito(self):
        bid = self.storage.create_batch("test_skill", batch_id="custom-id-123")
        self.assertEqual(bid, "custom-id-123")
        batch = self.storage.get_batch(bid)
        self.assertIsNotNone(batch)

    def test_batch_inicia_en_PENDING(self):
        bid = self.storage.create_batch("test_skill")
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["state"], BatchState.PENDING.value)

    def test_batch_persiste_context(self):
        context = {"empresa": "ACME Corp", "usuario": "alfredo"}
        bid = self.storage.create_batch("test_skill", context=context)
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["context"]["empresa"], "ACME Corp")

    def test_batch_sin_context_es_dict_vacio(self):
        bid = self.storage.create_batch("test_skill")
        batch = self.storage.get_batch(bid)
        self.assertEqual(batch["context"], {})
        self.assertEqual(batch["summary"], {})

    def test_get_batch_inexistente_retorna_none(self):
        self.assertIsNone(self.storage.get_batch("no-existe"))


class TestUpdateBatchState(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))
        self.bid = self.storage.create_batch("test_skill")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_actualizar_estado(self):
        self.storage.update_batch_state(self.bid, BatchState.VALIDATED)
        batch = self.storage.get_batch(self.bid)
        self.assertEqual(batch["state"], BatchState.VALIDATED.value)

    def test_actualizar_estado_con_summary(self):
        self.storage.update_batch_state(
            self.bid, BatchState.EXECUTED, summary={"ok": 10, "fail": 2}
        )
        batch = self.storage.get_batch(self.bid)
        self.assertEqual(batch["summary"]["ok"], 10)
        self.assertEqual(batch["summary"]["fail"], 2)

    def test_actualizar_estado_actualiza_updated_at(self):
        batch1 = self.storage.get_batch(self.bid)
        original_updated = batch1["updated_at"]
        self.storage.update_batch_state(self.bid, BatchState.CONFIRMED)
        batch2 = self.storage.get_batch(self.bid)
        self.assertGreaterEqual(batch2["updated_at"], original_updated)


class TestItems(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))
        self.bid = self.storage.create_batch("test_skill")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_agregar_item(self):
        item_id = self.storage.add_item(
            self.bid, 0, {"cliente": "ACME", "monto": 100.0}
        )
        self.assertIsInstance(item_id, str)

    def test_agregar_item_con_id_explicito(self):
        iid = self.storage.add_item(
            self.bid, 0, {"x": 1}, item_id="item-1"
        )
        self.assertEqual(iid, "item-1")

    def test_item_inicia_en_PENDING(self):
        iid = self.storage.add_item(self.bid, 0, {"x": 1})
        item = self.storage.get_item(iid)
        self.assertEqual(item["state"], ItemState.PENDING.value)

    def test_get_items_ordenados_por_index(self):
        self.storage.add_item(self.bid, 0, {"name": "A"})
        self.storage.add_item(self.bid, 1, {"name": "B"})
        self.storage.add_item(self.bid, 2, {"name": "C"})
        items = self.storage.get_items(self.bid)
        self.assertEqual(len(items), 3)
        self.assertEqual([i["input"]["name"] for i in items], ["A", "B", "C"])

    def test_update_item_a_ready(self):
        iid = self.storage.add_item(self.bid, 0, {"x": 1})
        self.storage.update_item(iid, ItemState.READY)
        item = self.storage.get_item(iid)
        self.assertEqual(item["state"], ItemState.READY.value)

    def test_update_item_con_output(self):
        iid = self.storage.add_item(self.bid, 0, {"x": 1})
        self.storage.update_item(
            iid, ItemState.EXECUTED, output={"qbo_id": "abc-123"}
        )
        item = self.storage.get_item(iid)
        self.assertEqual(item["output"]["qbo_id"], "abc-123")

    def test_update_item_con_error(self):
        iid = self.storage.add_item(self.bid, 0, {"x": 1})
        self.storage.update_item(iid, ItemState.FAILED, error="QBO 400")
        item = self.storage.get_item(iid)
        self.assertEqual(item["state"], ItemState.FAILED.value)
        self.assertEqual(item["error"], "QBO 400")


class TestAuditLog(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_audit_log_se_crea_al_crear_batch(self):
        bid = self.storage.create_batch("test_skill")
        log = self.storage.get_audit_log(bid)
        self.assertGreater(len(log), 0)
        self.assertEqual(log[0]["event"], "BATCH_CREATED")

    def test_audit_log_registra_cambios_de_estado(self):
        bid = self.storage.create_batch("test_skill")
        self.storage.update_batch_state(bid, BatchState.VALIDATED)
        self.storage.update_batch_state(bid, BatchState.CONFIRMED)
        log = self.storage.get_audit_log(bid)
        events = [e["event"] for e in log]
        self.assertIn("BATCH_STATE_CHANGED", events)
        self.assertGreaterEqual(events.count("BATCH_STATE_CHANGED"), 2)

    def test_audit_log_registra_items(self):
        bid = self.storage.create_batch("test_skill")
        iid = self.storage.add_item(bid, 0, {"x": 1})
        log = self.storage.get_audit_log(bid)
        item_events = [e for e in log if e.get("item_id") == iid]
        self.assertGreater(len(item_events), 0)

    def test_audit_log_incluye_timestamp(self):
        bid = self.storage.create_batch("test_skill")
        log = self.storage.get_audit_log(bid)
        for event in log:
            self.assertIn("timestamp", event)
            self.assertIsInstance(event["timestamp"], str)


class TestListBatches(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage = BatchStorage(os.path.join(self.tmpdir, "test.db"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_listar_batches_vacio(self):
        result = self.storage.list_batches()
        self.assertEqual(result, [])

    def test_listar_todos_los_batches(self):
        self.storage.create_batch("skill_a")
        self.storage.create_batch("skill_b")
        result = self.storage.list_batches()
        self.assertEqual(len(result), 2)

    def test_filtrar_por_skill(self):
        self.storage.create_batch("skill_a")
        self.storage.create_batch("skill_b")
        self.storage.create_batch("skill_a")
        result = self.storage.list_batches(skill="skill_a")
        self.assertEqual(len(result), 2)
        for b in result:
            self.assertEqual(b["skill"], "skill_a")

    def test_filtrar_por_state(self):
        bid1 = self.storage.create_batch("skill_a")
        self.storage.create_batch("skill_a")
        self.storage.update_batch_state(bid1, BatchState.EXECUTED)
        result = self.storage.list_batches(state=BatchState.EXECUTED)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], bid1)


if __name__ == "__main__":
    unittest.main()
