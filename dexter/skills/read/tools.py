"""dexter.skills.read.tools — 4 tool implementations."""
# NOTA: estas implementaciones fueron movidas desde main.py
# como parte del refactor v5.0 (sistema de skills).

from main import qbo_query

def tool_consulta_avanzada(query: str, start_position: int = 1, max_results: int = 100) -> dict:
    """Tool: Ejecuta una query SQL-like arbitraria en QuickBooks (SELECT only)."""
    return advanced_query(query, start_position, max_results)



def tool_leer_companyinfo() -> dict:
    """Tool: Lee información de la empresa (nombre legal, fiscal year, dirección)."""
    return get_company_info()



def tool_leer_preferencias() -> dict:
    """Tool: Lee las preferencias de configuración de la empresa."""
    return get_preferences()



def tool_qbo_query(query: str) -> dict:
    """Tool: Ejecuta una consulta SQL-like en QBO usando qbo_query real.

    Seguridad: bloquea DROP/DELETE/UPDATE/INSERT/ALTER/CREATE.
    Retorna: {rows: [...], total: N} o {error: ...}
    """
    # Bloquear operaciones destructivas (MISMA whitelist que consulta_avanzada)
    dangerous = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE")
    sql_upper = query.strip().upper()
    for kw in dangerous:
        if sql_upper.startswith(kw) or f" {kw} " in f" {sql_upper} ":
            return {"error": f"Operación rechazada por seguridad: {kw}"}
    result = qbo_query(query)
    if "error" in result:
        return {"error": result["error"]}
    qr = result.get("QueryResponse", {})
    entity_keys = [k for k in qr if k not in ("startPosition", "maxResults", "totalCount", "time")]
    rows = qr.get(entity_keys[0], []) if entity_keys else []
    return {"rows": rows, "total": qr.get("totalCount", len(rows))}



