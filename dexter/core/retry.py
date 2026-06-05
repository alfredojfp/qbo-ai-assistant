"""dexter.core.retry — retry con backoff exponencial para errores transitorios.

CRIT-4 fix: qbo_request solo manejaba 401 (token refresh). Errores 429 (rate limit)
y 503 (service unavailable) se propagaban inmediatamente, causando cascades
de fallos cuando QBO estaba sobrecargado.

Este módulo provee:
    - retry_request(callable, *args, max_attempts=3, base_delay=1.0, max_delay=4.0, **kwargs)
      Reintenta hasta `max_attempts` veces con backoff exponencial (1s, 2s, 4s).
      Maneja 429/503/Timeout/ConnectionError.
"""
from __future__ import annotations

import time
from typing import Callable, Optional, Tuple, Type

import requests


# Errores HTTP transitorios que ameritan retry
RETRYABLE_STATUS_CODES = (429, 503)

# Excepciones de red que ameritan retry
RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)


def _calculate_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 4.0) -> float:
    """Calcula delay para el intento N: base_delay * 2^attempt, cap a max_delay.

    Ejemplo con base=1.0, max=4.0:
        attempt 0 → 1.0s
        attempt 1 → 2.0s
        attempt 2 → 4.0s
        attempt 3 → 4.0s (cap)
    """
    return min(base_delay * (2 ** attempt), max_delay)


def retry_request(
    request_fn: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 4.0,
    sleep_fn: Optional[Callable[[float], None]] = None,
    **kwargs,
) -> "requests.Response":
    """Ejecuta request_fn con retry automático en errores transitorios.

    Args:
        request_fn: callable que retorna requests.Response (e.g., requests.get).
        *args, **kwargs: argumentos para request_fn.
        max_attempts: número máximo de intentos (default 3).
        base_delay: delay base en segundos (default 1.0).
        max_delay: delay máximo en segundos (default 4.0).
        sleep_fn: función de sleep (default time.sleep; inyectable para tests).
                   Si None, usa time.sleep al momento de la llamada (testable via patch).

    Returns:
        requests.Response del último intento.

    Raises:
        requests.exceptions.Timeout: si todos los intentos agotaron Timeout.
        requests.exceptions.ConnectionError: si todos los intentos agotaron ConnectionError.
        RuntimeError: si el último response no fue exitoso y no fue retryable.

    Note:
        - NO reintenta 401 (ese caso lo maneja qbo_request con token refresh).
        - NO reintenta 4xx (e.g., 400/404 son errores del cliente, no transitorios).
        - Solo reintenta 429/503/Timeout/ConnectionError.
    """
    if sleep_fn is None:
        # Resolver en call-time para que patch("...time.sleep") funcione en tests
        sleep_fn = time.sleep

    last_exc: Optional[Exception] = None
    last_response: Optional["requests.Response"] = None

    for attempt in range(max_attempts):
        try:
            response = request_fn(*args, **kwargs)
        except RETRYABLE_EXCEPTIONS as e:
            last_exc = e
            if attempt < max_attempts - 1:
                sleep_fn(_calculate_backoff(attempt, base_delay, max_delay))
                continue
            raise

        last_response = response

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt < max_attempts - 1:
                sleep_fn(_calculate_backoff(attempt, base_delay, max_delay))
                continue
            # Out of retries — return last response (caller decides what to do)
            return response

        # Success o non-retryable error → return immediately
        return response

    # Should not reach here, but just in case
    if last_response is not None:
        return last_response
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry_request: unexpected state")


__all__ = ["retry_request", "RETRYABLE_STATUS_CODES", "RETRYABLE_EXCEPTIONS"]
