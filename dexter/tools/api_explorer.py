"""dexter.tools.api_explorer — 5 tools."""
from typing import Any, Dict, List

from main import (
    tool_list_qbo_endpoints,
    tool_get_endpoint_info,
    tool_qbo_generic_request,
    tool_search_qbo_docs,
    tool_search_web,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'listarendpointsqbo', 'description': 'Lista los endpoints más comunes disponibles en la API de QuickBooks.', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'infoendpointqbo', 'description': 'Obtiene información detallada sobre cómo usar un endpoint específico de la API.', 'parameters': {'type': 'object', 'properties': {'endpoint_name': {'type': 'string'}}, 'required': ['endpoint_name']}}},
        {'type': 'function', 'function': {'name': 'qborequestgenerico', 'description': 'Realiza una petición genérica a cualquier endpoint de la API de QuickBooks v3.', 'parameters': {'type': 'object', 'properties': {'method': {'type': 'string', 'enum': ['GET', 'POST', 'UPDATE']}, 'endpoint': {'type': 'string', 'description': 'Nombre del recurso (ej: Purchase, PaymentMethod)'}, 'data': {'type': 'object', 'description': 'Cuerpo del JSON para POST/UPDATE'}, 'entity_id': {'type': 'string', 'description': 'ID del recurso para GET/UPDATE específico'}}, 'required': ['method', 'endpoint']}}},
        {'type': 'function', 'function': {'name': 'buscardocsqbo', 'description': 'Busca específicamente en la documentación oficial de QuickBooks Online API.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Consulta técnica sobre la API'}}, 'required': ['query']}}},
        {'type': 'function', 'function': {'name': 'buscarenweb', 'description': 'Busca información actualizada en internet (vía DuckDuckGo).', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Consulta de búsqueda'}}, 'required': ['query']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["web", "internet", "google", "api", "endpoint", "documentación", "qbo api"]
FUNCTIONS: Dict[str, Any] = {
    "listarendpointsqbo": tool_list_qbo_endpoints,
    "infoendpointqbo": tool_get_endpoint_info,
    "qborequestgenerico": tool_qbo_generic_request,
    "buscardocsqbo": tool_search_qbo_docs,
    "buscarenweb": tool_search_web,
}
