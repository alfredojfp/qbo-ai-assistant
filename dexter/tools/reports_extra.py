"""dexter.tools.reports_extra — 10 tools de reportes nativos de QuickBooks."""
from typing import Any, Dict, List

from main import (
    tool_reporte_trial_balance,
    tool_reporte_general_ledger,
    tool_reporte_cash_flow,
    tool_reporte_ar_aging,
    tool_reporte_ap_aging,
    tool_reporte_customer_balance,
    tool_reporte_vendor_balance,
    tool_reporte_pl_detail,
    tool_reporte_journal,
    tool_reporte_account_list,
)

SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "reporte_trial_balance",
            "description": "Genera Trial Balance (Balance de Comprobación) de QuickBooks. Suma débitos vs créditos por cuenta en un período.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                    "fecha_fin": {"type": "string", "description": "YYYY-MM-DD"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_general_ledger",
            "description": "Genera el libro mayor (General Ledger) con todas las transacciones por cuenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string"},
                    "fecha_fin": {"type": "string"},
                    "cuenta_id": {"type": "string", "description": "Filtrar por cuenta específica (opcional)"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_cash_flow",
            "description": "Genera Cash Flow Statement (Estado de Flujo de Efectivo) clasificado en Operating/Investing/Financing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string"},
                    "fecha_fin": {"type": "string"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_ar_aging",
            "description": "Genera A/R Aging Summary (antigüedad de cuentas por cobrar) — clientes con facturas vencidas agrupadas por 0-30, 31-60, 61-90, 91+ días.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_corte": {"type": "string", "description": "Fecha de corte YYYY-MM-DD"},
                    "metodo_aging": {
                        "type": "string",
                        "enum": ["ReportDate", "DueDate", "TransactionDate"],
                        "default": "ReportDate",
                    },
                },
                "required": ["fecha_corte"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_ap_aging",
            "description": "Genera A/P Aging Summary (antigüedad de cuentas por pagar) — vendors con bills vencidos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_corte": {"type": "string"},
                    "metodo_aging": {"type": "string", "enum": ["ReportDate", "DueDate", "TransactionDate"], "default": "ReportDate"},
                },
                "required": ["fecha_corte"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_customer_balance",
            "description": "Genera Open Customer Balance Detail (balances abiertos por cliente).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_corte": {"type": "string", "description": "YYYY-MM-DD (opcional, default: hoy)"},
                    "cliente_id": {"type": "string", "description": "Filtrar por cliente específico (opcional)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_vendor_balance",
            "description": "Genera Open Vendor Balance Detail (balances abiertos por proveedor).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_corte": {"type": "string"},
                    "vendor_id": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_pl_detail",
            "description": "Genera Profit and Loss Detail (P&L detallado por transacción).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string"},
                    "fecha_fin": {"type": "string"},
                    "metodo": {"type": "string", "enum": ["Accrual", "Cash"], "default": "Accrual"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_journal",
            "description": "Genera Journal Report (todos los journal entries en un período).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string"},
                    "fecha_fin": {"type": "string"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reporte_account_list",
            "description": "Genera Account List (lista completa del Chart of Accounts con saldos).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

KEYWORDS: List[str] = [
    "trial balance", "balance de comprobación", "comprobación",
    "general ledger", "libro mayor", "mayor",
    "cash flow", "flujo de efectivo", "estado de flujo",
    "ar aging", "aging de cobros", "antigüedad por cobrar",
    "ap aging", "aging de pagos", "antigüedad por pagar",
    "customer balance", "balance cliente", "saldo cliente",
    "vendor balance", "balance proveedor", "saldo proveedor",
    "p&l detail", "p&l detallado", "profit and loss detail",
    "journal", "asientos", "journal entries", "pólizas",
    "account list", "lista de cuentas", "chart of accounts listado",
    "reporte nativo", "quickbooks report", "qb report",
]

FUNCTIONS: Dict[str, Any] = {
    "reporte_trial_balance": tool_reporte_trial_balance,
    "reporte_general_ledger": tool_reporte_general_ledger,
    "reporte_cash_flow": tool_reporte_cash_flow,
    "reporte_ar_aging": tool_reporte_ar_aging,
    "reporte_ap_aging": tool_reporte_ap_aging,
    "reporte_customer_balance": tool_reporte_customer_balance,
    "reporte_vendor_balance": tool_reporte_vendor_balance,
    "reporte_pl_detail": tool_reporte_pl_detail,
    "reporte_journal": tool_reporte_journal,
    "reporte_account_list": tool_reporte_account_list,
}
