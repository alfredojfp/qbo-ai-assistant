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
    advanced,
    api_explorer,
    bank_feed,
    batch,
    behavior,
    journal,
    master_data,
    ocr,
    operations,
    read,
    reconciliation,
    recurring,
    report_custom,
    reports,
    reports_extra,
    search,
    tokens,
    transaction_extra,
    transactions,
    web_code,
)

ALL_SCHEMAS: List[Dict[str, Any]] = []
ALL_FUNCTIONS: Dict[str, Callable[..., Any]] = {}

_MODULES = [
    search, transactions, transaction_extra, master_data, operations,
    reports, reports_extra, read, recurring, advanced,
    tokens, admin, batch,
    reconciliation, ocr, behavior, report_custom, api_explorer,
    journal, web_code, bank_feed,
]

# Routing keywords: mapea cada módulo → keywords que activan sus tools.
# Usado por get_relevant_tools() en main.py para reducir el schema payload
# enviado al LLM (data-driven, no hardcoded).
KEYWORDS_BY_MODULE: Dict[str, List[str]] = {
    mod.__name__: getattr(mod, "KEYWORDS", [])
    for mod in _MODULES
}


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


def verify_tool_integrity(verbose: bool = True) -> dict:
    """Verifica que cada tool_* en main.py esté registrada en dexter.tools.

    Returns:
        dict con:
            - 'ok': bool — True si todo está bien
            - 'total_wrappers': int — wrappers tool_* en main.py
            - 'total_registered': int — tools en ALL_FUNCTIONS
            - 'orphans': list — wrappers en main.py no conectados al registry
            - 'registered_unwired': list — entradas en registry sin schema

    Detecta:
        1. tool_xxx en main.py que NO está en ALL_FUNCTIONS (LLM no lo ve)
        2. ALL_FUNCTIONS con nombre pero sin schema en ALL_SCHEMAS
    """
    import inspect
    result = {
        "ok": True,
        "total_wrappers": 0,
        "total_registered": len(ALL_FUNCTIONS),
        "orphans": [],
        "registered_unwired": [],
        "not_dispatched": [],
        "total_dispatched": 0,
    }

    try:
        import main as _main
    except ImportError:
        return result

    tool_wrappers: Dict[str, Any] = {}
    for name, obj in inspect.getmembers(_main):
        if name.startswith("tool_") and callable(obj):
            bare = name[len("tool_"):]
            tool_wrappers[bare] = obj
    unique_funcs = {id(fn) for fn in tool_wrappers.values()}
    result["total_wrappers"] = len(unique_funcs)

    # 1) Buscar wrappers que no están en ALL_FUNCTIONS (deduplicado por identidad)
    seen_unique: set = set()
    for bare_name, fn in tool_wrappers.items():
        if id(fn) in seen_unique:
            continue
        seen_unique.add(id(fn))
        if fn not in ALL_FUNCTIONS.values():
            result["orphans"].append(f"tool_{bare_name}")

    # 2) Buscar entradas en ALL_FUNCTIONS sin schema
    schema_names = {_extract_name(s) for s in ALL_SCHEMAS}
    for name in ALL_FUNCTIONS:
        if name not in schema_names:
            result["registered_unwired"].append(name)

    # 3) Buscar schemas que NO están en TOOL_FUNCTIONS (LLM los ve, pero dispatch falla)
    if hasattr(_main, "TOOL_FUNCTIONS"):
        dispatch_names = set(_main.TOOL_FUNCTIONS.keys())
        result["total_dispatched"] = len(dispatch_names)
        for sname in schema_names:
            if sname not in dispatch_names:
                result["not_dispatched"].append(sname)

    result["ok"] = not (
        result["orphans"]
        or result["registered_unwired"]
        or result["not_dispatched"]
    )

    if verbose and not result["ok"]:
        import sys
        sys.stderr.write("\n" + "=" * 70 + "\n")
        sys.stderr.write("⚠️  DEXTER TOOLS INTEGRITY CHECK FAILED\n")
        sys.stderr.write("=" * 70 + "\n")
        sys.stderr.write(f"Wrappers tool_* en main.py:  {result['total_wrappers']}\n")
        sys.stderr.write(f"Tools registradas:           {result['total_registered']}\n")
        sys.stderr.write(f"Tools en dispatch (TOOL_FUNCTIONS): {result['total_dispatched']}\n")
        if result["orphans"]:
            sys.stderr.write(
                f"\n❌ {len(result['orphans'])} wrappers HUÉRFANAS (en main.py "
                "pero NO en el registry — el LLM NO las ve):\n"
            )
            for o in result["orphans"]:
                sys.stderr.write(f"   - {o}\n")
        if result["registered_unwired"]:
            sys.stderr.write(
                f"\n❌ {len(result['registered_unwired'])} entradas en "
                "ALL_FUNCTIONS sin schema:\n"
            )
            for u in result["registered_unwired"]:
                sys.stderr.write(f"   - {u}\n")
        if result["not_dispatched"]:
            sys.stderr.write(
                f"\n❌ {len(result['not_dispatched'])} schemas SIN dispatch en "
                "TOOL_FUNCTIONS (LLM los ve pero el dispatch falla → "
                "'Tool no encontrado'):\n"
            )
            for nd in result["not_dispatched"]:
                sys.stderr.write(f"   - {nd}\n")
        sys.stderr.write(
            "\nAcción: agrega los entries faltantes a TOOL_FUNCTIONS en main.py "
            "y/o schemas en dexter/tools/<modulo>.py apropiado.\n"
            + ("=" * 70)
            + "\n\n"
        )
    return result


# Auto-verify on import (warning only, no raise — para no romper import en otros contextos)
try:
    _integrity = verify_tool_integrity(verbose=False)
    if not _integrity["ok"] and __import__("os").getenv("DEXTER_STRICT_INTEGRITY"):
        raise RuntimeError(
            f"Tool integrity check failed: {len(_integrity['orphans'])} orphans, "
            f"{len(_integrity['registered_unwired'])} unwired. "
            "Set DEXTER_STRICT_INTEGRITY=0 to allow degraded mode."
        )
except Exception:  # pragma: no cover
    pass


__all__ = [
    "ALL_SCHEMAS",
    "ALL_FUNCTIONS",
    "KEYWORDS_BY_MODULE",
    "search", "transactions", "transaction_extra", "master_data", "operations",
    "reports", "reports_extra", "read", "recurring", "advanced",
    "tokens", "admin", "batch",
    "reconciliation", "ocr", "behavior", "report_custom", "api_explorer",
    "journal", "web_code", "bank_feed",
]
