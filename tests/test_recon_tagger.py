# -*- coding: utf-8 -*-
"""
Tests para ReconciliationTaggerSkill.
Ejecutar: python -m unittest tests.test_recon_tagger
"""
import csv
import os
import shutil
import tempfile
import unittest

from dexter.core.batch import (
    BatchEngine, BatchState, BatchStorage, Disambiguator
)
from dexter.core.batch.recon_tagger import (
    ReconciliationTaggerSkill, QBOClientProtocol, TAG_FIELD_BY_TYPE
)


class MockQBOClient:
    """Mock del cliente QBO para tests."""

    def __init__(self, transactions=None):
        self.transactions = transactions or []
        self.updates = []
        self._next_id = 1000

    def get_transactions(self, account_id, start_date, end_date):
        return [t for t in self.transactions
                if t.get("account_id") == account_id
                and start_date <= t["date"] <= end_date]

    def update_transaction(self, txn_type, txn_id, fields):
        self.updates.append({
            "type": txn_type, "id": txn_id, "fields": dict(fields)
        })
        return {"id": txn_id, **fields}


def make_skill(qbo=None, period_start="2026-06-01", period_end="2026-06-30"):
    tmpdir = tempfile.mkdtemp()
    storage = BatchStorage(os.path.join(tmpdir, "test.db"))
    engine = BatchEngine(storage)
    qbo = qbo or MockQBOClient()
    skill = ReconciliationTaggerSkill(
        engine=engine,
        qbo_client=qbo,
        period_start=period_start,
        period_end=period_end,
        account_id="bank_1",
    )
    return skill, qbo, tmpdir, engine


def write_csv(tmpdir, name, rows, fieldnames=None):
    if fieldnames is None:
        fieldnames = ["date", "description", "amount"]
    path = os.path.join(tmpdir, name)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return path


class TestReconciliationTagField(unittest.TestCase):
    def test_deposit_usa_memo(self):
        self.assertEqual(TAG_FIELD_BY_TYPE["Deposit"], "Memo")

    def test_bill_usa_privatenote(self):
        self.assertEqual(TAG_FIELD_BY_TYPE["Bill"], "PrivateNote")

    def test_purchase_usa_privatenote(self):
        self.assertEqual(TAG_FIELD_BY_TYPE["Purchase"], "PrivateNote")


class TestReconciliationFromCSV(unittest.TestCase):
    def test_leer_csv_basico(self):
        skill, qbo, tmpdir, engine = make_skill()
        try:
            path = write_csv(tmpdir, "bank.csv", [
                {"date": "2026-06-01", "description": "Acme", "amount": 100.0},
                {"date": "2026-06-02", "description": "Globex", "amount": 200.0},
            ])
            bid = skill.from_csv(path)
            self.assertIsInstance(bid, str)
            items = engine.storage.get_items(bid)
            self.assertEqual(len(items), 2)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_csv_sin_columnas_falla(self):
        skill, qbo, tmpdir, engine = make_skill()
        try:
            path = write_csv(tmpdir, "bad.csv", [
                {"date": "2026-06-01", "amount": 100.0}
            ], fieldnames=["date", "amount"])
            with self.assertRaises(ValueError):
                skill.from_csv(path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_csv_vacio_falla(self):
        skill, qbo, tmpdir, engine = make_skill()
        try:
            path = write_csv(tmpdir, "empty.csv", [])
            with self.assertRaises(ValueError):
                skill.from_csv(path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestReconciliationMatching(unittest.TestCase):
    def test_match_exacto(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 100.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["matched"], 1)
            self.assertEqual(summary["exact"], 1)
            self.assertEqual(summary["fuzzy"], 0)
            self.assertEqual(summary["unmatched"], 0)
            self.assertEqual(qbo.updates[0]["fields"]["Memo"],
                          "BNK-RECON-2026-06-8ad9b")  # hash de 5 chars
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_match_fuzzy_1_dia(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Bill", "date": "2026-06-15",
                 "amount": 50.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-16", "description": "A", "amount": 50.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["fuzzy"], 1)
            self.assertEqual(qbo.updates[0]["fields"]["PrivateNote"],
                          "BNK-RECON-2026-06-3c74b")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_sin_match(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 999.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["matched"], 0)
            self.assertEqual(summary["unmatched"], 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_no_modifica_qbo_si_sin_match(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 999.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            skill.run(bid)
            self.assertEqual(len(qbo.updates), 0)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_multiples_matches(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-01",
                 "amount": 100.0, "account_id": "bank_1"},
                {"id": "q2", "type": "Bill", "date": "2026-06-02",
                 "amount": 50.0, "account_id": "bank_1"},
                {"id": "q3", "type": "Purchase", "date": "2026-06-03",
                 "amount": 25.0, "account_id": "bank_1"},
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-01", "description": "A", "amount": 100.0},
                {"date": "2026-06-02", "description": "B", "amount": 50.0},
                {"date": "2026-06-03", "description": "C", "amount": 25.0},
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["matched"], 3)
            self.assertEqual(summary["unmatched"], 0)
            # Verifica que cada tipo usó su campo correcto
            field_by_update = {u["type"]: u["fields"] for u in qbo.updates}
            self.assertIn("Memo", field_by_update["Deposit"])
            self.assertIn("PrivateNote", field_by_update["Bill"])
            self.assertIn("PrivateNote", field_by_update["Purchase"])
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_no_matchea_dos_csv_a_mismo_qbo(self):
        """Dos filas del CSV no pueden matchear al mismo QBO txn."""
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 100.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0},
                {"date": "2026-06-15", "description": "B", "amount": 100.0},
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["matched"], 1)
            self.assertEqual(summary["unmatched"], 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_match_con_signo_invertido(self):
        """Bank CSV puede tener débitos como positivos; QBO los guarda igual."""
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Bill", "date": "2026-06-15",
                 "amount": 50.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "Office", "amount": 50.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertEqual(summary["matched"], 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestReconciliationReport(unittest.TestCase):
    def test_genera_reporte_csv(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 100.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            self.assertIsNotNone(summary["report_path"])
            self.assertTrue(os.path.exists(summary["report_path"]))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_reporte_contiene_tags(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 100.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            summary = skill.run(bid)
            with open(summary["report_path"], "r") as f:
                content = f.read()
            self.assertIn("BNK-RECON-2026-06", content)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestReconciliationCleanup(unittest.TestCase):
    def test_cleanup_borra_tags(self):
        skill, qbo, tmpdir, engine = make_skill(
            qbo=MockQBOClient(transactions=[
                {"id": "q1", "type": "Deposit", "date": "2026-06-15",
                 "amount": 100.0, "account_id": "bank_1"}
            ])
        )
        try:
            path = write_csv(tmpdir, "b.csv", [
                {"date": "2026-06-15", "description": "A", "amount": 100.0}
            ])
            bid = skill.from_csv(path)
            skill.run(bid)
            # Guardar report_path en el batch summary
            summary = engine.storage.get_batch(bid)
            assert summary is not None
            qbo.updates.clear()
            result = skill.cleanup_tags(bid)
            self.assertEqual(result["removed"], 1)
            self.assertEqual(qbo.updates[0]["fields"]["Memo"], "")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
