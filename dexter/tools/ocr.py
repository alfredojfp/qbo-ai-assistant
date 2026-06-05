"""dexter.tools.ocr — 1 tools."""
from typing import Any, Dict, List

from main import (
    tool_procesar_lote_bills,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'procesar_lote_bills', 'description': "Procesa un lote de bills/invoices desde un PDF usando OCR con Gemini. Busca automáticamente en la carpeta 'Pending bills'. Si hay un solo PDF, lo procesa automáticamente. Si hay múltiples, lista los disponibles para que el usuario elija. Extrae: vendor, customer, invoice#, date, total, tax. Genera CSV preview para revisión antes de crear Bills en QuickBooks.", 'parameters': {'type': 'object', 'properties': {'nombre_archivo': {'type': 'string', 'description': "Nombre del archivo PDF a procesar (opcional). Si no se especifica y hay solo 1 PDF en 'Pending bills', se procesa automáticamente. Puede ser nombre parcial (ej: 'okna' encontrará 'DONE-Okna-Invoices-dated1.8.26.pdf')"}}, 'required': []}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["ocr", "pdf", "factura pdf", "pending", "procesar bill", "extraer"]
FUNCTIONS: Dict[str, Any] = {
    "procesar_lote_bills": tool_procesar_lote_bills,
}
