"""dexter.tools.reconciliation — 3 tools."""
from typing import Any, Dict, List

from main import (
    tool_procesar_reconciliacion_bancaria,
    tool_taggear_reconciliacion,
    tool_limpiar_tags_reconciliacion,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_reconciliacion_bancaria', 'description': 'Procesa CSV de reconciliación bancaria y crea transacciones en QuickBooks. Soporta dos formatos: CON balance (6 columnas con validación completa) o SIN balance (5 columnas con cálculo automático). Columnas obligatorias: date, description, debit, credit. Columnas opcionales: balance, reference.', 'parameters': {'type': 'object', 'properties': {'archivo_csv': {'type': 'string', 'description': 'Ruta del archivo CSV de reconciliación bancaria'}}, 'required': ['archivo_csv']}}},
        {'type': 'function', 'function': {'name': 'taggear_reconciliacion', 'description': 'BNK-RECON tagger: marca transactions existentes en QBO (Deposit.Memo, Bill.PrivateNote, Purchase.PrivateNote) con el tag BNK-RECON-YYYY-MM-xxxxx. NO crea transactions nuevas, solo agrega tags visibles. Útil para reconciliación en QBO UI. Columnas requeridas del CSV: date, description, amount.', 'parameters': {'type': 'object', 'properties': {'archivo_csv': {'type': 'string', 'description': 'Ruta del archivo CSV del bank statement (columnas: date, description, amount)'}, 'cuenta_id': {'type': 'string', 'description': 'ID de la cuenta bancaria en QBO (opcional; se auto-detecta por categoría BANK si se omite)'}, 'fecha_inicio': {'type': 'string', 'description': 'Fecha de inicio del período en formato YYYY-MM-DD (opcional; default: primer día del mes actual)'}, 'fecha_fin': {'type': 'string', 'description': 'Fecha de fin del período en formato YYYY-MM-DD (opcional; default: último día del mes actual)'}, 'dias_fuzzy': {'type': 'integer', 'description': 'Tolerancia en días para fuzzy match (default 2)', 'default': 2}, 'monto_fuzzy': {'type': 'number', 'description': 'Tolerancia en USD para diferencia de monto (default 0.50)', 'default': 0.5}}, 'required': ['archivo_csv']}}},
        {'type': 'function', 'function': {'name': 'limpiar_tags_reconciliacion', 'description': 'Limpia los tags BNK-RECON aplicados por un batch previo. Lee el reporte del batch y borra los Memo/PrivateNote. Útil para deshacer una reconciliación de prueba.', 'parameters': {'type': 'object', 'properties': {'batch_id': {'type': 'string', 'description': 'ID del batch cuyos tags se quieren limpiar'}}, 'required': ['batch_id']}}},
]

FUNCTIONS: Dict[str, Any] = {
    "procesar_reconciliacion_bancaria": tool_procesar_reconciliacion_bancaria,
    "taggear_reconciliacion": tool_taggear_reconciliacion,
    "limpiar_tags_reconciliacion": tool_limpiar_tags_reconciliacion,
}
