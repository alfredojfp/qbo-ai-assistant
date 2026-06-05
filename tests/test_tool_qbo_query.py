"""Tests para tool_qbo_query registrado como LLM tool.

Bug: qbo_query existe como función en main.py pero no está en el
registry de tools. El LLM no puede ejecutar queries SQL contra QBO.
Cuando el usuario pide "busca los estimates del cliente 70", el LLM
alucina tools como 'buscar_estimate' porque no tiene un tool de query.

Fix: registrar qbo_query como tool en dexter/tools/read.py, con schema
y función. Verificar que está en ALL_SCHEMAS y en TOOL_FUNCTIONS.
"""
import unittest
import sys
from unittest.mock import patch, MagicMock


class TestQboQueryAsLlmTool(unittest.TestCase):
    """qbo_query debe existir como tool registrado para el LLM."""

    def setUp(self):
        sys.path.insert(0, '.')
        import dexter.tools
        import main

    def test_qbo_query_registered_in_all_schemas(self):
        """RED/GREEN: qbo_query debe aparecer en ALL_SCHEMAS."""
        from dexter.tools import ALL_SCHEMAS
        names = [s.get("function", {}).get("name") for s in ALL_SCHEMAS]
        self.assertIn("qbo_query", names,
                      "qbo_query debe estar en ALL_SCHEMAS")

    def test_qbo_query_registered_in_all_functions(self):
        """GREEN: qbo_query debe tener función dispatchable."""
        from dexter.tools import ALL_FUNCTIONS
        self.assertIn("qbo_query", ALL_FUNCTIONS,
                      "qbo_query debe estar en ALL_FUNCTIONS")

    def test_qbo_query_wrapper_exists_in_main(self):
        """GREEN: main.py debe exportar tool_qbo_query."""
        import main
        self.assertTrue(hasattr(main, "tool_qbo_query"),
                        "main debe tener tool_qbo_query")
        self.assertTrue(callable(main.tool_qbo_query))

    def test_qbo_query_tool_basic_sql_execution(self):
        """GREEN: tool_qbo_query(sql) ejecuta query y retorna filas."""
        import main
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "QueryResponse": {
                "Customer": [
                    {"Id": "70", "DisplayName": "Prueba2", "Active": True}
                ],
                "startPosition": 1,
                "maxResults": 1,
                "totalCount": 1,
            }
        }
        with patch("main.qbo_request", return_value=mock_resp):
            result = main.tool_qbo_query("SELECT * FROM Customer WHERE Id = '70'")
        self.assertIsInstance(result, dict)
        self.assertIn("rows", result, "tool_qbo_query debe retornar {rows: [...]}")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0]["DisplayName"], "Prueba2")

    def test_qbo_query_blocks_dangerous_sql(self):
        """GREEN: tool_qbo_query debe rechazar DROP, DELETE, UPDATE."""
        import main
        for dangerous in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]:
            result = main.tool_qbo_query(f"{dangerous} TABLE Account")
            self.assertIn("error", result,
                          f"Debe bloquear {dangerous}")
            self.assertIn("rechazada", result.get("error", "").lower())

    def test_qbo_query_handles_api_error(self):
        """GREEN: tool_qbo_query debe retornar error struct si falla."""
        import main
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        with patch("main.qbo_request", return_value=mock_resp):
            result = main.tool_qbo_query("SELECT * FROM Account")
        self.assertIn("error", result)
