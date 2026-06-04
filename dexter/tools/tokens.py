"""dexter.tools.tokens — 2 tools."""
from typing import Any, Dict, List

from main import (
    tool_obtener_estadisticas_tokens,
    tool_generar_informe_tokens,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'obtener_estadisticas_tokens', 'description': 'Muestra estadísticas de consumo de tokens del LLM.', 'parameters': {'type': 'object', 'properties': {'periodo': {'type': 'string', 'enum': ['sesion', 'hoy', 'mes'], 'description': 'Periodo a consultar'}}, 'required': ['periodo']}}},
        {'type': 'function', 'function': {'name': 'generar_informe_tokens', 'description': 'Genera informe Excel con estadísticas detalladas de consumo (sobrescribe archivo).', 'parameters': {'type': 'object', 'properties': {}}}},
]

FUNCTIONS: Dict[str, Any] = {
    "obtener_estadisticas_tokens": tool_obtener_estadisticas_tokens,
    "generar_informe_tokens": tool_generar_informe_tokens,
}
