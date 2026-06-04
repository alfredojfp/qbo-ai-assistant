"""dexter.tools.admin — 4 tools."""
from typing import Any, Dict, List

from main import (
    tool_refrescar_chart_accounts,
    tool_gestionar_empresas,
    tool_ver_log_errores,
    tool_limpiar_log_errores,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'refrescar_chart_accounts', 'description': 'Refresca el Chart of Accounts desde QuickBooks Online (fuerza actualización del caché).', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'gestionar_empresas', 'description': 'Permite registrar una nueva empresa (vía link QBO o ID), listar las registradas o cambiar entre ellas.', 'parameters': {'type': 'object', 'properties': {'accion': {'type': 'string', 'enum': ['registrar', 'listar', 'cambiar'], 'description': "Acción a realizar: 'registrar' una nueva, 'listar' todas, o 'cambiar' a una existente."}, 'nombre': {'type': 'string', 'description': "Nombre de la empresa (requerido para 'registrar' y 'cambiar')."}, 'link_o_id': {'type': 'string', 'description': "URL de QuickBooks o Realm ID de la empresa (requerido para 'registrar')."}}, 'required': ['accion']}}},
        {'type': 'function', 'function': {'name': 'ver_log_errores', 'description': 'Muestra las últimas N entradas del log de errores persistido (jsonl en logs/dexter_errors.log). Util para diagnostico post-mortem.', 'parameters': {'type': 'object', 'properties': {'n': {'type': 'integer', 'description': 'Numero de entradas a retornar (1-200, default 20)', 'default': 20}, 'categoria': {'type': 'string', 'enum': ['api_call', 'tool_dispatch', 'user_input', 'auth', 'unknown'], 'description': 'Filtrar por categoria (opcional)'}}}}},
        {'type': 'function', 'function': {'name': 'limpiar_log_errores', 'description': 'Borra el archivo de log de errores (logs/dexter_errors.log).', 'parameters': {'type': 'object', 'properties': {}}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = [
    "refrescar", "empresa", "compañía", "registrar empresa", "cambiar empresa",
    "listar empresa", "log", "error", "errores", "diagnostico",
]
FUNCTIONS: Dict[str, Any] = {
    "refrescar_chart_accounts": tool_refrescar_chart_accounts,
    "gestionar_empresas": tool_gestionar_empresas,
    "ver_log_errores": tool_ver_log_errores,
    "limpiar_log_errores": tool_limpiar_log_errores,
}
