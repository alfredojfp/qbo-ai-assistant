"""Tests para HIGH-2: CSV deposits con columnas bank_account / line_account.

HIGH-2: El CSV puede especificar cuentas por línea:
  - bank_account → DepositToAccountRef (override del default)
  - line_account → AccountRef de la línea (cualquier tipo: Income, Liability, Asset)
  - Ambas son opcionales. Si no se dan, se usan los defaults auto-detectados.
"""
import csv
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dexter.core.batch.deposits import DepositBatchSkill
from dexter.core.batch.disambiguator import Disambiguator
from dexter.core.batch.engine import BatchEngine
from dexter.core.batch.storage import BatchStorage


class FakeQBOClient:
    """QBO simulado para tests. Soporta search_customer y create_deposit."""

    def __init__(self, known_customers=None):
        self.known = known_customers or {}
        self.created_customers = []
        self.created_deposits = []

    def search_customer(self, name: str):
        if name in self.known:
            return [{"id": self.known[name], "name": name}]
        return []

    def create_customer(self, data):
        cid = f"cust_{len(self.created_customers) + 1}"
        display_name = data.get("DisplayName", data.get("name", "?"))
        self.created_customers.append({"id": cid, "name": display_name})
        return {"Id": cid, "DisplayName": display_name}

    def create_deposit(self, date, account_id, lines, memo=None):
        did = f"dep_{len(self.created_deposits) + 1}"
        total = sum(l["amount"] for l in lines)
        self.created_deposits.append({
            "deposit_id": did,
            "total": total,
            "date": date,
            "_account_id": account_id,
            "_lines": lines,
            "_memo": memo,
        })
        return {"deposit_id": did, "total": total, "date": date}


def make_csv(rows, path):
    fields = rows[0].keys() if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class TestHigh2BasicBackwardCompat(unittest.TestCase):
    """CSV sin bank_account ni line_account sigue funcionando."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.tmp, "test_basic.csv")
        self.db_path = os.path.join(self.tmp, "test.db")

    def test_csv_sin_columnas_nuevas_funciona(self):
        """CSV con solo date,client_name,amount debe funcionar sin error."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00"},
            {"date": "2026-06-15", "client_name": "Jane Doe", "amount": "500.00"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1", "Jane Doe": "cs2"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_99",
            income_account_id="income_42",
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        # HIGH-2 grouping: mismo date+bank → 1 depósito con 2 líneas
        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "bank_99")
        self.assertEqual(len(qbo.created_deposits[0]["_lines"]), 2)
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "income_42")

    def test_csv_con_columnas_viejas_backward_compat(self):
        """from_account y to_account del template legacy se mapean a line_account y bank_account."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "from_account": "Legacy Income", "to_account": "Legacy Bank"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        def mock_finder(name, exact=False, category=None):
            if "Legacy Income" in name:
                return [{"id": "li_99", "name": "Legacy Income", "type": "Income"}]
            if "Legacy Bank" in name:
                return [{"id": "lb_99", "name": "Legacy Bank", "type": "Bank"}]
            return []

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=mock_finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "lb_99")
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "li_99")


class TestHigh2PerLineAccounts(unittest.TestCase):
    """bank_account y line_account por línea."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.tmp, "test_perline.csv")
        self.db_path = os.path.join(self.tmp, "test_perline.db")

        def mock_finder(name, exact=False, category=None):
            accounts = {
                "Business Account": [{"id": "ba_100", "name": "Business Account", "type": "Bank"}],
                "Customer Deposits": [{"id": "cd_2100", "name": "Customer Deposits", "type": "Other Current Liability"}],
                "Sales": [{"id": "s_252", "name": "Sales", "type": "Income"}],
            }
            return accounts.get(name, [])

        self.finder = mock_finder

    def test_line_account_liability(self):
        """line_account puede ser pasivo (ej. Customer Deposits)."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "bank_account": "Business Account", "line_account": "Customer Deposits"},
            {"date": "2026-06-15", "client_name": "Jane Doe", "amount": "500.00",
             "bank_account": "Business Account", "line_account": "Customer Deposits"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1", "Jane Doe": "cs2"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=self.finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        # HIGH-2 grouping: mismo date+bank → 1 depósito con 2 líneas
        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "ba_100")
        self.assertEqual(len(qbo.created_deposits[0]["_lines"]), 2)
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "cd_2100")
        self.assertEqual(qbo.created_deposits[0]["_lines"][1]["from_account_id"], "cd_2100")

    def test_mixed_per_line_accounts(self):
        """Diferentes cuentas por línea dentro del mismo batch."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "bank_account": "Business Account", "line_account": "Customer Deposits"},
            {"date": "2026-06-15", "client_name": "Jane Doe", "amount": "500.00",
             "bank_account": "Business Account", "line_account": "Sales"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1", "Jane Doe": "cs2"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=self.finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        # HIGH-2 grouping: mismo date+bank → 1 depósito con 2 líneas, diferentes cuentas
        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "cd_2100")
        self.assertEqual(qbo.created_deposits[0]["_lines"][1]["from_account_id"], "s_252")

    def test_only_bank_account_no_line_account(self):
        """Solo bank_account especificado, line_account usa default."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "bank_account": "Business Account"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=self.finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "ba_100")
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "income_default")

    def test_only_line_account_no_bank_account(self):
        """Solo line_account especificado, bank_account usa default."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "line_account": "Sales"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=self.finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "bank_default")
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "s_252")

    def test_account_finder_not_provided_uses_defaults(self):
        """Sin account_finder inyectado, las columnas se ignoran y usan defaults."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "bank_account": "Business Account", "line_account": "Customer Deposits"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            # NO account_finder
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(len(qbo.created_deposits), 1)
        self.assertEqual(qbo.created_deposits[0]["_account_id"], "bank_default")
        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "income_default")

    def test_classifier_still_overrides_when_no_line_account(self):
        """Si no hay line_account en el CSV pero hay classifier, el classifier gana."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        def dummy_classifier(desc, amt):
            return {"account_id": "classified_99"}

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            classifier=dummy_classifier,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "classified_99")

    def test_line_account_skips_classifier(self):
        """Si line_account está en el CSV, el classifier NO se usa."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "line_account": "Sales"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        def dummy_classifier(desc, amt):
            return {"account_id": "SHOULD_NOT_BE_USED"}

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=self.finder,
            classifier=dummy_classifier,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "s_252")


class TestHigh2AccountFuzzyDisambiguation(unittest.TestCase):
    """Cuentas con múltiples matches preguntan al usuario vía Disambiguator."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.tmp, "test_fuzzy.csv")
        self.db_path = os.path.join(self.tmp, "test_fuzzy.db")

    def test_multiple_candidates_asks_user(self):
        """Cuando hay múltiples candidatos para una cuenta, se pregunta."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "line_account": "Sales"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        self.user_choices = ["1"]
        disambiguator = Disambiguator(
            input_func=lambda prompt: self.user_choices.pop(0),
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        def mock_finder(name, exact=False, category=None):
            return [
                {"id": "s99", "name": "Sales Revenue", "type": "Income"},
                {"id": "s100", "name": "Sales of Product", "type": "Income"},
            ]

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=mock_finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "s99")

    def test_cuenta_no_encontrada_usa_default(self):
        """Si la cuenta no existe en el Chart, se ignora y usa default."""
        make_csv([
            {"date": "2026-06-15", "client_name": "John Smith", "amount": "1000.00",
             "line_account": "Ghost Account XYZ"},
        ], self.csv_path)

        storage = BatchStorage(self.db_path)
        engine = BatchEngine(storage)
        disambiguator = Disambiguator(
            input_func=lambda _: "",
            output_func=lambda s: None,
        )
        qbo = FakeQBOClient(known_customers={"John Smith": "cs1"})

        def mock_finder(name, exact=False, category=None):
            return []

        skill = DepositBatchSkill(
            engine=engine,
            disambiguator=disambiguator,
            qbo_client=qbo,
            bank_account_id="bank_default",
            income_account_id="income_default",
            account_finder=mock_finder,
        )
        batch_id = skill.from_csv(self.csv_path)
        skill.validate(batch_id)
        engine.dry_run(batch_id)
        engine.confirm(batch_id)
        skill.execute(batch_id)

        self.assertEqual(qbo.created_deposits[0]["_lines"][0]["from_account_id"], "income_default")


if __name__ == "__main__":
    unittest.main()
