"""dexter.tools.read — 4 tools de lectura directa (CompanyInfo, Preferences, Query, QBO Query)."""
from typing import Any, Dict, List

from main import (
    tool_leer_companyinfo,
    tool_leer_preferencias,
    tool_consulta_avanzada,
    tool_qbo_query,
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
    {
        "type": "function",
        "function": {
            "name": "qbo_query",
            "description": "Ejecuta consultas SQL en QuickBooks Online. Usa este tool para buscar, filtrar o contar cualquier entidad (clientes, invoices, estimates, items, vendors, cuentas). Ejemplos: 'SELECT * FROM Estimate WHERE CustomerRef.value = \"70\"', 'SELECT COUNT(*) FROM Invoice WHERE Balance > 0'. Seguro: solo SELECT, bloquea DROP/DELETE/UPDATE/INSERT/ALTER/CREATE.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query para QBO. Ej: 'SELECT * FROM Estimate WHERE CustomerRef.value = \"70\" MAXRESULTS 10'. Usa MAXRESULTS para limitar resultados.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "company info", "información", "datos",
    "preferencias", "preferences", "configuración",
    "consulta", "query", "sql", "qbo query",
    "select", "select * from",
    "leer metadata", "metadata",
    "buscar", "busca", "buscá", "busco", "busqué", "buscando",
    "search", "find", "list", "filter", "count",
    "cuántos", "cuantos", "cuantas", "cuántas",
    "dame", "dáme", "mostrar", "muéstrame", "muestrame",
    "ver", "enseñar", "consultar", "listar",
    "filtra", "filtrame", "filtrar",
    "lista", "listado", "resumen", "detalle",
    "qué", "cual", "cuál", "cuales", "cuáles",
]

FUNCTIONS: Dict[str, Any] = {
    "leer_companyinfo": tool_leer_companyinfo,
    "leer_preferencias": tool_leer_preferencias,
    "consulta_avanzada": tool_consulta_avanzada,
    "qbo_query": tool_qbo_query,
}
