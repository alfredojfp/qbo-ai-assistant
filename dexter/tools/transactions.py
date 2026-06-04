"""dexter.tools.transactions — 4 tools."""
from typing import Any, Dict, List

from main import (
    tool_crear_invoice,
    tool_crear_bill,
    tool_crear_deposito,
    tool_crear_pago,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'crear_invoice', 'description': 'Crea un invoice/factura en QuickBooks. Requiere customer_id y líneas con items.', 'parameters': {'type': 'object', 'properties': {'customer_id': {'type': 'string', 'description': 'ID del cliente (obtener con buscar_cliente)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del invoice', 'items': {'type': 'object', 'properties': {'item_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'quantity': {'type': 'number', 'default': 1}, 'description': {'type': 'string'}}, 'required': ['item_id', 'amount']}}, 'fecha': {'type': 'string', 'description': 'Fecha en formato YYYY-MM-DD (opcional, usa hoy por defecto)'}, 'memo': {'type': 'string', 'description': 'Nota privada (opcional)'}}, 'required': ['customer_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_bill', 'description': 'Crea un bill/cuenta por pagar en QuickBooks. Requiere vendor_id y líneas con cuentas de gasto.', 'parameters': {'type': 'object', 'properties': {'vendor_id': {'type': 'string', 'description': 'ID del vendor (obtener con buscar_vendor)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del bill con cuentas de gasto', 'items': {'type': 'object', 'properties': {'account_id': {'type': 'string', 'description': 'ID de cuenta de gasto'}, 'amount': {'type': 'number'}, 'description': {'type': 'string'}}, 'required': ['account_id', 'amount']}}, 'fecha': {'type': 'string', 'description': 'Fecha YYYY-MM-DD'}, 'fecha_vencimiento': {'type': 'string', 'description': 'Fecha vencimiento YYYY-MM-DD'}, 'memo': {'type': 'string'}}, 'required': ['vendor_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_deposito', 'description': 'Crea un depósito en QuickBooks. Mueve dinero de cuentas origen (ej: Client Retainers) a cuenta destino (ej: Checking).', 'parameters': {'type': 'object', 'properties': {'cuenta_destino_id': {'type': 'string', 'description': 'ID de cuenta bancaria destino (obtener con buscar_cuenta)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del depósito', 'items': {'type': 'object', 'properties': {'cuenta_origen_id': {'type': 'string', 'description': 'ID cuenta origen'}, 'amount': {'type': 'number'}, 'customer_id': {'type': 'string', 'description': 'ID cliente (opcional)'}, 'description': {'type': 'string'}}, 'required': ['cuenta_origen_id', 'amount']}}, 'fecha': {'type': 'string'}, 'memo': {'type': 'string'}}, 'required': ['cuenta_destino_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_pago', 'description': 'Registra un pago recibido de un cliente en QuickBooks.', 'parameters': {'type': 'object', 'properties': {'customer_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'cuenta_id': {'type': 'string', 'description': 'Cuenta donde se deposita el pago'}, 'fecha': {'type': 'string'}, 'aplicar_a_invoices': {'type': 'array', 'description': 'Lista de invoices a los que aplicar el pago', 'items': {'type': 'object', 'properties': {'invoice_id': {'type': 'string'}, 'amount': {'type': 'number'}}}}}, 'required': ['customer_id', 'amount', 'cuenta_id']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = ["invoice", "pago", "cobro", "bill", "factura", "crear txn", "transaccion"]
FUNCTIONS: Dict[str, Any] = {
    "crear_invoice": tool_crear_invoice,
    "crear_bill": tool_crear_bill,
    "crear_deposito": tool_crear_deposito,
    "crear_pago": tool_crear_pago,
}
