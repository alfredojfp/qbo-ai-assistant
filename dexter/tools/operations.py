"""dexter.tools.operations — 15 tools para actualizar/void/delete/deactivate/send."""
from typing import Any, Dict, List

from main import (
    tool_actualizar_cliente,
    tool_actualizar_vendor,
    tool_actualizar_factura,
    tool_actualizar_bill,
    tool_actualizar_estimate,
    tool_actualizar_payment,
    tool_actualizar_deposit,
    tool_actualizar_purchase,
    tool_actualizar_journalentry,
    tool_eliminar_transaccion,
    tool_void_transaccion,
    tool_desactivar_cliente,
    tool_desactivar_vendor,
    tool_enviar_factura,
    tool_enviar_orden_compra,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "actualizar_cliente",
            "description": "Actualiza campos de un cliente (Customer) en QuickBooks. Si sync_token no se pasa, se obtiene automáticamente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string", "description": "ID del cliente a actualizar"},
                    "cambios": {
                        "type": "object",
                        "description": "Dict con campos a modificar (DisplayName, PrimaryEmailAddr, Phone, etc.)",
                    },
                    "sync_token": {"type": "string", "description": "SyncToken (se auto-obtiene si se omite)"},
                },
                "required": ["cliente_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_vendor",
            "description": "Actualiza campos de un proveedor (Vendor) en QuickBooks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string"},
                },
                "required": ["vendor_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_factura",
            "description": "Actualiza una factura (Invoice) en QuickBooks. Solo facturas no pagadas se pueden editar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string"},
                },
                "required": ["invoice_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_bill",
            "description": "Actualiza un bill (Bill) en QuickBooks. Solo bills no pagados se pueden editar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bill_id": {"type": "string"},
                    "cambios": {"type": "object"},
                    "sync_token": {"type": "string"},
                },
                "required": ["bill_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_estimate",
            "description": "Actualiza un estimate en QBO via sparse update. Solo envia los campos indicados en cambios. Ej: cambios={'TxnDate': '2026-05-31'}.",
            "parameters": {
                "type": "object",
                "properties": {
                    "estimate_id": {"type": "string", "description": "ID del estimate"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string", "description": "Sync token (opcional)"},
                },
                "required": ["estimate_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "eliminar_transaccion",
            "description": "Elimina (deletes) una transacción en QuickBooks via simplified delete. Soporta: Invoice, Bill, Deposit, Transfer, JournalEntry, CreditMemo, VendorCredit, Purchase, SalesReceipt, RefundReceipt, BillPayment, PurchaseOrder, Estimate, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "description": "Tipo de transacción (ej: 'Invoice', 'Bill', 'Deposit')"},
                    "transaccion_id": {"type": "string", "description": "ID de la transacción"},
                    "sync_token": {"type": "string", "description": "SyncToken (requerido para entidades de doble entrada)"},
                },
                "required": ["tipo", "transaccion_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "void_transaccion",
            "description": "Anula (void) una transacción en QuickBooks. A diferencia de delete, preserva el historial y genera accounting impact inverso.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "description": "Tipo de transacción"},
                    "transaccion_id": {"type": "string"},
                    "sync_token": {"type": "string"},
                },
                "required": ["tipo", "transaccion_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "desactivar_cliente",
            "description": "Desactiva (Active=false) un cliente en QuickBooks. No lo elimina, solo lo oculta de dropdowns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente_id": {"type": "string"},
                    "sync_token": {"type": "string"},
                },
                "required": ["cliente_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "desactivar_vendor",
            "description": "Desactiva (Active=false) un proveedor en QuickBooks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string"},
                    "sync_token": {"type": "string"},
                },
                "required": ["vendor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_factura",
            "description": "Envía una Invoice por email al cliente. Si email no se pasa, usa el del cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string"},
                    "email": {"type": "string", "description": "Email destino (opcional, default: email del cliente)"},
                },
                "required": ["invoice_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_orden_compra",
            "description": "Envía una PurchaseOrder por email al vendor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "po_id": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["po_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_payment",
            "description": "Actualiza un pago (Payment) en QuickBooks via sparse update. Solo envia campos en cambios.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string", "description": "ID del pago"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string", "description": "Sync token (opcional)"},
                },
                "required": ["payment_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_deposit",
            "description": "Actualiza un deposito (Deposit) en QuickBooks via sparse update.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deposit_id": {"type": "string", "description": "ID del deposito"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string", "description": "Sync token (opcional)"},
                },
                "required": ["deposit_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_purchase",
            "description": "Actualiza una compra (Purchase) en QuickBooks via sparse update.",
            "parameters": {
                "type": "object",
                "properties": {
                    "purchase_id": {"type": "string", "description": "ID de la compra"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string", "description": "Sync token (opcional)"},
                },
                "required": ["purchase_id", "cambios"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_journalentry",
            "description": "Actualiza un asiento contable (JournalEntry) en QuickBooks via sparse update.",
            "parameters": {
                "type": "object",
                "properties": {
                    "journal_id": {"type": "string", "description": "ID del asiento"},
                    "cambios": {"type": "object", "description": "Campos a modificar"},
                    "sync_token": {"type": "string", "description": "Sync token (opcional)"},
                },
                "required": ["journal_id", "cambios"],
            },
        },
    },
]

KEYWORDS: List[str] = [
    "actualizar cliente", "modificar cliente", "cambiar cliente", "update customer",
    "actualizar vendor", "modificar proveedor", "update vendor",
    "actualizar factura", "modificar invoice", "update invoice",
    "actualizar bill", "modificar factura proveedor", "update bill",
    "eliminar", "delete", "borrar", "remove",
    "anular", "void", "cancelar transacción",
    "desactivar", "deactivate", "inactivar",
    "enviar", "send", "email", "mandar por correo", "send invoice", "send po",
    "operaciones", "maintenance", "edición",
]

FUNCTIONS: Dict[str, Any] = {
    "actualizar_cliente": tool_actualizar_cliente,
    "actualizar_vendor": tool_actualizar_vendor,
    "actualizar_factura": tool_actualizar_factura,
    "actualizar_bill": tool_actualizar_bill,
    "actualizar_estimate": tool_actualizar_estimate,
    "actualizar_payment": tool_actualizar_payment,
    "actualizar_deposit": tool_actualizar_deposit,
    "actualizar_purchase": tool_actualizar_purchase,
    "actualizar_journalentry": tool_actualizar_journalentry,
    "eliminar_transaccion": tool_eliminar_transaccion,
    "void_transaccion": tool_void_transaccion,
    "desactivar_cliente": tool_desactivar_cliente,
    "desactivar_vendor": tool_desactivar_vendor,
    "enviar_factura": tool_enviar_factura,
    "enviar_orden_compra": tool_enviar_orden_compra,
}
