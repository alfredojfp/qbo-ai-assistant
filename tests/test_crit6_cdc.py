"""Tests para CRIT-6: tool_cdc_query envía payload con schema incorrecto → 4xx siempre.

Bug: main.py:1859-1870 — cdc_query construye payload como
      {entities: [strings], since: string}
      pero QBO CDC API espera:
      {trackedEntities: [{entities: [{name: string}], lastModified: ISO}]}
      → HTTP 400 con "Invalid CDC request"

Fix: reshape cdc_query payload al schema QBO CDC documented.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestCdcQueryPayload(unittest.TestCase):
    """CRIT-6: cdc_query debe enviar payload con schema QBO CDC correcto."""

    def test_cdc_query_sends_tracked_entities_wrapper(self):
        """RED: cdc_query debe envolver entities en trackedEntities[].entities[].name."""
        from main import cdc_query

        captured_payload = []

        def mock_qbo_request(method, endpoint, data=None, params=None):
            captured_payload.append({
                "method": method,
                "endpoint": endpoint,
                "data": data,
            })
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"CDCResponse": []}
            return response

        with patch("main.qbo_request", side_effect=mock_qbo_request):
            cdc_query(["Customer", "Invoice"], "2026-06-01T00:00:00Z")

        self.assertEqual(len(captured_payload), 1, "qbo_request debe ser llamado una vez")
        payload = captured_payload[0]["data"]

        # QBO CDC schema esperado
        self.assertIn(
            "trackedEntities", payload,
            f"Payload debe tener clave 'trackedEntities'. Got keys: {list(payload.keys())}"
        )
        self.assertIsInstance(
            payload["trackedEntities"], list,
            f"trackedEntities debe ser list. Got: {type(payload['trackedEntities'])}"
        )
        self.assertEqual(
            len(payload["trackedEntities"]), 1,
            f"trackedEntities debe tener 1 entry (single since). Got: {len(payload['trackedEntities'])}"
        )

        tracked = payload["trackedEntities"][0]
        self.assertIn("entities", tracked, "Cada trackedEntity debe tener 'entities'")
        self.assertIn("lastModified", tracked, "Cada trackedEntity debe tener 'lastModified'")

    def test_cdc_query_entities_have_name_key(self):
        """RED: cada entity en trackedEntities debe ser {name: 'Customer'} (no string solo)."""
        from main import cdc_query

        captured_payload = []
        def mock_qbo_request(method, endpoint, data=None, params=None):
            captured_payload.append({"data": data})
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"CDCResponse": []}
            return response

        with patch("main.qbo_request", side_effect=mock_qbo_request):
            cdc_query(["Customer", "Invoice"], "2026-06-01T00:00:00Z")

        payload = captured_payload[0]["data"]
        entities = payload["trackedEntities"][0]["entities"]

        self.assertEqual(len(entities), 2, f"2 entities esperadas. Got: {len(entities)}")
        for ent in entities:
            self.assertIsInstance(
                ent, dict,
                f"Cada entity debe ser dict con clave 'name'. Got: {ent} (type {type(ent)})"
            )
            self.assertIn("name", ent, f"Entity debe tener 'name'. Got: {ent}")

        names = [ent["name"] for ent in entities]
        self.assertEqual(names, ["Customer", "Invoice"])

    def test_cdc_query_last_modified_preserved(self):
        """RED: cdc_query debe pasar el timestamp 'since' como 'lastModified'."""
        from main import cdc_query

        captured_payload = []
        def mock_qbo_request(method, endpoint, data=None, params=None):
            captured_payload.append({"data": data})
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"CDCResponse": []}
            return response

        with patch("main.qbo_request", side_effect=mock_qbo_request):
            cdc_query(["Customer"], "2026-06-01T12:30:45Z")

        payload = captured_payload[0]["data"]
        self.assertEqual(
            payload["trackedEntities"][0]["lastModified"],
            "2026-06-01T12:30:45Z",
            f"lastModified debe preservar el timestamp. Got: {payload['trackedEntities'][0]['lastModified']}"
        )

    def test_cdc_query_endpoint_is_cdc(self):
        """RED: cdc_query debe llamar a endpoint 'cdc' con método POST."""
        from main import cdc_query

        captured = []
        def mock_qbo_request(method, endpoint, data=None, params=None):
            captured.append({"method": method, "endpoint": endpoint})
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"CDCResponse": []}
            return response

        with patch("main.qbo_request", side_effect=mock_qbo_request):
            cdc_query(["Customer"], "2026-06-01T00:00:00Z")

        self.assertEqual(captured[0]["method"], "POST", "method debe ser POST")
        self.assertEqual(captured[0]["endpoint"], "cdc", "endpoint debe ser 'cdc'")


if __name__ == "__main__":
    unittest.main()
