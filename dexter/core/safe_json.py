"""dexter.core.safe_json — JSONEncoder que maneja tipos no-serializables.

CRIT-5 fix: `json.dumps(result_data)` en main.py fallaba con `TypeError` cuando
un tool retornaba Decimal, datetime, Path, UUID, set u objetos custom.

Este módulo provee:
    - DexterJSONEncoder: subclase de json.JSONEncoder con default() que convierte
      tipos comunes a representaciones JSON-safe.
    - safe_dumps(obj, **kwargs): wrapper de json.dumps con ensure_ascii=False
      y cls=DexterJSONEncoder.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID


class DexterJSONEncoder(json.JSONEncoder):
    """JSONEncoder que maneja tipos contables comunes no-serializables.

    Conversiones (en orden):
        Decimal    → float
        datetime   → ISO 8601 string
        date       → ISO 8601 string
        Path       → str (string representation)
        UUID       → str (hex format)
        set/frozenset → list
        bytes     → str (decoded utf-8 con fallback a repr)
        Otros     → str() (fallback final)
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                return repr(obj)
        return str(obj)


def safe_dumps(obj: Any, **kwargs) -> str:
    """Wrapper de json.dumps con DexterJSONEncoder.

    Garantiza:
        - ensure_ascii=False por defecto (preserva acentos/ñ/ü)
        - Maneja Decimal, datetime, date, Path, UUID, set, bytes
        - Fallback a str() para objetos custom
    """
    kwargs.setdefault("ensure_ascii", False)
    kwargs.setdefault("cls", DexterJSONEncoder)
    return json.dumps(obj, **kwargs)


__all__ = ["DexterJSONEncoder", "safe_dumps"]
