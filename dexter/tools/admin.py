"""dexter.tools.admin — 6 tools de administración."""
from typing import Any, Dict, List

from main import (
    tool_refrescar_chart_accounts,
    tool_gestionar_empresas,
    tool_ver_log_errores,
    tool_limpiar_log_errores,
    tool_gestionar_memoria,
    tool_leer_archivo,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'refrescar_chart_accounts', 'description': 'Refresca el Chart of Accounts desde QuickBooks Online (fuerza actualización del caché).', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'gestionar_empresas', 'description': 'Permite registrar una nueva empresa (vía link QBO o ID), listar las registradas o cambiar entre ellas.', 'parameters': {'type': 'object', 'properties': {'accion': {'type': 'string', 'enum': ['registrar', 'listar', 'cambiar'], 'description': "Acción a realizar: 'registrar' una nueva, 'listar' todas, o 'cambiar' a una existente."}, 'nombre': {'type': 'string', 'description': "Nombre de la empresa (requerido para 'registrar' y 'cambiar')."}, 'link_o_id': {'type': 'string', 'description': "URL de QuickBooks o Realm ID de la empresa (requerido para 'registrar')."}}, 'required': ['accion']}}},
        {'type': 'function', 'function': {'name': 'ver_log_errores', 'description': 'Muestra las últimas N entradas del log de errores persistido (jsonl en logs/dexter_errors.log). Util para diagnostico post-mortem.', 'parameters': {'type': 'object', 'properties': {'n': {'type': 'integer', 'description': 'Numero de entradas a retornar (1-200, default 20)', 'default': 20}, 'categoria': {'type': 'string', 'enum': ['api_call', 'tool_dispatch', 'user_input', 'auth', 'unknown'], 'description': 'Filtrar por categoria (opcional)'}}}}},
        {'type': 'function', 'function': {'name': 'limpiar_log_errores', 'description': 'Borra el archivo de log de errores (logs/dexter_errors.log).', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'gestionar_memoria', 'description': 'Gestiona la memoria persistente del agente. Acciones: add (agregar), remove (eliminar), status (ver estado).', 'parameters': {'type': 'object', 'properties': {'target': {'type': 'string', 'enum': ['memory', 'user'], 'description': "Tipo: 'memory' (notas del agente) o 'user' (perfil de Alfredo)"}, 'action': {'type': 'string', 'enum': ['add', 'remove', 'status'], 'description': 'Acción a realizar'}, 'content': {'type': 'string', 'description': 'Texto a agregar (para action=add)'}, 'old_text': {'type': 'string', 'description': 'Substring a eliminar (para action=remove)'}}, 'required': ['target', 'action']}}},
        {'type': 'function', 'function': {'name': 'leer_archivo', 'description': 'Lee un archivo del proyecto (PROFILE.md, MEMORY.md, documentación, templates). Retorna el contenido. Útil para consultar datos de la empresa.', 'parameters': {'type': 'object', 'properties': {'ruta': {'type': 'string', 'description': 'Ruta relativa del archivo. Ej: companies/Sandbox/PROFILE.md'}}, 'required': ['ruta']}}},
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
    "gestionar_memoria": tool_gestionar_memoria,
    "leer_archivo": tool_leer_archivo,
}
