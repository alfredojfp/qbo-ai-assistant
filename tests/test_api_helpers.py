"""Tests para R-2: dexter.core.api_helpers.

API helpers de alto nivel sobre qbo_request (de main.py):
  - post_entity(entity_type, payload) → 200 OK → response.json()[EntityType]
  - get_entity(entity_type, entity_id) → response.json()[EntityType]
  - query_with_pagination(sql) → lista agregada de resultados

Diseño: cada helper acepta qbo_request_fn opcional (default usa
main.qbo_request). Esto permite tests con mocks sin tocar red.

Backward compat: main.py NO se modifica. Estos helpers son NUEVOS y
disponibles via 'from dexter.core.api_helpers import ...'.
"""
import unittest
from unittest.mock import MagicMock


def _resp(status, json_body=None, text=""):
    r = MagicMock()
    r.status_code = status
    r.text = text or (str(json_body)[:200] if json_body else "")
    if json_body is not None:
        r.json.return_value = json_body
    return r


class TestPostEntity(unittest.TestCase):
    """R-2: post_entity extrae el sub-dict correcto."""

    def test_returns_entity_dict_on_200(self):
        """post_entity('Customer', {...}) retorna r.json()['Customer']."""
        from dexter.core.api_helpers import post_entity
        fake_qbo = MagicMock(return_value=_resp(200, {
            "Customer": {"Id": "61", "DisplayName": "Test"},
        }))
        result = post_entity("Customer", {"DisplayName": "Test"}, qbo_request_fn=fake_qbo)
        self.assertEqual(result["Id"], "61")
        self.assertEqual(result["DisplayName"], "Test")
        fake_qbo.assert_called_once()

    def test_endpoint_format_is_singular_lowercase(self):
        """Endpoint = 'customer' (singular, lowercase)."""
        from dexter.core.api_helpers import post_entity
        fake_qbo = MagicMock(return_value=_resp(200, {"Customer": {"Id": "1"}}))
        post_entity("Customer", {}, qbo_request_fn=fake_qbo)
        args, kwargs = fake_qbo.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "customer")
        self.assertEqual(kwargs["data"], {})

    def test_returns_error_dict_on_400(self):
        """post_entity en error retorna {'error': ..., 'status': ...}."""
        from dexter.core.api_helpers import post_entity
        fake_qbo = MagicMock(return_value=_resp(400, text="bad request"))
        result = post_entity("Invoice", {}, qbo_request_fn=fake_qbo)
        self.assertIn("error", result)
        self.assertEqual(result.get("status"), 400)

    def test_other_entity_types(self):
        """Funciona para Invoice, Bill, Vendor, Item, etc."""
        from dexter.core.api_helpers import post_entity
        for entity_type, endpoint in [
            ("Invoice", "invoice"),
            ("Bill", "bill"),
            ("Vendor", "vendor"),
            ("Item", "item"),
            ("Deposit", "deposit"),
        ]:
            fake_qbo = MagicMock(return_value=_resp(200, {entity_type: {"Id": "1"}}))
            result = post_entity(entity_type, {}, qbo_request_fn=fake_qbo)
            self.assertEqual(result["Id"], "1")
            args, kwargs = fake_qbo.call_args
            self.assertEqual(args[1], endpoint, f"endpoint mismatch for {entity_type}")


class TestGetEntity(unittest.TestCase):
    """R-2: get_entity por ID."""

    def test_returns_entity_dict_on_200(self):
        """get_entity('Customer', '61') retorna r.json()['Customer']."""
        from dexter.core.api_helpers import get_entity
        fake_qbo = MagicMock(return_value=_resp(200, {
            "Customer": {"Id": "61", "DisplayName": "AlfredoTPM"},
        }))
        result = get_entity("Customer", "61", qbo_request_fn=fake_qbo)
        self.assertEqual(result["Id"], "61")
        self.assertEqual(result["DisplayName"], "AlfredoTPM")

    def test_endpoint_format_includes_id(self):
        """Endpoint = 'customer/61' (id appended)."""
        from dexter.core.api_helpers import get_entity
        fake_qbo = MagicMock(return_value=_resp(200, {"Customer": {"Id": "61"}}))
        get_entity("Customer", "61", qbo_request_fn=fake_qbo)
        args, kwargs = fake_qbo.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "customer/61")

    def test_returns_error_on_404(self):
        """get_entity con id inexistente retorna error dict."""
        from dexter.core.api_helpers import get_entity
        fake_qbo = MagicMock(return_value=_resp(404, text="not found"))
        result = get_entity("Customer", "9999", qbo_request_fn=fake_qbo)
        self.assertIn("error", result)
        self.assertEqual(result.get("status"), 404)


class TestQueryWithPagination(unittest.TestCase):
    """R-2: query_withPagination auto-pagina con STARTPOSITION."""

    def test_single_page_returns_all(self):
        """Si la respuesta cabe en 1 página, retorna todos los rows."""
        from dexter.core.api_helpers import query_with_pagination
        rows = [{"Id": str(i), "DisplayName": f"C{i}"} for i in range(1, 6)]
        fake_qbo = MagicMock(return_value=_resp(200, {
            "QueryResponse": {
                "Customer": rows,
                "maxResults": 5,
                "startPosition": 1,
            }
        }))
        result = query_with_pagination(
            "SELECT * FROM Customer", page_size=1000,
            qbo_request_fn=fake_qbo,
        )
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["Id"], "1")

    def test_multi_page_aggregates(self):
        """Si la respuesta trae page_size filas, sigue paginando."""
        from dexter.core.api_helpers import query_with_pagination
        page1 = [{"Id": str(i)} for i in range(1, 1001)]
        page2 = [{"Id": str(i)} for i in range(1001, 1501)]

        responses = [
            _resp(200, {
                "QueryResponse": {
                    "Customer": page1,
                    "maxResults": 1000,
                    "startPosition": 1,
                }
            }),
            _resp(200, {
                "QueryResponse": {
                    "Customer": page2,
                    "maxResults": 1000,
                    "startPosition": 1001,
                }
            }),
        ]
        fake_qbo = MagicMock(side_effect=responses)

        result = query_with_pagination(
            "SELECT * FROM Customer", page_size=1000,
            qbo_request_fn=fake_qbo,
        )
        self.assertEqual(len(result), 1500)
        self.assertEqual(result[0]["Id"], "1")
        self.assertEqual(result[-1]["Id"], "1500")
        self.assertEqual(fake_qbo.call_count, 2)

    def test_error_returns_empty_list(self):
        """Si la primera query falla, retorna []."""
        from dexter.core.api_helpers import query_with_pagination
        fake_qbo = MagicMock(return_value=_resp(500, text="server error"))
        result = query_with_pagination(
            "SELECT * FROM Customer",
            qbo_request_fn=fake_qbo,
        )
        self.assertEqual(result, [])

    def test_empty_response_returns_empty_list(self):
        """Si no hay resultados, retorna []."""
        from dexter.core.api_helpers import query_with_pagination
        fake_qbo = MagicMock(return_value=_resp(200, {
            "QueryResponse": {"maxResults": 0, "startPosition": 0}
        }))
        result = query_with_pagination(
            "SELECT * FROM Customer",
            qbo_request_fn=fake_qbo,
        )
        self.assertEqual(result, [])


class TestApiHelpersIntegration(unittest.TestCase):
    """R-2: helpers disponibles via 'from dexter.core.api_helpers'."""

    def test_all_helpers_exported(self):
        """post_entity, get_entity, query_with_pagination son importables."""
        from dexter.core import api_helpers
        for name in ("post_entity", "get_entity", "query_with_pagination"):
            self.assertTrue(hasattr(api_helpers, name), f"missing: {name}")
            self.assertTrue(callable(getattr(api_helpers, name)))


if __name__ == "__main__":
    unittest.main()
