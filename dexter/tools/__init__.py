"""dexter.tools — registry agregador de todas las herramientas.

Cada módulo (bank_feed, search, transactions, etc.) exporta:
    SCHEMA: List[dict]  — schemas para el LLM
    FUNCTIONS: Dict[str, Callable]  — name → callable

Este agregador los itera y construye:
    ALL_SCHEMAS: List[dict]  — para inyectar a OpenRouter
    ALL_FUNCTIONS: Dict[str, Callable]  — para dispatch del function calling
"""
from typing import Any, Callable, Dict, List

from dexter.tools import bank_feed
# Los siguientes módulos se irán agregando en fases posteriores:
# from dexter.tools import search, transactions, reports, tokens, admin,
#     batch, reconciliation, ocr, behavior, report_custom,
#     api_explorer, journal, web_code

ALL_SCHEMAS: List[Dict[str, Any]] = []
ALL_FUNCTIONS: Dict[str, Callable[..., Any]] = {}

_MODULES = [bank_feed]

for _module in _MODULES:
    for _schema in _module.SCHEMA:
        _name = _schema["name"]
        if _name in ALL_FUNCTIONS:
            raise ValueError(
                f"Duplicate tool name '{_name}' in {_module.__name__}"
            )
        ALL_SCHEMAS.append(_schema)
        ALL_FUNCTIONS[_name] = _module.FUNCTIONS[_name]


__all__ = ["ALL_SCHEMAS", "ALL_FUNCTIONS", "bank_feed"]
