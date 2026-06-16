"""dexter.skills.search.tools — 7 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).
# HIGH-1: search_customer / search_vendor ahora viven en fuzzy.py (≥85% match).

from main import qbo_query, find_account, search_item, session_state
from dexter.skills.search.fuzzy import search_customer, search_vendor

def tool_buscar_cliente(nombre: str, exacto: bool = False) -> dict:
    """Tool: Busca cliente por nombre"""
    results = search_customer(nombre, exact=exacto)

    # Guardar en session state para referencia rápida
    session_state["last_search_results"]["customers"] = results

    return {
        "encontrados": len(results),
        "clientes": results[:5]  # Máximo 5 resultados
    }


def tool_buscar_cuenta(termino: str, categoria: str = None) -> dict:
    """Tool: Busca cuenta contable"""
    results = find_account(termino, category=categoria)
    session_state["last_search_results"]["accounts"] = results

    return {
        "encontradas": len(results),
        "cuentas": [{
            "id": acc["id"],
            "numero": acc["number"],
            "nombre": acc["name"],
            "tipo": acc["type"],
            "categoria": acc["category"],
            "balance": acc["balance"],
            "similitud": round(acc.get("match_score", 1.0) * 100, 1)
        } for acc in results[:5]]
    }


def tool_buscar_item(nombre: str) -> dict:
    """Tool: Busca item/servicio"""
    results = search_item(nombre)

    return {
        "encontrados": len(results),
        "items": results[:5]
    }


def tool_buscar_vendor(nombre: str) -> dict:
    """Tool: Busca vendor por nombre"""
    results = search_vendor(nombre)
    session_state["last_search_results"]["vendors"] = results

    return {
        "encontrados": len(results),
        "vendors": results[:5]
    }


def tool_listar_clientes(activos: bool = True, max_results: int = 50) -> dict:
    """Tool: Lista todos los clientes en QBO."""
    filter_clause = "WHERE Active = true" if activos else ""
    result = qbo_query(f"SELECT * FROM Customer {filter_clause} MAXRESULTS {max_results}")
    if "error" in result:
        return result
    rows = result.get("QueryResponse", {}).get("Customer", [])
    return {"total": len(rows), "clientes": [
        {"id": r.get("Id"), "name": r.get("DisplayName", "?"),
         "balance": r.get("Balance", 0), "active": r.get("Active", True)}
        for r in rows
    ]}



def tool_listar_items(max_results: int = 50) -> dict:
    """Tool: Lista todos los items/servicios disponibles en QBO."""
    result = qbo_query(f"SELECT * FROM Item MAXRESULTS {max_results}")
    if "error" in result:
        return result
    rows = result.get("QueryResponse", {}).get("Item", [])
    return {"total": len(rows), "items": [
        {"id": r.get("Id"), "name": r.get("Name", "?"), "type": r.get("Type", "?"),
         "unit_price": r.get("UnitPrice", 0), "active": r.get("Active", True)}
        for r in rows
    ]}



def tool_listar_vendors(activos: bool = True, max_results: int = 50) -> dict:
    """Tool: Lista todos los proveedores en QBO."""
    filter_clause = "WHERE Active = true" if activos else ""
    result = qbo_query(f"SELECT * FROM Vendor {filter_clause} MAXRESULTS {max_results}")
    if "error" in result:
        return result
    rows = result.get("QueryResponse", {}).get("Vendor", [])
    return {"total": len(rows), "vendors": [
        {"id": r.get("Id"), "name": r.get("DisplayName", "?"),
         "balance": r.get("Balance", 0), "active": r.get("Active", True)}
        for r in rows
    ]}


# ── Skill: Distribuir gasto en el tiempo (prepaid expense amortization) ──


