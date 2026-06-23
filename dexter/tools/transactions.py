"""dexter.tools.transactions — 7 tools."""
from typing import Any, Dict, List

from main import (
    tool_crear_invoice,
    tool_crear_bill,
    tool_crear_deposito,
    tool_crear_pago,
    tool_crear_cliente,
    tool_agregar_linea_invoice,
    tool_aplicar_customer_deposit,
)

SCHEMA: List[Dict[str, Any]] = [
        {'type': 'function', 'function': {'name': 'crear_invoice', 'description': 'Crea un invoice/factura en QuickBooks. Requiere customer_id y líneas con items.', 'parameters': {'type': 'object', 'properties': {'customer_id': {'type': 'string', 'description': 'ID del cliente (obtener con buscar_cliente)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del invoice', 'items': {'type': 'object', 'properties': {'item_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'quantity': {'type': 'number', 'default': 1}, 'description': {'type': 'string'}}, 'required': ['item_id', 'amount']}}, 'fecha': {'type': 'string', 'description': 'Fecha en formato YYYY-MM-DD (opcional, usa hoy por defecto)'}, 'memo': {'type': 'string', 'description': 'Nota privada (opcional)'}}, 'required': ['customer_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_bill', 'description': 'Crea un bill/cuenta por pagar en QuickBooks. Requiere vendor_id y líneas con cuentas de gasto.', 'parameters': {'type': 'object', 'properties': {'vendor_id': {'type': 'string', 'description': 'ID del vendor (obtener con buscar_vendor)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del bill con cuentas de gasto', 'items': {'type': 'object', 'properties': {'account_id': {'type': 'string', 'description': 'ID de cuenta de gasto'}, 'amount': {'type': 'number'}, 'description': {'type': 'string'}}, 'required': ['account_id', 'amount']}}, 'fecha': {'type': 'string', 'description': 'Fecha YYYY-MM-DD'}, 'fecha_vencimiento': {'type': 'string', 'description': 'Fecha vencimiento YYYY-MM-DD'}, 'memo': {'type': 'string'}}, 'required': ['vendor_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_deposito', 'description': 'Crea un depósito en QuickBooks. Mueve dinero de cuentas origen (ej: Client Retainers) a cuenta destino (ej: Checking).', 'parameters': {'type': 'object', 'properties': {'cuenta_destino_id': {'type': 'string', 'description': 'ID de cuenta bancaria destino (obtener con buscar_cuenta)'}, 'lineas': {'type': 'array', 'description': 'Lista de líneas del depósito', 'items': {'type': 'object', 'properties': {'cuenta_origen_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'customer_id': {'type': 'string', 'description': 'ID cliente (opcional)'}, 'description': {'type': 'string'}}, 'required': ['cuenta_origen_id', 'amount']}}, 'fecha': {'type': 'string'}, 'memo': {'type': 'string'}}, 'required': ['cuenta_destino_id', 'lineas']}}},
        {'type': 'function', 'function': {'name': 'crear_pago', 'description': 'Registra un pago recibido de un cliente en QuickBooks.', 'parameters': {'type': 'object', 'properties': {'customer_id': {'type': 'string'}, 'amount': {'type': 'number'}, 'cuenta_id': {'type': 'string', 'description': 'Cuenta donde se deposita el pago'}, 'fecha': {'type': 'string'}, 'aplicar_a_invoices': {'type': 'array', 'description': 'Lista de invoices a los que aplicar el pago', 'items': {'type': 'object', 'properties': {'invoice_id': {'type': 'string'}, 'amount': {'type': 'number'}}}}}, 'required': ['customer_id', 'amount', 'cuenta_id']}}},
        {'type': 'function', 'function': {'name': 'crear_cliente', 'description': 'Crea un cliente (Customer) en QuickBooks. Solo requiere el nombre (DisplayName). Email, teléfono, dirección y nombre de empresa son opcionales.', 'parameters': {'type': 'object', 'properties': {'nombre': {'type': 'string', 'description': 'Nombre del cliente (DisplayName, único en QBO)'}, 'email': {'type': 'string', 'description': 'Email principal del cliente (opcional)'}, 'telefono': {'type': 'string', 'description': 'Teléfono principal del cliente (opcional)'}, 'direccion': {'type': 'string', 'description': 'Dirección del cliente (opcional)'}, 'empresa': {'type': 'string', 'description': 'Nombre de la empresa del cliente (opcional, distinto del DisplayName)'}}, 'required': ['nombre']}}},
        {'type': 'function', 'function': {'name': 'agregar_linea_invoice', 'description': 'Agrega una línea a un invoice existente (full update). Útil para aplicar Customer Deposits o ajustes que reducen el balance. Busca el item por nombre (fuzzy), hace GET del invoice, agrega la línea, y POST del invoice completo.', 'parameters': {'type': 'object', 'properties': {'invoice_id': {'type': 'string', 'description': 'ID del invoice a modificar'}, 'item_name': {'type': 'string', 'description': 'Nombre del producto/servicio (ej. Customer Deposit)'}, 'amount': {'type': 'number', 'description': 'Monto de la línea. Negativo para reducir el balance del invoice.'}, 'description': {'type': 'string', 'description': 'Descripción opcional de la línea (ej. Aplicación de Customer Deposit)'}}, 'required': ['invoice_id', 'item_name', 'amount']}}},
        {'type': 'function', 'function': {'name': 'aplicar_customer_deposit', 'description': 'Aplica un Customer Deposit al invoice abierto de un cliente. Encadena buscar_cliente → listar_invoices_abiertos → agregar_linea_invoice. Un solo comando. Útil para conciliación de Customer Deposits. Si hay varios invoices abiertos, usa el primero (más antiguo).', 'parameters': {'type': 'object', 'properties': {'client_name': {'type': 'string', 'description': 'Nombre del cliente (fuzzy matching ≥85%)'}, 'amount': {'type': 'number', 'description': 'Monto a aplicar (se convierte a negativo automáticamente)'}, 'item_name': {'type': 'string', 'description': 'Nombre del item (default: Customer Deposit)', 'default': 'Customer Deposit'}}, 'required': ['client_name', 'amount']}}},
]


# Routing keywords — usadas por get_relevant_tools()
KEYWORDS: List[str] = [
    "invoice", "pago", "cobro", "bill", "factura",
    "crear txn", "transaccion", "cliente", "customer", "nuevo cliente",
    "agregar linea", "customer deposit", "aplicar deposito",
    "ajustar invoice", "modificar invoice",
]
FUNCTIONS: Dict[str, Any] = {
    "crear_invoice": tool_crear_invoice,
    "crear_bill": tool_crear_bill,
    "crear_deposito": tool_crear_deposito,
    "crear_pago": tool_crear_pago,
    "crear_cliente": tool_crear_cliente,
    "agregar_linea_invoice": tool_agregar_linea_invoice,
    "aplicar_customer_deposit": tool_aplicar_customer_deposit,
}
