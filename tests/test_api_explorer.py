# -*- coding: utf-8 -*-
"""
Tests para autonomia.autonomia_nivel2_api_explorer.
Ejecutar: python3 -m unittest tests.test_api_explorer
"""
import os
import unittest
from unittest.mock import patch, MagicMock

from autonomia.autonomia_nivel2_api_explorer import (
    tool_list_qbo_endpoints,
    tool_get_endpoint_info,
    tool_qbo_generic_request,
    tool_create_journal_entry,
    tool_create_transfer,
    QBO_ENDPOINTS,
)


class TestListQBOEndpoints(unittest.TestCase):
    def test_retorna_lista(self):
        result = tool_list_qbo_endpoints()
        self.assertTrue(result["success"])
        self.assertIn("endpoints", result)
        self.assertIn("endpoints_count", result)

    def test_incluye_endpoints_comunes(self):
        result = tool_list_qbo_endpoints()
        names = list(result["endpoints"].keys())
        for required in ["JournalEntry", "Transfer", "Invoice", "Bill", "Deposit"]:
            self.assertIn(required, names)

    def test_cada_endpoint_tiene_descripcion(self):
        result = tool_list_qbo_endpoints()
        for name, info in result["endpoints"].items():
            self.assertIn("description", info)
            self.assertIn("methods", info)


class TestGetEndpointInfo(unittest.TestCase):
    def test_journal_entry(self):
        result = tool_get_endpoint_info("JournalEntry")
        self.assertTrue(result["success"])
        self.assertEqual(result["endpoint"], "JournalEntry")
        self.assertIn("POST", result["info"]["methods"])

    def test_transfer(self):
        result = tool_get_endpoint_info("Transfer")
        self.assertTrue(result["success"])
        self.assertEqual(result["endpoint"], "Transfer")

    def test_invoice(self):
        result = tool_get_endpoint_info("Invoice")
        self.assertTrue(result["success"])

    def test_endpoint_desconocido(self):
        result = tool_get_endpoint_info("NonExistent")
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestQBOGenericRequest(unittest.TestCase):
    @patch("requests.get")
    def test_get_exitoso(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_qbo_generic_request("GET", "Customer")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], {"data": "ok"})

    @patch("requests.get")
    def test_get_con_entity_id(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Id": "1"}
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_qbo_generic_request("GET", "Customer", entity_id="42")
        self.assertTrue(result["success"])
        # Verifica que llamó a customer/42
        called_url = mock_get.call_args[0][0]
        self.assertIn("customer/42", called_url)

    @patch("requests.post")
    def test_post_exitoso(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Id": "100"}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_qbo_generic_request("POST", "Customer", data={"DisplayName": "X"})
        self.assertTrue(result["success"])

    def test_metodo_no_soportado(self):
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_qbo_generic_request("DELETE", "Customer")
        self.assertFalse(result["success"])

    @patch("requests.get")
    def test_error_http(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_qbo_generic_request("GET", "Customer", entity_id="999")
        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 404)


class TestCreateJournalEntry(unittest.TestCase):
    @patch("requests.post")
    def test_asiento_cuadrado_exitoso(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"JournalEntry": {"Id": "je_1"}}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_journal_entry(
                lines=[
                    {"account_id": "acc_1", "amount": 100.0, "posting_type": "Debit",
                     "description": "Debe"},
                    {"account_id": "acc_2", "amount": 100.0, "posting_type": "Credit",
                     "description": "Haber"},
                ],
                txn_date="2026-06-15",
                memo="Asiento test",
            )
        self.assertTrue(result["success"])
        # Verifica que el payload tiene las líneas correctas
        payload = mock_post.call_args[1]["json"]
        self.assertEqual(len(payload["Line"]), 2)
        self.assertEqual(payload["TxnDate"], "2026-06-15")
        self.assertEqual(payload["PrivateNote"], "Asiento test")

    def test_asiento_descuadrado_retorna_error(self):
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_journal_entry(
                lines=[
                    {"account_id": "acc_1", "amount": 100.0, "posting_type": "Debit"},
                    {"account_id": "acc_2", "amount": 50.0, "posting_type": "Credit"},
                ],
                txn_date="2026-06-15",
            )
        self.assertFalse(result["success"])
        self.assertIn("descuadrado", result["error"].lower())

    def test_asiento_sin_lineas(self):
        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_journal_entry(
                lines=[],
                txn_date="2026-06-15",
            )
        self.assertFalse(result["success"])

    @patch("requests.post")
    def test_asiento_sin_memo(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"JournalEntry": {"Id": "1"}}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_journal_entry(
                lines=[
                    {"account_id": "acc_1", "amount": 50.0, "posting_type": "Debit"},
                    {"account_id": "acc_2", "amount": 50.0, "posting_type": "Credit"},
                ],
                txn_date="2026-06-15",
            )
        self.assertTrue(result["success"])
        payload = mock_post.call_args[1]["json"]
        self.assertNotIn("PrivateNote", payload)


class TestCreateTransfer(unittest.TestCase):
    @patch("requests.post")
    def test_transferencia_exitosa(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Transfer": {"Id": "tr_1"}}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_transfer(
                from_account_id="bank_1",
                to_account_id="bank_2",
                amount=500.0,
                txn_date="2026-06-15",
                memo="Transfer test",
            )
        self.assertTrue(result["success"])
        payload = mock_post.call_args[1]["json"]
        self.assertEqual(payload["FromAccountRef"]["value"], "bank_1")
        self.assertEqual(payload["ToAccountRef"]["value"], "bank_2")
        self.assertEqual(payload["Amount"], 500.0)
        self.assertEqual(payload["PrivateNote"], "Transfer test")

    @patch("requests.post")
    def test_transferencia_sin_memo(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Transfer": {"Id": "tr_1"}}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            "QB_ACCESS_TOKEN": "tok",
            "QB_REALM_ID": "realm",
        }):
            result = tool_create_transfer(
                from_account_id="bank_1",
                to_account_id="bank_2",
                amount=100.0,
                txn_date="2026-06-15",
            )
        self.assertTrue(result["success"])
        payload = mock_post.call_args[1]["json"]
        self.assertNotIn("PrivateNote", payload)


class TestQBOEndpointsRegistry(unittest.TestCase):
    def test_tiene_minimo_10_endpoints(self):
        self.assertGreaterEqual(len(QBO_ENDPOINTS), 10)

    def test_todos_tienen_description_y_methods(self):
        for name, info in QBO_ENDPOINTS.items():
            self.assertIn("description", info, f"{name} sin description")
            self.assertIn("methods", info, f"{name} sin methods")
            self.assertIsInstance(info["methods"], list)


if __name__ == "__main__":
    unittest.main()
