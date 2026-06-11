"""dexter.skills.transaction_extra.tools — 9 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).


def tool_crear_billpayment(vendor_id: str, monto_total: float, tipo_pago: str = "Check",
                           fecha: str = None, cuenta_banco_id: str = None,
                           cuenta_cc_id: str = None, aplicar_a_bills: List[dict] = None,
                           memo: str = None) -> dict:
    """Tool: Paga uno o más bills (BillPayment) en QuickBooks."""
    return create_billpayment(vendor_id, monto_total, tipo_pago, fecha, cuenta_banco_id,
                              cuenta_cc_id, aplicar_a_bills, memo)



def tool_crear_creditmemo(cliente_id: str, lineas: List[dict], fecha: str = None,
                          memo: str = None) -> dict:
    """Tool: Crea una nota de crédito (CreditMemo) para un cliente."""
    return create_creditmemo(cliente_id, lineas, fecha, memo)



def tool_crear_estimate(cliente_id: str, lineas: List[dict], fecha: str = None,
                        fecha_expiracion: str = None, memo: str = None) -> dict:
    """Tool: Crea una cotización (Estimate) en QuickBooks."""
    return create_estimate(cliente_id, lineas, fecha, fecha_expiracion, memo)



def tool_crear_purchase(vendor_id: str, cuenta_gasto_id: str, monto: float,
                        tipo_pago: str = "Cash", fecha: str = None,
                        descripcion: str = None, memo: str = None) -> dict:
    """Tool: Crea una compra genérica (Purchase) por cash, check o tarjeta."""
    return create_purchase(vendor_id, cuenta_gasto_id, monto, tipo_pago, fecha,
                           descripcion, memo)



def tool_crear_purchaseorder(vendor_id: str, lineas: List[dict], fecha: str = None,
                             direccion_envio: str = None, memo: str = None,
                             email_po: str = None) -> dict:
    """Tool: Crea una orden de compra (PurchaseOrder) en QuickBooks."""
    return create_purchaseorder(vendor_id, lineas, fecha, direccion_envio, memo, email_po)



def tool_crear_refundreceipt(cliente_id: str, lineas: List[dict], cuenta_reembolso_id: str,
                             fecha: str = None, memo: str = None) -> dict:
    """Tool: Crea un recibo de reembolso (RefundReceipt) para un cliente."""
    return create_refundreceipt(cliente_id, lineas, cuenta_reembolso_id, fecha, memo)



def tool_crear_salesreceipt(cliente_id: str = None, lineas: List[dict] = None,
                            fecha: str = None, cuenta_deposito_id: str = None,
                            metodo_pago_id: str = None, memo: str = None) -> dict:
    """Tool: Crea un recibo de venta inmediata (SalesReceipt)."""
    return create_salesreceipt(cliente_id, lineas, fecha, cuenta_deposito_id,
                               metodo_pago_id, memo= memo)



def tool_crear_timeactivity(empleado_id: str, horas: int = 0, minutos: int = 0,
                            fecha: str = None, cliente_id: str = None,
                            item_id: str = None, facturable: bool = True,
                            descripcion: str = None) -> dict:
    """Tool: Registra horas trabajadas (TimeActivity)."""
    return create_timeactivity(empleado_id, horas, minutos, fecha, cliente_id,
                               item_id, facturable, descripcion)



def tool_crear_vendorcredit(vendor_id: str, lineas: List[dict], fecha: str = None,
                            memo: str = None) -> dict:
    """Tool: Crea un crédito de proveedor (VendorCredit)."""
    return create_vendorcredit(vendor_id, lineas, fecha, memo)



