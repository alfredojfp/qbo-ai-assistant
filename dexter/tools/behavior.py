"""dexter.tools.behavior — 4 tools."""
from typing import Any, Dict, List

from main import (
    tool_learn_from_interaction,
    tool_get_user_suggestions,
    tool_record_user_correction,
    tool_get_conversation_context,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'aprenderinteraccion', 'description': 'Aprende de las preferencias del usuario basadas en sus interacciones.', 'parameters': {'type': 'object', 'properties': {'interaction_type': {'type': 'string', 'enum': ['account_use', 'vendor_use', 'report_use']}, 'details': {'type': 'object'}, 'context': {'type': 'string'}}, 'required': ['interaction_type', 'details']}}},
        {'type': 'function', 'function': {'name': 'obtenersugerencias', 'description': 'Obtiene sugerencias de acciones basadas en el comportamiento histórico del usuario.', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'registrarcorreccion', 'description': 'Registra una corrección del usuario cuando el sistema comete un error.', 'parameters': {'type': 'object', 'properties': {'wrong': {'type': 'string'}, 'correct': {'type': 'string'}, 'context': {'type': 'string'}}, 'required': ['wrong', 'correct', 'context']}}},
        {'type': 'function', 'function': {'name': 'obtenercontexto', 'description': 'Obtiene un resumen del contexto reciente de la conversación y tareas activas.', 'parameters': {'type': 'object', 'properties': {}}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["sugerencia", "corrección", "aprender", "contexto", "interacción"]
FUNCTIONS: Dict[str, Any] = {
    "aprenderinteraccion": tool_learn_from_interaction,
    "obtenersugerencias": tool_get_user_suggestions,
    "registrarcorreccion": tool_record_user_correction,
    "obtenercontexto": tool_get_conversation_context,
}
