"""Tests para HIGH-8: qbo_query debe auto-paginar > 1000 resultados.

Bug: main.py:335-342 — qbo_query hace un solo GET a /query.
     QBO API limita a 1000 resultados por query por default.
     Si hay 2500 customers, retorna 1000 + totalCount=2500 en el
     response. El caller no recibe los 1500 que faltan.

Fix: detectar truncamiento (count(returned) == maxResults o
     totalCount > count(returned)) y auto-paginar agregando
     STARTPOSITION N a la siguiente query. Agregar MAXRESULTS 1000
     si no está presente en el SQL.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestQboQueryPagination(unittest.TestCase):
    """HIGH-8: qbo_query debe auto-paginar cuando hay > 1000 resultados."""

    def setUp(self):
        import os
        os.environ.setdefault("QB_ACCESS_TOKEN", "fake-token-for-test")
        os.environ.setdefault("QB_REALM_ID", "9341455870833544")

    def test_single_page_under_1000(self):
        """GREEN: si la query retorna < 1000, no paginar (1 sola call)."""
        from main import qbo_query

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i), "DisplayName": f"C{i}"} for i in range(50)],
                "maxResults": 1000,
            }
        }

        with patch("main.qbo_request", return_value=response) as mock_qbo:
            result = qbo_query("SELECT * FROM Customer")
            self.assertEqual(len(result["QueryResponse"]["Customer"]), 50)
            self.assertEqual(mock_qbo.call_count, 1)

    def test_auto_paginates_when_1000_returned(self):
        """RED: si retorna 1000 exactos, debe paginar para traer el resto."""
        from main import qbo_query

        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i), "DisplayName": f"C{i}"} for i in range(1, 1001)],
                "maxResults": 1000,
                "startPosition": 1,
            }
        }
        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i), "DisplayName": f"C{i}"} for i in range(1001, 1501)],
                "maxResults": 1000,
                "startPosition": 1001,
            }
        }

        with patch("main.qbo_request", side_effect=[page1, page2]) as mock_qbo:
            result = qbo_query("SELECT * FROM Customer")
            all_customers = result["QueryResponse"]["Customer"]
            self.assertEqual(len(all_customers), 1500)
            self.assertEqual(mock_qbo.call_count, 2)

    def test_total_count_triggers_pagination(self):
        """RED: si totalCount > len(returned), paginar para llegar a totalCount."""
        from main import qbo_query

        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i)} for i in range(1000)],
                "maxResults": 1000,
            }
        }
        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i)} for i in range(1000, 1500)],
                "maxResults": 1000,
            }
        }

        with patch("main.qbo_request", side_effect=[page1, page2]) as mock_qbo:
            result = qbo_query("SELECT * FROM Customer")
            self.assertEqual(len(result["QueryResponse"]["Customer"]), 1500)
            self.assertEqual(mock_qbo.call_count, 2)

    def test_pagination_stops_when_short_page_returned(self):
        """GREEN: cuando la página retorna < 1000, parar de paginar."""
        from main import qbo_query

        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i)} for i in range(1000)],
            }
        }
        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {
            "QueryResponse": {
                "Customer": [{"Id": str(i)} for i in range(1000, 1234)],
            }
        }

        with patch("main.qbo_request", side_effect=[page1, page2]) as mock_qbo:
            result = qbo_query("SELECT * FROM Customer")
            self.assertEqual(len(result["QueryResponse"]["Customer"]), 1234)
            self.assertEqual(mock_qbo.call_count, 2)


if __name__ == "__main__":
    unittest.main()
