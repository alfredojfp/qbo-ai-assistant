"""dexter.tools.search — 4 tools."""
from typing import Any, Dict, List

from main import (
    tool_buscar_cliente,
    tool_buscar_vendor,
    tool_buscar_cuenta,
    tool_buscar_item,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'buscar_cliente', 'description': 'Busca clientes en QuickBooks por nombre (fuzzy search). Retorna lista de clientes con ID, nombre, balance.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre o parte del nombre del cliente a buscar'}, 'exacto': {'type': 'boolean', 'description': 'Si es true, busca coincidencia exacta. Por defecto false (fuzzy).', 'default': False}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'buscar_vendor', 'description': 'Busca vendors/proveedores en QuickBooks por nombre.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del vendor a buscar'}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'buscar_cuenta', 'description': 'Busca cuenta contable por nombre o número en el Chart of Accounts. Usa fuzzy matching.', 'parameters': {'type': 'object', 'properties': {'termino': {'type': 'string', 'description': 'Nombre o número de cuenta a buscar'}, 'categoria': {'type': 'string', 'enum': ['ACTIVO', 'PASIVO', 'INGRESO', 'GASTO'], 'description': 'Filtrar por categoría de cuenta (opcional)'}}, 'required': ['termino']}}},
        {'type': 'function', 'function': {'name': 'buscar_item', 'description': 'Busca items/servicios en QuickBooks por nombre.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del item/servicio'}}, 'required': ['nombre']}}},
]

FUNCTIONS: Dict[str, Any] = {
    "buscar_cliente": tool_buscar_cliente,
    "buscar_vendor": tool_buscar_vendor,
    "buscar_cuenta": tool_buscar_cuenta,
    "buscar_item": tool_buscar_item,
}
