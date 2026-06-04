# -*- coding: utf-8 -*-
"""
Tests para DepositBatchSkill (Sprint 2 deliverable).
Ejecutar: python -m unittest tests.test_batch_deposits
"""
import csv
import os
import shutil
import tempfile
import unittest

from dexter.core.batch import (
    BatchEngine, BatchState, BatchStorage, Disambiguator,
    DepositBatchSkill, ItemState
)


class MockQBOClient:
    """Mock del cliente QBO para tests."""

    def __init__(self, existing_customers=None):
        self.existing = {c["name"]: c for c in (existing_customers or [])}
        self.created = []
        self.deposits_created = []
        self._next_id = 1000

    def search_customer(self, name):
        results = []
        for c in self.existing.values():
            if c["name"].lower() == name.lower():
                results.append(c)
        return results

    def create_customer(self, data):
        cid = str(self._next_id)
        self._next_id += 1
        new = {
            "id": cid,
            "name": data["name"],
            "email": data.get("email", ""),
        }
        self.existing[data["name"]] = new
        self.created.append(new)
        return new

    def create_deposit(self, date, account_id, lines, memo=None):
        did = str(self._next_id)
        self._next_id += 1
        d = {
            "id": did,
            "date": date,
            "account_id": account_id,
            "lines": lines,
            "memo": memo,
        }
        self.deposits_created.append(d)
        return d


class MockIO:
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


def setup_skill(responses=None, existing_customers=None):
    """Helper: crea engine + storage + disambiguator + skill con QBO mock."""
    tmpdir = tempfile.mkdtemp()
    storage = BatchStorage(os.path.join(tmpdir, "test.db"))
    engine = BatchEngine(storage)
    io = MockIO(responses or [])
    disambiguator = Disambiguator(input_func=io, output_func=io.output)
    qbo = MockQBOClient(existing_customers=existing_customers)
    skill = DepositBatchSkill(
        engine=engine,
        disambiguator=disambiguator,
        qbo_client=qbo,
        bank_account_id="bank_1",
        income_account_id="income_1"
    )
    return skill, qbo, tmpdir, io


class TestDepositSkillSetup(unittest.TestCase):
    def test_skill_crea_batch_desde_csv(self):
        skill, qbo, tmpdir, io = setup_skill()
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME", "amount": 1000.0})
            bid = skill.from_csv(csv_path)
            self.assertIsInstance(bid, str)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestDepositSkillValidation(unittest.TestCase):
    def test_cliente_existente_se_resuelve_sin_preguntar(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME Corp"}]
        )
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME Corp", "amount": 1000.0})
            bid = skill.from_csv(csv_path)
            result = skill.validate(bid)
            self.assertEqual(result["ready"], 1)
            self.assertEqual(result["failed"], 0)
            self.assertEqual(result["resolved_clients"]["ACME Corp"], "42")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_cliente_nuevo_se_pregunta_y_se_crea(self):
        skill, qbo, tmpdir, io = setup_skill(responses=[
            "s",  # sí crear
            "maria@x.com",  # email
            "Net 30",  # terms
            "",  # phone vacío
            "",  # company vacío
        ])
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "Maria", "amount": 500.0})
            bid = skill.from_csv(csv_path)
            result = skill.validate(bid)
            self.assertEqual(result["ready"], 1)
            self.assertEqual(len(qbo.created), 1)
            self.assertEqual(qbo.created[0]["name"], "Maria")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_usuario_cancela_creacion_item_falla(self):
        skill, qbo, tmpdir, io = setup_skill(responses=["n"])  # no crear
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "Maria", "amount": 500.0})
            bid = skill.from_csv(csv_path)
            result = skill.validate(bid)
            self.assertEqual(result["ready"], 0)
            self.assertEqual(result["failed"], 1)
            self.assertEqual(len(qbo.created), 0)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_multiples_clientes_algunos_existen_algunos_nuevos(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME Corp"}],
            responses=[
                "s", "jose@x.com", "Net 15", "", ""  # crear José
            ]
        )
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME Corp", "amount": 1000.0})
                writer.writerow({"date": "2026-06-01", "client_name": "Jose", "amount": 500.0})
            bid = skill.from_csv(csv_path)
            result = skill.validate(bid)
            self.assertEqual(result["ready"], 2)
            self.assertEqual(result["failed"], 0)
            self.assertEqual(len(qbo.created), 1)  # solo Jose fue creado
            self.assertEqual(result["resolved_clients"]["ACME Corp"], "42")
            self.assertIn("Jose", result["resolved_clients"])
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestDepositSkillExecute(unittest.TestCase):
    def test_execute_crea_deposit_por_cada_item(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME Corp"}]
        )
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME Corp", "amount": 1000.0})
                writer.writerow({"date": "2026-06-01", "client_name": "ACME Corp", "amount": 500.0})
            bid = skill.from_csv(csv_path)
            skill.validate(bid)
            skill.engine.dry_run(bid)
            skill.engine.confirm(bid)
            result = skill.execute(bid)
            self.assertEqual(result["executed"], 2)
            self.assertEqual(len(qbo.deposits_created), 2)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_execute_con_classifier_usa_cuenta_sugerida(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME"}]
        )
        try:
            def fake_classifier(desc, amount):
                return {
                    "account_id": "income_special",
                    "account_name": "Special Income",
                    "confidence": 90,
                    "match_type": "exact"
                }
            skill.classifier = fake_classifier
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME", "amount": 1000.0})
            bid = skill.from_csv(csv_path)
            skill.validate(bid)
            skill.engine.dry_run(bid)
            skill.engine.confirm(bid)
            skill.execute(bid)
            self.assertEqual(qbo.deposits_created[0]["lines"][0]["from_account_id"],
                          "income_special")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_execute_falla_si_no_se_confirmo(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME"}]
        )
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME", "amount": 1000.0})
            bid = skill.from_csv(csv_path)
            skill.validate(bid)
            skill.engine.dry_run(bid)
            # No confirmamos
            from dexter.core.batch.engine import InvalidStateTransition
            with self.assertRaises(InvalidStateTransition):
                skill.execute(bid)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestDepositSkillCSVErrors(unittest.TestCase):
    def test_csv_sin_columnas_requeridas_falla(self):
        skill, qbo, tmpdir, io = setup_skill()
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "amount": 1000.0})
            with self.assertRaises(ValueError):
                skill.from_csv(csv_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_csv_vacio_falla(self):
        skill, qbo, tmpdir, io = setup_skill()
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
            with self.assertRaises(ValueError):
                skill.from_csv(csv_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_csv_no_existe_falla(self):
        skill, qbo, tmpdir, io = setup_skill()
        try:
            with self.assertRaises(FileNotFoundError):
                skill.from_csv("/no/existe.csv")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_monto_invalido_falla(self):
        skill, qbo, tmpdir, io = setup_skill()
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME", "amount": "no-es-numero"})
            with self.assertRaises(ValueError):
                skill.from_csv(csv_path)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestAuditLog(unittest.TestCase):
    def test_audit_log_captura_todo_el_ciclo(self):
        skill, qbo, tmpdir, io = setup_skill(
            existing_customers=[{"id": "42", "name": "ACME"}]
        )
        try:
            csv_path = os.path.join(tmpdir, "deps.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "client_name", "amount"])
                writer.writeheader()
                writer.writerow({"date": "2026-06-01", "client_name": "ACME", "amount": 1000.0})
            bid = skill.from_csv(csv_path)
            skill.validate(bid)
            skill.engine.dry_run(bid)
            skill.engine.confirm(bid)
            skill.execute(bid)
            log = skill.engine.storage.get_audit_log(bid)
            events = [e["event"] for e in log]
            self.assertIn("BATCH_CREATED", events)
            self.assertIn("BATCH_STATE_CHANGED", events)
            self.assertIn("ITEM_ADDED", events)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
