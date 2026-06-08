"""dexter.tools.ocr — 3 tools (OCR lote + CSV corregido + estado cuenta)."""
from typing import Any, Dict, List

from main import (
    tool_procesar_lote_bills,
    tool_procesar_csv_corregido,
    tool_procesar_estado_cuenta,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_lote_bills', 'description': "Procesa un lote de bills/invoices desde un PDF usando OCR con Gemini. Busca automáticamente en la carpeta 'Pending bills'. Extrae: vendor, customer, invoice#, date, total, tax. Genera CSV preview para revisión antes de crear Bills en QuickBooks.", 'parameters': {'type': 'object', 'properties': {'nombre_archivo': {'type': 'string', 'description': "Nombre del archivo PDF a procesar (opcional). Si no se especifica y hay solo 1 PDF en 'Pending bills', se procesa automáticamente."}}, 'required': []}}},
        {'type': 'function', 'function': {'name': 'procesar_csv_corregido', 'description': 'Lee un CSV de bills editado manualmente, detecta correcciones, aprende tips por proveedor, y opcionalmente crea los bills en QBO.', 'parameters': {'type': 'object', 'properties': {'csv_path': {'type': 'string', 'description': 'Ruta del CSV editado'}, 'crear_bills': {'type': 'boolean', 'description': 'Si true, crea los bills en QBO', 'default': False}}, 'required': ['csv_path']}}},
        {'type': 'function', 'function': {'name': 'procesar_estado_cuenta', 'description': 'Convierte un PDF de estado de cuenta bancario a CSV usando OCR. Compatible con cualquier banco (Santander, BBVA, Chase, etc.). Extrae fecha, descripcion, cargo, abono y saldo de cada transaccion.', 'parameters': {'type': 'object', 'properties': {'pdf_path': {'type': 'string', 'description': 'Ruta del PDF del banco'}, 'bank_name': {'type': 'string', 'description': 'Nombre del banco para aplicar tips de extraccion (opcional)'}}, 'required': ['pdf_path']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["ocr", "pdf", "factura pdf", "pending", "procesar bill", "extraer"]
FUNCTIONS: Dict[str, Any] = {
    "procesar_lote_bills": tool_procesar_lote_bills,
    "procesar_csv_corregido": tool_procesar_csv_corregido,
    "procesar_estado_cuenta": tool_procesar_estado_cuenta,
}
