"""dexter.tools.advanced — 8 tools: Tax, Exchange, Batch, CDC, Budget, Amortización."""
from typing import Any, Dict, List

from main import (
    tool_crear_taxcode,
    tool_crear_taxrate,
    tool_leer_exchange_rate,
    tool_ejecutar_batch,
    tool_cdc_query,
    tool_crear_budget,
    tool_calcular_distribucion,
    tool_ejecutar_distribucion,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "crear_taxcode",
            "description": "Crea un TaxCode en QuickBooks (NON = no tax, TAX = taxed). Asocia opcionalmente un TaxRate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del código (ej: 'IVA 16%', 'EXENTO')"},
                    "tax_rate_id": {"type": "string", "description": "ID del TaxRate a asociar (None = NON)"},
                    "descripcion": {"type": "string"},
                    "activo": {"type": "boolean", "default": True},
                },
                "required": ["nombre"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_taxrate",
            "description": "Crea una tasa de impuesto (TaxRate) en QuickBooks — ej: 16% IVA, 8% Sales Tax.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre de la tasa (ej: 'IVA México 16%')"},
                    "tasa": {"type": "number", "description": "Tasa en porcentaje (ej: 16 para 16%)"},
                    "agencia_id": {"type": "string", "description": "ID de la agencia recaudadora (opcional)"},
                    "descripcion": {"type": "string"},
                    "activo": {"type": "boolean", "default": True},
                },
                "required": ["nombre", "tasa"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "leer_exchange_rate",
            "description": "Lee la tasa de cambio entre dos monedas (currency) en una fecha. Útil para empresas multi-moneda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda_origen": {"type": "string", "description": "Código ISO (ej: 'EUR', 'MXN', 'CAD')"},
                    "moneda_destino": {"type": "string", "default": "USD", "description": "Código ISO destino"},
                    "fecha": {"type": "string", "description": "YYYY-MM-DD (opcional, default: hoy)"},
                },
                "required": ["moneda_origen"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_batch",
            "description": "Ejecuta hasta 30 operaciones QBO en una sola llamada HTTP (batch API). Reduce latencia y mejora atomicidad parcial.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operaciones": {
                        "type": "array",
                        "description": "Lista de operaciones (ej: [{'method': 'POST', 'entity': 'Customer', 'body': {...}}])",
                        "items": {"type": "object"},
                        "maxItems": 30,
                    },
                },
                "required": ["operaciones"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cdc_query",
            "description": "Change Data Capture (CDC): retorna todas las entidades de tipos dados modificadas desde un timestamp. Útil para sync incremental con sistemas externos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entidades": {
                        "type": "array",
                        "description": "Lista de entidades a consultar (ej: ['Customer', 'Invoice', 'Bill'])",
                        "items": {"type": "string"},
                    },
                    "desde": {"type": "string", "description": "Timestamp ISO 8601 (ej: '2026-06-01T00:00:00Z')"},
                },
                "required": ["entidades", "desde"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_budget",
            "description": "Crea un Budget (presupuesto) en QuickBooks con líneas de presupuesto por cuenta y período.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del budget (ej: 'Presupuesto 2026')"},
                    "fecha_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                    "fecha_fin": {"type": "string", "description": "YYYY-MM-DD"},
                    "lineas_presupuesto": {
                        "type": "array",
                        "description": "Líneas con Amount y AccountId por período",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "period": {"type": "string", "description": "YYYY-MM"},
                            },
                        },
                    },
                },
                "required": ["nombre", "fecha_inicio", "fecha_fin", "lineas_presupuesto"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_distribucion",
            "description": "Calcula un plan de amortizacion para distribuir un gasto en N meses. Paso 1 de 2. No crea nada en QBO. Pregunta la cuenta puente (Prepaid Expenses). Ej: distribuir $1200 de 'Travel' en 12 meses via 'Prepaid Expenses'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monto": {"type": "number", "description": "Monto total a distribuir"},
                    "cuenta_origen": {"type": "string", "description": "Nombre de la cuenta de gasto"},
                    "meses": {"type": "integer", "description": "Meses (default 12)"},
                    "cuenta_puente": {"type": "string", "description": "Cuenta puente (Prepaid Expenses, Deferred Charges)"},
                    "fecha_inicio": {"type": "string", "description": "Fecha inicio YYYY-MM-DD (default: 1er dia del mes actual)"},
                },
                "required": ["monto", "cuenta_origen"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_distribucion",
            "description": "Ejecuta el plan de amortizacion generado por calcular_distribucion. Paso 2 de 2. Crea journal entries en QBO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {"type": "object", "description": "Plan generado por calcular_distribucion"},
                },
                "required": ["plan"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "taxcode", "tax code", "código de impuesto", "iva", "sales tax",
    "taxrate", "tax rate", "tasa impuesto", "porcentaje impuesto",
    "exchange rate", "tasa de cambio", "currency", "moneda", "divisa",
    "batch", "lote", "operaciones múltiples", "bulk",
    "cdc", "change data capture", "sync incremental", "delta sync",
    "budget", "presupuesto", "proyección", "forecast",
    "p2", "avanzado", "advanced", "enterprise",
]

FUNCTIONS: Dict[str, Any] = {
    "crear_taxcode": tool_crear_taxcode,
    "crear_taxrate": tool_crear_taxrate,
    "leer_exchange_rate": tool_leer_exchange_rate,
    "ejecutar_batch": tool_ejecutar_batch,
    "cdc_query": tool_cdc_query,
    "crear_budget": tool_crear_budget,
    "calcular_distribucion": tool_calcular_distribucion,
    "ejecutar_distribucion": tool_ejecutar_distribucion,
}
