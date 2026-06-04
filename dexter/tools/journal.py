"""dexter.tools.journal — 2 tools."""
from typing import Any, Dict, List

from main import (
    tool_create_journal_entry,
    tool_create_transfer,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'crearasientodiario', 'description': 'Crea un Journal Entry (asiento contable) complejo en QuickBooks. Los débitos deben ser iguales a los créditos.', 'parameters': {'type': 'object', 'properties': {'lines': {'type': 'array', 'items': {'type': 'object', 'properties': {'account_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'posting_type': {'type': 'string', 'enum': ['Debit', 'Credit']}, 'description': {'type': 'string'}}, 'required': ['account_id', 'amount', 'posting_type']}}, 'txn_date': {'type': 'string', 'description': 'Fecha YYYY-MM-DD'}, 'memo': {'type': 'string'}}, 'required': ['lines', 'txn_date']}}},
        {'type': 'function', 'function': {'name': 'creartransferencia', 'description': 'Crea una transferencia de fondos entre dos cuentas bancarias en QuickBooks.', 'parameters': {'type': 'object', 'properties': {'from_account_id': {'type': 'string'}, 'to_account_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'txn_date': {'type': 'string'}, 'memo': {'type': 'string'}}, 'required': ['from_account_id', 'to_account_id', 'amount', 'txn_date']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["asiento", "journal", "transferencia", "mover entre cuentas"]
FUNCTIONS: Dict[str, Any] = {
    "crearasientodiario": tool_create_journal_entry,
    "creartransferencia": tool_create_transfer,
}
