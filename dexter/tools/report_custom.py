"""dexter.tools.report_custom — 2 tools."""
from typing import Any, Dict, List

from main import (
    tool_generate_custom_report,
    tool_parse_date_expression,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'generarreportecustom', 'description': 'Genera reportes personalizados interpretando peticiones en lenguaje natural.', 'parameters': {'type': 'object', 'properties': {'user_request': {'type': 'string'}, 'filters': {'type': 'object'}}, 'required': ['user_request']}}},
        {'type': 'function', 'function': {'name': 'parsearfecha', 'description': "Convierte expresiones temporales (ej: 'el mes pasado') en fechas específicas.", 'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["custom", "reporte custom", "fecha", "expresión fecha", "parsear"]
FUNCTIONS: Dict[str, Any] = {
    "generarreportecustom": tool_generate_custom_report,
    "parsearfecha": tool_parse_date_expression,
}
