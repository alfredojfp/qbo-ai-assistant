"""dexter.error_log — sistema centralizado de logging de errores.

Todos los errores que captura Dexter se persisten en `logs/dexter_errors.log`
(formato JSON Lines, una entrada por línea). Esto permite:

1. Diagnóstico post-mortem: ver qué pasó en una sesión anterior
2. Identificar bugs recurrentes: contar errores por categoría/tool
3. Auditoría: timestamp + contexto completo (user_input, tool, company)

API pública:
    log_error(error, category, user_input=None, tool_name=None,
              company=None, extra=None) -> dict
        Persiste un error. Retorna la entry creada (útil para tests).

    get_recent_errors(n=20) -> List[dict]
        Retorna las últimas N entradas (default 20), más recientes primero.

    tail_log(n=50) -> str
        Formato legible de las últimas N entradas (para mostrar al usuario).

    clear_log() -> None
        Borra el archivo de log (útil para tests).

    setup_logging() -> None
        Inicializa el directorio y handler. Idempotente.

Categorías estándar:
    - api_call:    errores de QBO API (4xx, 5xx)
    - tool_dispatch: errores al ejecutar tool functions
    - user_input:  errores derivados de input inválido
    - auth:        errores de autenticación (token expirado, etc.)
    - unknown:     fallback
"""
from __future__ import annotations

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ============================================================================
# Configuración
# ============================================================================

LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE: Path = LOG_DIR / "dexter_errors.log"
MAX_LOG_BYTES: int = 5 * 1024 * 1024  # 5 MB antes de rotar
LOG_BACKUP_COUNT: int = 3  # mantener 3 backups

CATEGORIES = frozenset({
    "api_call", "tool_dispatch", "user_input", "auth", "unknown",
})

_logger: Optional[logging.Logger] = None
_initialized: bool = False


# ============================================================================
# Inicialización
# ============================================================================

def setup_logging() -> None:
    """Inicializa el directorio de logs y configura el logger con RotatingFileHandler.

    Idempotente: llamar varias veces no duplica handlers.
    """
    global _logger, _initialized
    if _initialized:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    _logger = logging.getLogger("dexter.errors")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(handler)
    _logger.propagate = False  # no duplicar a root logger

    _initialized = True


def _get_logger() -> logging.Logger:
    """Retorna el logger (placeholder — el JSONL se escribe directamente).

    El logger estándar existe solo para mantener la API simétrica con sistemas
    externos. El log real se escribe vía open() en JSONL puro a LOG_FILE.
    """
    if not _initialized:
        setup_logging()
    assert _logger is not None
    return _logger


# ============================================================================
# API principal
# ============================================================================

def log_error(
    error: Union[BaseException, str],
    category: str = "unknown",
    user_input: Optional[str] = None,
    tool_name: Optional[str] = None,
    company: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Persiste un error en el log.

    Args:
        error:       Excepción o string describiendo el error.
        category:    Una de CATEGORIES (default "unknown").
        user_input:  Input del usuario que disparó el error (si aplica).
        tool_name:   Nombre del tool siendo ejecutado (si aplica).
        company:     Empresa activa cuando ocurrió el error.
        extra:       Contexto adicional (status_code, endpoint, etc.).

    Returns:
        La entry creada (dict con todos los campos, incluido timestamp).
    """
    if category not in CATEGORIES:
        # Aceptamos cualquier categoría (CATEGORIES es solo documentación de las
        # estándar). Si llega una desconocida, la guardamos tal cual para que el
        # caller pueda usar categorías custom sin que log_error las sobreescriba.
        pass

    if isinstance(error, BaseException):
        error_type = type(error).__name__
        message = str(error)
        stack = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
    else:
        error_type = "UnknownError"
        message = str(error)
        stack = "".join(traceback.format_stack())

    entry: Dict[str, Any] = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "level": "ERROR",
        "category": category,
        "error_type": error_type,
        "message": message,
        "stack_trace": stack,
    }
    if user_input is not None:
        entry["user_input"] = user_input
    if tool_name is not None:
        entry["tool_name"] = tool_name
    if company is not None:
        entry["company"] = company
    if extra:
        entry["extra"] = extra

    logger = _get_logger()
    # Log JSON-line directo al file (formato puro, sin contaminación del logger)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        # Si no podemos escribir al log, al menos imprimir a stderr
        print(f"[error_log] No se pudo escribir al log: {e}", file=sys.stderr)

    return entry


def get_recent_errors(n: int = 20) -> List[Dict[str, Any]]:
    """Retorna las últimas N entradas del log (más recientes primero).

    Si el log no existe, retorna lista vacía.
    """
    if not LOG_FILE.exists():
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []

    entries: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # skip líneas corruptas

    return entries[-n:]


def tail_log(n: int = 50) -> str:
    """Retorna las últimas N entradas en formato legible para humanos."""
    entries = get_recent_errors(n=n)
    if not entries:
        return "(log vacío)"

    lines: List[str] = []
    lines.append(f"Últimas {len(entries)} entradas de {LOG_FILE}:")
    lines.append("=" * 70)
    for i, e in enumerate(entries, 1):
        lines.append(
            f"[{i}] {e.get('timestamp', '?')}  "
            f"{e.get('level', '?')}  "
            f"{e.get('category', '?')}"
        )
        if e.get("tool_name"):
            lines.append(f"    tool:   {e['tool_name']}")
        if e.get("company"):
            lines.append(f"    company: {e['company']}")
        if e.get("user_input"):
            lines.append(f"    input:  {e['user_input'][:80]}")
        lines.append(
            f"    {e.get('error_type', '?')}: {e.get('message', '')[:200]}"
        )
        lines.append("")

    return "\n".join(lines)


def clear_log() -> None:
    """Borra el archivo de log (útil para tests)."""
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
        except OSError:
            pass


# Inicialización lazy: el primer log_error() o setup_logging() crea el dir.
__all__ = [
    "LOG_DIR", "LOG_FILE", "CATEGORIES",
    "setup_logging", "log_error", "get_recent_errors", "tail_log", "clear_log",
]
