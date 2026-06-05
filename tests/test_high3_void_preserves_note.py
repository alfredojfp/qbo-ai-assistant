"""Tests para HIGH-3: void_transaction debe preservar PrivateNote original.

Bug: main.py:1455 — `void_transaction` siempre sobreescribe PrivateNote
     con "[VOIDED]", destruyendo notas de auditoría (e.g. BNK-RECON tag).

Fix: leer la transacción primero (GET), prepend "[VOIDED] " a la
     PrivateNote existente (o usar "[VOIDED]" si está vacía). Si el
     read falla, fallback a "[VOIDED]" sin bloquear el void.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestVoidTransactionPreservesPrivateNote(unittest.TestCase):
    """HIGH-3: void_transaction debe preservar la PrivateNote original."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def _mock_void_response(self):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "Invoice": {
                "Id": "1",
                "SyncToken": "1",
                "PrivateNote": "[VOIDED] BNK-RECON-2026-06-abcde",
            }
        }
        return response

    def test_void_preserves_existing_private_note(self):
        """RED: si la txn tiene PrivateNote, void debe prepender [VOIDED] y conservar."""
        from main import void_transaction

        read_response = MagicMock()
        read_response.status_code = 200
        read_response.json.return_value = {
            "Invoice": {
                "Id": "1",
                "SyncToken": "0",
                "PrivateNote": "BNK-RECON-2026-06-abcde",
            }
        }

        with patch("main.qbo_request", side_effect=[read_response, self._mock_void_response()]) as mock_qbo:
            result = void_transaction("invoice", "1", "0")

        self.assertTrue(result["success"])
        self.assertTrue(result["voided"])
        # La segunda llamada (POST void) debe llevar PrivateNote con la nota original
        post_call = mock_qbo.call_args_list[1]
        sent_body = post_call.kwargs.get("data") or post_call[1].get("data")
        self.assertIn("BNK-RECON-2026-06-abcde", sent_body["PrivateNote"])
        self.assertIn("[VOIDED]", sent_body["PrivateNote"])

    def test_void_with_empty_private_note_uses_just_voided(self):
        """GREEN: si la txn no tiene PrivateNote, void usa solo '[VOIDED]'."""
        from main import void_transaction

        read_response = MagicMock()
        read_response.status_code = 200
        read_response.json.return_value = {
            "Invoice": {"Id": "1", "SyncToken": "0"}
        }

        with patch("main.qbo_request", side_effect=[read_response, self._mock_void_response()]) as mock_qbo:
            result = void_transaction("invoice", "1", "0")

        self.assertTrue(result["success"])
        post_call = mock_qbo.call_args_list[1]
        sent_body = post_call.kwargs.get("data") or post_call[1].get("data")
        self.assertEqual(sent_body["PrivateNote"], "[VOIDED]")

    def test_void_continues_when_read_fails(self):
        """GREEN: si el read falla, void continúa con fallback '[VOIDED]'."""
        from main import void_transaction

        read_response = MagicMock()
        read_response.status_code = 404
        read_response.text = "Not Found"

        with patch("main.qbo_request", side_effect=[read_response, self._mock_void_response()]) as mock_qbo:
            result = void_transaction("invoice", "1", "0")

        self.assertTrue(result["success"])
        post_call = mock_qbo.call_args_list[1]
        sent_body = post_call.kwargs.get("data") or post_call[1].get("data")
        self.assertEqual(sent_body["PrivateNote"], "[VOIDED]")


if __name__ == "__main__":
    unittest.main()
