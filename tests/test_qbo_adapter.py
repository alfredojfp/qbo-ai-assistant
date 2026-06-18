"""Tests for QBOAdapter — QBOClientProtocol via MCP server."""
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dexter.core.qbo_adapter import QBOAdapter


class MockMCPBridge:
    """Simulates MCPBridge for isolated unit tests."""

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

    def test_calls_search_customers_mcp_tool(self):
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: {"QueryResponse": {"Customer": []}}
        })
        adapter = QBOAdapter(mock)
        adapter.search_customer("John")
        self.assertEqual(mock._calls[0][0], "search_customers")
        self.assertEqual(mock._calls[0][1]["searchTerm"], "John")

    def test_returns_dexter_format_lowercase_keys(self):
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: {
                "QueryResponse": {
                    "Customer": [{
                        "Id": "42",
                        "DisplayName": "John Smith",
                        "CompanyName": "ACME",
                        "Balance": 100.0,
                        "Active": True,
                    }]
                }
            }
        })
        adapter = QBOAdapter(mock)
        results = adapter.search_customer("John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "42")
        self.assertEqual(results[0]["name"], "John Smith")

    def test_fuzzy_fallback_when_mcp_returns_nothing(self):
        mock = MockMCPBridge(tools_map={
            "search_customers": lambda a: {"QueryResponse": {}}
        })
        # Patch the fuzzy import that would trigger full main.py load
        fake_fuzzy = [
            {"id": "99", "name": "Jon Smith", "balance": 0, "active": True, "company": "",
             "_fuzzy_score": 0.87},
        ]
        with patch(
            "dexter.skills.search.fuzzy.find_similar_customers",
            return_value=fake_fuzzy,
        ):
            adapter = QBOAdapter(mock)
            results = adapter.search_customer("John Smith")
            self.assertGreaterEqual(len(results), 1)
            self.assertIn("_fuzzy_score", results[0])


class TestQBOAdapterCreateCustomer(unittest.TestCase):

    def test_calls_create_customer_with_display_name(self):
        mock = MockMCPBridge(tools_map={
            "create_customer": lambda a: {
                "Customer": {"Id": "100", "DisplayName": a.get("displayName", "")}
            }
        })
        adapter = QBOAdapter(mock)
        result = adapter.create_customer({
            "DisplayName": "New Corp",
            "PrimaryEmailAddr": {"Address": "test@test.com"},
            "CompanyName": "New Corp LLC",
        })
        self.assertEqual(result["Id"], "100")
        self.assertEqual(result["DisplayName"], "New Corp")
        call = mock._calls[0]
        self.assertIn("companyName", call[1])

    def test_handles_name_field_for_backward_compat(self):
        mock = MockMCPBridge(tools_map={
            "create_customer": lambda a: {
                "Customer": {"Id": "50", "DisplayName": a["displayName"]}
            }
        })
        adapter = QBOAdapter(mock)
        result = adapter.create_customer({"name": "Old Format"})
        self.assertEqual(result["DisplayName"], "Old Format")

    def test_email_string_not_dict(self):
        mock = MockMCPBridge(tools_map={
            "create_customer": lambda a: {
                "Customer": {"Id": "1", "DisplayName": "X"}
            }
        })
        adapter = QBOAdapter(mock)
        adapter.create_customer({"DisplayName": "X", "PrimaryEmailAddr": "test@x.com"})
        self.assertEqual(mock._calls[0][1]["email"], "test@x.com")


class TestQBOAdapterCreateDeposit(unittest.TestCase):

    def test_creates_single_line_deposit(self):
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {
                "Deposit": {"Id": "dep_1", "TotalAmt": 500.0, "TxnDate": "2026-06-15"}
            }
        })
        adapter = QBOAdapter(mock)
        result = adapter.create_deposit(
            date="2026-06-15",
            account_id="226",
            lines=[{"amount": 500.0, "from_account_id": "250"}],
        )
        self.assertEqual(result["deposit_id"], "dep_1")
        self.assertEqual(result["total"], 500.0)

    def test_entity_uses_flat_format(self):
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {
                "Deposit": {"Id": "d1", "TotalAmt": 100.0, "TxnDate": "2026-01-01"}
            }
        })
        adapter = QBOAdapter(mock)
        adapter.create_deposit(
            date="2026-01-01",
            account_id="5",
            lines=[{
                "amount": 100.0,
                "from_account_id": "10",
                "customer_id": "3575",
            }],
        )
        call = mock._calls[0]
        entity = call[1]["line"][0]["entity"]
        self.assertEqual(entity["value"], "3575")
        self.assertEqual(entity["type"], "Customer")
        self.assertNotIn("Type", entity)
        self.assertNotIn("EntityRef", entity)

    def test_second_line_without_customer_has_no_entity(self):
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {
                "Deposit": {"Id": "d1", "TotalAmt": 300.0, "TxnDate": "2026-01-01"}
            }
        })
        adapter = QBOAdapter(mock)
        adapter.create_deposit(
            date="2026-01-01",
            account_id="5",
            lines=[
                {"amount": 100.0, "from_account_id": "10", "customer_id": "1"},
                {"amount": 200.0, "from_account_id": "10"},
            ],
        )
        call = mock._calls[0]
        self.assertIn("entity", call[1]["line"][0])
        self.assertNotIn("entity", call[1]["line"][1])

    def test_memo_becomes_private_note(self):
        mock = MockMCPBridge(tools_map={
            "create_deposit": lambda a: {
                "Deposit": {"Id": "d1", "TotalAmt": 1.0, "TxnDate": "2026-01-01"}
            }
        })
        adapter = QBOAdapter(mock)
        adapter.create_deposit(
            date="2026-01-01", account_id="1",
            lines=[{"amount": 1.0, "from_account_id": "2"}],
            memo="Test memo",
        )
        self.assertEqual(mock._calls[0][1]["privateNote"], "Test memo")


class TestQBOAdapterUpdateTransaction(unittest.TestCase):

    def test_update_deposit_calls_update_deposit(self):
        mock = MockMCPBridge(tools_map={
            "update_deposit": lambda a: {
                "Deposit": {"Id": a["id"], "Memo": a.get("Memo", "")}
            }
        })
        adapter = QBOAdapter(mock)
        result = adapter.update_transaction(
            "Deposit", "dep_1", {"Memo": "BNK-RECON-tag"}, sync_token="1"
        )
        self.assertIn("Deposit", result)
        call = mock._calls[0]
        self.assertEqual(call[0], "update_deposit")
        self.assertEqual(call[1]["syncToken"], "1")

    def test_unknown_type_raises(self):
        mock = MockMCPBridge()
        adapter = QBOAdapter(mock)
        with self.assertRaises(ValueError):
            adapter.update_transaction("Unknown", "id", {})

    def test_get_transactions_returns_formatted_list(self):
        mock = MockMCPBridge(tools_map={
            "search_deposits": lambda a: {
                "QueryResponse": {"Deposit": [
                    {"Id": "d1", "TxnDate": "2026-06-15", "TotalAmt": 100,
                     "DepositToAccountRef": {"value": "bank_1"}},
                ]}
            },
            "search_purchases": lambda a: {"QueryResponse": {"Purchase": []}},
        })
        adapter = QBOAdapter(mock)
        txns = adapter.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0]["type"], "Deposit")
        self.assertEqual(txns[0]["id"], "d1")
        self.assertEqual(txns[0]["account_id"], "bank_1")
