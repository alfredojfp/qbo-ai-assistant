"""dexter.tools.recurring — 2 tools: transacciones recurrentes y adjuntar archivos."""
from typing import Any, Dict, List

from main import (
    tool_crear_recurringtransaction,
    tool_adjuntar_archivo,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "crear_recurringtransaction",
            "description": "Crea una plantilla de transacción recurrente. QuickBooks generará automáticamente transacciones hijas según el intervalo (Monthly, Weekly, Daily, Yearly, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaccion_base": {
                        "type": "object",
                        "description": "Dict con el cuerpo de la transacción base (ej: {'TxnDate': '2026-07-01', 'Line': [...], 'VendorRef': {...}})",
                    },
                    "nombre": {"type": "string", "description": "Nombre de la plantilla (ej: 'Alquiler mensual')"},
                    "tipo_recur": {"type": "string", "enum": ["Automated", "Reminder", "Unscheduled"], "default": "Automated"},
                    "intervalo": {"type": "string", "enum": ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"], "default": "Monthly"},
                    "num_intervalo": {"type": "integer", "default": 1, "description": "Cada cuántos intervalos (ej: 2 = cada 2 meses)"},
                    "fecha_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                    "max_ocurrencias": {"type": "integer", "description": "Máx ocurrencias (None=infinito)"},
                    "dia_del_mes": {"type": "integer", "description": "Día del mes (1-31) para Monthly"},
                    "dias_antes": {"type": "integer", "default": 2, "description": "Días antes de crear la transacción"},
                    "activa": {"type": "boolean", "default": True},
                },
                "required": ["transaccion_base", "nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adjuntar_archivo",
            "description": "Adjunta un archivo (PDF, imagen, doc) a una transacción o entidad de QuickBooks vía upload API multipart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta_archivo": {"type": "string", "description": "Path absoluto al archivo en disco"},
                    "tipo_entidad": {"type": "string", "description": "Tipo de entidad (ej: 'Bill', 'Invoice', 'Customer')"},
                    "id_entidad": {"type": "string", "description": "ID de la entidad"},
                    "nota": {"type": "string", "description": "Nota opcional sobre el adjunto"},
                },
                "required": ["ruta_archivo", "tipo_entidad", "id_entidad"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "recurring", "recurrente", "plantilla", "template", "transacción automática",
    "alquiler mensual", "suscripción", "pago recurrente", "cargo automático",
    "adjuntar", "adjunto", "attachment", "upload", "subir archivo",
    "pdf", "imagen", "scan factura", "escaneo",
    "automático", "automation", "scheduled",
]

FUNCTIONS: Dict[str, Any] = {
    "crear_recurringtransaction": tool_crear_recurringtransaction,
    "adjuntar_archivo": tool_adjuntar_archivo,
}
