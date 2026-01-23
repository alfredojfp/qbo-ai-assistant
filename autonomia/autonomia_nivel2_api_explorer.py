# -*- coding: utf-8 -*-
import requests
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

QB_ACCESS_TOKEN = os.getenv('QB_ACCESS_TOKEN')
QB_REALM_ID = os.getenv('QB_REALM_ID')
QB_BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{QB_REALM_ID}"

def qbo_generic_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                        params: Optional[Dict] = None, entity_id: Optional[str] = None) -> Dict:
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
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "UPDATE":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            return {"success": False, "error": f"Método {method} no soportado"}

        if response.status_code in [200, 201]:
            return {"success": True, "status_code": response.status_code, "data": response.json()}
        else:
            return {"success": False, "status_code": response.status_code, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}

def create_journal_entry(lines: List[Dict], txn_date: str, memo: str = None) -> Dict:
    total_debit = sum(l['amount'] for l in lines if l['posting_type'] == 'Debit')
    total_credit = sum(l['amount'] for l in lines if l['posting_type'] == 'Credit')

    if abs(total_debit - total_credit) > 0.01:
        return {"success": False, "error": f"Asiento descuadrado: Débitos ${total_debit:.2f} ≠ Créditos ${total_credit:.2f}"}

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

    payload = {"Line": journal_lines, "TxnDate": txn_date}
    if memo:
        payload['PrivateNote'] = memo

    return qbo_generic_request("POST", "JournalEntry", data=payload)

def create_transfer(from_account_id: str, to_account_id: str, amount: float, 
                   txn_date: str, memo: str = None) -> Dict:
    payload = {
        "FromAccountRef": {"value": from_account_id},
        "ToAccountRef": {"value": to_account_id},
        "Amount": amount,
        "TxnDate": txn_date
    }
    if memo:
        payload['PrivateNote'] = memo

    return qbo_generic_request("POST", "Transfer", data=payload)

def tool_create_journal_entry(lines: List[Dict], txn_date: str, memo: str = None) -> dict:
    return create_journal_entry(lines, txn_date, memo)

def tool_create_transfer(from_account_id: str, to_account_id: str, amount: float, 
                        txn_date: str, memo: str = None) -> dict:
    return create_transfer(from_account_id, to_account_id, amount, txn_date, memo)

def tool_qbo_generic_request(method: str, endpoint: str, data: dict = None, entity_id: str = None) -> dict:
    return qbo_generic_request(method, endpoint, data, entity_id=entity_id)

def tool_list_qbo_endpoints() -> dict:
    endpoints = {
        "JournalEntry": "Asientos diarios/contables",
        "Transfer": "Transferencias entre cuentas bancarias",
        "Invoice": "Facturas a clientes",
        "Bill": "Facturas de proveedores",
        "Deposit": "Depósitos bancarios",
        "Payment": "Pagos recibidos"
    }
    return {"success": True, "endpoints_count": len(endpoints), "endpoints": endpoints}

def tool_get_endpoint_info(endpoint_name: str) -> dict:
    info = {
        "JournalEntry": {"description": "Asientos diarios", "methods": ["GET", "POST"]},
        "Transfer": {"description": "Transferencias", "methods": ["GET", "POST"]}
    }
    if endpoint_name in info:
        return {"success": True, "endpoint": endpoint_name, "info": info[endpoint_name]}
    return {"success": False, "error": "Endpoint no encontrado"}
