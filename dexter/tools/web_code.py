"""dexter.tools.web_code — 1 tools."""
from typing import Any, Dict, List

from main import (
    tool_execute_python,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'ejecutarcodigo', 'description': 'Ejecuta fragmentos de código Python para análisis de datos avanzados o cálculos complejos.', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string', 'description': 'Código Python a ejecutar'}}, 'required': ['code']}}},
]

FUNCTIONS: Dict[str, Any] = {
    "ejecutarcodigo": tool_execute_python,
}
