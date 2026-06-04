"""dexter.tools._schema_utils — helpers para construir schemas de tool.

Una tool de OpenAI/Anthropic tiene la forma:
    {"name": str, "description": str, "parameters": {"type": "object", "properties": {...}, "required": [...]}}

Estos helpers reducen boilerplate y mantienen consistencia.
"""
from typing import Any, Dict, List, Optional


def make_schema(
    name: str,
    description: str,
    properties: Dict[str, Any],
    required: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Construye un schema de tool con la forma canónica de OpenRouter.

    Args:
        name: nombre único de la tool (snake_case)
        description: qué hace, cuándo usarla, qué retorna (1-3 frases)
        properties: dict de parámetros con sus tipos
        required: lista de nombres de parámetros obligatorios

    Returns:
        Schema listo para enviar al LLM.
    """
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
    }


def prop_str(description: str, enum: Optional[List[str]] = None) -> Dict[str, Any]:
    """Helper para propiedad string."""
    out: Dict[str, Any] = {"type": "string", "description": description}
    if enum is not None:
        out["enum"] = enum
    return out


def prop_num(description: str, minimum: Optional[float] = None) -> Dict[str, Any]:
    """Helper para propiedad number."""
    out: Dict[str, Any] = {"type": "number", "description": description}
    if minimum is not None:
        out["minimum"] = minimum
    return out


def prop_bool(description: str) -> Dict[str, Any]:
    """Helper para propiedad boolean."""
    return {"type": "boolean", "description": description}


def prop_list(description: str, items: Dict[str, Any]) -> Dict[str, Any]:
    """Helper para propiedad array."""
    return {
        "type": "array",
        "description": description,
        "items": items,
    }
