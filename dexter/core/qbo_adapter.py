"""QBOAdapter: Implements QBOClientProtocol using Intuit MCP Server.

HIGH-3: bridges Dexter's batch engine and reconciliation skill to
        Intuit's official QBO MCP Server. Translates Dexter's
        lowercase-key interface to MCP tool calls and back.
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

    def search_customer(self, name: str) -> List[Dict[str, Any]]:
        result = self._bridge.call_tool("search_customers", {"searchTerm": name})
        customers = result.get("QueryResponse", {}).get("Customer", [])
        results = []
        for c in customers:
            results.append({
                "id": c.get("Id"),
                "name": c.get("DisplayName", ""),
                "company": c.get("CompanyName", ""),
                "balance": float(c.get("Balance", 0)),
                "active": c.get("Active", True),
            })
        if results:
            return results
        from dexter.skills.search.fuzzy import find_similar_customers
        return find_similar_customers(name)

    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        display_name = data.get("DisplayName", data.get("name", ""))
        args = {"displayName": display_name}
        email = data.get("PrimaryEmailAddr")
        if email:
            if isinstance(email, dict):
                email = email.get("Address", "")
            args["email"] = email
        if data.get("CompanyName"):
            args["companyName"] = data["CompanyName"]
        result = self._bridge.call_tool("create_customer", args)
        cust = result.get("Customer", result)
        return {
            "Id": cust.get("Id", ""),
            "DisplayName": cust.get("DisplayName", display_name),
        }

    def create_deposit(
        self,
        date: str,
        account_id: str,
        lines: List[Dict[str, Any]],
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        deposit_lines = []
        for item in lines:
            line = {
                "amount": item["amount"],
                "accountRef": {"value": item["from_account_id"]},
            }
            if item.get("customer_id"):
                line["entity"] = {
                    "value": item["customer_id"],
                    "type": "Customer",
                }
            if item.get("description"):
                line["description"] = item["description"]
            deposit_lines.append(line)

        args = {
            "depositToAccountRef": {"value": account_id},
            "txnDate": date,
            "line": deposit_lines,
        }
        if memo:
            args["privateNote"] = memo

        result = self._bridge.call_tool("create_deposit", args)
        deposit = result.get("Deposit", result)
        return {
            "deposit_id": deposit.get("Id", ""),
            "total": deposit.get("TotalAmt", 0),
            "date": deposit.get("TxnDate", ""),
        }

    def get_transactions(
        self, account_id: str, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        txns = []
        for txn_type, tool_name in [("Deposit", "search_deposits"), ("Purchase", "search_purchases")]:
            try:
                batch = self._bridge.call_tool(tool_name, {
                    "startDate": start_date,
                    "endDate": end_date,
                })
                for item in batch.get("QueryResponse", {}).get(txn_type, []):
                    txns.append({
                        "id": item.get("Id", ""),
                        "type": txn_type,
                        "date": item.get("TxnDate", ""),
                        "amount": float(item.get("TotalAmt", 0) or 0),
                        "account_id": item.get("DepositToAccountRef", {}).get("value", "")
                        if txn_type == "Deposit"
                        else item.get("AccountRef", {}).get("value", ""),
                        "raw": item,
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
            "Deposit": "update_deposit",
            "Purchase": "update_purchase",
            "Bill": "update_bill",
        }
        tool = tool_map.get(txn_type)
        if not tool:
            raise ValueError(f"No MCP tool for transaction type: {txn_type}")
        args = {"id": txn_id, "syncToken": sync_token, **fields}
        return self._bridge.call_tool(tool, args)
