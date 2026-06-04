"""dexter.tools.read — 3 tools de lectura directa (CompanyInfo, Preferences, Query)."""
from typing import Any, Dict, List

from main import (
    tool_leer_companyinfo,
    tool_leer_preferencias,
    tool_consulta_avanzada,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "leer_companyinfo",
            "description": "Lee la información de la empresa activa: nombre legal, dirección, país, año fiscal, moneda base, etc.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "leer_preferencias",
            "description": "Lee las preferencias de la empresa (preferences) — config de accounting, sales, vendor, payroll, etc.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consulta_avanzada",
            "description": "Ejecuta una consulta QBO SQL-like (query language) sobre cualquier entidad. WHITELIST DE SEGURIDAD: bloquea DROP/DELETE/UPDATE/INSERT/ALTER/CREATE; max_results limitado a 1000. Solo SELECT está permitido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query QBO: ej: 'SELECT * FROM Customer WHERE Active=true MAXRESULTS 100'",
                    },
                    "start_position": {"type": "integer", "default": 1, "description": "Posición de inicio (paginación)"},
                    "max_results": {"type": "integer", "default": 100, "maximum": 1000, "description": "Máx resultados (1-1000)"},
                },
                "required": ["query"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "company info", "información de la empresa", "datos de la empresa",
    "preferencias", "preferences", "configuración empresa",
    "consulta", "query", "sql", "búsqueda personalizada", "qbo query",
    "select", "select * from", "búsqueda raw", "raw query",
    "leer metadata", "metadata empresa", "company metadata",
]

FUNCTIONS: Dict[str, Any] = {
    "leer_companyinfo": tool_leer_companyinfo,
    "leer_preferencias": tool_leer_preferencias,
    "consulta_avanzada": tool_consulta_avanzada,
}
