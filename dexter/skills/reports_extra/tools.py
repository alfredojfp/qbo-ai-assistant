"""dexter.skills.reports_extra.tools — 16 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

def tool_reporte_account_list() -> dict:
    """Tool: Genera Account List (lista de cuentas contables)."""
    return generate_account_list_report()



def tool_reporte_ap_aging(fecha_corte: str, metodo_aging: str = "ReportDate",
                          num_periodos: int = 4) -> dict:
    """Tool: Genera A/P Aging Summary (reporte de pagos pendientes por antigüedad)."""
    return generate_ap_aging_report(fecha_corte, metodo_aging, num_periodos)



def tool_reporte_ar_aging(fecha_corte: str, metodo_aging: str = "ReportDate",
                          num_periodos: int = 4) -> dict:
    """Tool: Genera A/R Aging Summary (reporte de cobranzas por antigüedad)."""
    return generate_ar_aging_report(fecha_corte, metodo_aging, num_periodos)



def tool_reporte_cash_flow(fecha_inicio: str, fecha_fin: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera el Statement of Cash Flows."""
    return generate_cash_flow_report(fecha_inicio, fecha_fin, metodo)



def tool_reporte_class_sales(fecha_inicio: str, fecha_fin: str,
                              clase_id: str = None) -> dict:
    """Tool: Genera Sales by Class Summary (ventas agrupadas por clase)."""
    return generate_class_sales_report(fecha_inicio, fecha_fin, clase_id)



def tool_reporte_customer_balance(fecha_corte: str = None, cliente_id: str = None) -> dict:
    """Tool: Genera Customer Balance Summary."""
    return generate_customer_balance_report(fecha_corte, cliente_id)



def tool_reporte_department_sales(fecha_inicio: str, fecha_fin: str,
                                  departamento_id: str = None) -> dict:
    """Tool: Genera Sales by Department Summary (ventas agrupadas por departamento)."""
    return generate_department_sales_report(fecha_inicio, fecha_fin, departamento_id)



def tool_reporte_expenses_by_vendor(fecha_inicio: str, fecha_fin: str,
                                     vendor_id: str = None) -> dict:
    """Tool: Genera Expenses by Vendor Summary (gastos agrupados por proveedor)."""
    return generate_expenses_by_vendor_report(fecha_inicio, fecha_fin, vendor_id)



def tool_reporte_general_ledger(fecha_inicio: str, fecha_fin: str, cuenta_id: str = None,
                                metodo: str = "Accrual") -> dict:
    """Tool: Genera el General Ledger (libro mayor) de la empresa."""
    return generate_general_ledger_report(fecha_inicio, fecha_fin, metodo, cuenta_id)



def tool_reporte_inventory_valuation(fecha_inicio: str = None, fecha_fin: str = None,
                                      item_id: str = None) -> dict:
    """Tool: Genera Inventory Valuation Summary (valorización de inventario)."""
    return generate_inventory_valuation_report(fecha_inicio, fecha_fin, item_id)



def tool_reporte_journal(fecha_inicio: str, fecha_fin: str) -> dict:
    """Tool: Genera Journal Report (todos los asientos en un período)."""
    return generate_journal_report(fecha_inicio, fecha_fin)



def tool_reporte_pl_detail(fecha_inicio: str, fecha_fin: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera Profit & Loss Detail (más granular que P&L)."""
    return generate_pl_detail_report(fecha_inicio, fecha_fin, metodo)



def tool_reporte_sales_by_customer(fecha_inicio: str, fecha_fin: str,
                                    cliente_id: str = None) -> dict:
    """Tool: Genera Sales by Customer Summary (ventas agrupadas por cliente)."""
    return generate_sales_by_customer_report(fecha_inicio, fecha_fin, cliente_id)



def tool_reporte_transaction_list(fecha_inicio: str, fecha_fin: str,
                                   cuenta_id: str = None,
                                   tipo_transaccion: str = None) -> dict:
    """Tool: Genera Transaction List (lista de transacciones filtrable)."""
    return generate_transaction_list_report(fecha_inicio, fecha_fin, cuenta_id, tipo_transaccion)



def tool_reporte_trial_balance(fecha_inicio: str, fecha_fin: str, metodo: str = "Accrual") -> dict:
    """Tool: Genera el Trial Balance (balance de comprobación) de la empresa."""
    return generate_trial_balance_report(fecha_inicio, fecha_fin, metodo)



def tool_reporte_vendor_balance(fecha_corte: str = None, vendor_id: str = None) -> dict:
    """Tool: Genera Vendor Balance Summary."""
    return generate_vendor_balance_report(fecha_corte, vendor_id)



