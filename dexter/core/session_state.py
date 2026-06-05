"""dexter.core.session_state — wrapper tipado del global session_state.

R-8: API tipada sobre el patrón dict session_state = {...} de main.py:132.

SessionState:
  Atributos tipados:
    .chart_of_accounts (dict)
    .language (str, default 'es')
    .input_tokens, .output_tokens (int, default 0)
    .total_cost (float, default 0.0)
    .start_time (datetime, default now)
    .operations (dict[str, int], default {})
    .last_search_results (dict, default {})
    .saved_reports (dict, default {})
    .current_company (str|None, default None)

  Métodos:
    .to_dict()              # dump all fields
    .get(key, default=None) # dict-style access
    .set(key, value)        # dict-style mutation
    .reset()                # back to defaults

Backward compat: main.py NO se modifica. session_state global de
main.py:132 sigue funcionando idéntico. Esta clase es NUEVA y
opcional, para callers que quieran API tipada (tests, otros módulos).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class SessionState:
    """State tipado de la sesión del usuario.

    Equivalente tipado al dict `session_state` de main.py:132. Cubre
    los campos usados más frecuentes (lenguaje, tokens, chart,
    operaciones, búsqueda, reportes guardados, empresa actual).
    """

    def __init__(self):
        self.chart_of_accounts: Dict[str, Any] = {}
        self.language: str = "es"
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.total_cost: float = 0.0
        self.start_time: datetime = datetime.now()
        self.operations: Dict[str, int] = {}
        self.last_search_results: Dict[str, Any] = {}
        self.saved_reports: Dict[str, Any] = {}
        self.current_company: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Dump todos los campos como dict (start_time como ISO string)."""
        return {
            "chart_of_accounts": self.chart_of_accounts,
            "language": self.language,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost": self.total_cost,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "operations": dict(self.operations),
            "last_search_results": dict(self.last_search_results),
            "saved_reports": dict(self.saved_reports),
            "current_company": self.current_company,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """dict-style access. Búsqueda por nombre de atributo."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """dict-style mutation. Setea atributo por nombre."""
        setattr(self, key, value)

    def reset(self) -> None:
        """Restaura todos los campos a sus defaults."""
        self.chart_of_accounts = {}
        self.language = "es"
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self.start_time = datetime.now()
        self.operations = {}
        self.last_search_results = {}
        self.saved_reports = {}
        self.current_company = None

    def __repr__(self) -> str:
        return (
            f"SessionState(language={self.language!r}, "
            f"company={self.current_company!r}, "
            f"input_tokens={self.input_tokens}, "
            f"output_tokens={self.output_tokens}, "
            f"total_cost={self.total_cost}, "
            f"operations={len(self.operations)})"
        )
