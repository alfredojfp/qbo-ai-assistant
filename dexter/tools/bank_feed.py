"""dexter.tools.bank_feed — 4 tools para análisis y clasificación de bank feeds.

Delega a autonomia.bank_feed_intelligence (motor de matching en cascada).
Los schemas aquí son los mismos que estaban en main.py TOOLS (preservamos
contrato externo con el LLM).
"""
from typing import Any, Dict, List

from autonomia.bank_feed_intelligence import (
    tool_analyze_bank_feed_for_classification,
    tool_find_pattern_for_transaction,
    tool_get_classification_history_stats,
    tool_record_bank_feed_classification,
)
from dexter.tools._schema_utils import (
    make_schema,
    prop_list,
    prop_num,
    prop_str,
)

SCHEMA: List[Dict[str, Any]] = [
    make_schema(
        name="analizarbankfeed",
        description=(
            "Analiza una lista de transacciones bancarias para sugerir "
            "clasificaciones contables basadas en aprendizaje previo. "
            "Retorna: análisis con sugerencias por transacción, confidence "
            "(0-100%), account sugerido."
        ),
        properties={
            "account_name": prop_str("Nombre de la cuenta QBO (ej. 'Chase Checking')"),
            "transactions": prop_list(
                "Lista de transacciones a analizar",
                items={"type": "object"},
            ),
            "min_confidence": prop_num(
                "Confianza mínima 0-1 (default 0.7)",
                minimum=0.0,
            ),
        },
        required=["account_name", "transactions"],
    ),
    make_schema(
        name="registrarclasificacion",
        description=(
            "Registra el aprendizaje de una clasificación manual hecha por el "
            "usuario. Aumenta el contador del patrón (idempotente). El motor "
            "usa estos datos para sugerir clasificaciones futuras."
        ),
        properties={
            "description": prop_str("Descripción original de la transacción"),
            "account_id": prop_str("QBO account ID destino"),
            "account_name": prop_str("QBO account name destino"),
            "amount": prop_num("Monto en USD (positivo=ingreso, negativo=gasto)"),
            "date": prop_str("Fecha ISO YYYY-MM-DD"),
            "vendor": prop_str("QBO vendor ID (opcional)"),
            "qb_suggestion": prop_str("Sugerencia original del motor (opcional)"),
        },
        required=["description", "account_id", "account_name", "amount", "date"],
    ),
    make_schema(
        name="estadisticasclasificacion",
        description=(
            "Obtiene estadísticas sobre el aprendizaje del sistema de "
            "clasificación bancaria. Retorna: total clasificaciones "
            "registradas, patrones aprendidos, accuracy promedio."
        ),
        properties={},
        required=[],
    ),
    make_schema(
        name="buscarpatron",
        description=(
            "Busca si existe un patrón de clasificación previo para una "
            "descripción dada. Retorna match_found (bool), confidence "
            "(0-100), y el patrón matched (exacto/regex/fuzzy/default)."
        ),
        properties={
            "description": prop_str(
                "Descripción a buscar (ej. 'AMAZON.COM*123456')"
            ),
        },
        required=["description"],
    ),
]

FUNCTIONS: Dict[str, Any] = {
    "analizarbankfeed": tool_analyze_bank_feed_for_classification,
    "registrarclasificacion": tool_record_bank_feed_classification,
    "estadisticasclasificacion": tool_get_classification_history_stats,
    "buscarpatron": tool_find_pattern_for_transaction,
}
