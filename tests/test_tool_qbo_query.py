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


class TestQboQueryAlwaysIncluded(unittest.TestCase):
    """qbo_query debe estar siempre presente en get_relevant_tools()."""

    def _extract_names(self, schemas):
        out = []
        for s in schemas:
            if isinstance(s, dict):
                if "function" in s and isinstance(s["function"], dict):
                    out.append(s["function"].get("name", ""))
                elif "name" in s:
                    out.append(s["name"])
        return [n for n in out if n]

    def test_qbo_query_included_for_generic_message(self):
        """qbo_query incluido aunque no haya keywords de read module."""
        import main
        tools = main.get_relevant_tools("dame los datos que tengas de este cliente")
        names = self._extract_names(tools)
        self.assertIn("qbo_query", names,
                      "qbo_query debe estar SIEMPRE presente")

    def test_qbo_query_included_for_estimate_query(self):
        """'busca el estimate del cliente' debe incluir qbo_query."""
        import main
        tools = main.get_relevant_tools("busca el estimate del cliente Prueba2")
        names = self._extract_names(tools)
        self.assertIn("qbo_query", names)

    def test_qbo_query_included_for_hola(self):
        """Incluso 'hola' debe incluir qbo_query (siempre-presente)."""
        import main
        tools = main.get_relevant_tools("hola")
        names = self._extract_names(tools)
        self.assertIn("qbo_query", names)

    def test_qbo_query_included_for_salir(self):
        """'salir' también debe incluir qbo_query."""
        import main
        tools = main.get_relevant_tools("salir")
        names = self._extract_names(tools)
        self.assertIn("qbo_query", names)


class TestReadModuleKeywords(unittest.TestCase):
    """Verificar que las keywords del módulo read matcheen frases comunes."""

    def setUp(self):
        from dexter.tools.read import KEYWORDS
        self.kws = KEYWORDS

    def _activates(self, msg):
        import main
        bi = main._bilingual_keywords(self.kws)
        return any(kw.lower() in msg.lower() for kw in bi)

    def test_busca_activates_read(self):
        self.assertTrue(self._activates("busca el estimate"),
                        "'busca' debe activar read module")

    def test_dame_activates_read(self):
        self.assertTrue(self._activates("dame los datos del cliente"),
                        "'dame' debe activar read module")

    def test_ver_activates_read(self):
        self.assertTrue(self._activates("ver los estimates"),
                        "'ver' debe activar read module")

    def test_muestrame_activates_read(self):
        self.assertTrue(self._activates("muéstrame el balance"),
                        "'muéstrame' debe activar read module")

    def test_cuantos_activates_read(self):
        self.assertTrue(self._activates("cuántos clientes tengo"),
                        "'cuántos' debe activar read module")
