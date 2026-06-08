"""dexter.tools.ocr — 2 tools (OCR lote + CSV corregido)."""
from typing import Any, Dict, List

from main import (
    tool_procesar_lote_bills,
    tool_procesar_csv_corregido,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_lote_bills', 'description': "Procesa un lote de bills/invoices desde un PDF usando OCR con Gemini. Busca automáticamente en la carpeta 'Pending bills'. Extrae: vendor, customer, invoice#, date, total, tax. Genera CSV preview para revisión antes de crear Bills en QuickBooks.", 'parameters': {'type': 'object', 'properties': {'nombre_archivo': {'type': 'string', 'description': "Nombre del archivo PDF a procesar (opcional). Si no se especifica y hay solo 1 PDF en 'Pending bills', se procesa automáticamente."}}, 'required': []}}},
        {'type': 'function', 'function': {'name': 'procesar_csv_corregido', 'description': 'Lee un CSV de bills editado manualmente por Alfredo, detecta correcciones, aprende tips por proveedor, y opcionalmente crea los bills en QBO. Usar después de que Alfredo editó el CSV preview.', 'parameters': {'type': 'object', 'properties': {'csv_path': {'type': 'string', 'description': 'Ruta del CSV editado (ej: Pending bills/preview_bills_20260606.csv)'}, 'crear_bills': {'type': 'boolean', 'description': 'Si true, crea los bills en QBO después de procesar. Default false (solo aprende).', 'default': False}}, 'required': ['csv_path']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["ocr", "pdf", "factura pdf", "pending", "procesar bill", "extraer"]
FUNCTIONS: Dict[str, Any] = {
    "procesar_lote_bills": tool_procesar_lote_bills,
    "procesar_csv_corregido": tool_procesar_csv_corregido,
}
