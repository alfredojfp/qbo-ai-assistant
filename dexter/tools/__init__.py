"""dexter.tools — registry agregador de todas las herramientas.

Cada módulo (bank_feed, search, transactions, etc.) exporta:
    SCHEMA: List[dict]  — schemas para el LLM (formato OpenAI: {type, function:{name,...}})
    FUNCTIONS: Dict[str, Callable]  — name → callable

Este agregador los itera y construye:
    ALL_SCHEMAS: List[dict]  — para inyectar a OpenRouter
    ALL_FUNCTIONS: Dict[str, Callable]  — para dispatch del function calling
"""
from typing import Any, Callable, Dict, List

from dexter.tools import (
    admin,
    api_explorer,
    bank_feed,
    batch,
    behavior,
    journal,
    ocr,
    reconciliation,
    report_custom,
    reports,
    search,
    tokens,
    transactions,
    web_code,
)

ALL_SCHEMAS: List[Dict[str, Any]] = []
ALL_FUNCTIONS: Dict[str, Callable[..., Any]] = {}

_MODULES = [
    search, transactions, reports, tokens, admin, batch,
    reconciliation, ocr, behavior, report_custom, api_explorer,
    journal, web_code, bank_feed,
]


def _extract_name(schema: Dict[str, Any]) -> str:
    """Extrae el nombre de un schema en formato OpenAI ({type:function, function:{name,...}})."""
    if "function" in schema and isinstance(schema["function"], dict):
        return schema["function"]["name"]
    return schema.get("name", "")


for _module in _MODULES:
    for _schema in _module.SCHEMA:
        _name = _extract_name(_schema)
        if not _name:
            raise ValueError(f"Schema sin nombre en {_module.__name__}: {_schema}")
        if _name in ALL_FUNCTIONS:
            raise ValueError(
                f"Duplicate tool name '{_name}' in {_module.__name__}"
            )
        ALL_SCHEMAS.append(_schema)
        ALL_FUNCTIONS[_name] = _module.FUNCTIONS[_name]


__all__ = [
    "ALL_SCHEMAS",
    "ALL_FUNCTIONS",
    "search", "transactions", "reports", "tokens", "admin", "batch",
    "reconciliation", "ocr", "behavior", "report_custom", "api_explorer",
    "journal", "web_code", "bank_feed",
]
