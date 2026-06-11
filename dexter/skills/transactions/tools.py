"""dexter.skills.transactions.tools — 5 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).


def tool_crear_bill(vendor_id: str, lineas: List[dict], fecha: str = None, 
                   fecha_vencimiento: str = None, memo: str = None) -> dict:
    """Tool: Crea bill"""
    return create_bill(vendor_id, lineas, fecha, fecha_vencimiento, memo)


def tool_crear_cliente(nombre: str, email: str = None, telefono: str = None,
                       direccion: str = None, empresa: str = None) -> dict:
    """Tool: Crea un cliente (Customer) en QuickBooks."""
    return create_customer(nombre, email, telefono, direccion, empresa)



def tool_crear_deposito(cuenta_destino_id: str, lineas: List[dict], fecha: str = None, memo: str = None) -> dict:
    """Tool: Crea depósito"""
    return create_deposit(cuenta_destino_id, lineas, fecha, memo)


def tool_crear_invoice(customer_id: str, lineas: List[dict], fecha: str = None, memo: str = None) -> dict:
    """Tool: Crea invoice"""
    return create_invoice(customer_id, lineas, fecha, memo)


def tool_crear_pago(customer_id: str, amount: float, cuenta_id: str, fecha: str = None,
                   aplicar_a_invoices: List[dict] = None) -> dict:
    """Tool: Crea payment"""
    return create_payment(customer_id, amount, cuenta_id, fecha, aplicar_a_invoices)


