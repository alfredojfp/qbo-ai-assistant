# -*- coding: utf-8 -*-
"""
Adapter que conecta la QBOClientProtocol de dexter
con las funciones qbo_query / qbo_request de main.py.

Este módulo se importa desde main.py (NO desde dexter.core.*)
para evitar acoplamiento circular.
"""
import os
from typing import Any, Callable, Dict, List


class QBOClientError(Exception):
    """Error del cliente QBO durante reconcile/get/update."""


def make_qbo_client(
    qbo_query_fn: Callable[[str], Dict[str, Any]],
    qbo_request_fn: Callable[[str, str, dict, dict], Any],
) -> "QBOClientImpl":
    """
    Crea un QBOClientImpl a partir de las funciones de main.py.

    Args:
        qbo_query_fn: La función `qbo_query(sql)` de main.py
        qbo_request_fn: La función `qbo_request(method, endpoint, data, params)` de main.py
    """
    return QBOClientImpl(qbo_query_fn, qbo_request_fn)


class QBOClientImpl:
    """Implementación real de QBOClientProtocol usando qbo_query/request."""

    def __init__(self, qbo_query_fn, qbo_request_fn):
        self._query = qbo_query_fn
        self._request = qbo_request_fn

    def get_transactions(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Trae Deposits + Purchases + Transfers del bank account en el rango.
        """
        txns: List[Dict[str, Any]] = []
        txns.extend(self._fetch_by_type(
            "Deposit", account_id, start_date, end_date
        ))
        txns.extend(self._fetch_by_type(
            "Purchase", account_id, start_date, end_date
        ))
        txns.extend(self._fetch_by_type(
            "Transfer", account_id, start_date, end_date
        ))
        return txns

    def _fetch_by_type(
        self,
        txn_type: str,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Query QBO de un tipo de txn en un rango de fechas."""
        # QBO query: account = 'X' AND txnDate between 'A' and 'B'
        # Para Deposit: Deposit.DepositToAccountRef = 'X'
        # Para Purchase: Purchase.AccountRef = 'X'
        # Para Transfer: Transfer.FromAccountRef = 'X' OR Transfer.ToAccountRef = 'X'
        if txn_type == "Deposit":
            where = f"DepositToAccountRef = '{account_id}'"
        elif txn_type == "Purchase":
            where = f"AccountRef = '{account_id}'"
        elif txn_type == "Transfer":
            where = (
                f"(FromAccountRef = '{account_id}' OR "
                f"ToAccountRef = '{account_id}')"
            )
        else:
            return []

        sql = (
            f"SELECT * FROM {txn_type} WHERE {where} "
            f"AND TxnDate >= '{start_date}' AND TxnDate <= '{end_date}' "
            f"ORDERBY TxnDate ASC"
        )

        result = self._query(sql)
        if not isinstance(result, dict) or "QueryResponse" not in result:
            return []
        raw_list = result["QueryResponse"].get(txn_type, [])
        if not isinstance(raw_list, list):
            return []
        return [self._normalize(txn_type, raw) for raw in raw_list]

    @staticmethod
    def _normalize(txn_type: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte el formato QBO a un formato uniforme para matching."""
        txn_id = raw.get("Id", "")
        date = raw.get("TxnDate", "")
        # Monto: Deposit.TotalAmt, Purchase.TotalAmt, Transfer.Amount
        amount = float(
            raw.get("TotalAmt", 0) or raw.get("Amount", 0) or 0
        )
        # Account ID (de donde sale el dinero)
        if txn_type == "Deposit":
            acc = raw.get("DepositToAccountRef", {}).get("value", "")
        elif txn_type == "Purchase":
            acc = raw.get("AccountRef", {}).get("value", "")
        else:  # Transfer
            acc = raw.get("FromAccountRef", {}).get("value", "")
        return {
            "id": txn_id,
            "type": txn_type,
            "date": date,
            "amount": amount,
            "account_id": acc,
            "raw": raw,
        }

    def update_transaction(
        self,
        txn_type: str,
        txn_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza un campo (Memo o PrivateNote) en una transaction.
        QBO requiere POST con `sparse: true` y el Id.
        """
        # Construir payload con el type discriminador
        payload = {
            "Id": txn_id,
            "sparse": True,
            **fields,
        }
        # syncToken puede ser necesario; usamos "0" como fallback
        # (QBO lo aceptará si es la primera actualización, fallará si no)
        payload["SyncToken"] = "0"

        response = self._request(
            "POST", f"{txn_type.lower()}/{txn_id}", data=payload
        )
        if hasattr(response, "status_code"):
            if response.status_code != 200:
                raise QBOClientError(
                    f"HTTP {response.status_code}: {response.text}"
                )
            try:
                return response.json()
            except Exception:
                return {"raw": response.text}
        return {"raw": str(response)}


def find_bank_account_id(
    find_account_fn: Callable,
    search_terms: List[str] = None,
) -> str:
    """
    Helper: encuentra el ID de la cuenta bancaria principal.
    Busca por términos comunes (en español e inglés).
    """
    if search_terms is None:
        search_terms = [
            "bank", "banco", "checking", "efectivo", "cash",
            "operating", "principal", "general",
        ]
    for term in search_terms:
        results = find_account_fn(term, exact=False, category="BANK")
        if results:
            return results[0]["id"]
    return ""
