"""dexter.skills.operations.tools — 15 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from main import update_entity

def tool_actualizar_bill(bill_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un bill en QuickBooks."""
    return update_entity("bill", bill_id, cambios, sync_token, sparse=True)



def tool_actualizar_cliente(cliente_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un cliente (Customer) en QuickBooks vía sparse update."""
    return update_entity("customer", cliente_id, cambios, sync_token, sparse=True)



def tool_actualizar_deposit(deposit_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un depósito (Deposit) en QuickBooks. Usa sparse update."""
    return update_entity("deposit", deposit_id, cambios, sync_token, sparse=True)



def tool_actualizar_estimate(estimate_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un estimate (cotización) en QuickBooks.
    
    Usa sparse update: solo envía los campos en 'cambios'.
    Ej: tool_actualizar_estimate('183', {'TxnDate': '2026-05-31'})
    """
    return update_entity("estimate", estimate_id, cambios, sync_token, sparse=True)



def tool_actualizar_factura(invoice_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza una factura (Invoice) en QuickBooks."""
    return update_entity("invoice", invoice_id, cambios, sync_token, sparse=True)



def tool_actualizar_journalentry(journal_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un asiento contable (JournalEntry) en QuickBooks. Usa sparse update."""
    return update_entity("journalentry", journal_id, cambios, sync_token, sparse=True)


# ── Listing tools: listar sin filtro ──


def tool_actualizar_payment(payment_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un pago (Payment) en QuickBooks. Usa sparse update."""
    return update_entity("payment", payment_id, cambios, sync_token, sparse=True)



def tool_actualizar_purchase(purchase_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza una compra (Purchase) en QuickBooks. Usa sparse update."""
    return update_entity("purchase", purchase_id, cambios, sync_token, sparse=True)



def tool_actualizar_vendor(vendor_id: str, cambios: dict, sync_token: str = None) -> dict:
    """Tool: Actualiza un vendor en QuickBooks vía sparse update."""
    return update_entity("vendor", vendor_id, cambios, sync_token, sparse=True)



def tool_desactivar_cliente(cliente_id: str, sync_token: str = None) -> dict:
    """Tool: Desactiva un cliente (soft delete via Active=false)."""
    return deactivate_entity("customer", cliente_id, sync_token)



def tool_desactivar_vendor(vendor_id: str, sync_token: str = None) -> dict:
    """Tool: Desactiva un vendor (soft delete)."""
    return deactivate_entity("vendor", vendor_id, sync_token)



def tool_eliminar_transaccion(tipo: str, transaccion_id: str, sync_token: str) -> dict:
    """Tool: Elimina una transacción (Invoice, Bill, Payment, etc.) vía hard delete."""
    return delete_transaction(tipo, transaccion_id, sync_token)



def tool_enviar_factura(invoice_id: str, email: str = None) -> dict:
    """Tool: Envía una factura (Invoice) por email al cliente."""
    return send_transaction_email("invoice", invoice_id, email)



def tool_enviar_orden_compra(po_id: str, email: str = None) -> dict:
    """Tool: Envía una orden de compra (PurchaseOrder) por email al vendor."""
    return send_transaction_email("purchaseorder", po_id, email)



def tool_void_transaccion(tipo: str, transaccion_id: str, sync_token: str) -> dict:
    """Tool: Anula (void) una transacción sin eliminarla del histórico."""
    return void_transaction(tipo, transaccion_id, sync_token)



