"""dexter.tools.admin — 2 tools."""
from typing import Any, Dict, List

from main import (
    tool_refrescar_chart_accounts,
    tool_gestionar_empresas,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'refrescar_chart_accounts', 'description': 'Refresca el Chart of Accounts desde QuickBooks Online (fuerza actualización del caché).', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'gestionar_empresas', 'description': 'Permite registrar una nueva empresa (vía link QBO o ID), listar las registradas o cambiar entre ellas.', 'parameters': {'type': 'object', 'properties': {'accion': {'type': 'string', 'enum': ['registrar', 'listar', 'cambiar'], 'description': "Acción a realizar: 'registrar' una nueva, 'listar' todas, o 'cambiar' a una existente."}, 'nombre': {'type': 'string', 'description': "Nombre de la empresa (requerido para 'registrar' y 'cambiar')."}, 'link_o_id': {'type': 'string', 'description': "URL de QuickBooks o Realm ID de la empresa (requerido para 'registrar')."}}, 'required': ['accion']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["refrescar", "empresa", "compañía", "registrar empresa", "cambiar empresa", "listar empresa"]
FUNCTIONS: Dict[str, Any] = {
    "refrescar_chart_accounts": tool_refrescar_chart_accounts,
    "gestionar_empresas": tool_gestionar_empresas,
}
