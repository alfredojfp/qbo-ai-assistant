"""dexter.tools.search — 7 tools (4 search + 3 list)."""
from typing import Any, Dict, List

from main import (
    tool_buscar_cliente,
    tool_buscar_vendor,
    tool_buscar_cuenta,
    tool_buscar_item,
    tool_listar_items,
    tool_listar_clientes,
    tool_listar_vendors,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'buscar_cliente', 'description': 'Busca clientes en QuickBooks por nombre (fuzzy search).', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del cliente'}, 'exacto': {'type': 'boolean', 'description': 'Busqueda exacta', 'default': False}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'buscar_vendor', 'description': 'Busca vendors/proveedores en QuickBooks por nombre.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del vendor'}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'buscar_cuenta', 'description': 'Busca cuenta contable por nombre en el Chart of Accounts.', 'parameters': {'type': 'object', 'properties': {'termino': {'type': 'string', 'description': 'Nombre de cuenta'}, 'categoria': {'type': 'string', 'enum': ['ACTIVO', 'PASIVO', 'INGRESO', 'GASTO']}}, 'required': ['termino']}}},
        {'type': 'function', 'function': {'name': 'buscar_item', 'description': 'Busca items/servicios en QuickBooks por nombre. Para listar todos los items sin filtro, usar listar_items.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del item'}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'listar_items', 'description': 'Lista TODOS los items/servicios disponibles en QBO sin filtro. Usar cuando Alfredo dice "cualquier item", "qué items hay", o "listame los items".', 'parameters': {'type': 'object', 'properties': {'max_results': {'type': 'integer', 'description': 'Max resultados (default 50)'}}, 'required': []}}},
        {'type': 'function', 'function': {'name': 'listar_clientes', 'description': 'Lista TODOS los clientes en QBO. Usar cuando Alfredo pide ver todos los clientes sin filtro.', 'parameters': {'type': 'object', 'properties': {'activos': {'type': 'boolean', 'description': 'Solo activos (default true)'}, 'max_results': {'type': 'integer', 'description': 'Max resultados (default 50)'}}, 'required': []}}},
        {'type': 'function', 'function': {'name': 'listar_vendors', 'description': 'Lista TODOS los proveedores en QBO.', 'parameters': {'type': 'object', 'properties': {'activos': {'type': 'boolean', 'description': 'Solo activos (default true)'}, 'max_results': {'type': 'integer', 'description': 'Max resultados (default 50)'}}, 'required': []}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["busca", "search", "cliente", "vendor", "cuenta", "item", "encontrar"]
FUNCTIONS: Dict[str, Any] = {
    "buscar_cliente": tool_buscar_cliente,
    "buscar_vendor": tool_buscar_vendor,
    "buscar_cuenta": tool_buscar_cuenta,
    "buscar_item": tool_buscar_item,
    "listar_items": tool_listar_items,
    "listar_clientes": tool_listar_clientes,
    "listar_vendors": tool_listar_vendors,
}
