"""dexter.core.conversation — wrapper de deque(maxlen=N) para historial.

R-5: API limpia sobre el patrón global conversation_history de main.py.

ConversationHistory:
  - append(msg), clear(), recent(n), to_list()
  - __len__, __iter__, __getitem__
  - bounded con maxlen (default 200) — no OOM en sesiones largas
  - __repr__ no leak del contenido (privacidad)

Backward compat: main.py NO se modifica. conversation_history global
de main.py:154 sigue funcionando idéntico. Esta clase es NUEVA y
opcional, para callers que quieran API tipada.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Deque, List


class ConversationHistory:
    """Bounded conversation history (deque-backed).

    Args:
        maxlen: máximo número de mensajes a retener. Default 200
                (igual que CONVERSATION_HISTORY_MAXLEN en main.py).
    """

    DEFAULT_MAXLEN = 200

    def __init__(self, maxlen: int = DEFAULT_MAXLEN):
        if maxlen <= 0:
            raise ValueError(f"maxlen debe ser > 0, got {maxlen}")
        self.maxlen = maxlen
        self._messages: Deque[Any] = deque(maxlen=maxlen)

    def append(self, message: Any) -> None:
        """Agrega un mensaje al final (drop oldest si excede maxlen)."""
        self._messages.append(message)

    def clear(self) -> None:
        """Vacía el historial completamente."""
        self._messages.clear()

    def to_list(self) -> List[Any]:
        """Retorna copia como list (oldest → newest)."""
        return list(self._messages)

    def recent(self, n: int) -> List[Any]:
        """Retorna los últimos n mensajes (oldest → newest).

        Args:
            n: número de mensajes a retornar. Si n >= len, retorna todo.
               Si n == 0, retorna [].

        Raises:
            ValueError: si n < 0.
        """
        if n < 0:
            raise ValueError(f"n debe ser >= 0, got {n}")
        if n == 0:
            return []
        lst = list(self._messages)
        if n >= len(lst):
            return lst
        return lst[-n:]

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self):
        return iter(self._messages)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(self._messages)[index]
        return self._messages[index]

    def __repr__(self) -> str:
        return (
            f"ConversationHistory(len={len(self._messages)}, "
            f"maxlen={self.maxlen})"
        )
