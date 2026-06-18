"""dexter.skills.search.fuzzy — Fuzzy matching de clientes/vendors ≥85%.

Algoritmo de dos pasos:
1. QBO LIKE search (rápido, server-side)
2. Si QBO no encuentra nada → fallback local con SequenceMatcher ≥85%
   contra TODOS los clientes/vendors activos (cache 5 min).

El cache se invalida automáticamente al crear un cliente/vendor nuevo.
"""
import time
from difflib import SequenceMatcher
from typing import Dict, List

FUZZY_THRESHOLD = 0.85

_customer_cache: List[Dict] = None
_customer_cache_time: float = 0.0
_vendor_cache: List[Dict] = None
_vendor_cache_time: float = 0.0


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _token_similarity(query: str, candidate: str) -> float:
    """Token-based fuzzy matching para nombres de personas/empresas.

    Divide en tokens por espacio y para cada token del query busca
    el mejor match en los tokens del candidato. Soporta:
    - Match exacto (token == token) → 1.0
    - Prefijo común (Ben → Benjamin) → 0.90
    - String similarity (SequenceMatcher) → ratio()

    Los tokens de 1 carácter (iniciales como "M" en "Amy M Petersen")
    se ignoran para no penalizar el score.
    Promedia los scores de todos los tokens multi-carácter del query.
    """
    qt = query.lower().split()
    ct = candidate.lower().split()
    if not qt or not ct:
        return _similarity(query, candidate)

    total = 0.0
    count = 0
    for q in qt:
        if len(q) <= 1:
            continue
        count += 1
        best = 0.0
        for c in ct:
            if q == c:
                best = 1.0
                break
            if c.startswith(q) or q.startswith(c):
                best = max(best, 0.90)
            else:
                best = max(best, SequenceMatcher(None, q, c).ratio())
        total += best
    return total / max(count, 1) if count > 0 else _similarity(query, candidate)


def _name_similarity(query: str, candidate: str) -> float:
    """Combina token-based y string-level similarity, tomando el mejor."""
    return max(_token_similarity(query, candidate), _similarity(query, candidate))


def invalidate_customer_cache():
    global _customer_cache, _customer_cache_time
    _customer_cache = None
    _customer_cache_time = 0.0


def invalidate_vendor_cache():
    global _vendor_cache, _vendor_cache_time
    _vendor_cache = None
    _vendor_cache_time = 0.0


def _qbo():
    from main import qbo_query
    return qbo_query


def _get_all_customers() -> List[Dict]:
    global _customer_cache, _customer_cache_time
    now = time.time()
    if _customer_cache is not None and (now - _customer_cache_time) < 300:
        return _customer_cache
    customers = []
    start = 1
    while True:
        sql = f"SELECT * FROM Customer WHERE Active = true MAXRESULTS 1000 STARTPOSITION {start}"
        result = _qbo()(sql)
        if "error" in result:
            break
        batch = result.get("QueryResponse", {}).get("Customer", [])
        if not batch:
            break
        for c in batch:
            customers.append({
                "id": c.get("Id"),
                "name": c.get("DisplayName", ""),
                "company": c.get("CompanyName", ""),
                "balance": float(c.get("Balance", 0)),
                "active": c.get("Active", True),
            })
        if len(batch) < 1000:
            break
        start += 1000
    _customer_cache = customers
    _customer_cache_time = now
    return customers


def _get_all_vendors() -> List[Dict]:
    global _vendor_cache, _vendor_cache_time
    now = time.time()
    if _vendor_cache is not None and (now - _vendor_cache_time) < 300:
        return _vendor_cache
    vendors = []
    start = 1
    while True:
        sql = f"SELECT * FROM Vendor WHERE Active = true MAXRESULTS 1000 STARTPOSITION {start}"
        result = _qbo()(sql)
        if "error" in result:
            break
        batch = result.get("QueryResponse", {}).get("Vendor", [])
        if not batch:
            break
        for v in batch:
            vendors.append({
                "id": v.get("Id"),
                "name": v.get("DisplayName", ""),
                "company": v.get("CompanyName", ""),
                "balance": float(v.get("Balance", 0)),
                "active": v.get("Active", True),
            })
        if len(batch) < 1000:
            break
        start += 1000
    _vendor_cache = vendors
    _vendor_cache_time = now
    return vendors


def find_similar_customers(name: str, threshold: float = None, max_results: int = 5) -> List[Dict]:
    if threshold is None:
        threshold = FUZZY_THRESHOLD
    scored = []
    seen_ids = set()
    for c in _get_all_customers():
        if c["id"] in seen_ids:
            continue
        score = _name_similarity(name, c["name"])
        if score >= threshold:
            seen_ids.add(c["id"])
            scored.append({**c, "_fuzzy_score": round(score, 2)})
    scored.sort(key=lambda x: x["_fuzzy_score"], reverse=True)
    return scored[:max_results]


def find_similar_vendors(name: str, threshold: float = None, max_results: int = 5) -> List[Dict]:
    if threshold is None:
        threshold = FUZZY_THRESHOLD
    scored = []
    seen_ids = set()
    for v in _get_all_vendors():
        if v["id"] in seen_ids:
            continue
        score = _name_similarity(name, v["name"])
        if score >= threshold:
            seen_ids.add(v["id"])
            scored.append({**v, "_fuzzy_score": round(score, 2)})
    scored.sort(key=lambda x: x["_fuzzy_score"], reverse=True)
    return scored[:max_results]


def search_customer(search_term: str, exact: bool = False, fuzzy_fallback: bool = True) -> List[Dict]:
    """Busca clientes en QuickBooks con fuzzy fallback ≥85%."""
    if exact:
        sql = f"SELECT * FROM Customer WHERE DisplayName = '{search_term}'"
    else:
        sql = f"SELECT * FROM Customer WHERE DisplayName LIKE '%{search_term}%'"

    result = _qbo()(sql)

    if "error" in result:
        qbo_results = []
    else:
        customers = result.get("QueryResponse", {}).get("Customer", [])
        qbo_results = []
        for c in customers:
            qbo_results.append({
                "id": c.get("Id"),
                "name": c.get("DisplayName"),
                "company": c.get("CompanyName", ""),
                "balance": float(c.get("Balance", 0)),
                "active": c.get("Active", True),
            })

    if qbo_results:
        return qbo_results

    if fuzzy_fallback and not exact:
        fuzzy = find_similar_customers(search_term)
        if fuzzy:
            return fuzzy

    return []


def search_vendor(search_term: str, exact: bool = False, fuzzy_fallback: bool = True) -> List[Dict]:
    """Busca vendors en QuickBooks con fuzzy fallback ≥85%."""
    if exact:
        sql = f"SELECT * FROM Vendor WHERE DisplayName = '{search_term}'"
    else:
        sql = f"SELECT * FROM Vendor WHERE DisplayName LIKE '%{search_term}%'"

    result = _qbo()(sql)

    if "error" in result:
        qbo_results = []
    else:
        vendors = result.get("QueryResponse", {}).get("Vendor", [])
        qbo_results = []
        for v in vendors:
            qbo_results.append({
                "id": v.get("Id"),
                "name": v.get("DisplayName"),
                "company": v.get("CompanyName", ""),
                "balance": float(v.get("Balance", 0)),
                "active": v.get("Active", True),
            })

    if qbo_results:
        return qbo_results

    if fuzzy_fallback and not exact:
        fuzzy = find_similar_vendors(search_term)
        if fuzzy:
            return fuzzy

    return []
