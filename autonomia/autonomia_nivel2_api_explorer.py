# -*- coding: utf-8 -*-
"""
API Explorer de QBO - herramientas de autonomía nivel 2.

Componentes:
- QBO_ENDPOINTS: registry estática de endpoints conocidos de QBO API v3
- qbo_generic_request: wrapper sobre HTTP a QBO
- create_journal_entry: valida débitos = créditos antes de crear
- create_transfer: transferencia entre cuentas
- tool_list_qbo_endpoints: lista endpoints con descripción y métodos
- tool_get_endpoint_info: info detallada de un endpoint
- tool_qbo_generic_request: wrapper con manejo de tokens
"""
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

QB_ACCESS_TOKEN = os.getenv('QB_ACCESS_TOKEN')
QB_REALM_ID = os.getenv('QB_REALM_ID')
QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"


# Registry estática de endpoints de QBO API v3
# https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities
QBO_ENDPOINTS: Dict[str, Dict[str, Any]] = {
    "Account": {
        "description": "Cuentas del Chart of Accounts",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "Bill": {
        "description": "Facturas de proveedores (gastos)",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "BillPayment": {
        "description": "Pagos a proveedores",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "Class": {
        "description": "Clases contables (por departamento, proyecto, etc.)",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "CompanyInfo": {
        "description": "Información de la empresa",
        "methods": ["GET"],
        "category": "Configuración",
    },
    "CreditMemo": {
        "description": "Notas de crédito a clientes",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "Customer": {
        "description": "Clientes",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Contactos",
    },
    "Department": {
        "description": "Departamentos de la empresa",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "Deposit": {
        "description": "Depósitos bancarios con splits",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "Employee": {
        "description": "Empleados",
        "methods": ["GET", "POST"],
        "category": "Contactos",
    },
    "Estimate": {
        "description": "Cotizaciones / presupuestos",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "Invoice": {
        "description": "Facturas a clientes (ingresos)",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "Item": {
        "description": "Items y servicios (catálogo)",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "JournalEntry": {
        "description": "Asientos contables / diarios",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "Payment": {
        "description": "Pagos recibidos de clientes",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "PaymentMethod": {
        "description": "Métodos de pago (efectivo, tarjeta, etc.)",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "Purchase": {
        "description": "Compras (gastos directos sin bill)",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "PurchaseOrder": {
        "description": "Órdenes de compra",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "RefundReceipt": {
        "description": "Recibos de reembolso",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "Report": {
        "description": "Reportes (P&L, Balance Sheet, etc.)",
        "methods": ["GET"],
        "category": "Reportes",
    },
    "SalesReceipt": {
        "description": "Recibos de venta (sin invoice)",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
    "TaxCode": {
        "description": "Códigos de impuesto",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "Term": {
        "description": "Términos de pago (Net 30, etc.)",
        "methods": ["GET", "POST"],
        "category": "Configuración",
    },
    "Transfer": {
        "description": "Transferencias entre cuentas bancarias",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Transacciones",
    },
    "Vendor": {
        "description": "Proveedores / vendors",
        "methods": ["GET", "POST", "DELETE"],
        "category": "Contactos",
    },
    "VendorCredit": {
        "description": "Notas de crédito de proveedores",
        "methods": ["GET", "POST"],
        "category": "Transacciones",
    },
}


def qbo_generic_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    entity_id: Optional[str] = None,
) -> Dict:
    """Wrapper genérico sobre QBO API con manejo de tokens y refresh."""
    import requests

    headers = {
        'Authorization': f'Bearer {QB_ACCESS_TOKEN}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if entity_id:
        url = f"{QB_BASE_URL}/{endpoint.lower()}/{entity_id}"
    elif method == "GET" and params and 'query' in params:
        url = f"{QB_BASE_URL}/query"
    else:
        url = f"{QB_BASE_URL}/{endpoint.lower()}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method in ("POST", "UPDATE"):
            # QBO usa POST para update con sparse=true
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            return {"success": False, "error": f"Método {method} no soportado"}

        if response.status_code in (200, 201):
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
            }
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_journal_entry(
    lines: List[Dict],
    txn_date: str,
    memo: str = None,
) -> Dict:
    """
    Crea un asiento contable. Valida que débitos = créditos.

    Args:
        lines: lista de dicts con:
            - account_id (str): ID de cuenta
            - amount (float): monto
            - posting_type (str): "Debit" o "Credit"
            - description (str, opcional)
        txn_date: fecha en formato YYYY-MM-DD
        memo: nota privada del asiento
    """
    if not lines:
        return {"success": False, "error": "Se requiere al menos una línea"}

    total_debit = sum(
        l['amount'] for l in lines if l.get('posting_type') == 'Debit'
    )
    total_credit = sum(
        l['amount'] for l in lines if l.get('posting_type') == 'Credit'
    )

    if abs(total_debit - total_credit) > 0.01:
        return {
            "success": False,
            "error": (
                f"Asiento descuadrado: Débitos ${total_debit:.2f} "
                f"≠ Créditos ${total_credit:.2f}"
            ),
        }

    journal_lines = []
    for line in lines:
        journal_lines.append({
            "DetailType": "JournalEntryLineDetail",
            "Amount": line['amount'],
            "Description": line.get('description', ''),
            "JournalEntryLineDetail": {
                "PostingType": line['posting_type'],
                "AccountRef": {"value": line['account_id']}
            }
        })

    payload: Dict[str, Any] = {
        "Line": journal_lines,
        "TxnDate": txn_date,
    }
    if memo:
        payload['PrivateNote'] = memo

    return qbo_generic_request("POST", "JournalEntry", data=payload)


def create_transfer(
    from_account_id: str,
    to_account_id: str,
    amount: float,
    txn_date: str,
    memo: str = None,
) -> Dict:
    """
    Crea una transferencia entre dos cuentas bancarias.

    Args:
        from_account_id: cuenta origen
        to_account_id: cuenta destino
        amount: monto (positivo)
        txn_date: fecha en formato YYYY-MM-DD
        memo: nota privada
    """
    payload: Dict[str, Any] = {
        "FromAccountRef": {"value": from_account_id},
        "ToAccountRef": {"value": to_account_id},
        "Amount": amount,
        "TxnDate": txn_date,
    }
    if memo:
        payload['PrivateNote'] = memo

    return qbo_generic_request("POST", "Transfer", data=payload)


def tool_create_journal_entry(
    lines: List[Dict],
    txn_date: str,
    memo: str = None,
) -> dict:
    """Crea un asiento contable (valida débitos = créditos)."""
    return create_journal_entry(lines, txn_date, memo)


def tool_create_transfer(
    from_account_id: str,
    to_account_id: str,
    amount: float,
    txn_date: str,
    memo: str = None,
) -> dict:
    """Crea una transferencia entre cuentas bancarias."""
    return create_transfer(from_account_id, to_account_id, amount, txn_date, memo)


def tool_qbo_generic_request(
    method: str,
    endpoint: str,
    data: dict = None,
    params: dict = None,
    entity_id: str = None,
) -> dict:
    """Wrapper genérico para cualquier endpoint de QBO."""
    return qbo_generic_request(method, endpoint, data, params, entity_id)


def tool_list_qbo_endpoints(
    category: Optional[str] = None,
) -> dict:
    """
    Lista todos los endpoints conocidos de QBO API v3.
    Opcionalmente filtra por categoría.
    """
    if category:
        filtered = {
            name: info for name, info in QBO_ENDPOINTS.items()
            if info.get("category", "").lower() == category.lower()
        }
        return {
            "success": True,
            "endpoints_count": len(filtered),
            "category": category,
            "endpoints": filtered,
        }
    return {
        "success": True,
        "endpoints_count": len(QBO_ENDPOINTS),
        "endpoints": QBO_ENDPOINTS,
    }


def tool_get_endpoint_info(endpoint_name: str) -> dict:
    """Retorna información detallada de un endpoint."""
    if endpoint_name in QBO_ENDPOINTS:
        return {
            "success": True,
            "endpoint": endpoint_name,
            "info": QBO_ENDPOINTS[endpoint_name],
        }
    return {
        "success": False,
        "error": f"Endpoint '{endpoint_name}' no encontrado",
        "available": list(QBO_ENDPOINTS.keys()),
    }
