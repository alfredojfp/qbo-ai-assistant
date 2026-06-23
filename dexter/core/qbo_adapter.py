"""QBOAdapter: Implements QBOClientProtocol using Intuit MCP Server.

HIGH-3: bridges Dexter's batch engine and reconciliation skill to
        Intuit's official QBO MCP Server. Translates Dexter's
        lowercase-key interface to MCP tool calls and back.

Argument mapping based on Intuit MCP Zod schemas in
vendor/quickbooks-online-mcp-server/src/tools/*.tool.ts
"""
from typing import Any, Dict, List, Optional

from dexter.core.mcp_bridge import MCPBridge


class QBOAdapter:
    """Implements QBOClientProtocol via Intuit MCP Server."""

    def __init__(self, bridge: MCPBridge):
        self._bridge = bridge

    def start(self):
        self._bridge.start()

    def stop(self):
        self._bridge.stop()

    # ── Customer ───────────────────────────────────────────

    def search_customer(self, name: str) -> List[Dict[str, Any]]:
        args = {
            "criteria": [{"field": "DisplayName", "operator": "LIKE", "value": name}],
        }
        result = self._bridge.call_tool("search_customers", args)
        customers = _extract_list(result)
        results = _adapt_customers(customers)
        if results:
            return results
        from dexter.skills.search.fuzzy import find_similar_customers
        return find_similar_customers(name)

    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        display_name = data.get("DisplayName", data.get("name", ""))
        customer = {"DisplayName": display_name}
        email = data.get("PrimaryEmailAddr")
        if email:
            addr = email.get("Address", email) if isinstance(email, dict) else email
            customer["PrimaryEmailAddr"] = {"Address": addr}
        if data.get("CompanyName"):
            customer["CompanyName"] = data["CompanyName"]
        result = self._bridge.call_tool("create_customer", {"customer": customer})
        cust = result.get("Customer", result)
        return {
            "Id": cust.get("Id", ""),
            "DisplayName": cust.get("DisplayName", display_name),
        }

    # ── Deposit ─────────────────────────────────────────────

    def create_deposit(
        self,
        date: str,
        account_id: str,
        lines: List[Dict[str, Any]],
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        line_items = []
        for item in lines:
            li = {
                "amount": item["amount"],
                "account_ref": item["from_account_id"],
            }
            if item.get("description"):
                li["description"] = item["description"]
            line_items.append(li)

        args: Dict[str, Any] = {
            "deposit_to_account_ref": account_id,
            "line_items": line_items,
        }
        if date:
            args["txn_date"] = date
        if memo:
            args["private_note"] = memo

        result = self._bridge.call_tool("create_deposit", args)
        deposit = result.get("Deposit", result)
        return {
            "deposit_id": deposit.get("Id", ""),
            "total": deposit.get("TotalAmt", 0),
            "date": deposit.get("TxnDate", ""),
        }

    # ── Item ─────────────────────────────────────────────────

    def search_item(self, name: str) -> List[Dict[str, Any]]:
        """Busca items en QBO via Intuit MCP search_items."""
        args = {
            "criteria": [{"field": "Name", "operator": "LIKE", "value": name}],
        }
        result = self._bridge.call_tool("search_items", args)
        items = _extract_list(result)
        results = []
        for it in items:
            results.append({
                "id": it.get("Id", ""),
                "name": it.get("Name", ""),
                "type": it.get("Type", ""),
                "unit_price": float(it.get("UnitPrice", 0)),
                "active": it.get("Active", True),
            })
        return results

    # ── Invoice ──────────────────────────────────────────────

    def update_invoice(self, invoice_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Sparse update de un invoice via Intuit MCP update_invoice."""
        args = {"invoice_id": invoice_id, "patch": patch}
        result = self._bridge.call_tool("update_invoice", args)
        inv = result.get("Invoice", result)
        return {
            "Id": inv.get("Id", ""),
            "DocNumber": inv.get("DocNumber", ""),
            "TotalAmt": inv.get("TotalAmt", 0),
            "Balance": inv.get("Balance", 0),
        }

    # ── Transaction Read/Update ─────────────────────────────

    def get_transactions(
        self, account_id: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        txns = []
        search_args = {"txn_date_from": start_date, "txn_date_to": end_date}
        try:
            deposits = self._bridge.call_tool("search_deposits", search_args)
            for d in _extract_list(deposits):
                txns.append({
                    "id": d.get("Id", ""),
                    "type": "Deposit",
                    "date": d.get("TxnDate", ""),
                    "amount": float(d.get("TotalAmt", 0) or 0),
                    "account_id": d.get("DepositToAccountRef", {}).get("value", ""),
                    "raw": d,
                })
        except Exception:
            pass
        try:
            purchases = self._bridge.call_tool("search_purchases", {})
            for p in _extract_list(purchases):
                txns.append({
                    "id": p.get("Id", ""),
                    "type": "Purchase",
                    "date": p.get("TxnDate", ""),
                    "amount": float(p.get("TotalAmt", 0) or 0),
                    "account_id": p.get("AccountRef", {}).get("value", ""),
                    "raw": p,
                })
        except Exception:
            pass
        return txns

    def update_transaction(
        self,
        txn_type: str,
        txn_id: str,
        fields: Dict[str, Any],
        sync_token: str = "0",
    ) -> Dict[str, Any]:
        tool_map = {
            "Deposit": ("update_deposit", _build_update_deposit),
            "Purchase": ("update_purchase", _build_update_purchase),
            "Bill": ("update_bill", _build_update_bill),
        }
        entry = tool_map.get(txn_type)
        if not entry:
            raise ValueError(f"No MCP tool for transaction type: {txn_type}")
        tool_name, builder = entry
        args = builder(txn_id=txn_id, sync_token=sync_token, fields=fields)
        return self._bridge.call_tool(tool_name, args)


# ── Internal helpers ────────────────────────────────────────

def _extract_list(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract a list from Intuit MCP result (varies by tool)."""
    if isinstance(result, list):
        return result
    for key in ("result", "QueryResponse"):
        if key in result:
            inner = result[key]
            if isinstance(inner, list):
                return inner
            if isinstance(inner, dict):
                for subkey in ("Customer", "Deposit", "Purchase", "Bill"):
                    if subkey in inner and isinstance(inner[subkey], list):
                        return inner[subkey]
    return []


def _adapt_customers(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for c in raw:
        results.append({
            "id": c.get("Id"),
            "name": c.get("DisplayName", ""),
            "company": c.get("CompanyName", ""),
            "balance": float(c.get("Balance", 0)),
            "active": c.get("Active", True),
        })
    return results


def _build_update_deposit(txn_id: str, sync_token: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    args = {"id": txn_id, "sync_token": sync_token}
    if "Memo" in fields:
        # Intuit MCP update_deposit supports private_note, not Memo
        args["private_note"] = fields["Memo"]
    if "PrivateNote" in fields:
        args["private_note"] = fields["PrivateNote"]
    return args


def _build_update_purchase(txn_id: str, sync_token: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    purchase: Dict[str, Any] = {"Id": txn_id, "SyncToken": sync_token}
    if "Memo" in fields:
        purchase["Memo"] = fields["Memo"]
    if "PrivateNote" in fields:
        purchase["PrivateNote"] = fields["PrivateNote"]
    return {"purchase": purchase}


def _build_update_bill(txn_id: str, sync_token: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """update_bill requires full bill object. We build a minimal one."""
    bill: Dict[str, Any] = {"Id": txn_id, "SyncToken": sync_token}
    if "Memo" in fields:
        bill["Memo"] = fields["Memo"]
    if "PrivateNote" in fields:
        bill["PrivateNote"] = fields["PrivateNote"]
    return {"bill": bill}
