"""Tests para HIGH-2: update_transaction debe usar ?operation=sparseUpdate en URL, no 'sparse' en body.

Bug: dexter/core/qbo_client.py:135 — `"sparse": True` en el body y `f"{txn}/{id}"` en URL.
     QBO API expects: POST /v3/company/{realmId}/{entity}/{id}?operation=sparseUpdate
     con el body conteniendo solo los campos a actualizar (sin 'sparse' key).
     El style "sparse: true" en body es deprecated.

Fix: enviar `params={"operation": "sparseUpdate"}` en la request, y remover
     la key `"sparse": True` del body. QBO maneja el sparse via query param.

Tests existentes en tests/test_qbo_client.py::TestQBOClientUpdate tienen
assertions sobre el comportamiento BUGGY (asume "sparse" en body). Esos
se actualizan en este commit (mismo fix, mismo comportamiento esperado).
"""
import unittest
from unittest.mock import MagicMock, patch

from dexter.core.qbo_client import QBOClientImpl, QBOClientError


class TestQBOClientUpdateSparseURL(unittest.TestCase):
    """HIGH-2: update_transaction debe usar QBO sparse via URL, no via body."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_update_uses_operation_sparseUpdate_in_url_params(self):
        """RED: la request POST debe llevar params={'operation': 'sparseUpdate'}."""
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Deposit": {"Id": "1", "Memo": "X"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        client.update_transaction("Deposit", "1", {"Memo": "X"})

        request.assert_called_once()
        args = request.call_args
        params = args[1].get("params")
        self.assertIsNotNone(params, "update_transaction debe pasar params={...} a _request")
        self.assertEqual(params.get("operation"), "sparseUpdate")

    def test_update_body_has_no_sparse_key(self):
        """RED: el body NO debe contener la key 'sparse' (estilo deprecated)."""
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Deposit": {"Id": "1"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        client.update_transaction("Deposit", "1", {"Memo": "X"})

        args = request.call_args
        sent_body = args[1]["data"]
        self.assertNotIn(
            "sparse", sent_body,
            "QBO modern API no acepta 'sparse' en body; usa ?operation=sparseUpdate"
        )

    def test_update_body_still_has_id_sync_and_fields(self):
        """GREEN: body debe tener Id, SyncToken, y los fields del update."""
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Deposit": {"Id": "1"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        client.update_transaction("Deposit", "1", {"Memo": "NEW"})

        sent_body = request.call_args[1]["data"]
        self.assertEqual(sent_body["Id"], "1")
        self.assertIn("SyncToken", sent_body)
        self.assertEqual(sent_body["Memo"], "NEW")

    def test_update_endpoint_is_entity_id_lowercase(self):
        """GREEN: URL path sigue siendo /entity/{id} en lowercase (no cambia)."""
        request = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"Bill": {"Id": "2"}}
        request.return_value = response

        client = QBOClientImpl(MagicMock(), request)
        client.update_transaction("Bill", "42", {"PrivateNote": "PN"})

        endpoint = request.call_args[0][1]
        self.assertEqual(endpoint, "bill/42")


if __name__ == "__main__":
    unittest.main()
