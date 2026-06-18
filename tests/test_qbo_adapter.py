"""Tests for QBOAdapter — QBOClientProtocol via MCP server (HIGH-3).

Tests validate argument translation to Intuit MCP Zod schemas.
"""
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dexter.core.qbo_adapter import QBOAdapter


class MockMCPBridge:
    def __init__(self, tools_map=None):
        self._tools = tools_map or {}
        self._calls = []

    def start(self):
        pass

    def stop(self):
        pass

    def call_tool(self, name, arguments=None):
        self._calls.append((name, arguments or {}))
        handler = self._tools.get(name)
        if handler:
            return handler(arguments or {})
        return {}


class TestQBOAdapterSearchCustomer(unittest.TestCase):

    def test_uses_criteria_format(self):
        """search_customers expects {criteria: [{field, operator, value}]}."""
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: [{"Id": "42", "DisplayName": "John"}]
        })
        adapter = QBOAdapter(mock)
        adapter.search_customer("John")
        args = mock._calls[0][1]
        self.assertIn("criteria", args)
        self.assertEqual(args["criteria"][0]["field"], "DisplayName")
        self.assertEqual(args["criteria"][0]["operator"], "LIKE")
        self.assertEqual(args["criteria"][0]["value"], "John")

    def test_returns_dexter_lowercase_format(self):
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: [
                {"Id": "42", "DisplayName": "John Smith", "CompanyName": "ACME",
                 "Balance": 100.0, "Active": True}
            ]
        })
        adapter = QBOAdapter(mock)
        results = adapter.search_customer("John")
        self.assertEqual(results[0]["id"], "42")
        self.assertEqual(results[0]["name"], "John Smith")

    def test_fuzzy_fallback_when_no_results(self):
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: []
        })
        with patch("dexter.skills.search.fuzzy.find_similar_customers",
                   return_value=[{"id": "99", "name": "Jon", "_fuzzy_score": 0.87}]):
            adapter = QBOAdapter(mock)
            results = adapter.search_customer("John")
            self.assertGreaterEqual(len(results), 1)
            self.assertIn("_fuzzy_score", results[0])


class TestQBOAdapterCreateCustomer(unittest.TestCase):

    def test_wraps_in_customer_object(self):
        """create_customer expects {customer: {DisplayName, ...}}."""
        mock = MockMCPBridge(tools_map={
            "create_customer": lambda a: {"Id": "100", "DisplayName": "New"}
        })
        adapter = QBOAdapter(mock)
        adapter.create_customer({"DisplayName": "New Corp", "CompanyName": "New LLC"})
        args = mock._calls[0][1]
        self.assertIn("customer", args)
        self.assertEqual(args["customer"]["DisplayName"], "New Corp")
        self.assertEqual(args["customer"]["CompanyName"], "New LLC")


class TestQBOAdapterCreateDeposit(unittest.TestCase):

    def test_uses_snake_case_zod_format(self):
        """create_deposit expects {deposit_to_account_ref, line_items, txn_date, private_note}."""
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {"Deposit": {"Id": "d1", "TotalAmt": 100.0, "TxnDate": "2026-06-15"}}
        })
        adapter = QBOAdapter(mock)
        adapter.create_deposit(
            date="2026-06-15",
            account_id="226",
            lines=[{"amount": 100.0, "from_account_id": "250", "description": "Carl"}],
            memo="test",
        )
        args = mock._calls[0][1]
        self.assertEqual(args["deposit_to_account_ref"], "226")
        self.assertEqual(args["line_items"][0]["amount"], 100.0)
        self.assertEqual(args["line_items"][0]["account_ref"], "250")
        self.assertEqual(args["line_items"][0]["description"], "Carl")
        self.assertEqual(args["txn_date"], "2026-06-15")
        self.assertEqual(args["private_note"], "test")

    def test_no_customer_id_in_line_items(self):
        """Intuit MCP create_deposit does NOT support entity/customer on lines."""
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {"Deposit": {"Id": "d1", "TotalAmt": 1.0, "TxnDate": "2026-01-01"}}
        })
        adapter = QBOAdapter(mock)
        adapter.create_deposit(
            date="2026-01-01", account_id="1",
            lines=[{"amount": 1.0, "from_account_id": "2", "customer_id": "999"}],
        )
        args = mock._calls[0][1]
        self.assertNotIn("customer_id", args["line_items"][0])
        self.assertNotIn("entity", args["line_items"][0])


class TestQBOAdapterUpdateTransaction(unittest.TestCase):

    def test_update_deposit_uses_private_note(self):
        """update_deposit expects {id, sync_token, private_note}."""
        mock = MockMCPBridge(tools_map={
            "update_deposit": lambda a: {"Deposit": {"Id": a["id"]}}
        })
        adapter = QBOAdapter(mock)
        adapter.update_transaction("Deposit", "dep_1", {"Memo": "BNK-RECON-tag"}, sync_token="1")
        args = mock._calls[0][1]
        self.assertEqual(args["id"], "dep_1")
        self.assertEqual(args["sync_token"], "1")
        self.assertEqual(args["private_note"], "BNK-RECON-tag")

    def test_update_purchase_wraps_in_object(self):
        mock = MockMCPBridge(tools_map={
            "update_purchase": lambda a: {"Purchase": {"Id": "p1"}}
        })
        adapter = QBOAdapter(mock)
        adapter.update_transaction("Purchase", "p1", {"PrivateNote": "tag"}, sync_token="2")
        args = mock._calls[0][1]["purchase"]
        self.assertEqual(args["Id"], "p1")
        self.assertEqual(args["SyncToken"], "2")
        self.assertEqual(args["PrivateNote"], "tag")

    def test_unknown_type_raises(self):
        mock = MockMCPBridge()
        adapter = QBOAdapter(mock)
        with self.assertRaises(ValueError):
            adapter.update_transaction("Unknown", "id", {})

    def test_get_transactions_uses_txn_date_range(self):
        mock = MockMCPBridge(tools_map={
            "search_deposits": lambda a: [{"Id": "d1", "TxnDate": "2026-06-15", "TotalAmt": 100,
                                           "DepositToAccountRef": {"value": "bank_1"}}],
            "search_purchases": lambda a: [],
        })
        adapter = QBOAdapter(mock)
        txns = adapter.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        call = mock._calls[0]  # search_deposits call
        self.assertEqual(call[0], "search_deposits")
        self.assertEqual(call[1]["txn_date_from"], "2026-06-01")
        self.assertEqual(call[1]["txn_date_to"], "2026-06-30")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["type"], "Deposit")
