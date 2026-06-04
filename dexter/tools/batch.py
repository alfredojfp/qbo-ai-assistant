"""dexter.tools.batch — 3 tools."""
from typing import Any, Dict, List

from main import (
    tool_procesar_csv_depositos,
    tool_crear_template_csv,
    tool_depositar_lote_csv,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_csv_depositos', 'description': 'Procesa archivo CSV con múltiples depósitos y los crea en batch.', 'parameters': {'type': 'object', 'properties': {'ruta_archivo': {'type': 'string', 'description': 'Ruta del archivo CSV'}}, 'required': ['ruta_archivo']}}},
        {'type': 'function', 'function': {'name': 'crear_template_csv', 'description': 'Crea archivo CSV template para depósitos batch.', 'parameters': {'type': 'object', 'properties': {}}}},
        {'type': 'function', 'function': {'name': 'depositar_lote_csv', 'description': 'Procesa CSV de deposits multi-cliente usando el motor batch con state machine, disambiguación interactiva y dry-run obligatorio. Columnas requeridas: date, client_name, amount. Si un cliente no existe, pregunta si crearlo. Si confirmar=false, solo hace dry-run sin crear nada en QBO.', 'parameters': {'type': 'object', 'properties': {'ruta_archivo': {'type': 'string', 'description': 'Ruta al CSV de líneas de deposit (date, client_name, amount)'}, 'cuenta_banco_id': {'type': 'string', 'description': 'ID de la cuenta bancaria destino (opcional; se auto-detecta)'}, 'cuenta_ingreso_id': {'type': 'string', 'description': 'ID de la cuenta de ingreso (opcional; se auto-detecta)'}, 'confirmar': {'type': 'boolean', 'description': 'Si False, solo corre dry-run sin crear (default True)', 'default': True}}, 'required': ['ruta_archivo']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["lote", "batch", "depositar csv", "csv depositos", "multiple deposit", "template"]
FUNCTIONS: Dict[str, Any] = {
    "procesar_csv_depositos": tool_procesar_csv_depositos,
    "crear_template_csv": tool_crear_template_csv,
    "depositar_lote_csv": tool_depositar_lote_csv,
}
