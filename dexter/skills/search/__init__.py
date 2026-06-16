"""dexter.skills.search — auto-importado de dexter.tools.search."""
from dexter.tools.search import SCHEMA, FUNCTIONS, KEYWORDS
from dexter.skills.search.fuzzy import (
    search_customer,
    search_vendor,
    find_similar_customers,
    find_similar_vendors,
    invalidate_customer_cache,
    invalidate_vendor_cache,
    FUZZY_THRESHOLD,
)
