# -*- coding: utf-8 -*-
"""
Tests para dexter.core.qbo_client.
Ejecutar: python3 -m unittest tests.test_qbo_client
"""
import unittest
from unittest.mock import MagicMock

from dexter.core.qbo_client import (
    QBOClientImpl, QBOClientError, make_qbo_client, find_bank_account_id,
)


class TestQBOClientGetTransactions(unittest.TestCase):
    def test_consulta_deposits(self):
        query = MagicMock(return_value={
            "QueryResponse": {
                "Deposit": [{
                    "Id": "100",
                    "TxnDate": "2026-06-15",
                    "TotalAmt": "500.00",
                    "DepositToAccountRef": {"value": "bank_1"},
                }]
            }
        })
        request = MagicMock()
        client = QBOClientImpl(query, request)

        result = client.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        # Llama query para Deposit, Purchase, Transfer
        self.assertEqual(query.call_count, 3)
        # Solo Deposit tuvo resultado
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "100")
        self.assertEqual(result[0]["type"], "Deposit")
        self.assertEqual(result[0]["amount"], 500.0)

    def test_consulta_purchases(self):
        query = MagicMock(return_value={
            "QueryResponse": {
                "Purchase": [{
                    "Id": "200",
                    "TxnDate": "2026-06-15",
                    "TotalAmt": "75.50",
                    "AccountRef": {"value": "bank_1"},
                }]
            }
        })
        client = QBOClientImpl(query, MagicMock())
        result = client.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "Purchase")
        self.assertEqual(result[0]["amount"], 75.5)

    def test_consulta_transfers(self):
        query = MagicMock(return_value={
            "QueryResponse": {
                "Transfer": [{
                    "Id": "300",
                    "TxnDate": "2026-06-15",
                    "Amount": "1000.00",
                    "FromAccountRef": {"value": "bank_1"},
                }]
            }
        })
        client = QBOClientImpl(query, MagicMock())
        result = client.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "Transfer")

    def test_respuesta_sin_queryresponse(self):
        query = MagicMock(return_value={"error": "bad query"})
        client = QBOClientImpl(query, MagicMock())
        result = client.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        self.assertEqual(result, [])

    def test_respuesta_lista_vacia(self):
        query = MagicMock(return_value={"QueryResponse": {"Deposit": []}})
        client = QBOClientImpl(query, MagicMock())
        result = client.get_transactions("bank_1", "2026-06-01", "2026-06-30")
        self.assertEqual(result, [])

    def test_query_sql_incluye_cuenta_y_fechas(self):
        query = MagicMock(return_value={"QueryResponse": {"Deposit": []}})
        client = QBOClientImpl(query, MagicMock())
        client.get_transactions("bank_42", "2026-06-01", "2026-06-30")
        deposit_call = query.call_args_list[0][0][0]
        self.assertIn("bank_42", deposit_call)
        self.assertIn("2026-06-01", deposit_call)
        self.assertIn("2026-06-30", deposit_call)
        self.assertIn("Deposit", deposit_call)

    def test_transfer_query_usa_or(self):
        query = MagicMock(return_value={"QueryResponse": {"Transfer": []}})
        client = QBOClientImpl(query, MagicMock())
        client.get_transactions("bank_42", "2026-06-01", "2026-06-30")
        transfer_call = query.call_args_list[2][0][0]
        self.assertIn("FromAccountRef", transfer_call)
        self.assertIn("ToAccountRef", transfer_call)
        self.assertIn("OR", transfer_call)

    def test_tipo_desconocido_retorna_vacio(self):
        query = MagicMock(return_value={})
        client = QBOClientImpl(query, MagicMock())
        result = client._fetch_by_type(
            "Unknown", "bank_1", "2026-06-01", "2026-06-30"
        )
        self.assertEqual(result, [])


class TestQBOClientNormalize(unittest.TestCase):
    def test_normalize_deposit(self):
        raw = {
            "Id": "1", "TxnDate": "2026-06-01", "TotalAmt": "100.0",
            "DepositToAccountRef": {"value": "acc_1"},
        }
        out = QBOClientImpl._normalize("Deposit", raw)
        self.assertEqual(out["id"], "1")
        self.assertEqual(out["type"], "Deposit")
        self.assertEqual(out["date"], "2026-06-01")
        self.assertEqual(out["amount"], 100.0)
        self.assertEqual(out["account_id"], "acc_1")

    def test_normalize_purchase(self):
        raw = {
            "Id": "2", "TxnDate": "2026-06-02", "TotalAmt": "50.0",
            "AccountRef": {"value": "acc_1"},
        }
        out = QBOClientImpl._normalize("Purchase", raw)
        self.assertEqual(out["type"], "Purchase")
        self.assertEqual(out["account_id"], "acc_1")

    def test_normalize_transfer_usa_from(self):
        raw = {
            "Id": "3", "TxnDate": "2026-06-03", "Amount": "200.0",
            "FromAccountRef": {"value": "acc_1"},
            "ToAccountRef": {"value": "acc_2"},
        }
        out = QBOClientImpl._normalize("Transfer", raw)
        self.assertEqual(out["type"], "Transfer")
        self.assertEqual(out["account_id"], "acc_1")
        self.assertEqual(out["amount"], 200.0)

    def test_normalize_monto_none_o_vacio(self):
        raw = {
            "Id": "4", "TxnDate": "2026-06-04",
            "TotalAmt": None, "Amount": None,
        }
        out = QBOClientImpl._normalize("Deposit", raw)
        self.assertEqual(out["amount"], 0.0)

    def test_normalize_campos_faltantes(self):
        raw = {"Id": "5"}
        out = QBOClientImpl._normalize("Deposit", raw)
        self.assertEqual(out["id"], "5")
        self.assertEqual(out["date"], "")
        self.assertEqual(out["amount"], 0.0)


class TestQBOClientUpdate(unittest.TestCase):
    def test_update_memo_exitoso(self):
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Deposit": {"Id": "1", "Memo": "BNK-RECON"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        result = client.update_transaction("Deposit", "1", {"Memo": "BNK-RECON"})
        request.assert_called_once()
        # Endpoint debe ser deposit/1
        args = request.call_args
        self.assertEqual(args[0][0], "POST")
        self.assertEqual(args[0][1], "deposit/1")
        # Payload debe tener Id, sparse, SyncToken
        self.assertEqual(args[1]["data"]["Id"], "1")
        self.assertTrue(args[1]["data"]["sparse"])
        self.assertEqual(args[1]["data"]["SyncToken"], "0")
        self.assertEqual(args[1]["data"]["Memo"], "BNK-RECON")
        self.assertIn("Deposit", result)

    def test_update_privatenote(self):
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Bill": {"Id": "1"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        client.update_transaction("Bill", "2", {"PrivateNote": "BNK-RECON-2026-06-abcde"})
        args = request.call_args
        self.assertEqual(args[0][1], "bill/2")
        self.assertEqual(args[1]["data"]["PrivateNote"], "BNK-RECON-2026-06-abcde")

    def test_update_falla_con_error(self):
        request = MagicMock()
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request: invalid field"
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        with self.assertRaises(QBOClientError) as ctx:
            client.update_transaction("Deposit", "1", {"Memo": "x"})
        self.assertIn("400", str(ctx.exception))

    def test_update_response_no_json(self):
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        # json() raises
        response.json.side_effect = ValueError("not json")
        response.text = "raw text"
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        result = client.update_transaction("Deposit", "1", {"Memo": "x"})
        self.assertIn("raw", result)


class TestMakeQBOClient(unittest.TestCase):
    def test_factory(self):
        q = MagicMock()
        r = MagicMock()
        client = make_qbo_client(q, r)
        self.assertIsInstance(client, QBOClientImpl)
        self.assertIs(client._query, q)
        self.assertIs(client._request, r)


class TestFindBankAccount(unittest.TestCase):
    def test_encuentra_primera_cuenta_banco(self):
        find_account = MagicMock(return_value=[{"id": "acc_1", "name": "Bank"}])
        result = find_bank_account_id(find_account)
        self.assertEqual(result, "acc_1")

    def test_no_encuentra_retorna_vacio(self):
        find_account = MagicMock(return_value=[])
        result = find_bank_account_id(find_account)
        self.assertEqual(result, "")

    def test_usa_terminos_default(self):
        find_account = MagicMock(return_value=[])
        find_bank_account_id(find_account)
        # Verifica que llamó con varios términos
        self.assertGreater(find_account.call_count, 1)
        first_call = find_account.call_args_list[0]
        # El primer término debería ser uno de los default
        self.assertIn(first_call[0][0], [
            "bank", "banco", "checking", "efectivo", "cash",
            "operating", "principal", "general",
        ])

    def test_acepta_terminos_custom(self):
        find_account = MagicMock(return_value=[{"id": "acc_99"}])
        result = find_bank_account_id(find_account, ["custom1", "custom2"])
        self.assertEqual(result, "acc_99")
        # Primera llamada debe ser con custom1
        self.assertEqual(find_account.call_args_list[0][0][0], "custom1")


if __name__ == "__main__":
    unittest.main()
