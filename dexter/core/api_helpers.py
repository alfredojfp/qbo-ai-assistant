"""dexter.core.api_helpers — helpers de alto nivel sobre qbo_request.

R-2: extract API surface reutilizable para tools, tests, scripts.

Funciones:
  - post_entity(entity_type, payload, qbo_request_fn=None) → dict
      POST /<entity_lowercase> con payload. Retorna el sub-dict
      de la respuesta (e.g. r.json()['Customer']). En error,
      retorna {'error': ..., 'status': ...}.
  - get_entity(entity_type, entity_id, qbo_request_fn=None) → dict
      GET /<entity_lowercase>/<id>. Mismo shape de retorno.
  - query_with_pagination(sql, page_size=1000, qbo_request_fn=None) → list
      Ejecuta SQL con auto-paginación STARTPOSITION. Retorna lista
      plana de rows (la entidad del QueryResponse).

Backward compat: main.py NO se modifica. Estos helpers son NUEVOS y
opcionales. El default qbo_request_fn es None; si no se pasa, se
intenta usar main.qbo_request (import lazy para evitar circular).
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional


def _default_qbo_request():
    """Import lazy de main.qbo_request para evitar import circular."""
    try:
        from main import qbo_request
        return qbo_request
    except ImportError:
        raise RuntimeError(
            "dexter.core.api_helpers requires main.qbo_request. "
            "Pass qbo_request_fn= explicitly, or run from dexter root."
        )


def _entity_to_endpoint(entity_type: str) -> str:
    """Mapea 'Customer' → 'customer', 'SalesReceipt' → 'salesreceipt'."""
    return entity_type.lower()


def _is_success(status: int) -> bool:
    return 200 <= status < 300


def post_entity(entity_type: str, payload: Dict[str, Any],
                qbo_request_fn: Optional[Callable] = None) -> Dict[str, Any]:
    """POST /<entity>. Retorna sub-dict de la respuesta."""
    fn = qbo_request_fn or _default_qbo_request()
    endpoint = _entity_to_endpoint(entity_type)
    response = fn("POST", endpoint, data=payload)
    if not _is_success(response.status_code):
        return {
            "error": getattr(response, "text", ""),
            "status": response.status_code,
        }
    body = response.json()
    return body.get(entity_type, body)


def get_entity(entity_type: str, entity_id: str,
               qbo_request_fn: Optional[Callable] = None) -> Dict[str, Any]:
    """GET /<entity>/<id>. Retorna sub-dict de la respuesta."""
    fn = qbo_request_fn or _default_qbo_request()
    endpoint = f"{_entity_to_endpoint(entity_type)}/{entity_id}"
    response = fn("GET", endpoint)
    if not _is_success(response.status_code):
        return {
            "error": getattr(response, "text", ""),
            "status": response.status_code,
        }
    body = response.json()
    return body.get(entity_type, body)


_STARTPOSITION_RE = re.compile(r"\bSTARTPOSITION\s+\d+", re.IGNORECASE)


def _inject_startposition(sql: str, position: int) -> str:
    """Inserta/actualiza STARTPOSITION N en el SQL."""
    if _STARTPOSITION_RE.search(sql):
        return _STARTPOSITION_RE.sub(f"STARTPOSITION {position}", sql)
    return f"{sql.rstrip(';').rstrip()} STARTPOSITION {position}"


def _detect_entity_key(qr: Dict[str, Any]) -> Optional[str]:
    """Detecta qué entidad tiene el QueryResponse.

    QBO QueryResponse tiene keys como 'Customer', 'Invoice', 'Bill'.
    También tiene metadata: 'maxResults', 'startPosition', 'time'.
    """
    metadata = {"maxResults", "startPosition", "time", "QueryResponse"}
    for k in qr.keys():
        if k not in metadata:
            return k
    return None


def query_with_pagination(sql: str, page_size: int = 1000,
                          qbo_request_fn: Optional[Callable] = None) -> List[Dict]:
    """Query con auto-paginación. Retorna lista plana de rows.

    Si la SQL no tiene MAXRESULTS, agrega MAXRESULTS page_size.
    Si la respuesta trae page_size filas, sigue paginando con
    STARTPOSITION hasta agotar.
    """
    fn = qbo_request_fn or _default_qbo_request()

    sql_upper = sql.upper()
    if "MAXRESULTS" not in sql_upper:
        sql = f"{sql.rstrip(';').rstrip()} MAXRESULTS {page_size}"

    first = fn("GET", "query", params={"query": sql})
    if not _is_success(first.status_code):
        return []

    aggregated = first.json()
    qr = aggregated.get("QueryResponse", {})

    entity_key = _detect_entity_key(qr)
    if not entity_key:
        return []

    rows = list(qr.get(entity_key, []))

    start_position = len(rows) + 1
    while rows and len(rows) % page_size == 0:
        paged_sql = _inject_startposition(sql, start_position)
        next_resp = fn("GET", "query", params={"query": paged_sql})
        if not _is_success(next_resp.status_code):
            break
        next_qr = next_resp.json().get("QueryResponse", {})
        next_rows = next_qr.get(entity_key, [])
        if not next_rows:
            break
        rows.extend(next_rows)
        start_position += len(next_rows)
        if len(next_rows) < page_size:
            break

    return rows
