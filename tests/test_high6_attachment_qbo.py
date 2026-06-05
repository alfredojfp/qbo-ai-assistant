"""Tests para HIGH-6: upload_attachment debe usar qbo_request (no requests.post directo).

Bug: main.py:2047 — upload_attachment llama requests.post() directamente,
     bypaseando el timeout=30 (CRIT-1), retry 429/503 (CRIT-4), token
     refresh en 401, y el error log. Si QBO está lento o rate-limited,
     el upload se cuelga o falla.

Fix: refactorizar para que pase por qbo_request (que ya tiene todos los
     safeguards). Agregar parámetros opcionales raw_body y extra_headers
     a qbo_request para soportar multipart/form-data (no JSON).
"""
import unittest
from unittest.mock import patch, MagicMock


class TestUploadAttachmentUsesQboRequest(unittest.TestCase):
    """HIGH-6: upload_attachment debe pasar por qbo_request para tener retry/timeout/refresh."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_upload_attachment_does_not_call_requests_post_directly(self):
        """RED: upload_attachment NO debe llamar requests.post directamente."""
        from main import upload_attachment

        with patch("main.requests.post") as mock_post, \
             patch("main.qbo_request") as mock_qbo:
            mock_qbo.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "AttachableResponse": [{
                        "Attachable": {"Id": "att1", "FileName": "test.pdf"}
                    }]
                }
            )

            result = upload_attachment(
                file_content=b"PDF data",
                file_name="test.pdf",
                content_type="application/pdf",
                entity_type="Bill",
                entity_id="99",
            )

            mock_post.assert_not_called()
            mock_qbo.assert_called_once()
            self.assertTrue(result["success"])
            self.assertEqual(result["attachable_id"], "att1")

    def test_upload_attachment_passes_multipart_body_to_qbo_request(self):
        """RED: el body multipart debe llegar a qbo_request (raw_body o data)."""
        from main import upload_attachment

        with patch("main.qbo_request") as mock_qbo:
            mock_qbo.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "AttachableResponse": [{
                        "Attachable": {"Id": "att1"}
                    }]
                }
            )

            upload_attachment(
                file_content=b"X",
                file_name="x.pdf",
                content_type="application/pdf",
                entity_type="Bill",
                entity_id="1",
            )

            call_args = mock_qbo.call_args
            kwargs = call_args.kwargs if call_args.kwargs else call_args[1]
            headers = kwargs.get("headers") or kwargs.get("extra_headers")
            self.assertIsNotNone(headers)
            ct = headers.get("Content-Type", "") if isinstance(headers, dict) else ""
            self.assertIn("multipart/form-data", ct)


if __name__ == "__main__":
    unittest.main()
