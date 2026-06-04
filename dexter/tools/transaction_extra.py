"""dexter.tools.transaction_extra — 9 tools para crear transacciones faltantes."""
from typing import Any, Dict, List

from main import (
    tool_crear_billpayment,
    tool_crear_estimate,
    tool_crear_salesreceipt,
    tool_crear_creditmemo,
    tool_crear_purchase,
    tool_crear_purchaseorder,
    tool_crear_refundreceipt,
    tool_crear_vendorcredit,
    tool_crear_timeactivity,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "crear_billpayment",
            "description": "Paga uno o más bills (BillPayment) en QuickBooks via Check o CreditCard. Asocia automáticamente a bills específicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "ID del vendor"},
                    "monto_total": {"type": "number", "description": "Monto total del pago"},
                    "tipo_pago": {"type": "string", "enum": ["Check", "CreditCard"], "default": "Check"},
                    "fecha": {"type": "string", "description": "Fecha del pago (YYYY-MM-DD)"},
                    "cuenta_banco_id": {"type": "string", "description": "ID de la cuenta bancaria (para Check)"},
                    "cuenta_cc_id": {"type": "string", "description": "ID de la tarjeta de crédito (para CreditCard)"},
                    "aplicar_a_bills": {
                        "type": "array",
                        "description": "Bills a pagar con sus montos",
                        "items": {
                            "type": "object",
                            "properties": {
                                "bill_id": {"type": "string"},
                                "amount": {"type": "number"},
                            },
                        },
                    },
                    "memo": {"type": "string", "description": "Nota privada"},
                },
                "required": ["vendor_id", "monto_total"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_estimate",
            "description": "Crea una cotización (Estimate) para un cliente. Se puede convertir luego en Invoice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string", "description": "ID del cliente"},
                    "lineas": {
                        "type": "array",
                        "description": "Líneas del estimate",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"},
                            },
                            "required": ["item_id", "amount"],
                        },
                    },
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "fecha_expiracion": {"type": "string", "description": "Fecha de expiración"},
                    "memo": {"type": "string", "description": "Nota privada"},
                },
                "required": ["cliente_id", "lineas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_salesreceipt",
            "description": "Crea un recibo de venta inmediata (SalesReceipt) con pago al momento (ej: venta de mostrador).",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string", "description": "ID del cliente (opcional para venta anónima)"},
                    "lineas": {
                        "type": "array",
                        "description": "Líneas del recibo",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"},
                            },
                            "required": ["item_id", "amount"],
                        },
                    },
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "cuenta_deposito_id": {"type": "string", "description": "Cuenta donde se deposita el dinero"},
                    "metodo_pago_id": {"type": "string", "description": "ID del método de pago"},
                    "memo": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_creditmemo",
            "description": "Crea una nota de crédito (CreditMemo) para reducir el balance de un cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "lineas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"},
                            },
                            "required": ["item_id", "amount"],
                        },
                    },
                    "fecha": {"type": "string"},
                    "memo": {"type": "string"},
                },
                "required": ["cliente_id", "lineas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_purchase",
            "description": "Crea una compra genérica (Purchase) vía cash, check o credit card. Útil para gastos sin bill formal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string"},
                    "cuenta_gasto_id": {"type": "string", "description": "ID de la cuenta de gasto"},
                    "monto": {"type": "number"},
                    "tipo_pago": {"type": "string", "enum": ["Cash", "Check", "CreditCard"], "default": "Cash"},
                    "fecha": {"type": "string"},
                    "descripcion": {"type": "string"},
                    "memo": {"type": "string"},
                },
                "required": ["vendor_id", "cuenta_gasto_id", "monto"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_purchaseorder",
            "description": "Crea una orden de compra (PurchaseOrder) para un vendor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string"},
                    "lineas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"},
                            },
                            "required": ["item_id", "amount"],
                        },
                    },
                    "fecha": {"type": "string"},
                    "direccion_envio": {"type": "string", "description": "ShipTo address"},
                    "memo": {"type": "string"},
                    "email_po": {"type": "string", "description": "Email del vendor para enviar la PO"},
                },
                "required": ["vendor_id", "lineas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_refundreceipt",
            "description": "Crea un recibo de reembolso (RefundReceipt) para devolver dinero a un cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "lineas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "amount": {"type": "number"},
                                "quantity": {"type": "number", "default": 1},
                                "description": {"type": "string"},
                            },
                            "required": ["item_id", "amount"],
                        },
                    },
                    "cuenta_reembolso_id": {"type": "string", "description": "Cuenta de donde sale el reembolso"},
                    "fecha": {"type": "string"},
                    "memo": {"type": "string"},
                },
                "required": ["cliente_id", "lineas", "cuenta_reembolso_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_vendorcredit",
            "description": "Crea un crédito de proveedor (VendorCredit) para reducir el balance que se le debe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string"},
                    "lineas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string", "description": "ID de la cuenta de gasto"},
                                "amount": {"type": "number"},
                                "description": {"type": "string"},
                            },
                            "required": ["account_id", "amount"],
                        },
                    },
                    "fecha": {"type": "string"},
                    "memo": {"type": "string"},
                },
                "required": ["vendor_id", "lineas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_timeactivity",
            "description": "Registra horas trabajadas (TimeActivity) por un empleado para luego facturar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "empleado_id": {"type": "string", "description": "ID del empleado"},
                    "horas": {"type": "integer", "default": 0},
                    "minutos": {"type": "integer", "default": 0},
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "cliente_id": {"type": "string", "description": "Cliente (si es para un cliente)"},
                    "item_id": {"type": "string", "description": "Item/servicio facturable"},
                    "facturable": {"type": "boolean", "default": True},
                    "descripcion": {"type": "string", "description": "Qué se hizo"},
                },
                "required": ["empleado_id"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "pagar bill", "bill payment", "pago de factura", "pago proveedor",
    "estimate", "cotización", "cotizar", "presupuesto",
    "sales receipt", "recibo de venta", "venta inmediata", "venta mostrador",
    "credit memo", "nota de crédito", "devolución cliente",
    "compra", "purchase", "gasto", "cash expense", "check expense",
    "purchase order", "orden de compra", "PO",
    "refund", "reembolso", "devolver dinero",
    "vendor credit", "crédito proveedor",
    "time activity", "horas trabajadas", "registro de tiempo", "timesheet",
]

FUNCTIONS: Dict[str, Any] = {
    "crear_billpayment": tool_crear_billpayment,
    "crear_estimate": tool_crear_estimate,
    "crear_salesreceipt": tool_crear_salesreceipt,
    "crear_creditmemo": tool_crear_creditmemo,
    "crear_purchase": tool_crear_purchase,
    "crear_purchaseorder": tool_crear_purchaseorder,
    "crear_refundreceipt": tool_crear_refundreceipt,
    "crear_vendorcredit": tool_crear_vendorcredit,
    "crear_timeactivity": tool_crear_timeactivity,
}
