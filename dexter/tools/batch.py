"""dexter.tools.batch — 3 tools.

⚠️  Importa desde main.py (shims), NO desde dexter/skills/batch/tools.py.
Esto es necesario para evitar circular import durante _discover_skills().
Si modificás una implementación, editala en main.py.
"""
from typing import Any, Dict, List

from main import (
    tool_procesar_csv_depositos,
    tool_crear_template_csv,
    tool_depositar_lote_csv,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_csv_depositos', 'description': 'Procesa archivo CSV con múltiples depósitos y los crea en batch.', 'parameters': {'type': 'object', 'properties': {'ruta_archivo': {'type': 'string', 'description': 'Ruta del archivo CSV'}}, 'required': ['ruta_archivo']}}},
        {'type': 'function', 'function': {'name': 'crear_template_csv', 'description': 'Crea archivo CSV template para depósitos batch.', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'depositar_lote_csv', 'description': 'Procesa CSV de deposits multi-cliente con dry-run obligatorio. Columnas requeridas: date, client_name, amount. Opcionales: bank_account (cuenta bancaria destino, ej. "Business Account"), line_account (cuenta contable, ej. "Customer Deposits" — cualquier tipo: Income/Liability/Asset), memo. Si un cliente no existe, pregunta si crearlo (fuzzy ≥85%). Si confirmar=false, solo hace dry-run.', 'parameters': {'type': 'object', 'properties': {'ruta_archivo': {'type': 'string', 'description': 'Ruta al CSV de líneas de deposit'}, 'cuenta_banco_id': {'type': 'string', 'description': 'ID de la cuenta bancaria default (opcional; se auto-detecta)'}, 'cuenta_ingreso_id': {'type': 'string', 'description': 'ID de la cuenta de ingreso default (opcional; se auto-detecta)'}, 'confirmar': {'type': 'boolean', 'description': 'Si False, solo corre dry-run sin crear (default True)', 'default': True}}, 'required': ['ruta_archivo']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["lote", "batch", "csv", "deposito", "depósito", "depositar", "template", "dry-run"]
FUNCTIONS: Dict[str, Any] = {
    "procesar_csv_depositos": tool_procesar_csv_depositos,
    "crear_template_csv": tool_crear_template_csv,
    "depositar_lote_csv": tool_depositar_lote_csv,
}
